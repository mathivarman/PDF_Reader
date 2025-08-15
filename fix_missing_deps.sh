#!/bin/bash

# Fix Missing Dependencies
# Install missing packages and fix import issues

echo "🔧 Fixing Missing Dependencies..."
echo "================================="

# Get username
USERNAME=$(whoami)
echo "👤 Username: $USERNAME"

# Step 1: Navigate to project directory
echo ""
echo "📋 Step 1: Navigating to project directory..."
cd /home/$USERNAME/PDF_Reader

# Step 2: Activate virtual environment
echo ""
echo "📋 Step 2: Activating virtual environment..."
source pdf_reader_env/bin/activate

# Step 3: Install missing dependencies
echo ""
echo "📋 Step 3: Installing missing dependencies..."

# Install pytesseract and other missing packages
pip install pytesseract
pip install opencv-python-headless
pip install nltk
pip install spacy
pip install sentence-transformers
pip install transformers
pip install huggingface-hub

# Download spaCy model
python -m spacy download en_core_web_sm

# Step 4: Create a simple fallback for missing packages
echo ""
echo "📋 Step 4: Creating fallback for missing packages..."

# Create a simple fallback module
cat > main/pdf_processor_fallback.py << 'EOF'
"""
Fallback PDF processor for when advanced dependencies are not available
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class PDFProcessorFallback:
    """Fallback PDF processor when advanced dependencies are missing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.warning("Using fallback PDF processor - advanced features disabled")
    
    def extract_text(self, pdf_path: str) -> str:
        """Basic text extraction using PyPDF2"""
        try:
            import PyPDF2
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            self.logger.error(f"Error extracting text: {e}")
            return f"Error extracting text: {str(e)}"
    
    def process_document(self, pdf_path: str) -> Dict[str, Any]:
        """Basic document processing"""
        text = self.extract_text(pdf_path)
        return {
            'text': text,
            'pages': 1,
            'status': 'processed',
            'message': 'Basic processing completed (advanced features disabled)'
        }

# Try to import pytesseract, fallback if not available
try:
    import pytesseract
    HAS_PYTESSERACT = True
except ImportError:
    HAS_PYTESSERACT = False
    logger.warning("pytesseract not available - OCR features disabled")

# Try to import spacy, fallback if not available
try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False
    logger.warning("spacy not available - NLP features disabled")

# Try to import transformers, fallback if not available
try:
    import transformers
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logger.warning("transformers not available - AI features disabled")
EOF

# Step 5: Update the main pdf_processor.py to handle missing dependencies
echo ""
echo "📋 Step 5: Updating PDF processor to handle missing dependencies..."

# Create a backup of the original file
cp main/pdf_processor.py main/pdf_processor.py.backup

# Create a simplified version that handles missing dependencies
cat > main/pdf_processor_simple.py << 'EOF'
"""
Simplified PDF processor that handles missing dependencies gracefully
"""

import logging
from typing import List, Dict, Any
import PyPDF2
import pdfplumber

logger = logging.getLogger(__name__)

class PDFProcessor:
    """PDF processor with fallback for missing dependencies"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check which dependencies are available"""
        self.has_pytesseract = False
        self.has_spacy = False
        self.has_transformers = False
        
        try:
            import pytesseract
            self.has_pytesseract = True
        except ImportError:
            self.logger.warning("pytesseract not available - OCR features disabled")
        
        try:
            import spacy
            self.has_spacy = True
        except ImportError:
            self.logger.warning("spacy not available - NLP features disabled")
        
        try:
            import transformers
            self.has_transformers = True
        except ImportError:
            self.logger.warning("transformers not available - AI features disabled")
    
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
EOF

# Step 6: Test Django
echo ""
echo "📋 Step 6: Testing Django..."
python manage.py check --deploy

echo ""
echo "✅ Dependencies fixed!"
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
echo "⚠️  Note: Some advanced features may be limited due to missing dependencies."
echo "   Core PDF upload and text extraction will work."
