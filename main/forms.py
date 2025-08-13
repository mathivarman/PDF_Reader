from django import forms
from .models import Document

class DocumentUploadForm(forms.ModelForm):
    """Form for uploading legal documents."""
    
    class Meta:
        model = Document
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter document title (optional)'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf',
                'required': True
            })
        }
    
    def clean_file(self):
        """Validate uploaded file."""
        file = self.cleaned_data.get('file')
        
        if not file:
            raise forms.ValidationError('Please select a file to upload.')
        
        # Check file type
        if not file.name.lower().endswith('.pdf'):
            raise forms.ValidationError('Only PDF files are allowed.')
        
        # Check file size (25MB limit)
        if file.size > 25 * 1024 * 1024:
            raise forms.ValidationError('File size must be less than 25MB.')
        
        return file
    
    def clean_title(self):
        """Set default title if not provided."""
        title = self.cleaned_data.get('title')
        if not title:
            # Use filename as title
            file = self.cleaned_data.get('file')
            if file:
                title = file.name
        return title
