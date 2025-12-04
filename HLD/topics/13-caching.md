# 13. Caching (Redis, Memcached)

Caching is like remembering where you left your keys instead of searching the entire house every time. Except sometimes the keys move, and your memory is lying to you. 🔑

[← Back to Main](../README.md) | [Previous: ACID vs BASE](12-acid-vs-base.md) | [Next: CDN →](14-cdn.md)

---

## 🎯 Quick Summary

**Caching** stores frequently accessed data in fast memory (RAM) to avoid slow database queries. Redis and Memcached are popular caching systems. Caching trades memory for speed: data loads 10-100x faster from cache than database. But cached data can become stale, requiring invalidation strategies.

Think of it as: **Cache = Fast Memory for Hot Data**

---

## 🌟 Beginner Explanation

### The Library Analogy

**WITHOUT CACHE (Slow):**

```
Student needs book "System Design 101"

Every time they need it:
├─ Walk to library (5 minutes)
├─ Find book in catalog (2 minutes)
├─ Go to shelf (3 minutes)
├─ Find book (2 minutes)
├─ Walk back (5 minutes)
└─ Total: 17 minutes per lookup! 🐢

If they need it 10 times:
10 × 17 minutes = 170 minutes (almost 3 hours!)
```

**WITH CACHE (Fast):**

```
Student keeps book on desk (cache)

First time:
├─ Walk to library (5 minutes)
├─ Find book (12 minutes)
├─ Keep on desk ✅
└─ Total: 17 minutes

Next 9 times:
├─ Reach to desk (5 seconds)
└─ Total: 45 seconds

Overall:
17 minutes + 45 seconds = ~18 minutes total ⚡
vs 170 minutes without cache
Speedup: 9.4x faster!
```

### How Caching Works

```
USER REQUEST FLOW:

Client: "Get user 123's data"
    ↓
Application:
├─ 1. Check cache: "Is user 123 in cache?"
│  ├─ YES (cache hit): Return from cache ✅ (1ms)
│  └─ NO (cache miss): Go to step 2
│
└─ 2. Query database: "SELECT * FROM users WHERE id=123"
   ├─ Database responds (50ms) 🐢
   ├─ Store in cache for next time
   └─ Return to client

Next request for user 123:
├─ Cache hit! ✅
└─ Response time: 1ms (50x faster!)

CACHE HIT RATIO:
- 90% cache hits = 90% of requests fast ✅
- 10% cache hits = 90% of requests slow ❌
```

### Redis vs Memcached

```
REDIS (Rich Features):
├─ Data structures: Strings, Lists, Sets, Hashes, Sorted Sets
├─ Persistence: Can save to disk
├─ Replication: Master-slave
├─ Pub/Sub: Message broadcasting
├─ Atomic operations: INCR, DECR
└─ Use: Complex caching, counters, leaderboards

MEMCACHED (Simple & Fast):
├─ Data structures: Key-value only (strings)
├─ Persistence: None (RAM only)
├─ Replication: None
├─ Simple: Just get/set
├─ Multi-threaded: Better CPU usage
└─ Use: Simple caching, sessions

COMPARISON:
Speed: Memcached slightly faster
Features: Redis wins
Complexity: Memcached simpler
Persistence: Redis only
```

---

## 🔬 Advanced Explanation

### Cache Strategies

**STRATEGY 1: Cache-Aside (Lazy Loading)**

```
Application controls cache

READ:
Client → App
App checks cache:
├─ Hit: Return cached data ✅
└─ Miss:
    ├─ Query database
    ├─ Store in cache
    └─ Return data

WRITE:
Client → App → Database
App invalidates/updates cache

Pros:
✅ Only cache what's needed
✅ Simple
✅ Cache failures don't break app

Cons:
❌ First request always slow (cache miss)
❌ Stale data possible
❌ More code in application
```

**STRATEGY 2: Write-Through**

```
Application writes to cache AND database

WRITE:
Client → App
App writes to:
├─ Cache (fast)
└─ Database (slow, but both updated)

READ:
Client → App → Cache (always fresh!)

Pros:
✅ Data always consistent
✅ No stale reads

Cons:
❌ Write penalty (must write to both)
❌ Cache might store unused data
```

**STRATEGY 3: Write-Behind (Write-Back)**

```
Write to cache first, database later

WRITE:
Client → App → Cache (fast! ✅)
Later: Cache → Database (async)

READ:
Client → App → Cache

Pros:
✅ Fast writes
✅ Can batch database writes
✅ Reduces database load

Cons:
❌ Data loss risk (if cache crashes before DB write)
❌ Complex
❌ Consistency issues
```

**STRATEGY 4: Read-Through**

```
Cache handles database reads

READ:
Client → App → Cache
Cache checks:
├─ Hit: Return data
└─ Miss:
    ├─ Cache queries database
    ├─ Cache stores result
    └─ Return to app

Pros:
✅ Application simpler (cache handles DB)
✅ Consistent loading

Cons:
❌ First request slow
❌ Requires cache to know about DB
```

### Cache Eviction Policies

**When cache is full, what to remove?**

**LRU (Least Recently Used):**
```
Cache full, need space

Items in cache:
├─ User 1: Last accessed 5 minutes ago
├─ User 2: Last accessed 2 hours ago ← Evict this!
├─ User 3: Last accessed 10 minutes ago
└─ User 4: Last accessed 1 minute ago

Remove User 2 (oldest access)

Good for: General purpose
Bad for: Scan-based access (everything becomes "recent")
```

**LFU (Least Frequently Used):**
```
Cache full, need space

Items in cache:
├─ User 1: Accessed 100 times
├─ User 2: Accessed 5 times ← Evict this!
├─ User 3: Accessed 50 times
└─ User 4: Accessed 200 times

Remove User 2 (least frequent)

Good for: Popular items
Bad for: New popular items (start with low count)
```

**FIFO (First In First Out):**
```
Cache full, need space

Items in cache:
├─ User 1: Added at T=0 ← Evict this!
├─ User 2: Added at T=5
├─ User 3: Added at T=10
└─ User 4: Added at T=15

Remove oldest entry

Good for: Simple, fair
Bad for: Doesn't consider popularity
```

**TTL (Time To Live):**
```
Every item has expiration time

Items in cache:
├─ User 1: TTL=60s (expires in 60s)
├─ User 2: TTL=300s (expires in 5 min)
└─ User 3: TTL=expired! ← Remove

Good for: Ensures freshness
Bad for: Popular items might expire
```

### Cache Invalidation

**PROBLEM: Stale Data**

```
Database: user.email = "new@example.com"
Cache: user.email = "old@example.com" ❌ Stale!

User confused: "I updated my email, why does it show old?"
```

**SOLUTION 1: TTL (Time-Based)**

```
Set expiration on cache entry:

SET user:123 {...} EX 300  # Expires in 300 seconds

After 5 minutes:
├─ Cache automatically removes entry
├─ Next request: Cache miss
├─ Re-fetch from database (fresh data)

Pros: Simple, automatic
Cons: Stale for up to TTL duration
```

**SOLUTION 2: Explicit Invalidation**

```
On database write:

UPDATE users SET email='new@...' WHERE id=123;
DELETE cache key "user:123";  ← Invalidate cache

Next read:
├─ Cache miss (was deleted)
├─ Fetch fresh from database
└─ Store in cache

Pros: Always fresh
Cons: Every write must invalidate cache (complexity)
```

**SOLUTION 3: Write-Through**

```
On write:

UPDATE users SET email='new@...' WHERE id=123;
SET cache "user:123" to new data;  ← Update cache

Cache and DB always synchronized

Pros: Never stale
Cons: Extra work on writes
```

### Distributed Caching

**SINGLE CACHE (Simple):**

```
All apps → Single Redis

Problems:
❌ Single point of failure
❌ Limited capacity (one server's RAM)
❌ Can't scale beyond one machine
```

**DISTRIBUTED CACHE (Scalable):**

```
Consistent Hashing:

Cache 1: Keys hash(0) - hash(333)
Cache 2: Keys hash(334) - hash(666)
Cache 3: Keys hash(667) - hash(999)

Request for "user:123":
├─ hash("user:123") = 456
├─ Route to Cache 2 ✅
└─ Get/Set on Cache 2

Benefits:
✅ Scale horizontally (add more caches)
✅ Higher capacity
✅ Better throughput

Challenges:
❌ Resharding when adding/removing nodes
❌ Replication for reliability
```

### Cache Stampede Problem

```
PROBLEM: Cache expires during high traffic

Timeline:

T=0s: Cache has user:123 ✅
T=300s: TTL expires, cache empty
T=300.001s: 1000 requests arrive simultaneously!

All 1000 requests:
├─ Cache miss
├─ Query database (1000 queries!) 💥
└─ Database overwhelmed!

SOLUTION 1: Locking
Request 1: Gets lock, queries DB
Requests 2-1000: Wait for Request 1 to finish

SOLUTION 2: Probabilistic Early Expiration
Refresh cache BEFORE expiry (randomly)
├─ TTL=300s
├─ At T=280s: Randomly refresh
└─ Avoids everyone hitting at T=300s

SOLUTION 3: Background Refresh
Separate process refreshes popular keys
Never let them expire
```

---

## 🐍 Python Code Example

### ❌ Without Cache (Slow)

```python
# ===== WITHOUT CACHE (SLOW) =====

import time

class SlowDatabase:
    """Simulates slow database"""
    
    def __init__(self):
        self.users = {
            1: {"name": "Alice", "email": "alice@example.com"},
            2: {"name": "Bob", "email": "bob@example.com"},
            3: {"name": "Carol", "email": "carol@example.com"}
        }
    
    def get_user(self, user_id):
        """Simulate slow database query"""
        time.sleep(0.05)  # 50ms query time
        return self.users.get(user_id)

# Usage
db = SlowDatabase()

print("=== WITHOUT CACHE ===\n")

# 100 requests for same user
start = time.time()
for i in range(100):
    user = db.get_user(1)
elapsed = time.time() - start

print(f"100 requests for user 1:")
print(f"Time: {elapsed:.2f}s")
print(f"Avg per request: {elapsed/100*1000:.1f}ms")

# Output:
# 100 requests for user 1:
# Time: 5.00s
# Avg per request: 50.0ms
#
# ❌ Every request hits slow database!
```

### ✅ With Cache (Fast)

```python
# ===== WITH CACHE (FAST) =====

import time

class SimpleCache:
    """Simple in-memory cache"""
    
    def __init__(self):
        self.cache = {}
    
    def get(self, key):
        """Get from cache"""
        return self.cache.get(key)
    
    def set(self, key, value, ttl=None):
        """Set in cache"""
        self.cache[key] = value
        # TTL not implemented in simple version
    
    def delete(self, key):
        """Delete from cache"""
        if key in self.cache:
            del self.cache[key]

class CachedDatabase:
    """Database with caching"""
    
    def __init__(self, db):
        self.db = db
        self.cache = SimpleCache()
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get_user(self, user_id):
        """Get user with cache-aside pattern"""
        
        # Check cache first
        cache_key = f"user:{user_id}"
        cached = self.cache.get(cache_key)
        
        if cached is not None:
            # Cache hit!
            self.cache_hits += 1
            return cached
        
        # Cache miss - query database
        self.cache_misses += 1
        user = self.db.get_user(user_id)
        
        # Store in cache for next time
        if user:
            self.cache.set(cache_key, user)
        
        return user
    
    def get_stats(self):
        """Cache statistics"""
        total = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total * 100 if total > 0 else 0
        return {
            "hits": self.cache_hits,
            "misses": self.cache_misses,
            "hit_rate": hit_rate
        }

# Usage
db = SlowDatabase()
cached_db = CachedDatabase(db)

print("=== WITH CACHE ===\n")

# 100 requests for same user
start = time.time()
for i in range(100):
    user = cached_db.get_user(1)
elapsed = time.time() - start

print(f"100 requests for user 1:")
print(f"Time: {elapsed:.3f}s")
print(f"Avg per request: {elapsed/100*1000:.1f}ms")

stats = cached_db.get_stats()
print(f"\nCache Stats:")
print(f"  Hits: {stats['hits']}")
print(f"  Misses: {stats['misses']}")
print(f"  Hit Rate: {stats['hit_rate']:.1f}%")
print(f"\nSpeedup: {5.0/elapsed:.0f}x faster!")

# Output:
# 100 requests for user 1:
# Time: 0.050s
# Avg per request: 0.5ms
#
# Cache Stats:
#   Hits: 99
#   Misses: 1
#   Hit Rate: 99.0%
#
# Speedup: 100x faster!
```

### ✅ Production Redis Cache

```python
# ===== PRODUCTION REDIS CACHE =====

import redis
import json
import time

class RedisCache:
    """Production-grade Redis cache"""
    
    def __init__(self, host='localhost', port=6379):
        self.client = redis.Redis(
            host=host,
            port=port,
            decode_responses=True
        )
    
    def get(self, key):
        """Get from Redis"""
        value = self.client.get(key)
        if value:
            return json.loads(value)
        return None
    
    def set(self, key, value, ttl=300):
        """Set in Redis with TTL"""
        self.client.setex(
            key,
            ttl,
            json.dumps(value)
        )
    
    def delete(self, key):
        """Delete from Redis"""
        self.client.delete(key)
    
    def increment(self, key, amount=1):
        """Atomic increment (Redis-specific)"""
        return self.client.incr(key, amount)
    
    def get_stats(self):
        """Redis server stats"""
        info = self.client.info('stats')
        return {
            "hits": info.get('keyspace_hits', 0),
            "misses": info.get('keyspace_misses', 0),
            "total_keys": self.client.dbsize()
        }

class ProductionCachedDB:
    """Production database with Redis caching"""
    
    def __init__(self, db):
        self.db = db
        self.cache = RedisCache()
    
    def get_user(self, user_id):
        """Get user with cache"""
        cache_key = f"user:{user_id}"
        
        # Try cache
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # Query database
        user = self.db.get_user(user_id)
        
        # Store in cache with 5-minute TTL
        if user:
            self.cache.set(cache_key, user, ttl=300)
        
        return user
    
    def update_user(self, user_id, updates):
        """Update user and invalidate cache"""
        # Update database
        self.db.update_user(user_id, updates)
        
        # Invalidate cache (cache-aside pattern)
        cache_key = f"user:{user_id}"
        self.cache.delete(cache_key)
    
    def increment_view_count(self, user_id):
        """Atomic counter (Redis-specific)"""
        cache_key = f"user:{user_id}:views"
        return self.cache.increment(cache_key)

# Usage (requires running Redis server)
# redis-server --port 6379

# db = SlowDatabase()
# cached_db = ProductionCachedDB(db)
# 
# user = cached_db.get_user(1)
# print(f"User: {user}")
# 
# # Increment view count
# views = cached_db.increment_view_count(1)
# print(f"Views: {views}")
```

### ✅ Cache Strategies Implementation

```python
class CacheStrategies:
    """Different caching strategies"""
    
    def __init__(self, db, cache):
        self.db = db
        self.cache = cache
    
    def cache_aside(self, user_id):
        """Cache-Aside (Lazy Loading)"""
        key = f"user:{user_id}"
        
        # Check cache
        cached = self.cache.get(key)
        if cached:
            return cached
        
        # Load from DB
        user = self.db.get_user(user_id)
        
        # Store in cache
        self.cache.set(key, user, ttl=300)
        
        return user
    
    def write_through(self, user_id, user_data):
        """Write-Through (update both)"""
        key = f"user:{user_id}"
        
        # Write to database
        self.db.update_user(user_id, user_data)
        
        # Write to cache
        self.cache.set(key, user_data, ttl=300)
    
    def write_behind(self, user_id, user_data):
        """Write-Behind (async DB write)"""
        key = f"user:{user_id}"
        
        # Write to cache immediately
        self.cache.set(key, user_data, ttl=300)
        
        # Queue DB write (async)
        import threading
        def async_write():
            time.sleep(1)  # Simulate delay
            self.db.update_user(user_id, user_data)
        
        threading.Thread(target=async_write, daemon=True).start()
        
        return True  # Return immediately!
```

---

## 💡 Mini Project: "Build a Caching System"

### Phase 1: Simple In-Memory Cache ⭐

**Requirements:**
- Get/Set operations
- TTL support
- Cache statistics
- LRU eviction

---

### Phase 2: Distributed Cache ⭐⭐

**Requirements:**
- Multiple cache nodes
- Consistent hashing
- Replication
- Failover

---

### Phase 3: Production-Grade ⭐⭐⭐

**Requirements:**
- Redis integration
- Multiple strategies
- Cache warming
- Monitoring & alerts
- Stampede prevention

---

## ⚖️ Redis vs Memcached

| Feature | Redis | Memcached |
|---------|-------|-----------|
| **Data Types** | Many (strings, lists, sets, hashes) | Strings only |
| **Persistence** | Yes (RDB, AOF) | No |
| **Replication** | Yes (master-slave) | No |
| **Atomic Ops** | Yes (INCR, DECR, etc.) | Basic |
| **Pub/Sub** | Yes | No |
| **Lua Scripts** | Yes | No |
| **Multi-threading** | Single-threaded | Multi-threaded |
| **Memory** | <1GB-256GB | <1GB-100GB |
| **Speed** | Fast | Slightly faster |
| **Complexity** | Medium | Low |
| **Use Case** | Rich features needed | Simple caching |

---

## 🎯 When to Use Caching

```
✅ USE CACHE WHEN:
- Same data accessed frequently
- Database queries slow
- Read >> Writes
- Stale data acceptable (for TTL)
- Need high throughput

❌ DON'T CACHE WHEN:
- Data changes constantly
- Every request unique
- Cache misses expensive
- Strong consistency required
- Memory limited
```

---

## ❌ Common Mistakes

### Mistake 1: Caching Everything

```python
# ❌ Cache every database query
cache.set(f"query:{sql_hash}", result)

# Problem: Cache bloat
# Most queries are unique
# Wastes memory

# ✅ Cache only hot data
if access_count > 10:
    cache.set(key, result)
```

### Mistake 2: No TTL

```python
# ❌ No expiration
cache.set("user:123", user)  # Lives forever!

# Problem: Stale data forever
# Memory never freed

# ✅ Always set TTL
cache.set("user:123", user, ttl=300)
```

### Mistake 3: Ignoring Cache Stampede

```python
# ❌ No protection
# 1000 requests hit expired cache
# All query database simultaneously 💥

# ✅ Use locking
if not cache.get(key):
    with lock(key):
        if not cache.get(key):  # Double-check
            data = db.query()
            cache.set(key, data)
```

---

## 📚 Additional Resources

**Redis:**
- [Redis Documentation](https://redis.io/documentation)
- [Redis in Action](https://redislabs.com/redis-in-action/)
- [Redis University](https://university.redis.com/)

**Memcached:**
- [Memcached Wiki](https://github.com/memcached/memcached/wiki)
- [Memcached Tutorial](https://www.tutorialspoint.com/memcached/)

**Caching Patterns:**
- [Caching Best Practices](https://aws.amazon.com/caching/best-practices/)
- [Cache Strategies](https://codeahoy.com/2017/08/11/caching-strategies-and-how-to-choose-the-right-one/)

---

## 🎯 Before You Leave

**Can you answer these?**

1. **What's a cache hit vs cache miss?**
   - Answer: Hit = found in cache; Miss = not in cache, query DB

2. **What's TTL and why is it important?**
   - Answer: Time To Live; prevents stale data

3. **What's the cache-aside pattern?**
   - Answer: App checks cache, on miss queries DB and stores result

4. **What's the cache stampede problem?**
   - Answer: Many requests hit expired cache simultaneously, overwhelm DB

5. **Redis vs Memcached: main difference?**
   - Answer: Redis has rich features; Memcached is simpler

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **Developer 1:** "I cached everything. Now queries are instant!"
>
> **Developer 2:** "How's your cache hit rate?"
>
> **Developer 1:** "5%... why?"
>
> **Developer 2:** "You cached everything but serve nothing. That's not caching, that's hoarding." 🗄️

---

[← Back to Main](../README.md) | [Previous: ACID vs BASE](12-acid-vs-base.md) | [Next: CDN →](14-cdn.md)

---

**Last Updated:** November 10, 2025  
**Difficulty:** ⭐⭐ Beginner-Intermediate (practical caching)  
**Time to Read:** 24 minutes  
**Time to Build System:** 3-6 hours per phase  

---

*Caching: The art of remembering the right things and forgetting them at the right time.* 🚀