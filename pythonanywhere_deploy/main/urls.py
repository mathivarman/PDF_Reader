from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_document, name='upload'),
    path('documents/', views.document_list, name='document_list'),
    path('document/<uuid:document_id>/', views.document_detail, name='document_detail'),
    path('document/<uuid:document_id>/process/', views.process_document, name='process_document'),
    path('document/<uuid:document_id>/delete/', views.delete_document, name='delete_document'),
    path('upload/progress/', views.upload_progress, name='upload_progress'),
    path('performance/', views.performance_dashboard, name='performance_dashboard'),
    path('document/<uuid:document_id>/qa/', views.document_qa, name='document_qa'),
    path('document/<uuid:document_id>/ask/', views.ask_question, name='ask_question'),
    path('document/<uuid:document_id>/qa/history/', views.question_history, name='question_history'),
    path('document/<uuid:document_id>/qa/summary/', views.document_qa_summary, name='document_qa_summary'),
    path('enhanced/performance/', views.enhanced_performance_metrics, name='enhanced_performance_metrics'),
    path('document/<uuid:document_id>/optimize/', views.optimize_document, name='optimize_document'),
    path('about/', views.about, name='about'),
]
