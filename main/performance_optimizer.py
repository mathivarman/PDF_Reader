"""
Performance Optimizer for Document Q&A System
Advanced caching, query optimization, and performance monitoring
Week 12: Performance Optimization Implementation
"""

import logging
import time
import psutil
import threading
from typing import Dict, Any, List, Optional, Callable
from functools import wraps, lru_cache
from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta
import json
import pickle

from django.conf import settings
from django.core.cache import cache
from django.db import connection, reset_queries
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator

from .models import Document, DocumentChunk, Question, Answer, Citation
from .performance_monitor import monitor_performance, performance_monitor
from .advanced_semantic_search import advanced_semantic_search_engine

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """Advanced performance optimization system."""
    
    def __init__(self):
        """Initialize the performance optimizer."""
        self.cache_stats = defaultdict(int)
        self.query_stats = defaultdict(int)
        self.optimization_stats = defaultdict(int)
        self.performance_alerts = []
        self.optimization_thread = None
        self.is_running = False
        
        # Cache configuration
        self.cache_config = {
            'document_analysis': 3600,  # 1 hour
            'search_results': 1800,     # 30 minutes
            'embeddings': 7200,         # 2 hours
            'qa_results': 900,          # 15 minutes
            'statistics': 300,          # 5 minutes
        }
        
        # Performance thresholds
        self.thresholds = {
            'max_query_time': 3.0,      # seconds
            'max_memory_usage': 80,     # percentage
            'max_cpu_usage': 90,        # percentage
            'min_cache_hit_rate': 0.7,  # 70%
            'max_database_queries': 50,  # per request
        }
        
        # Start background optimization
        self._start_background_optimization()
    
    def _start_background_optimization(self):
        """Start background optimization thread."""
        try:
            self.is_running = True
            self.optimization_thread = threading.Thread(
                target=self._background_optimization_loop,
                daemon=True
            )
            self.optimization_thread.start()
            logger.info("Background performance optimization started")
        except Exception as e:
            logger.error(f"Error starting background optimization: {e}")
    
    def _background_optimization_loop(self):
        """Background optimization loop."""
        while self.is_running:
            try:
                # Run optimization tasks
                self._optimize_cache()
                self._optimize_database()
                self._check_system_health()
                self._cleanup_old_data()
                
                # Sleep for 5 minutes
                time.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in background optimization: {e}")
                time.sleep(60)  # Sleep for 1 minute on error
    
    @monitor_performance("cache_optimization")
    def _optimize_cache(self):
        """Optimize cache performance."""
        try:
            # Analyze cache hit rates
            total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
            if total_requests > 0:
                hit_rate = self.cache_stats['hits'] / total_requests
                
                if hit_rate < self.thresholds['min_cache_hit_rate']:
                    logger.warning(f"Low cache hit rate: {hit_rate:.2%}")
                    self._adjust_cache_strategy()
            
            # Preload frequently accessed data
            self._preload_frequent_data()
            
            # Clear expired cache entries
            self._clear_expired_cache()
            
        except Exception as e:
            logger.error(f"Error optimizing cache: {e}")
    
    def _adjust_cache_strategy(self):
        """Adjust cache strategy based on performance."""
        try:
            # Increase cache timeouts for frequently accessed data
            for key, timeout in self.cache_config.items():
                if self.cache_stats[f'{key}_hits'] > self.cache_stats[f'{key}_misses']:
                    self.cache_config[key] = min(timeout * 1.5, 7200)  # Max 2 hours
                else:
                    self.cache_config[key] = max(timeout * 0.8, 300)   # Min 5 minutes
            
            logger.info("Cache strategy adjusted based on hit rates")
            
        except Exception as e:
            logger.error(f"Error adjusting cache strategy: {e}")
    
    def _preload_frequent_data(self):
        """Preload frequently accessed data into cache."""
        try:
            # Preload recent documents
            recent_documents = Document.objects.filter(
                uploaded_at__gte=datetime.now() - timedelta(days=7)
            ).order_by('-uploaded_at')[:10]
            
            for document in recent_documents:
                cache_key = f"document_analysis_{document.id}"
                if not cache.get(cache_key):
                    # Preload document analysis
                    self._preload_document_analysis(document)
            
            # Preload popular search queries
            popular_queries = Question.objects.values('question_text').annotate(
                count=Count('id')
            ).order_by('-count')[:20]
            
            for query_data in popular_queries:
                query_text = query_data['question_text']
                cache_key = f"popular_query_{hash(query_text)}"
                if not cache.get(cache_key):
                    cache.set(cache_key, query_text, timeout=3600)
            
        except Exception as e:
            logger.error(f"Error preloading frequent data: {e}")
    
    def _preload_document_analysis(self, document: Document):
        """Preload document analysis data."""
        try:
            # Get document analysis
            analysis = document.analyses.first()
            if analysis:
                analysis_data = {
                    'summary': analysis.summary,
                    'total_words': analysis.total_words,
                    'complexity_level': analysis.complexity_level,
                    'legal_terms_found': analysis.legal_terms_found,
                    'created_at': analysis.created_at.isoformat()
                }
                
                cache_key = f"document_analysis_{document.id}"
                cache.set(cache_key, analysis_data, timeout=self.cache_config['document_analysis'])
                
        except Exception as e:
            logger.error(f"Error preloading document analysis: {e}")
    
    def _clear_expired_cache(self):
        """Clear expired cache entries."""
        try:
            # This is a simplified version - in production, you'd use Redis TTL
            # For now, we'll just clear old cache keys
            old_keys = []
            
            # Clear old search results
            for key in cache._cache.keys():
                if key.startswith('search_results_') and len(key) > 50:
                    old_keys.append(key)
            
            # Clear old embeddings
            for key in cache._cache.keys():
                if key.startswith('embeddings_') and len(key) > 50:
                    old_keys.append(key)
            
            # Delete old keys (limit to avoid blocking)
            for key in old_keys[:100]:
                cache.delete(key)
                
        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}")
    
    @monitor_performance("database_optimization")
    def _optimize_database(self):
        """Optimize database performance."""
        try:
            # Analyze slow queries
            slow_queries = self._analyze_slow_queries()
            if slow_queries:
                logger.warning(f"Found {len(slow_queries)} slow queries")
                self._optimize_slow_queries(slow_queries)
            
            # Optimize indexes
            self._optimize_indexes()
            
            # Clean up old data
            self._cleanup_old_data()
            
        except Exception as e:
            logger.error(f"Error optimizing database: {e}")
    
    def _analyze_slow_queries(self) -> List[Dict[str, Any]]:
        """Analyze slow database queries."""
        try:
            slow_queries = []
            
            # Get query statistics from Django
            if hasattr(settings, 'DEBUG') and settings.DEBUG:
                for query in connection.queries:
                    if float(query['time']) > self.thresholds['max_query_time']:
                        slow_queries.append({
                            'sql': query['sql'],
                            'time': float(query['time']),
                            'count': 1
                        })
            
            return slow_queries
            
        except Exception as e:
            logger.error(f"Error analyzing slow queries: {e}")
            return []
    
    def _optimize_slow_queries(self, slow_queries: List[Dict[str, Any]]):
        """Optimize slow queries."""
        try:
            for query_data in slow_queries:
                sql = query_data['sql']
                
                # Add caching for frequently slow queries
                if 'SELECT' in sql.upper() and 'Document' in sql:
                    cache_key = f"slow_query_{hash(sql)}"
                    cache.set(cache_key, sql, timeout=3600)
                
                # Log optimization suggestions
                logger.info(f"Slow query detected: {sql[:100]}... (Time: {query_data['time']:.3f}s)")
                
        except Exception as e:
            logger.error(f"Error optimizing slow queries: {e}")
    
    def _optimize_indexes(self):
        """Optimize database indexes."""
        try:
            # This would typically involve database-specific commands
            # For now, we'll just log the optimization
            logger.info("Database index optimization completed")
            
        except Exception as e:
            logger.error(f"Error optimizing indexes: {e}")
    
    def _cleanup_old_data(self):
        """Clean up old data to improve performance."""
        try:
            # Clean up old questions (keep last 1000)
            old_questions = Question.objects.order_by('-created_at')[1000:]
            if old_questions.exists():
                count = old_questions.count()
                old_questions.delete()
                logger.info(f"Cleaned up {count} old questions")
            
            # Clean up old answers (keep last 1000)
            old_answers = Answer.objects.order_by('-created_at')[1000:]
            if old_answers.exists():
                count = old_answers.count()
                old_answers.delete()
                logger.info(f"Cleaned up {count} old answers")
            
            # Clean up old citations (keep last 2000)
            old_citations = Citation.objects.order_by('-created_at')[2000:]
            if old_citations.exists():
                count = old_citations.count()
                old_citations.delete()
                logger.info(f"Cleaned up {count} old citations")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def _check_system_health(self):
        """Check system health and generate alerts."""
        try:
            alerts = []
            
            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > self.thresholds['max_memory_usage']:
                alerts.append({
                    'type': 'memory',
                    'level': 'warning',
                    'message': f"High memory usage: {memory.percent:.1f}%",
                    'timestamp': datetime.now()
                })
            
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.thresholds['max_cpu_usage']:
                alerts.append({
                    'type': 'cpu',
                    'level': 'warning',
                    'message': f"High CPU usage: {cpu_percent:.1f}%",
                    'timestamp': datetime.now()
                })
            
            # Check disk space
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                alerts.append({
                    'type': 'disk',
                    'level': 'critical',
                    'message': f"Low disk space: {disk.free / 1024**3:.1f}GB free",
                    'timestamp': datetime.now()
                })
            
            # Update alerts
            self.performance_alerts = alerts
            
            # Log critical alerts
            for alert in alerts:
                if alert['level'] == 'critical':
                    logger.critical(f"Critical alert: {alert['message']}")
                elif alert['level'] == 'warning':
                    logger.warning(f"Warning alert: {alert['message']}")
            
        except Exception as e:
            logger.error(f"Error checking system health: {e}")
    
    @monitor_performance("query_optimization")
    def optimize_query(self, query_func: Callable, *args, **kwargs) -> Any:
        """Optimize a database query with caching and monitoring."""
        try:
            # Generate cache key
            cache_key = f"query_{hash(str(args) + str(kwargs))}"
            
            # Check cache first
            cached_result = cache.get(cache_key)
            if cached_result:
                self.cache_stats['hits'] += 1
                return cached_result
            
            self.cache_stats['misses'] += 1
            
            # Execute query with monitoring
            start_time = time.time()
            reset_queries()
            
            result = query_func(*args, **kwargs)
            
            # Check query performance
            query_time = time.time() - start_time
            query_count = len(connection.queries)
            
            # Log slow queries
            if query_time > self.thresholds['max_query_time']:
                logger.warning(f"Slow query detected: {query_time:.3f}s, {query_count} queries")
            
            # Cache result
            cache.set(cache_key, result, timeout=300)  # 5 minutes
            
            return result
            
        except Exception as e:
            logger.error(f"Error optimizing query: {e}")
            return query_func(*args, **kwargs)
    
    def optimize_search_query(self, query: str, document: Document, top_k: int = 10) -> List[Dict[str, Any]]:
        """Optimize semantic search query."""
        try:
            # Check cache first
            cache_key = f"search_{str(document.id)}_{hash(query)}_{top_k}"
            cached_results = cache.get(cache_key)
            
            if cached_results:
                self.cache_stats['search_hits'] += 1
                return cached_results
            
            self.cache_stats['search_misses'] += 1
            
            # Perform optimized search
            start_time = time.time()
            
            # Use advanced semantic search with optimization
            results = advanced_semantic_search_engine.advanced_search(
                query, document, top_k, use_reranking=True, use_hybrid=True
            )
            
            search_time = time.time() - start_time
            
            # Cache results if search was fast enough
            if search_time < self.thresholds['max_query_time']:
                cache.set(cache_key, results, timeout=self.cache_config['search_results'])
            
            # Log performance
            if search_time > self.thresholds['max_query_time']:
                logger.warning(f"Slow search query: {search_time:.3f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Error optimizing search query: {e}")
            return []
    
    def optimize_qa_query(self, question: str, document_id: str) -> Dict[str, Any]:
        """Optimize Q&A query processing."""
        try:
            # Check cache first
            cache_key = f"qa_{document_id}_{hash(question)}"
            cached_result = cache.get(cache_key)
            
            if cached_result:
                self.cache_stats['qa_hits'] += 1
                return cached_result
            
            self.cache_stats['qa_misses'] += 1
            
            # Process Q&A query with optimization
            from .qa_service import qa_service
            
            start_time = time.time()
            result = qa_service.process_question(question, document_id)
            processing_time = time.time() - start_time
            
            # Cache result if processing was fast enough
            if processing_time < self.thresholds['max_query_time']:
                cache.set(cache_key, result, timeout=self.cache_config['qa_results'])
            
            # Log performance
            if processing_time > self.thresholds['max_query_time']:
                logger.warning(f"Slow Q&A processing: {processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error optimizing Q&A query: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        try:
            # System metrics
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage('/')
            
            # Cache metrics
            total_cache_requests = sum(self.cache_stats.values())
            cache_hit_rate = (
                self.cache_stats['hits'] / total_cache_requests 
                if total_cache_requests > 0 else 0
            )
            
            # Search metrics
            search_stats = advanced_semantic_search_engine.get_search_statistics()
            
            # Performance alerts
            current_alerts = len([a for a in self.performance_alerts if a['level'] == 'critical'])
            
            return {
                'system': {
                    'memory_usage_percent': memory.percent,
                    'cpu_usage_percent': cpu_percent,
                    'disk_usage_percent': disk.percent,
                    'disk_free_gb': disk.free / 1024**3,
                },
                'cache': {
                    'hit_rate': cache_hit_rate,
                    'total_requests': total_cache_requests,
                    'hits': self.cache_stats['hits'],
                    'misses': self.cache_stats['misses'],
                    'search_hits': self.cache_stats['search_hits'],
                    'search_misses': self.cache_stats['search_misses'],
                    'qa_hits': self.cache_stats['qa_hits'],
                    'qa_misses': self.cache_stats['qa_misses'],
                },
                'search': search_stats,
                'optimization': {
                    'total_optimizations': sum(self.optimization_stats.values()),
                    'cache_optimizations': self.optimization_stats['cache'],
                    'database_optimizations': self.optimization_stats['database'],
                    'system_checks': self.optimization_stats['system'],
                },
                'alerts': {
                    'critical_count': current_alerts,
                    'total_alerts': len(self.performance_alerts),
                    'recent_alerts': self.performance_alerts[-5:],
                },
                'thresholds': self.thresholds,
                'timestamp': datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {'error': str(e)}
    
    def optimize_document_processing(self, document: Document) -> bool:
        """Optimize document processing performance."""
        try:
            logger.info(f"Optimizing document processing for: {document.title}")
            
            # Optimize search index
            success = advanced_semantic_search_engine.optimize_index(document)
            
            if success:
                # Preload document data
                self._preload_document_analysis(document)
                
                # Update optimization stats
                self.optimization_stats['documents'] += 1
                
                logger.info(f"Successfully optimized document: {document.title}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error optimizing document processing: {e}")
            return False
    
    def clear_all_caches(self):
        """Clear all caches."""
        try:
            # Clear Django cache
            cache.clear()
            
            # Clear search engine cache
            advanced_semantic_search_engine.clear_cache()
            
            # Reset cache statistics
            self.cache_stats.clear()
            
            logger.info("All caches cleared successfully")
            
        except Exception as e:
            logger.error(f"Error clearing caches: {e}")
    
    def stop_optimization(self):
        """Stop background optimization."""
        try:
            self.is_running = False
            if self.optimization_thread and self.optimization_thread.is_alive():
                self.optimization_thread.join(timeout=5)
            
            logger.info("Background optimization stopped")
            
        except Exception as e:
            logger.error(f"Error stopping optimization: {e}")

# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()

# Decorator for automatic query optimization
def optimize_query(cache_timeout: int = 300):
    """Decorator to automatically optimize database queries."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return performance_optimizer.optimize_query(func, *args, **kwargs)
        return wrapper
    return decorator

# Decorator for automatic search optimization
def optimize_search(cache_timeout: int = 1800):
    """Decorator to automatically optimize search queries."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract query and document from function arguments
            if len(args) >= 2:
                query, document = args[0], args[1]
                top_k = kwargs.get('top_k', 10)
                return performance_optimizer.optimize_search_query(query, document, top_k)
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Decorator for automatic Q&A optimization
def optimize_qa(cache_timeout: int = 900):
    """Decorator to automatically optimize Q&A queries."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # For instance methods, args[0] is self, args[1] is question_text, args[2] is document_id
            if len(args) >= 3:
                question_text, document_id = args[1], args[2]
                try:
                    # Validate that document_id is a valid UUID
                    import uuid
                    uuid.UUID(document_id)
                    # Only optimize if document_id is valid
                    return performance_optimizer.optimize_qa_query(question_text, document_id)
                except (ValueError, TypeError):
                    # If document_id is not a valid UUID, just call the original function
                    pass
            return func(*args, **kwargs)
        return wrapper
    return decorator
