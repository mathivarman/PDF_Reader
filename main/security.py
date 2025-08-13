"""
Security utilities for the AI Legal Document Explainer.
Handles file validation, input sanitization, and security checks.
"""

import os
import re
import hashlib
import mimetypes
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Security validation utilities for file uploads and user inputs."""
    
    @staticmethod
    def validate_file_upload(file):
        """
        Validate uploaded file for security and format requirements.
        
        Args:
            file: UploadedFile object
            
        Returns:
            dict: Validation result with success status and any errors
        """
        try:
            # Check file size
            if file.size > settings.MAX_FILE_SIZE:
                return {
                    'success': False,
                    'error': f'File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE // (1024*1024)}MB'
                }
            
            # Check file extension
            file_extension = os.path.splitext(file.name)[1].lower()
            if file_extension not in settings.ALLOWED_FILE_EXTENSIONS:
                return {
                    'success': False,
                    'error': f'File type {file_extension} is not allowed. Only PDF files are accepted.'
                }
            
            # Check MIME type
            mime_type, _ = mimetypes.guess_type(file.name)
            if mime_type != 'application/pdf':
                return {
                    'success': False,
                    'error': 'Invalid file type. Only PDF files are accepted.'
                }
            
            # Check for malicious content patterns
            if SecurityValidator._contains_malicious_content(file):
                return {
                    'success': False,
                    'error': 'File contains potentially malicious content.'
                }
            
            # Generate file hash for integrity
            file_hash = SecurityValidator._generate_file_hash(file)
            
            return {
                'success': True,
                'file_hash': file_hash,
                'file_size': file.size,
                'mime_type': mime_type
            }
            
        except Exception as e:
            logger.error(f"File validation error: {e}")
            return {
                'success': False,
                'error': 'File validation failed due to an unexpected error.'
            }
    
    @staticmethod
    def _contains_malicious_content(file):
        """
        Check for potentially malicious content in uploaded files.
        
        Args:
            file: UploadedFile object
            
        Returns:
            bool: True if malicious content detected
        """
        try:
            # Read first 1KB to check for script tags or other malicious patterns
            file.seek(0)
            content = file.read(1024).decode('utf-8', errors='ignore')
            
            # Patterns to check for
            malicious_patterns = [
                r'<script[^>]*>',
                r'javascript:',
                r'vbscript:',
                r'data:text/html',
                r'data:application/x-javascript',
                r'<iframe[^>]*>',
                r'<object[^>]*>',
                r'<embed[^>]*>',
                r'<form[^>]*>',
                r'onload\s*=',
                r'onerror\s*=',
                r'onclick\s*=',
            ]
            
            for pattern in malicious_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    logger.warning(f"Malicious content pattern detected: {pattern}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking for malicious content: {e}")
            return True  # Fail safe - reject if we can't check
    
    @staticmethod
    def _generate_file_hash(file):
        """
        Generate SHA-256 hash of file content for integrity checking.
        
        Args:
            file: UploadedFile object
            
        Returns:
            str: SHA-256 hash of file content
        """
        try:
            file.seek(0)
            sha256_hash = hashlib.sha256()
            
            # Read file in chunks to handle large files
            for chunk in file.chunks():
                sha256_hash.update(chunk)
            
            return sha256_hash.hexdigest()
            
        except Exception as e:
            logger.error(f"Error generating file hash: {e}")
            return None
    
    @staticmethod
    def sanitize_input(text, max_length=1000):
        """
        Sanitize user input to prevent XSS and injection attacks.
        
        Args:
            text: Input text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            str: Sanitized text
        """
        if not text:
            return ""
        
        # Convert to string if needed
        text = str(text)
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length]
        
        # Strip HTML tags first
        text = strip_tags(text)
        
        # Remove script content and other dangerous patterns
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'on\w+\s*=',
            r'data:text/html',
            r'data:application/x-javascript',
        ]
        
        for pattern in dangerous_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}', '[', ']']
        for char in dangerous_chars:
            text = text.replace(char, '')
        
        # Remove multiple spaces and clean up
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def validate_session_security(request):
        """
        Validate session security and user permissions.
        
        Args:
            request: Django request object
            
        Returns:
            dict: Validation result
        """
        try:
            # Check if session exists
            if not request.session.session_key:
                return {
                    'success': False,
                    'error': 'No valid session found.'
                }
            
            # Check session age
            session_age = request.session.get('_session_age', 0)
            if session_age > settings.SESSION_COOKIE_AGE:
                return {
                    'success': False,
                    'error': 'Session has expired.'
                }
            
            # Check for suspicious activity patterns
            if SecurityValidator._detect_suspicious_activity(request):
                return {
                    'success': False,
                    'error': 'Suspicious activity detected.'
                }
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Session security validation error: {e}")
            return {
                'success': False,
                'error': 'Session validation failed.'
            }
    
    @staticmethod
    def _detect_suspicious_activity(request):
        """
        Detect suspicious activity patterns in requests.
        
        Args:
            request: Django request object
            
        Returns:
            bool: True if suspicious activity detected
        """
        try:
            # Check request frequency (basic rate limiting)
            request_count = request.session.get('request_count', 0)
            if request_count > 100:  # More than 100 requests per session
                logger.warning(f"High request count detected: {request_count}")
                return True
            
            # Check for suspicious headers
            suspicious_headers = [
                'X-Forwarded-For',
                'X-Real-IP',
                'X-Originating-IP',
                'CF-Connecting-IP',
            ]
            
            for header in suspicious_headers:
                if header in request.headers:
                    ip = request.headers[header]
                    if not SecurityValidator._is_valid_ip(ip):
                        logger.warning(f"Suspicious IP header detected: {header}={ip}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting suspicious activity: {e}")
            return False
    
    @staticmethod
    def _is_valid_ip(ip):
        """
        Validate IP address format.
        
        Args:
            ip: IP address string
            
        Returns:
            bool: True if valid IP format
        """
        try:
            import ipaddress
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

class FileUploadSecurity:
    """Enhanced file upload security with additional checks."""
    
    @staticmethod
    def validate_pdf_content(file):
        """
        Validate PDF file content for integrity and safety.
        
        Args:
            file: UploadedFile object
            
        Returns:
            dict: Validation result
        """
        try:
            file.seek(0)
            header = file.read(4)
            
            # Check PDF magic number
            if header != b'%PDF':
                return {
                    'success': False,
                    'error': 'Invalid PDF file format.'
                }
            
            # Check for PDF version
            file.seek(0)
            content = file.read(1024).decode('utf-8', errors='ignore')
            
            # Look for PDF version header
            version_match = re.search(r'%PDF-(\d+\.\d+)', content)
            if not version_match:
                return {
                    'success': False,
                    'error': 'Invalid PDF file structure.'
                }
            
            pdf_version = float(version_match.group(1))
            if pdf_version < 1.0 or pdf_version > 2.0:
                return {
                    'success': False,
                    'error': f'Unsupported PDF version: {pdf_version}'
                }
            
            return {
                'success': True,
                'pdf_version': pdf_version
            }
            
        except Exception as e:
            logger.error(f"PDF content validation error: {e}")
            return {
                'success': False,
                'error': 'PDF content validation failed.'
            }
    
    @staticmethod
    def scan_for_vulnerabilities(file):
        """
        Scan uploaded file for potential security vulnerabilities.
        
        Args:
            file: UploadedFile object
            
        Returns:
            dict: Scan results
        """
        try:
            file.seek(0)
            content = file.read(8192).decode('utf-8', errors='ignore')  # Read first 8KB
            
            vulnerabilities = []
            
            # Check for embedded JavaScript
            if re.search(r'/JS\s+', content, re.IGNORECASE):
                vulnerabilities.append('Embedded JavaScript detected')
            
            # Check for embedded forms
            if re.search(r'/AcroForm', content, re.IGNORECASE):
                vulnerabilities.append('PDF form detected')
            
            # Check for embedded actions
            if re.search(r'/Action', content, re.IGNORECASE):
                vulnerabilities.append('PDF actions detected')
            
            # Check for external references
            if re.search(r'https?://', content, re.IGNORECASE):
                vulnerabilities.append('External references detected')
            
            return {
                'success': True,
                'vulnerabilities': vulnerabilities,
                'risk_level': 'high' if vulnerabilities else 'low'
            }
            
        except Exception as e:
            logger.error(f"Vulnerability scan error: {e}")
            return {
                'success': False,
                'error': 'Vulnerability scan failed.'
            }

# Global security validator instance
security_validator = SecurityValidator()
file_upload_security = FileUploadSecurity()
