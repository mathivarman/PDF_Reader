from django.contrib import admin
from .models import Document, Analysis, Clause, RedFlag, Question, UserSession, DocumentChunk

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'original_filename', 'status', 'uploaded_at', 'file_size', 'pages')
    list_filter = ('status', 'uploaded_at')
    search_fields = ('title', 'original_filename')
    readonly_fields = ('uploaded_at', 'file_size', 'id')
    date_hierarchy = 'uploaded_at'

@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ('document', 'analysis_type', 'created_at', 'processing_time', 'confidence_score')
    list_filter = ('analysis_type', 'created_at', 'confidence_score')
    search_fields = ('document__title', 'document__original_filename')
    readonly_fields = ('created_at', 'processing_time', 'id')

@admin.register(Clause)
class ClauseAdmin(admin.ModelAdmin):
    list_display = ('document', 'clause_type', 'importance', 'page_number', 'confidence_score')
    list_filter = ('clause_type', 'importance', 'page_number')
    search_fields = ('document__title', 'content')
    readonly_fields = ('created_at', 'id')

@admin.register(RedFlag)
class RedFlagAdmin(admin.ModelAdmin):
    list_display = ('document', 'title', 'risk_level', 'page_number', 'created_at')
    list_filter = ('risk_level', 'created_at')
    search_fields = ('document__title', 'title', 'description')
    readonly_fields = ('created_at', 'id')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('document', 'question_text', 'answer', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('document__title', 'question_text', 'answer')
    readonly_fields = ('created_at', 'id')

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'created_at', 'last_activity', 'document_count')
    list_filter = ('created_at', 'last_activity')
    search_fields = ('session_id',)
    readonly_fields = ('created_at', 'last_activity', 'id')
    
    def document_count(self, obj):
        return obj.document_set.count()
    document_count.short_description = 'Documents'

@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('document', 'page_number', 'chunk_index', 'content_length')
    list_filter = ('page_number', 'created_at')
    search_fields = ('document__title', 'content')
    readonly_fields = ('created_at', 'id')
    
    def content_length(self, obj):
        return len(obj.content)
    content_length.short_description = 'Content Length'
