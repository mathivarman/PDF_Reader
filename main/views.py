from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
import uuid
from datetime import datetime
import logging

from .models import Document, Analysis, UserSession
from .forms import DocumentUploadForm
from .services import DocumentProcessingService, UserSessionService, DocumentManagementService
from .performance_monitor import performance_monitor, check_memory_usage, check_disk_space, get_performance_alerts
from .cache_manager import CacheManager

logger = logging.getLogger(__name__)

# Create your views here.

def home(request):
    """Home page view for the AI Legal Document Explainer."""
    context = {
        'title': 'AI Legal Document Explainer',
        'description': 'Upload legal documents and get AI-powered analysis, clause detection, and risk assessment',
    }
    return render(request, 'main/home.html', context)

def upload_document(request):
    """Handle document upload with validation and processing."""
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Create user session if not exists
                session_id = request.session.get('session_id')
                if not session_id:
                    session_id = str(uuid.uuid4())
                    request.session['session_id'] = session_id
                
                # Get or create user session using service
                user_session = UserSessionService.get_or_create_session(session_id)
                
                # Create document record
                document = form.save(commit=False)
                document.file_size = document.file.size
                document.original_filename = document.file.name
                
                # Set title to filename if not provided
                if not document.title:
                    # Extract filename without extension
                    filename = os.path.splitext(document.file.name)[0]
                    # Remove path and use just the filename
                    filename = os.path.basename(filename)
                    document.title = filename
                
                document.user_session = user_session
                document.status = 'uploaded'
                document.save()
                
                # Process document in background (for now, we'll do it synchronously)
                processing_result = DocumentProcessingService.process_document(document.id)
                
                if processing_result.get('success'):
                    messages.success(request, f'Document "{document.title}" uploaded and processed successfully!')
                else:
                    messages.warning(request, f'Document uploaded but processing failed: {processing_result.get("error")}')
                
                return redirect('main:document_detail', document_id=document.id)
                
            except Exception as e:
                logger.error(f"Error in upload_document: {e}")
                messages.error(request, f'Error uploading file: {str(e)}')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    
    else:
        form = DocumentUploadForm()
    
    return render(request, 'main/upload.html', {'form': form})

def document_detail(request, document_id):
    """Display document details and analysis results."""
    try:
        # Get analysis data using service
        analysis_data = DocumentProcessingService.get_document_analysis(document_id)
        
        if 'error' in analysis_data:
            messages.error(request, analysis_data['error'])
            return redirect('main:home')
        
        context = {
            'document': analysis_data['document'],
            'analysis': analysis_data['analysis'],
            'chunks': analysis_data['chunks'],
            'clauses': analysis_data.get('clauses', []),
            'red_flags': analysis_data.get('red_flags', []),
        }
        return render(request, 'main/document_detail_enhanced.html', context)
        
    except Exception as e:
        logger.error(f"Error in document_detail: {e}")
        messages.error(request, 'Error loading document details.')
        return redirect('main:home')

def document_list(request):
    """Display list of uploaded documents."""
    session_id = request.session.get('session_id')
    
    # Create session if not exists
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session['session_id'] = session_id
        logger.info(f"Created new session: {session_id}")
    
    if session_id:
        documents = UserSessionService.get_user_documents(session_id)
        stats = DocumentManagementService.get_document_stats(session_id)
        logger.info(f"Session {session_id}: Found {len(documents)} documents")
    else:
        documents = []
        stats = {
            'total_documents': 0,
            'processed_documents': 0,
            'pending_documents': 0,
            'total_pages': 0,
            'total_size_mb': 0,
            'average_pages': 0
        }
    
    context = {
        'documents': documents,
        'stats': stats,
    }
    return render(request, 'main/document_list.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def upload_progress(request):
    """Handle AJAX upload progress updates."""
    try:
        # This would be implemented with JavaScript for real-time progress
        # For now, return a simple status
        return JsonResponse({
            'status': 'success',
            'message': 'Upload in progress...'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

def process_document(request, document_id):
    """Process a document manually."""
    try:
        result = DocumentProcessingService.process_document(document_id)
        
        if result.get('success'):
            messages.success(request, 'Document processed successfully!')
        else:
            messages.error(request, f'Processing failed: {result.get("error")}')
            
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {e}")
        messages.error(request, 'Error processing document.')
    
    return redirect('main:document_detail', document_id=document_id)

@require_http_methods(["POST"])
def delete_document(request, document_id):
    """Delete a document."""
    logger.info(f"Delete request received for document {document_id}")
    
    # For debugging, also log the request method and headers
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    session_id = request.session.get('session_id')
    logger.info(f"Session ID: {session_id}")
    
    if not session_id:
        logger.error("No session ID found")
        return JsonResponse({'error': 'Session not found'}, status=400)
    
    try:
        result = DocumentManagementService.delete_document(document_id, session_id)
        logger.info(f"Delete result: {result}")
        
        if result.get('success'):
            messages.success(request, result['message'])
            return JsonResponse({'success': True, 'message': result['message']})
        else:
            logger.error(f"Delete failed: {result.get('error')}")
            return JsonResponse({'error': result.get('error')}, status=400)
    except Exception as e:
        logger.error(f"Exception in delete_document: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def performance_dashboard(request):
    """Display system performance metrics and monitoring data."""
    try:
        # Get system statistics
        system_stats = performance_monitor.get_system_stats()
        performance_summary = performance_monitor.get_performance_summary()
        
        # Get resource usage
        memory_usage = check_memory_usage()
        disk_space = check_disk_space()
        
        # Get performance alerts
        alerts = get_performance_alerts()
        
        # Get cache statistics
        cache_stats = CacheManager.get_cache_stats()
        
        # Get document statistics
        session_id = request.session.get('session_id')
        if session_id:
            doc_stats = DocumentManagementService.get_document_stats(session_id)
        else:
            doc_stats = {
                'total_documents': 0,
                'processed_documents': 0,
                'pending_documents': 0,
                'total_pages': 0,
                'total_size_mb': 0,
                'average_pages': 0
            }
        
        context = {
            'system_stats': system_stats,
            'performance_summary': performance_summary,
            'memory_usage': memory_usage,
            'disk_space': disk_space,
            'alerts': alerts,
            'cache_stats': cache_stats,
            'document_stats': doc_stats,
        }
        
        return render(request, 'main/performance_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error in performance dashboard: {e}")
        messages.error(request, 'Error loading performance dashboard.')
        return redirect('main:home')
