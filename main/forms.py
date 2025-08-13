from django import forms
from django.core.exceptions import ValidationError
from .models import Document
from .security import security_validator, file_upload_security

class DocumentUploadForm(forms.ModelForm):
    """Form for uploading legal documents with enhanced security validation."""
    
    class Meta:
        model = Document
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter document title (optional)',
                'maxlength': '255'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf',
                'required': True
            })
        }
    
    def clean_file(self):
        """Enhanced file validation with security checks."""
        file = self.cleaned_data.get('file')
        
        if not file:
            raise ValidationError('Please select a file to upload.')
        
        # Use security validator for comprehensive file validation
        validation_result = security_validator.validate_file_upload(file)
        
        if not validation_result['success']:
            raise ValidationError(validation_result['error'])
        
        # Additional PDF content validation
        pdf_validation = file_upload_security.validate_pdf_content(file)
        if not pdf_validation['success']:
            raise ValidationError(pdf_validation['error'])
        
        # Vulnerability scan
        vulnerability_scan = file_upload_security.scan_for_vulnerabilities(file)
        if vulnerability_scan['success'] and vulnerability_scan['vulnerabilities']:
            # Log vulnerabilities but don't block upload for now
            # In production, you might want to block certain vulnerabilities
            print(f"Vulnerabilities detected: {vulnerability_scan['vulnerabilities']}")
        
        # Store validation metadata for later use
        self.file_validation_data = {
            'file_hash': validation_result.get('file_hash'),
            'pdf_version': pdf_validation.get('pdf_version'),
            'vulnerabilities': vulnerability_scan.get('vulnerabilities', [])
        }
        
        return file
    
    def clean_title(self):
        """Sanitize and validate title input."""
        title = self.cleaned_data.get('title')
        
        if title:
            # Sanitize title input
            title = security_validator.sanitize_input(title, max_length=255)
        
        if not title:
            # Use filename as title
            file = self.cleaned_data.get('file')
            if file:
                # Extract filename without extension
                import os
                filename = os.path.splitext(file.name)[0]
                title = security_validator.sanitize_input(filename, max_length=255)
        
        return title
    
    def save(self, commit=True):
        """Save the document with security metadata."""
        document = super().save(commit=False)
        
        # Add security metadata if available
        if hasattr(self, 'file_validation_data'):
            # You could store this in a separate model or as JSON field
            document.processing_notes = f"Security validation: {self.file_validation_data}"
        
        if commit:
            document.save()
        
        return document
