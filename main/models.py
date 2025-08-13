from django.db import models
from django.contrib.auth.models import User
import uuid
import os

def document_upload_path(instance, filename):
    """Generate file path for uploaded documents."""
    # Create a unique path using document ID and original filename
    ext = filename.split('.')[-1]
    filename = f"{instance.id}.{ext}"
    return os.path.join('documents', filename)

class Document(models.Model):
    """Model for storing uploaded PDF documents."""
    
    DOCUMENT_STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('processed', 'Processed'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, blank=True)
    original_filename = models.CharField(max_length=255)
    file = models.FileField(upload_to=document_upload_path)
    file_size = models.BigIntegerField(help_text="File size in bytes")
    pages = models.IntegerField(default=0, help_text="Number of pages in the document")
    
    # Processing status
    status = models.CharField(max_length=20, choices=DOCUMENT_STATUS_CHOICES, default='uploaded')
    processing_started = models.DateTimeField(null=True, blank=True)
    processing_completed = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Text extraction
    extracted_text = models.TextField(blank=True)
    text_extraction_method = models.CharField(max_length=50, blank=True, help_text="OCR or direct extraction")
    
    # User session
    user_session = models.ForeignKey('UserSession', on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    
    # Metadata
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Document"
        verbose_name_plural = "Documents"
    
    def __str__(self):
        return f"{self.title or self.original_filename} ({self.id})"
    
    def get_file_size_mb(self):
        """Return file size in MB."""
        return round(self.file_size / (1024 * 1024), 2)

class Analysis(models.Model):
    """Model for storing document analysis results."""
    
    ANALYSIS_TYPE_CHOICES = [
        ('summary', 'Summary'),
        ('clauses', 'Clauses'),
        ('red_flags', 'Red Flags'),
        ('qa', 'Q&A'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='analyses')
    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPE_CHOICES, default='summary')
    
    # Analysis results
    content = models.JSONField(default=dict, help_text="Structured analysis results")
    confidence_score = models.FloatField(default=0.0, help_text="AI confidence score (0-1)")
    
    # Text analysis fields
    extraction_method = models.CharField(max_length=50, blank=True, help_text="OCR or direct extraction")
    total_words = models.IntegerField(default=0, help_text="Total words in document")
    total_sentences = models.IntegerField(default=0, help_text="Total sentences in document")
    complexity_level = models.CharField(max_length=20, default='medium', help_text="Document complexity")
    legal_terms_found = models.TextField(blank=True, help_text="Comma-separated legal terms")
    processing_notes = models.TextField(blank=True, help_text="Processing notes and summary")
    summary = models.TextField(blank=True, help_text="Analysis summary")
    
    # Processing metadata
    processing_time = models.FloatField(default=0.0, help_text="Processing time in seconds")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['document', 'analysis_type']
        verbose_name = "Analysis"
        verbose_name_plural = "Analyses"
    
    def __str__(self):
        return f"{self.document.title} - {self.get_analysis_type_display()}"

class Clause(models.Model):
    """Model for storing detected legal clauses."""
    
    CLAUSE_TYPE_CHOICES = [
        ('termination', 'Termination'),
        ('auto_renewal', 'Auto-renewal'),
        ('penalties', 'Penalties'),
        ('confidentiality', 'Confidentiality'),
        ('liability', 'Liability'),
        ('jurisdiction', 'Jurisdiction'),
        ('arbitration', 'Arbitration'),
        ('force_majeure', 'Force Majeure'),
        ('indemnification', 'Indemnification'),
        ('non_compete', 'Non-Compete'),
        ('severability', 'Severability'),
        ('entire_agreement', 'Entire Agreement'),
        ('amendment', 'Amendment'),
        ('assignment', 'Assignment'),
        ('notice', 'Notice'),
        ('governing_law', 'Governing Law'),
        ('other', 'Other'),
    ]
    
    IMPORTANCE_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='clauses')
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, related_name='clauses')
    
    # Clause details
    clause_type = models.CharField(max_length=20, choices=CLAUSE_TYPE_CHOICES)
    importance = models.CharField(max_length=10, choices=IMPORTANCE_CHOICES, default='medium')
    title = models.CharField(max_length=255)
    snippet = models.TextField(help_text="Extracted text snippet")
    
    # Location information
    page_number = models.IntegerField(default=0)
    start_position = models.IntegerField(default=0)
    end_position = models.IntegerField(default=0)
    
    # Analysis metadata
    confidence_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['page_number', 'start_position']
        verbose_name = "Clause"
        verbose_name_plural = "Clauses"
    
    def __str__(self):
        return f"{self.title} ({self.get_clause_type_display()})"

class RedFlag(models.Model):
    """Model for storing detected red flags and risks."""
    
    RISK_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    CATEGORY_CHOICES = [
        ('financial', 'Financial'),
        ('legal', 'Legal'),
        ('operational', 'Operational'),
        ('compliance', 'Compliance'),
        ('reputational', 'Reputational'),
        ('strategic', 'Strategic'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='red_flags')
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, related_name='red_flags')
    
    # Risk details
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='legal')
    risk_level = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(help_text="Description of the risk")
    reason = models.TextField(help_text="Why this is flagged as risky")
    recommendations = models.JSONField(default=list, help_text="List of recommended actions")
    
    # Location information
    page_number = models.IntegerField(default=0)
    start_position = models.IntegerField(default=0)
    end_position = models.IntegerField(default=0)
    snippet = models.TextField(help_text="Extracted text snippet")
    
    # Analysis metadata
    confidence_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-risk_level', 'page_number']
        verbose_name = "Red Flag"
        verbose_name_plural = "Red Flags"
    
    def __str__(self):
        return f"{self.title} ({self.get_risk_level_display()})"

class Question(models.Model):
    """Model for storing user questions about documents."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='questions')
    
    # Question details
    question_text = models.TextField()
    answer = models.TextField(blank=True)
    confidence_score = models.FloatField(default=0.0)
    
    # Citations
    citations = models.JSONField(default=list, help_text="List of source citations")
    
    # Processing metadata
    processing_time = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Question"
        verbose_name_plural = "Questions"
    
    def __str__(self):
        return f"Q: {self.question_text[:50]}..."

class UserSession(models.Model):
    """Model for tracking user sessions and document access."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=255, unique=True)
    
    # Session details
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-last_activity']
        verbose_name = "User Session"
        verbose_name_plural = "User Sessions"
    
    def __str__(self):
        return f"Session {self.session_id[:8]}..."

class DocumentChunk(models.Model):
    """Model for storing document chunks for semantic search."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    
    # Chunk details
    chunk_text = models.TextField()
    chunk_index = models.IntegerField()
    page_number = models.IntegerField()
    
    # Embedding storage (as JSON for simplicity)
    embedding = models.JSONField(default=list, help_text="Vector embedding of the chunk")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['page_number', 'chunk_index']
        unique_together = ['document', 'chunk_index']
        verbose_name = "Document Chunk"
        verbose_name_plural = "Document Chunks"
    
    def __str__(self):
        return f"Chunk {self.chunk_index} (Page {self.page_number})"
