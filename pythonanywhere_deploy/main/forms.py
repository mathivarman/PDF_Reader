from django import forms
from django.core.exceptions import ValidationError
from .models import Document
from .security import security_validator, file_upload_security
import re

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
        
        # Use the existing file_upload_security function
        try:
            file_upload_security(file)
        except ValidationError as e:
            raise ValidationError(str(e))
        
        # Store validation metadata for later use
        self.file_validation_data = {
            'file_size': file.size,
            'file_name': file.name,
            'content_type': file.content_type
        }
        
        return file
    
    def clean_title(self):
        """Sanitize and validate title input."""
        title = self.cleaned_data.get('title')
        
        if title:
            # Basic sanitization - remove dangerous characters
            title = re.sub(r'[<>:"/\\|?*]', '', title)
            title = title.strip()
        
        if not title:
            # Use filename as title
            file = self.cleaned_data.get('file')
            if file:
                # Extract filename without extension
                import os
                filename = os.path.splitext(file.name)[0]
                # Basic sanitization
                filename = re.sub(r'[<>:"/\\|?*]', '', filename)
                title = filename.strip()
        
        return title
    
    def save(self, commit=True):
        """Save the document with security metadata."""
        document = super().save(commit=False)
        
        # Security validation data is stored in self.file_validation_data
        # but Document model doesn't have a processing_notes field
        # This data could be logged or stored elsewhere if needed
        
        if commit:
            document.save()
        
        return document
