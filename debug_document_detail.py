#!/usr/bin/env python3
"""
Debug script for document detail functionality
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pdf_reader.settings')
django.setup()

from main.models import Document, Analysis, Clause, RedFlag
from main.services import DocumentProcessingService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_document_detail():
    """Debug document detail functionality."""
    print("🔍 Debugging Document Detail Functionality")
    print("=" * 50)
    
    try:
        # Check if we have any documents
        documents = Document.objects.all()
        print(f"📄 Total documents in database: {documents.count()}")
        
        if not documents.exists():
            print("❌ No documents found in database")
            return
        
        # Check each document
        for doc in documents:
            print(f"\n📋 Document: {doc.title} (ID: {doc.id})")
            print(f"   Status: {doc.status}")
            print(f"   Pages: {doc.pages}")
            
            # Check if analysis exists
            analysis = Analysis.objects.filter(document=doc).first()
            if analysis:
                print(f"   ✅ Analysis found (ID: {analysis.id})")
                print(f"   Extraction method: {analysis.extraction_method}")
                print(f"   Total words: {analysis.total_words}")
                print(f"   Total sentences: {analysis.total_sentences}")
                print(f"   Complexity: {analysis.complexity_level}")
                print(f"   Processing notes: {analysis.processing_notes}")
                
                # Check clauses
                clauses = Clause.objects.filter(document=doc)
                print(f"   Clauses: {clauses.count()}")
                
                # Check red flags
                red_flags = RedFlag.objects.filter(document=doc)
                print(f"   Red flags: {red_flags.count()}")
                
                # Test the service method
                print(f"\n🔧 Testing DocumentProcessingService.get_document_analysis...")
                try:
                    result = DocumentProcessingService.get_document_analysis(doc.id)
                    if 'error' in result:
                        print(f"   ❌ Service error: {result['error']}")
                    else:
                        print(f"   ✅ Service success!")
                        print(f"   Document title: {result['document']['title']}")
                        print(f"   Analysis words: {result['analysis']['total_words']}")
                        print(f"   Clauses: {len(result.get('clauses', []))}")
                        print(f"   Red flags: {len(result.get('red_flags', []))}")
                except Exception as e:
                    print(f"   ❌ Service exception: {e}")
                    import traceback
                    traceback.print_exc()
                
            else:
                print(f"   ❌ No analysis found for document")
        
    except Exception as e:
        print(f"❌ Error in debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_document_detail()
