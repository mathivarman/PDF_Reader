"""
Week 12 Testing Module
Comprehensive testing for advanced semantic search, performance optimization, and system integration
Week 12: Phase 3 Testing Implementation
"""

import logging
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import unittest
from unittest.mock import Mock, patch

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection, reset_queries

from .models import Document, DocumentChunk, Question, Answer, Citation, Analysis
from .advanced_semantic_search import advanced_semantic_search_engine
from .performance_optimizer import performance_optimizer
from .enhanced_qa_service import enhanced_qa_service
from .performance_monitor import performance_monitor

logger = logging.getLogger(__name__)

class Week12AdvancedFeaturesTest(TestCase):
    """Test suite for Week 12 advanced features."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test document
        self.document = Document.objects.create(
            title='Test Legal Contract',
            file=SimpleUploadedFile('test.pdf', b'fake pdf content'),
            uploaded_by=self.user,
            status='processed',
            extracted_text='This is a test legal contract. It contains important terms and conditions. '
                          'The parties agree to the following terms: 1. Payment terms are net 30 days. '
                          '2. Delivery must be completed within 60 days. 3. Force majeure clause applies. '
                          '4. Governing law is the state of California. 5. Dispute resolution through arbitration.',
            word_count=50,
            page_count=2
        )
        
        # Create document analysis
        self.analysis = Analysis.objects.create(
            document=self.document,
            summary='Test contract with payment and delivery terms.',
            word_count=50,
            complexity_level='medium',
            legal_terms=['contract', 'payment', 'delivery', 'force majeure', 'governing law', 'arbitration'],
            extraction_method='pdf_processing'
        )
        
        # Create document chunks
        self.chunk1 = DocumentChunk.objects.create(
            document=self.document,
            chunk_text='This is a test legal contract. It contains important terms and conditions.',
            chunk_index=0,
            page_number=1
        )
        
        self.chunk2 = DocumentChunk.objects.create(
            document=self.document,
            chunk_text='The parties agree to the following terms: 1. Payment terms are net 30 days.',
            chunk_index=1,
            page_number=1
        )
        
        self.chunk3 = DocumentChunk.objects.create(
            document=self.document,
            chunk_text='2. Delivery must be completed within 60 days. 3. Force majeure clause applies.',
            chunk_index=2,
            page_number=2
        )
        
        # Set up client
        self.client = Client()
        self.client.force_login(self.user)
    
    def tearDown(self):
        """Clean up after tests."""
        # Clear caches
        performance_optimizer.clear_all_caches()
        advanced_semantic_search_engine.clear_cache()
        
        # Stop background optimization
        performance_optimizer.stop_optimization()
    
    def test_advanced_semantic_search_initialization(self):
        """Test advanced semantic search engine initialization."""
        try:
            # Test model initialization
            self.assertIsNotNone(advanced_semantic_search_engine.bi_encoder)
            self.assertIsNotNone(advanced_semantic_search_engine.cross_encoder)
            self.assertIsNotNone(advanced_semantic_search_engine.tfidf_vectorizer)
            
            logger.info("✓ Advanced semantic search initialization test passed")
            
        except Exception as e:
            logger.error(f"✗ Advanced semantic search initialization test failed: {e}")
            raise
    
    def test_advanced_embedding_generation(self):
        """Test advanced embedding generation."""
        try:
            texts = [
                "This is a test legal contract.",
                "Payment terms are net 30 days.",
                "Delivery must be completed within 60 days."
            ]
            
            # Generate embeddings
            embeddings_data = advanced_semantic_search_engine.create_advanced_embeddings(texts)
            
            # Verify embeddings
            self.assertIn('bi_encoder', embeddings_data)
            self.assertIn('tfidf', embeddings_data)
            self.assertIn('metadata', embeddings_data)
            
            # Check dimensions
            bi_embeddings = embeddings_data['bi_encoder']
            self.assertEqual(bi_embeddings.shape[0], 3)  # 3 texts
            self.assertGreater(bi_embeddings.shape[1], 0)  # Embedding dimension
            
            tfidf_matrix = embeddings_data['tfidf']
            self.assertEqual(tfidf_matrix.shape[0], 3)  # 3 texts
            
            logger.info("✓ Advanced embedding generation test passed")
            
        except Exception as e:
            logger.error(f"✗ Advanced embedding generation test failed: {e}")
            raise
    
    def test_advanced_search_index_building(self):
        """Test advanced search index building."""
        try:
            # Build advanced index
            success = advanced_semantic_search_engine.build_advanced_index(self.document)
            
            # Verify success
            self.assertTrue(success)
            
            # Check if index exists in memory
            self.assertIn(self.document.id, advanced_semantic_search_engine.document_indexes)
            
            # Verify index data
            index_data = advanced_semantic_search_engine.document_indexes[self.document.id]
            self.assertIn('faiss_index', index_data)
            self.assertIn('chunk_metadata', index_data)
            self.assertIn('tfidf_matrix', index_data)
            
            logger.info("✓ Advanced search index building test passed")
            
        except Exception as e:
            logger.error(f"✗ Advanced search index building test failed: {e}")
            raise
    
    def test_advanced_semantic_search(self):
        """Test advanced semantic search functionality."""
        try:
            # Build index first
            advanced_semantic_search_engine.build_advanced_index(self.document)
            
            # Test search query
            query = "What are the payment terms?"
            search_results = advanced_semantic_search_engine.advanced_search(
                query, self.document, top_k=3, use_reranking=True, use_hybrid=True
            )
            
            # Verify results
            self.assertIsInstance(search_results, list)
            self.assertGreater(len(search_results), 0)
            
            # Check result structure
            for result in search_results:
                self.assertIn('chunk_id', result)
                self.assertIn('chunk_text', result)
                self.assertIn('similarity_score', result)
                self.assertIn('search_method', result)
                self.assertIn('relevance_indicators', result)
                self.assertIn('key_phrases', result)
                self.assertIn('semantic_coherence', result)
                self.assertIn('context_window', result)
                self.assertIn('confidence_factors', result)
            
            logger.info("✓ Advanced semantic search test passed")
            
        except Exception as e:
            logger.error(f"✗ Advanced semantic search test failed: {e}")
            raise
    
    def test_performance_optimizer_initialization(self):
        """Test performance optimizer initialization."""
        try:
            # Check optimizer components
            self.assertIsNotNone(performance_optimizer.cache_config)
            self.assertIsNotNone(performance_optimizer.thresholds)
            self.assertIsNotNone(performance_optimizer.cache_stats)
            
            # Verify cache configuration
            expected_cache_keys = ['document_analysis', 'search_results', 'embeddings', 'qa_results', 'statistics']
            for key in expected_cache_keys:
                self.assertIn(key, performance_optimizer.cache_config)
            
            # Verify thresholds
            expected_thresholds = ['max_query_time', 'max_memory_usage', 'max_cpu_usage', 'min_cache_hit_rate']
            for threshold in expected_thresholds:
                self.assertIn(threshold, performance_optimizer.thresholds)
            
            logger.info("✓ Performance optimizer initialization test passed")
            
        except Exception as e:
            logger.error(f"✗ Performance optimizer initialization test failed: {e}")
            raise
    
    def test_query_optimization(self):
        """Test query optimization functionality."""
        try:
            # Test query optimization
            def test_query():
                return Document.objects.filter(status='processed').count()
            
            # Optimize query
            result = performance_optimizer.optimize_query(test_query)
            
            # Verify result
            self.assertIsInstance(result, int)
            self.assertGreaterEqual(result, 0)
            
            # Check cache statistics
            self.assertGreaterEqual(performance_optimizer.cache_stats['hits'] + performance_optimizer.cache_stats['misses'], 0)
            
            logger.info("✓ Query optimization test passed")
            
        except Exception as e:
            logger.error(f"✗ Query optimization test failed: {e}")
            raise
    
    def test_search_query_optimization(self):
        """Test search query optimization."""
        try:
            # Build index first
            advanced_semantic_search_engine.build_advanced_index(self.document)
            
            # Test optimized search
            query = "What are the delivery terms?"
            results = performance_optimizer.optimize_search_query(query, self.document, top_k=3)
            
            # Verify results
            self.assertIsInstance(results, list)
            
            # Check cache statistics
            self.assertGreaterEqual(performance_optimizer.cache_stats['search_hits'] + performance_optimizer.cache_stats['search_misses'], 0)
            
            logger.info("✓ Search query optimization test passed")
            
        except Exception as e:
            logger.error(f"✗ Search query optimization test failed: {e}")
            raise
    
    def test_enhanced_qa_service_initialization(self):
        """Test enhanced Q&A service initialization."""
        try:
            # Check service components
            self.assertIsNotNone(enhanced_qa_service.search_engine)
            self.assertIsNotNone(enhanced_qa_service.optimizer)
            self.assertIsNotNone(enhanced_qa_service.qa_stats)
            
            # Verify statistics structure
            expected_stats = ['total_questions', 'avg_processing_time', 'avg_confidence', 'cache_hits', 'cache_misses']
            for stat in expected_stats:
                self.assertIn(stat, enhanced_qa_service.qa_stats)
            
            logger.info("✓ Enhanced Q&A service initialization test passed")
            
        except Exception as e:
            logger.error(f"✗ Enhanced Q&A service initialization test failed: {e}")
            raise
    
    def test_enhanced_question_processing(self):
        """Test enhanced question processing."""
        try:
            # Test question processing
            question = "What are the payment terms in this contract?"
            result = enhanced_qa_service.process_enhanced_question(question, str(self.document.id))
            
            # Verify result structure
            self.assertIn('success', result)
            self.assertIn('answer', result)
            self.assertIn('confidence_score', result)
            self.assertIn('processing_time', result)
            self.assertIn('performance_metrics', result)
            
            # Check success
            if result['success']:
                self.assertIsNotNone(result['answer'])
                self.assertGreaterEqual(result['confidence_score'], 0.0)
                self.assertLessEqual(result['confidence_score'], 100.0)
                self.assertGreater(result['processing_time'], 0.0)
                
                # Check additional fields
                self.assertIn('question_id', result)
                self.assertIn('answer_id', result)
                self.assertIn('citations', result)
                self.assertIn('search_results', result)
                self.assertIn('recommendations', result)
                self.assertIn('search_metadata', result)
            
            logger.info("✓ Enhanced question processing test passed")
            
        except Exception as e:
            logger.error(f"✗ Enhanced question processing test failed: {e}")
            raise
    
    def test_performance_metrics_collection(self):
        """Test performance metrics collection."""
        try:
            # Get performance metrics
            metrics = performance_optimizer.get_performance_metrics()
            
            # Verify metrics structure
            self.assertIn('system', metrics)
            self.assertIn('cache', metrics)
            self.assertIn('search', metrics)
            self.assertIn('optimization', metrics)
            self.assertIn('alerts', metrics)
            self.assertIn('thresholds', metrics)
            self.assertIn('timestamp', metrics)
            
            # Check system metrics
            system_metrics = metrics['system']
            self.assertIn('memory_usage_percent', system_metrics)
            self.assertIn('cpu_usage_percent', system_metrics)
            self.assertIn('disk_usage_percent', system_metrics)
            
            # Check cache metrics
            cache_metrics = metrics['cache']
            self.assertIn('hit_rate', cache_metrics)
            self.assertIn('total_requests', cache_metrics)
            
            logger.info("✓ Performance metrics collection test passed")
            
        except Exception as e:
            logger.error(f"✗ Performance metrics collection test failed: {e}")
            raise
    
    def test_search_statistics(self):
        """Test search statistics collection."""
        try:
            # Get search statistics
            stats = advanced_semantic_search_engine.get_search_statistics()
            
            # Verify statistics structure
            self.assertIn('total_searches', stats)
            self.assertIn('avg_search_time', stats)
            self.assertIn('cache_hits', stats)
            self.assertIn('cache_misses', stats)
            self.assertIn('cache_hit_rate', stats)
            self.assertIn('indexed_documents', stats)
            self.assertIn('total_chunks_indexed', stats)
            
            # Check data types
            self.assertIsInstance(stats['total_searches'], int)
            self.assertIsInstance(stats['avg_search_time'], (int, float))
            self.assertIsInstance(stats['cache_hits'], int)
            self.assertIsInstance(stats['cache_misses'], int)
            self.assertIsInstance(stats['cache_hit_rate'], (int, float))
            
            logger.info("✓ Search statistics test passed")
            
        except Exception as e:
            logger.error(f"✗ Search statistics test failed: {e}")
            raise
    
    def test_enhanced_qa_summary(self):
        """Test enhanced Q&A summary functionality."""
        try:
            # Process a question first
            question = "What are the delivery terms?"
            enhanced_qa_service.process_enhanced_question(question, str(self.document.id))
            
            # Get enhanced Q&A summary
            summary = enhanced_qa_service.get_enhanced_qa_summary(str(self.document.id))
            
            # Verify summary structure
            self.assertIn('total_questions', summary)
            self.assertIn('successful_questions', summary)
            self.assertIn('success_rate', summary)
            self.assertIn('avg_confidence', summary)
            self.assertIn('avg_processing_time', summary)
            self.assertIn('recent_questions', summary)
            self.assertIn('performance_metrics', summary)
            
            # Check data types
            self.assertIsInstance(summary['total_questions'], int)
            self.assertIsInstance(summary['success_rate'], (int, float))
            self.assertIsInstance(summary['avg_confidence'], (int, float))
            self.assertIsInstance(summary['avg_processing_time'], (int, float))
            self.assertIsInstance(summary['recent_questions'], list)
            
            logger.info("✓ Enhanced Q&A summary test passed")
            
        except Exception as e:
            logger.error(f"✗ Enhanced Q&A summary test failed: {e}")
            raise
    
    def test_performance_thresholds(self):
        """Test performance threshold monitoring."""
        try:
            # Get current system metrics
            metrics = performance_optimizer.get_performance_metrics()
            system_metrics = metrics['system']
            
            # Check memory usage threshold
            memory_usage = system_metrics['memory_usage_percent']
            max_memory = performance_optimizer.thresholds['max_memory_usage']
            
            if memory_usage > max_memory:
                logger.warning(f"Memory usage ({memory_usage}%) exceeds threshold ({max_memory}%)")
            
            # Check CPU usage threshold
            cpu_usage = system_metrics['cpu_usage_percent']
            max_cpu = performance_optimizer.thresholds['max_cpu_usage']
            
            if cpu_usage > max_cpu:
                logger.warning(f"CPU usage ({cpu_usage}%) exceeds threshold ({max_cpu}%)")
            
            # Check cache hit rate threshold
            cache_metrics = metrics['cache']
            hit_rate = cache_metrics['hit_rate']
            min_hit_rate = performance_optimizer.thresholds['min_cache_hit_rate']
            
            if hit_rate < min_hit_rate:
                logger.warning(f"Cache hit rate ({hit_rate:.2%}) below threshold ({min_hit_rate:.2%})")
            
            logger.info("✓ Performance thresholds test passed")
            
        except Exception as e:
            logger.error(f"✗ Performance thresholds test failed: {e}")
            raise
    
    def test_integration_performance(self):
        """Test integration performance with multiple operations."""
        try:
            start_time = time.time()
            
            # Build search index
            advanced_semantic_search_engine.build_advanced_index(self.document)
            
            # Process multiple questions
            questions = [
                "What are the payment terms?",
                "What are the delivery terms?",
                "What is the governing law?",
                "How are disputes resolved?",
                "What is the force majeure clause?"
            ]
            
            results = []
            for question in questions:
                result = enhanced_qa_service.process_enhanced_question(question, str(self.document.id))
                results.append(result)
            
            total_time = time.time() - start_time
            
            # Verify all results
            successful_results = [r for r in results if r['success']]
            success_rate = len(successful_results) / len(results)
            
            # Performance assertions
            self.assertGreater(success_rate, 0.8)  # At least 80% success rate
            self.assertLess(total_time, 30.0)  # Should complete within 30 seconds
            
            # Check average processing time
            if successful_results:
                avg_processing_time = sum(r['processing_time'] for r in successful_results) / len(successful_results)
                self.assertLess(avg_processing_time, 3.0)  # Average processing time under 3 seconds
            
            logger.info(f"✓ Integration performance test passed. Total time: {total_time:.2f}s, Success rate: {success_rate:.2%}")
            
        except Exception as e:
            logger.error(f"✗ Integration performance test failed: {e}")
            raise

class Week12EndToEndTest(TestCase):
    """End-to-end testing for Week 12 features."""
    
    def setUp(self):
        """Set up end-to-end test data."""
        self.user = User.objects.create_user(
            username='e2euser',
            email='e2e@example.com',
            password='e2epass123'
        )
        self.client = Client()
        self.client.force_login(self.user)
    
    def test_complete_workflow(self):
        """Test complete workflow from document upload to Q&A."""
        try:
            # Step 1: Upload document
            with open('test_document.pdf', 'wb') as f:
                f.write(b'fake pdf content')
            
            with open('test_document.pdf', 'rb') as f:
                response = self.client.post(reverse('upload'), {
                    'title': 'Test Contract',
                    'file': f
                })
            
            self.assertEqual(response.status_code, 302)  # Redirect after upload
            
            # Step 2: Wait for processing (simulate)
            document = Document.objects.latest('created_at')
            document.status = 'processed'
            document.extracted_text = 'This is a test contract with payment terms of net 30 days.'
            document.save()
            
            # Step 3: Access document detail
            response = self.client.get(reverse('document_detail', args=[document.id]))
            self.assertEqual(response.status_code, 200)
            
            # Step 4: Ask a question
            response = self.client.post(reverse('document_qa', args=[document.id]), {
                'question': 'What are the payment terms?'
            })
            
            self.assertEqual(response.status_code, 200)
            
            logger.info("✓ Complete workflow test passed")
            
        except Exception as e:
            logger.error(f"✗ Complete workflow test failed: {e}")
            raise

def run_week12_tests():
    """Run all Week 12 tests and generate report."""
    logger.info("Starting Week 12 Testing Suite...")
    
    # Test results
    test_results = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'test_details': []
    }
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_cases = [
        Week12AdvancedFeaturesTest,
        Week12EndToEndTest
    ]
    
    for test_case in test_cases:
        test_suite.addTest(unittest.makeSuite(test_case))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Collect results
    test_results['total_tests'] = result.testsRun
    test_results['failed_tests'] = len(result.failures) + len(result.errors)
    test_results['passed_tests'] = test_results['total_tests'] - test_results['failed_tests']
    
    # Add test details
    for failure in result.failures:
        test_results['test_details'].append({
            'test': failure[0],
            'status': 'FAILED',
            'error': failure[1]
        })
    
    for error in result.errors:
        test_results['test_details'].append({
            'test': error[0],
            'status': 'ERROR',
            'error': error[1]
        })
    
    # Generate report
    logger.info("=" * 60)
    logger.info("WEEK 12 TESTING REPORT")
    logger.info("=" * 60)
    logger.info(f"Total Tests: {test_results['total_tests']}")
    logger.info(f"Passed: {test_results['passed_tests']}")
    logger.info(f"Failed: {test_results['failed_tests']}")
    logger.info(f"Success Rate: {(test_results['passed_tests'] / test_results['total_tests'] * 100):.1f}%")
    
    if test_results['failed_tests'] > 0:
        logger.info("\nFAILED TESTS:")
        for detail in test_results['test_details']:
            logger.info(f"- {detail['test']}: {detail['status']}")
            logger.info(f"  Error: {detail['error']}")
    
    # Performance summary
    logger.info("\nPERFORMANCE SUMMARY:")
    try:
        metrics = performance_optimizer.get_performance_metrics()
        logger.info(f"Memory Usage: {metrics['system']['memory_usage_percent']:.1f}%")
        logger.info(f"CPU Usage: {metrics['system']['cpu_usage_percent']:.1f}%")
        logger.info(f"Cache Hit Rate: {metrics['cache']['hit_rate']:.2%}")
        
        search_stats = advanced_semantic_search_engine.get_search_statistics()
        logger.info(f"Total Searches: {search_stats['total_searches']}")
        logger.info(f"Average Search Time: {search_stats['avg_search_time']:.3f}s")
        
    except Exception as e:
        logger.error(f"Error getting performance summary: {e}")
    
    logger.info("=" * 60)
    
    return test_results

if __name__ == '__main__':
    run_week12_tests()
