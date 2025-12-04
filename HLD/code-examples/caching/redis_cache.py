"""
Redis Caching Example
"""

import redis
import json

class CacheLayer:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379)
    
    def get(self, key):
        value = self.redis.get(key)
        return json.loads(value) if value else None
    
    def set(self, key, value, ttl=3600):
        self.redis.setex(key, ttl, json.dumps(value))
