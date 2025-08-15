"""
Security utilities for the AI Legal Document Explainer.
Handles file validation, input sanitization, and security checks.
"""

import logging
import re
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Security validator class for session and file validation"""
    
    def validate_session_security(self, request: HttpRequest) -> Dict[str, Any]:
        """Validate session security"""
        try:
            # Basic session validation
            if not request.session:
                return {'valid': False, 'error': 'No session found'}
            
            # Check if user is authenticated (optional)
            if hasattr(request, 'user') and not request.user.is_authenticated:
                return {'valid': True, 'warning': 'User not authenticated'}
            
            return {'valid': True, 'message': 'Session validated'}
            
        except Exception as e:
            logger.error(f"Session security validation error: {e}")
            return {'valid': False, 'error': 'Session validation failed'}

# Create a global instance
security_validator = SecurityValidator()

def file_upload_security(file) -> None:
    """Validate file upload security"""
    try:
        # Check file size (5MB limit)
        if file.size > 5 * 1024 * 1024:
            raise ValidationError('File too large (max 5MB)')
        
        # Check file extension
        allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
        file_extension = file.name.lower()
        
        if not any(file_extension.endswith(ext) for ext in allowed_extensions):
            raise ValidationError('File type not allowed')
        
        # Check file name for dangerous characters
        if re.search(r'[<>:"/\\|?*]', file.name):
            raise ValidationError('Invalid file name')
        
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        else:
            logger.error(f"Error in file upload security: {e}")
            raise ValidationError('File upload security check failed')

def validate_document_content(content: str) -> bool:
    """Validate document content"""
    try:
        # Basic content validation
        if not content or len(content.strip()) == 0:
            return False
        
        # Check for minimum content length
        if len(content) < 10:
            return False
        
        # Check for maximum content length
        if len(content) > 1000000:  # 1MB limit
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating document content: {e}")
        return False
