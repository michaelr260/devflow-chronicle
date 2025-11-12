"""
Cache Manager Module
Intelligent caching system for Claude API responses
"""

import hashlib
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
from config import Config


class CacheManager:
    """Manages caching of API responses"""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Config.CACHE_DIR
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        self.enabled = Config.CACHE_ENABLED
        self.hits = 0
        self.misses = 0
    
    def _generate_cache_key(self, prompt: str, model: str, params: Optional[Dict] = None) -> str:
        """Generate unique cache key"""
        key_components = f"{model}:{prompt}"
        if params:
            key_components += f":{json.dumps(params, sort_keys=True)}"
        return hashlib.sha256(key_components.encode()).hexdigest()
    
    def get(self, prompt: str, model: str, params: Optional[Dict] = None, 
            max_age_hours: Optional[int] = None) -> Optional[Dict]:
        """Retrieve cached response if valid"""
        if not self.enabled:
            return None
        
        key = self._generate_cache_key(prompt, model, params)
        cache_file = self.cache_dir / f"{key}.json"
        
        if not cache_file.exists():
            self.misses += 1
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            max_age = max_age_hours or Config.CACHE_MAX_AGE_HOURS
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            age = datetime.now() - cached_time
            
            if age > timedelta(hours=max_age):
                self.misses += 1
                return None
            
            self.hits += 1
            return cache_data['response']
            
        except (json.JSONDecodeError, KeyError, ValueError):
            cache_file.unlink(missing_ok=True)
            self.misses += 1
            return None
    
    def set(self, prompt: str, model: str, response: Any, params: Optional[Dict] = None):
        """Store response in cache"""
        if not self.enabled:
            return
        
        key = self._generate_cache_key(prompt, model, params)
        cache_file = self.cache_dir / f"{key}.json"
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'model': model,
            'prompt_preview': prompt[:200],
            'params': params,
            'response': response
        }
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not write cache: {e}")
    
    def clear(self, max_age_days: Optional[int] = None):
        """Clear old cache files"""
        max_age = max_age_days or Config.CACHE_MAX_AGE_DAYS
        cutoff = datetime.now() - timedelta(days=max_age)
        removed_count = 0
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if file_time < cutoff:
                    cache_file.unlink()
                    removed_count += 1
            except Exception:
                pass
        
        if removed_count > 0:
            print(f"   [OK] Removed {removed_count} old cache file(s)")
    
    def clear_all(self):
        """Clear entire cache"""
        removed_count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                removed_count += 1
            except Exception:
                pass
        
        print(f"   [OK] Cleared {removed_count} cache file(s)")
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        cache_files = list(self.cache_dir.glob("*.json"))
        cache_size_bytes = sum(f.stat().st_size for f in cache_files)
        cache_size_mb = cache_size_bytes / (1024 * 1024)
        
        return {
            'enabled': self.enabled,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'total_files': len(cache_files),
            'size_mb': round(cache_size_mb, 2)
        }
