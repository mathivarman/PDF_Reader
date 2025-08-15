"""
Cache Manager for Performance Optimization
Handles caching of analysis results, clauses, and red flags
"""

import hashlib
import json
import logging
from typing import Dict, List, Optional, Any
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

class CacheManager:
    """Manages caching for document analysis and processing results."""
    
    CACHE_TIMEOUT = 3600  # 1 hour default
    CLAUSE_CACHE_PREFIX = "clause_"
    REDFLAG_CACHE_PREFIX = "redflag_"
    ANALYSIS_CACHE_PREFIX = "analysis_"
    DOCUMENT_CACHE_PREFIX = "document_"
    
    @staticmethod
    def _generate_cache_key(prefix: str, identifier: str) -> str:
        """Generate a cache key with prefix and identifier."""
        return f"{prefix}{identifier}"
    
    @staticmethod
    def _generate_content_hash(content: str) -> str:
        """Generate a hash for content-based caching."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    @classmethod
    def cache_document_analysis(cls, document_id: str, analysis_data: Dict[str, Any]) -> bool:
        """Cache document analysis results."""
        try:
            cache_key = cls._generate_cache_key(cls.ANALYSIS_CACHE_PREFIX, str(document_id))
            cache.set(cache_key, analysis_data, cls.CACHE_TIMEOUT)
            logger.info(f"Cached analysis for document {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error caching analysis for document {document_id}: {e}")
            return False
    
    @classmethod
    def get_cached_analysis(cls, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached analysis results."""
        try:
            cache_key = cls._generate_cache_key(cls.ANALYSIS_CACHE_PREFIX, str(document_id))
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"Retrieved cached analysis for document {document_id}")
            return cached_data
        except Exception as e:
            logger.error(f"Error retrieving cached analysis for document {document_id}: {e}")
            return None
    
    @classmethod
    def cache_clauses(cls, document_id: str, clauses: List[Dict[str, Any]]) -> bool:
        """Cache detected clauses."""
        try:
            cache_key = cls._generate_cache_key(cls.CLAUSE_CACHE_PREFIX, str(document_id))
            cache.set(cache_key, clauses, cls.CACHE_TIMEOUT)
            logger.info(f"Cached {len(clauses)} clauses for document {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error caching clauses for document {document_id}: {e}")
            return False
    
    @classmethod
    def get_cached_clauses(cls, document_id: str) -> Optional[List[Dict[str, Any]]]:
        """Retrieve cached clauses."""
        try:
            cache_key = cls._generate_cache_key(cls.CLAUSE_CACHE_PREFIX, str(document_id))
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"Retrieved cached clauses for document {document_id}")
            return cached_data
        except Exception as e:
            logger.error(f"Error retrieving cached clauses for document {document_id}: {e}")
            return None
    
    @classmethod
    def cache_red_flags(cls, document_id: str, red_flags: List[Dict[str, Any]]) -> bool:
        """Cache detected red flags."""
        try:
            cache_key = cls._generate_cache_key(cls.REDFLAG_CACHE_PREFIX, str(document_id))
            cache.set(cache_key, red_flags, cls.CACHE_TIMEOUT)
            logger.info(f"Cached {len(red_flags)} red flags for document {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error caching red flags for document {document_id}: {e}")
            return False
    
    @classmethod
    def get_cached_red_flags(cls, document_id: str) -> Optional[List[Dict[str, Any]]]:
        """Retrieve cached red flags."""
        try:
            cache_key = cls._generate_cache_key(cls.REDFLAG_CACHE_PREFIX, str(document_id))
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"Retrieved cached red flags for document {document_id}")
            return cached_data
        except Exception as e:
            logger.error(f"Error retrieving cached red flags for document {document_id}: {e}")
            return None
    
    @classmethod
    def invalidate_document_cache(cls, document_id: str) -> bool:
        """Invalidate all cache entries for a document."""
        try:
            keys_to_delete = [
                cls._generate_cache_key(cls.ANALYSIS_CACHE_PREFIX, str(document_id)),
                cls._generate_cache_key(cls.CLAUSE_CACHE_PREFIX, str(document_id)),
                cls._generate_cache_key(cls.REDFLAG_CACHE_PREFIX, str(document_id)),
                cls._generate_cache_key(cls.DOCUMENT_CACHE_PREFIX, str(document_id)),
            ]
            
            for key in keys_to_delete:
                cache.delete(key)
            
            logger.info(f"Invalidated cache for document {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error invalidating cache for document {document_id}: {e}")
            return False
    
    @classmethod
    def clear_all_cache(cls) -> bool:
        """Clear all cache entries."""
        try:
            cache.clear()
            logger.info("Cleared all cache entries")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            # This is a simplified version - in production you might want more detailed stats
            return {
                'cache_backend': getattr(settings, 'CACHES', {}).get('default', {}).get('BACKEND', 'Unknown'),
                'timeout': cls.CACHE_TIMEOUT,
                'status': 'active'
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {'status': 'error', 'message': str(e)}
