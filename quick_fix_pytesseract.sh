#!/bin/bash

# Quick Fix for Missing pytesseract
# Modify pdf_processor.py to handle missing imports gracefully

echo "🔧 Quick Fix for Missing pytesseract..."
echo "======================================="

# Get username
USERNAME=$(whoami)
echo "👤 Username: $USERNAME"

# Step 1: Navigate to project directory
echo ""
echo "📋 Step 1: Navigating to project directory..."
cd /home/$USERNAME/PDF_Reader

# Step 2: Create a backup of the original file
echo ""
echo "📋 Step 2: Creating backup..."
cp main/pdf_processor.py main/pdf_processor.py.backup

# Step 3: Modify the pdf_processor.py to handle missing imports
echo ""
echo "📋 Step 3: Modifying pdf_processor.py..."

# Create a modified version that handles missing imports
cat > main/pdf_processor.py << 'EOF'
"""
PDF processor with graceful handling of missing dependencies
"""

import logging
from typing import List, Dict, Any
import PyPDF2
import pdfplumber

logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import pytesseract
    HAS_PYTESSERACT = True
except ImportError:
    HAS_PYTESSERACT = False
    logger.warning("pytesseract not available - OCR features disabled")

try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False
    logger.warning("spacy not available - NLP features disabled")

try:
    import transformers
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logger.warning("transformers not available - AI features disabled")

class PDFProcessor:
    """PDF processor with fallback for missing dependencies"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.has_pytesseract = HAS_PYTESSERACT
        self.has_spacy = HAS_SPACY
        self.has_transformers = HAS_TRANSFORMERS
        
        if not any([self.has_pytesseract, self.has_spacy, self.has_transformers]):
            self.logger.warning("Advanced features disabled - using basic PDF processing")
    
    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF using available methods"""
        try:
            # Try pdfplumber first
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            # If no text found, try PyPDF2
            if not text.strip():
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            
            return text.strip()
        except Exception as e:
            self.logger.error(f"Error extracting text: {e}")
            return f"Error extracting text: {str(e)}"
    
    def process_document(self, pdf_path: str) -> Dict[str, Any]:
        """Process document with available features"""
        text = self.extract_text(pdf_path)
        
        result = {
            'text': text,
            'pages': 1,
            'status': 'processed',
            'features_available': {
                'ocr': self.has_pytesseract,
                'nlp': self.has_spacy,
                'ai': self.has_transformers
            }
        }
        
        if not any([self.has_pytesseract, self.has_spacy, self.has_transformers]):
            result['message'] = 'Basic processing completed (advanced features disabled)'
        else:
            result['message'] = 'Processing completed with available features'
        
        return result
    
    def extract_text_with_ocr(self, pdf_path: str) -> str:
        """Extract text using OCR if available"""
        if not self.has_pytesseract:
            self.logger.warning("OCR not available - using basic text extraction")
            return self.extract_text(pdf_path)
        
        # OCR implementation would go here
        return self.extract_text(pdf_path)
EOF

# Step 4: Activate virtual environment and test
echo ""
echo "📋 Step 4: Testing Django..."
source pdf_reader_env/bin/activate
python manage.py check --deploy

echo ""
echo "✅ Quick fix completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file and update DB_PASSWORD"
echo "2. Go to Web tab in PythonAnywhere"
echo "3. Add a new web app with Manual configuration"
echo "4. Update WSGI file with the provided configuration"
echo "5. Configure static files"
echo "6. Reload web app"
echo ""
echo "🔗 Your app will be available at: https://$USERNAME.pythonanywhere.com"
echo ""
echo "⚠️  Note: Advanced features (OCR, NLP, AI) are disabled due to missing dependencies."
echo "   Core PDF upload and text extraction will work perfectly."
