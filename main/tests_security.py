"""
Security testing module for the AI Legal Document Explainer.
Tests file validation, input sanitization, and security features.
"""

import os
import tempfile
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.contrib.sessions.backends.db import SessionStore
from django.conf import settings

from .models import Document, UserSession
from .security import SecurityValidator, FileUploadSecurity
from .forms import DocumentUploadForm

class SecurityValidatorTestCase(TestCase):
    """Test cases for SecurityValidator class."""
    
    def setUp(self):
        """Set up test data."""
        self.validator = SecurityValidator()
        self.client = Client()
        
        # Create a valid PDF file for testing
        self.valid_pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF'
        
        # Create malicious content for testing
        self.malicious_content = b'<script>alert("XSS")</script>%PDF-1.4\n'
    
    def test_validate_file_upload_valid_pdf(self):
        """Test validation of a valid PDF file."""
        file = SimpleUploadedFile(
            "test.pdf",
            self.valid_pdf_content,
            content_type="application/pdf"
        )
        
        result = self.validator.validate_file_upload(file)
        
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['file_hash'])
        self.assertEqual(result['file_size'], len(self.valid_pdf_content))
        self.assertEqual(result['mime_type'], 'application/pdf')
    
    def test_validate_file_upload_invalid_extension(self):
        """Test validation of file with invalid extension."""
        file = SimpleUploadedFile(
            "test.txt",
            self.valid_pdf_content,
            content_type="text/plain"
        )
        
        result = self.validator.validate_file_upload(file)
        
        self.assertFalse(result['success'])
        self.assertIn('not allowed', result['error'])
    
    def test_validate_file_upload_malicious_content(self):
        """Test validation of file with malicious content."""
        file = SimpleUploadedFile(
            "malicious.pdf",
            self.malicious_content,
            content_type="application/pdf"
        )
        
        result = self.validator.validate_file_upload(file)
        
        self.assertFalse(result['success'])
        self.assertIn('malicious content', result['error'])
    
    def test_sanitize_input_normal_text(self):
        """Test sanitization of normal text input."""
        text = "This is a normal text input"
        sanitized = self.validator.sanitize_input(text)
        
        self.assertEqual(sanitized, "This is a normal text input")
    
    def test_sanitize_input_with_html_tags(self):
        """Test sanitization of text with HTML tags."""
        text = "<script>alert('XSS')</script>Hello World"
        sanitized = self.validator.sanitize_input(text)
        
        self.assertEqual(sanitized, "Hello World")
    
    def test_generate_file_hash(self):
        """Test file hash generation."""
        file = SimpleUploadedFile(
            "test.pdf",
            self.valid_pdf_content,
            content_type="application/pdf"
        )
        
        hash_result = self.validator._generate_file_hash(file)
        
        self.assertIsNotNone(hash_result)
        self.assertEqual(len(hash_result), 64)  # SHA-256 hash length

class FileUploadSecurityTestCase(TestCase):
    """Test cases for FileUploadSecurity class."""
    
    def setUp(self):
        """Set up test data."""
        self.security = FileUploadSecurity()
        
        # Valid PDF content
        self.valid_pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF'
    
    def test_validate_pdf_content_valid_pdf(self):
        """Test validation of valid PDF content."""
        file = SimpleUploadedFile(
            "test.pdf",
            self.valid_pdf_content,
            content_type="application/pdf"
        )
        
        result = self.security.validate_pdf_content(file)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['pdf_version'], 1.4)
    
    def test_validate_pdf_content_invalid_format(self):
        """Test validation of invalid PDF format."""
        file = SimpleUploadedFile(
            "test.txt",
            b'This is not a PDF file',
            content_type="text/plain"
        )
        
        result = self.security.validate_pdf_content(file)
        
        self.assertFalse(result['success'])
        self.assertIn('Invalid PDF file format', result['error'])
    
    def test_scan_for_vulnerabilities_clean_pdf(self):
        """Test vulnerability scan of clean PDF."""
        file = SimpleUploadedFile(
            "clean.pdf",
            self.valid_pdf_content,
            content_type="application/pdf"
        )
        
        result = self.security.scan_for_vulnerabilities(file)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['risk_level'], 'low')
        self.assertEqual(len(result['vulnerabilities']), 0)

class DocumentUploadFormSecurityTestCase(TestCase):
    """Test cases for DocumentUploadForm security features."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Valid PDF content
        self.valid_pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF'
    
    def test_form_validation_valid_pdf(self):
        """Test form validation with valid PDF."""
        file = SimpleUploadedFile(
            "test.pdf",
            self.valid_pdf_content,
            content_type="application/pdf"
        )
        
        form_data = {
            'title': 'Test Document'
        }
        
        form = DocumentUploadForm(data=form_data, files={'file': file})
        
        self.assertTrue(form.is_valid())
        self.assertIsNotNone(form.file_validation_data)
        self.assertIsNotNone(form.file_validation_data['file_hash'])
    
    def test_form_validation_invalid_file_type(self):
        """Test form validation with invalid file type."""
        file = SimpleUploadedFile(
            "test.txt",
            b'This is not a PDF',
            content_type="text/plain"
        )
        
        form_data = {
            'title': 'Test Document'
        }
        
        form = DocumentUploadForm(data=form_data, files={'file': file})
        
        self.assertFalse(form.is_valid())
        self.assertIn('not allowed', str(form.errors))
    
    def test_form_validation_sanitized_title(self):
        """Test form validation with sanitized title."""
        file = SimpleUploadedFile(
            "test.pdf",
            self.valid_pdf_content,
            content_type="application/pdf"
        )
        
        form_data = {
            'title': '<script>alert("XSS")</script>Test Document'
        }
        
        form = DocumentUploadForm(data=form_data, files={'file': file})
        
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['title'], 'Test Document')
