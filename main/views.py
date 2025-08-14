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

from .models import Document, Analysis, UserSession, Question, Answer, Citation, DocumentChunk
from .forms import DocumentUploadForm
from .services import DocumentProcessingService, UserSessionService, DocumentManagementService
from .performance_monitor import performance_monitor, check_memory_usage, check_disk_space, get_performance_alerts
from .cache_manager import CacheManager
from .semantic_search import semantic_search_engine
from .enhanced_qa_service import enhanced_qa_service
from .advanced_semantic_search import advanced_semantic_search_engine
from .performance_optimizer import performance_optimizer
from .security import security_validator

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
    """Handle document upload with enhanced security validation and processing."""
    if request.method == 'POST':
        # Validate session security first
        session_validation = security_validator.validate_session_security(request)
        if not session_validation['success']:
            messages.error(request, session_validation['error'])
            return redirect('main:home')
        
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
                
                # Delete all previous documents for this session (keep only one document at a time)
                previous_documents = Document.objects.filter(user_session=user_session)
                if previous_documents.exists():
                    logger.info(f"Deleting {previous_documents.count()} previous documents for session {session_id}")
                    for prev_doc in previous_documents:
                        # Delete associated data
                        Analysis.objects.filter(document=prev_doc).delete()
                        DocumentChunk.objects.filter(document=prev_doc).delete()
                        Question.objects.filter(document=prev_doc).delete()
                        Answer.objects.filter(question__document=prev_doc).delete()
                        
                        # Delete file
                        if prev_doc.file:
                            try:
                                default_storage.delete(prev_doc.file.name)
                            except Exception as e:
                                logger.warning(f"Could not delete file {prev_doc.file.name}: {e}")
                        
                        # Delete document
                        prev_doc.delete()
                    
                    messages.info(request, f'Previous document(s) deleted. Uploading new document...')
                
                # Create document record with security metadata
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

def document_qa(request, document_id):
    """Enhanced Q&A interface for a document with advanced features."""
    try:
        # Get document
        document = Document.objects.get(id=document_id)
        
        # Get enhanced Q&A summary
        qa_summary = enhanced_qa_service.get_enhanced_qa_summary(document_id)
        
        # Get enhanced question history
        recent_questions = enhanced_qa_service.get_enhanced_question_history(document_id, limit=5)
        
        # Build advanced search index if document is processed
        if document.status == 'processed':
            try:
                # Build advanced search index
                advanced_semantic_search_engine.build_advanced_index(document)
                
                # Optimize document processing
                performance_optimizer.optimize_document_processing(document)
                
            except Exception as e:
                logger.warning(f"Could not build advanced search index: {e}")
        
        # Get performance metrics
        performance_metrics = performance_optimizer.get_performance_metrics()
        
        context = {
            'document': document,
            'qa_summary': qa_summary,
            'recent_questions': recent_questions,
            'performance_metrics': performance_metrics,
            'enhanced_features': True,  # Flag to enable enhanced UI features
        }
        
        return render(request, 'main/document_qa.html', context)
        
    except Document.DoesNotExist:
        messages.error(request, 'Document not found.')
        return redirect('main:document_list')
    except Exception as e:
        logger.error(f"Error in document_qa: {e}")
        messages.error(request, 'Error loading Q&A interface.')
        return redirect('main:document_list')

@require_http_methods(["POST"])
def ask_question(request, document_id):
    """Handle enhanced question asking via AJAX with advanced features."""
    try:
        question_text = request.POST.get('question_text', '').strip()
        
        if not question_text:
            return JsonResponse({
                'success': False,
                'error': 'Question text is required.'
            })
        
        # Process question using enhanced Q&A service
        result = enhanced_qa_service.process_enhanced_question(question_text, str(document_id))
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'answer': result['answer'],
                'confidence_score': result['confidence_score'],
                'confidence_breakdown': result.get('confidence_breakdown', {}),
                'citations': result['citations'],
                'processing_time': result['processing_time'],
                'question_id': result['question_id'],
                'answer_id': result.get('answer_id'),
                'search_results': result.get('search_results', []),
                'recommendations': result.get('recommendations', {}),
                'answer_type': result.get('answer_type', 'generated'),
                'grounded': result.get('grounded', True),
                'search_metadata': result.get('search_metadata', {}),
                'performance_metrics': result.get('performance_metrics', {})
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result['error']
            })
            
    except Exception as e:
        logger.error(f"Error in ask_question: {e}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while processing your question.'
        })

def question_history(request, document_id):
    """Get enhanced question history for a document."""
    try:
        # Get enhanced question history
        history = enhanced_qa_service.get_enhanced_question_history(str(document_id), limit=20)
        
        return JsonResponse({
            'success': True,
            'history': history
        })
        
    except Exception as e:
        logger.error(f"Error in question_history: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Error loading question history.'
        })

def document_qa_summary(request, document_id):
    """Get enhanced Q&A summary for a document."""
    try:
        # Get enhanced Q&A summary
        summary = enhanced_qa_service.get_enhanced_qa_summary(str(document_id))
        
        return JsonResponse({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Error in document_qa_summary: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Error loading Q&A summary.'
        })

def enhanced_performance_metrics(request):
    """Get enhanced performance metrics for the system."""
    try:
        # Get comprehensive performance metrics
        metrics = performance_optimizer.get_performance_metrics()
        
        # Get search statistics
        search_stats = advanced_semantic_search_engine.get_search_statistics()
        
        # Get Q&A statistics
        qa_stats = enhanced_qa_service.qa_stats
        
        return JsonResponse({
            'success': True,
            'performance_metrics': metrics,
            'search_statistics': search_stats,
            'qa_statistics': qa_stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in enhanced_performance_metrics: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Error loading performance metrics.'
        })

def optimize_document(request, document_id):
    """Optimize document processing and search index."""
    try:
        document = Document.objects.get(id=document_id)
        
        # Optimize document processing
        success = performance_optimizer.optimize_document_processing(document)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': f'Document "{document.title}" optimized successfully.'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to optimize document.'
            })
            
    except Document.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Document not found.'
        })
    except Exception as e:
        logger.error(f"Error in optimize_document: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Error optimizing document.'
        })

def about(request):
    """About page view showcasing the AI Legal Document Explainer features."""
    context = {
        'title': 'About - AI Legal Document Explainer',
        'description': 'Learn about our AI-powered legal document analysis platform',
        'features': [
            {
                'icon': 'fas fa-upload',
                'title': 'Smart Document Upload',
                'description': 'Upload PDF legal documents with advanced security validation and OCR support for scanned documents.',
                'color': 'primary'
            },
            {
                'icon': 'fas fa-brain',
                'title': 'AI-Powered Analysis',
                'description': 'Advanced AI algorithms analyze your documents to extract key information, detect clauses, and identify potential risks.',
                'color': 'success'
            },
            {
                'icon': 'fas fa-file-alt',
                'title': 'Simple Summaries',
                'description': 'Get easy-to-understand summaries in plain English, breaking down complex legal jargon into simple terms.',
                'color': 'info'
            },
            {
                'icon': 'fas fa-gavel',
                'title': 'Clause Detection',
                'description': 'Automatically identify and categorize important legal clauses by importance level (Critical, High, Medium, Low).',
                'color': 'warning'
            },
            {
                'icon': 'fas fa-exclamation-triangle',
                'title': 'Red Flag Detection',
                'description': 'Identify potential risks, unusual terms, and clauses that may need special attention or legal consultation.',
                'color': 'danger'
            },
            {
                'icon': 'fas fa-question-circle',
                'title': 'Interactive Q&A',
                'description': 'Ask specific questions about your document and get context-based answers with confidence scores and citations.',
                'color': 'secondary'
            },
            {
                'icon': 'fas fa-chart-line',
                'title': 'Performance Monitoring',
                'description': 'Real-time performance metrics, processing statistics, and system optimization recommendations.',
                'color': 'dark'
            },
            {
                'icon': 'fas fa-shield-alt',
                'title': 'Security & Privacy',
                'description': 'Advanced security validation, file sanitization, and privacy protection for your sensitive legal documents.',
                'color': 'success'
            }
        ],
        'how_it_works': [
            {
                'step': 1,
                'title': 'Upload Your Document',
                'description': 'Simply drag and drop or select your PDF legal document. Our system supports both text-based and scanned documents.',
                'icon': 'fas fa-upload'
            },
            {
                'step': 2,
                'title': 'AI Processing',
                'description': 'Our advanced AI algorithms analyze your document, extracting text, detecting clauses, and identifying potential risks.',
                'icon': 'fas fa-cogs'
            },
            {
                'step': 3,
                'title': 'Get Analysis Results',
                'description': 'View comprehensive analysis including simple summaries, clause breakdowns, red flags, and recommendations.',
                'icon': 'fas fa-chart-bar'
            },
            {
                'step': 4,
                'title': 'Ask Questions',
                'description': 'Use our interactive Q&A system to get specific answers about your document with confidence scores.',
                'icon': 'fas fa-comments'
            }
        ],
        'document_types': [
            'Lease Agreements',
            'Employment Contracts', 
            'Service Agreements',
            'Purchase Agreements',
            'Partnership Agreements',
            'Non-Disclosure Agreements',
            'Terms & Conditions',
            'Privacy Policies',
            'Business Contracts',
            'Legal Agreements'
        ],
        'stats': {
            'documents_processed': '1000+',
            'clauses_detected': '50,000+',
            'red_flags_identified': '5,000+',
            'questions_answered': '10,000+'
        }
    }
    return render(request, 'main/about.html', context)
