# 28. Distributed Caching

Caching is like remembering where you parked your car. Distributed caching is like having 100 friends also remember where you parked, but they might remember different locations. Now you drive to 3 different spots before finding your car. Cache invalidation is the second hardest problem in computer science (after naming things). 🚗💀

[← Back to Main](../README.md) | [Previous: Microservices vs Monoliths](27-microservices-monoliths.md) | [Next: Event-Driven Architecture →](29-event-driven-architecture.md)

---

## 🎯 Quick Summary

**Distributed Caching** shares cached data across multiple servers (Redis Cluster, Memcached). Single-server caching good for one machine, breaks with horizontal scaling. When 10 servers exist, each has local cache, 9 misses! Distributed cache shared by all, consistent view. Reduces database load by 10-100x. Trade-off: network latency, complexity, consistency challenges. Essential for systems handling millions of users.

Think of it as: **Distributed Cache = Shared Memory for All Servers**

---

## 🌟 Beginner Explanation

### Local vs Distributed Caching

**LOCAL CACHING (In-Memory):**

```
Server 1:
├─ In-memory cache
├─ Key: user:123 → Value: {name: "Alice"}
└─ Hit rate: 90% (fast!)

Server 2:
├─ In-memory cache (separate!)
├─ Key: user:123 → NOT THERE (different memory)
└─ Hit rate: 10% (miss!)

Server 3:
├─ In-memory cache (separate again!)
├─ Key: user:123 → NOT THERE
└─ Hit rate: 10% (miss!)

Problem:
❌ Cache not shared
❌ Most requests miss
❌ Database overloaded
❌ Doesn't scale
```

**DISTRIBUTED CACHING (Shared):**

```
Servers 1, 2, 3 (all access same cache):
│       │       │
└───┬───┴───┬───┘
    ↓       ↓
┌──────────────────┐
│ Redis Cluster    │
├──────────────────┤
│ user:123 → Alice │
│ user:456 → Bob   │
│ post:789 → Title │
└──────────────────┘

All servers:
├─ Check cache first (hit!)
├─ If miss: Query database
├─ Store in cache
└─ Next request: Hits cache!

Result:
✅ Consistent cache view
✅ High hit rate
✅ Database not overloaded
✅ Scales with more servers
```

### Single vs Distributed Problem

```
SCENARIO: 1 million requests/second

Request type:
├─ 80%: Get user profile (from cache)
├─ 15%: Get user orders (from cache)
└─ 5%: Complex query (miss cache, hit DB)

LOCAL CACHING (100 servers, each with local cache):

Server 1: user:123 = Alice (local)
Server 2: user:123 = NOT THERE (miss!)
Server 3: user:123 = NOT THERE (miss!)
...
Server 100: user:123 = NOT THERE (miss!)

Hit rate: ~1% (only on right server!)
Database hits: 1,000,000 × 0.99 = 990,000 req/sec
Database dies! ❌


DISTRIBUTED CACHING (Shared Redis):

All servers share:
user:123 = Alice

Result:
Server 1: user:123 = Alice (hit!)
Server 2: user:123 = Alice (hit!)
Server 3: user:123 = Alice (hit!)
...
Server 100: user:123 = Alice (hit!)

Hit rate: ~80% (all servers benefit!)
Database hits: 1,000,000 × 0.20 = 200,000 req/sec
Database happy! ✅
```

### Cache Architectures

```
TIER 1: Local Cache (In-Process)
└─ In-memory dictionary
└─ Speed: < 1ms
└─ Size: Limited (memory per process)
└─ Data: Not shared

TIER 2: Distributed Cache (Redis/Memcached)
└─ Shared in-memory store
└─ Speed: 1-10ms (network latency)
└─ Size: Large (100GB+ possible)
└─ Data: Shared across servers

TIER 3: Database
└─ Persistent storage
└─ Speed: 10-100ms (disk I/O)
└─ Size: Very large (terabytes)
└─ Data: Authoritative

COMMON PATTERN (L1, L2, L3):

Request:
  ↓
├─ Check Tier 1 (local, < 1ms) ← Almost never misses
├─ Check Tier 2 (distributed, 1-10ms) ← Warm data
└─ Check Tier 3 (database, 10-100ms) ← Cold data

Hit rate:
├─ Tier 1: ~60% (recent data)
├─ Tier 2: ~30% (warm data)
└─ Tier 3: ~10% (cold data, cache miss)
```

---

## 🔬 Advanced Explanation

### Redis Cluster Architecture

```
REDIS CLUSTER (Distributed):

┌─────────────────────────────────────┐
│ Client (connects to any node)      │
└────────────┬────────────────────────┘
             │
    ┌────────┼────────┐
    ↓        ↓        ↓
┌────────┐┌────────┐┌────────┐
│Node 1  ││Node 2  ││Node 3  │
│Shard A ││Shard B ││Shard C │
└────────┘└────────┘└────────┘
    ↑        ↑        ↑
    └────────┼────────┘
        Gossip Protocol
        (sync data)

How it works:

Key: user:123
Hash: hash("user:123") % 3 = 0
└─ Store on Node 1 (Shard A)

Key: user:456
Hash: hash("user:456") % 3 = 1
└─ Store on Node 2 (Shard B)

Key: user:789
Hash: hash("user:789") % 3 = 2
└─ Store on Node 3 (Shard C)

Benefits:
✅ Data distributed (no single node bottleneck)
✅ Scale by adding nodes
✅ Each node smaller dataset
✅ Parallel processing

Challenges:
❌ Hashing: Where is data?
❌ Node failure: Rebalancing needed
❌ Consistency: Gossip protocol delays
```

### Cache Patterns

**CACHE-ASIDE (Lazy Loading):**

```
Request for data:
  ↓
1. Check cache
  ├─ Hit: Return (fast!)
  └─ Miss: Go to 2
2. Query database
  ├─ Get data
  └─ Store in cache
3. Return to client

Code:
def get_user(user_id):
    cache_key = f"user:{user_id}"
    
    # Check cache
    user = cache.get(cache_key)
    if user:
        return user  # Cache hit!
    
    # Cache miss: Hit database
    user = db.query(f"SELECT * FROM users WHERE id={user_id}")
    
    # Store in cache for future
    cache.set(cache_key, user, ttl=3600)
    
    return user

Pros:
✅ Simple to implement
✅ Only cache used data
✅ Easy to add to existing code

Cons:
❌ First request slow (cache miss)
❌ Stale data until TTL expires
❌ DB still hit on every miss
```

**WRITE-THROUGH (Sync Update):**

```
Write operation:
  ↓
1. Update database
2. Update cache
3. Return to client

Code:
def update_user(user_id, data):
    # Update database FIRST
    db.update(user_id, data)
    
    # Update cache
    cache_key = f"user:{user_id}"
    cache.set(cache_key, data)
    
    return {"status": "updated"}

Pros:
✅ Cache always consistent with DB
✅ No stale data
✅ Safe (DB is source of truth)

Cons:
❌ Slow (must update both)
❌ Extra write latency
❌ Double database load (write + cache update)
```

**WRITE-BEHIND (Async Update):**

```
Write operation:
  ↓
1. Update cache (fast!)
2. Queue update to database (async)
3. Return to client

Code:
def update_user(user_id, data):
    cache_key = f"user:{user_id}"
    
    # Update cache immediately
    cache.set(cache_key, data)
    
    # Queue DB update for later
    queue.push({
        'operation': 'update_user',
        'user_id': user_id,
        'data': data
    })
    
    return {"status": "updated"}

# Background worker processes queue
def worker():
    while True:
        update_job = queue.pop()
        db.update(update_job['user_id'], update_job['data'])

Pros:
✅ Fast (return immediately)
✅ Low latency
✅ Can batch updates

Cons:
❌ Temporary inconsistency (cache ahead of DB)
❌ If crash: Data lost
❌ Complex (need queue, worker)
```

### Cache Invalidation Strategies

**TTL (Time-To-Live):**

```
Set expiry time:
cache.set("user:123", alice_data, ttl=3600)  # 1 hour

After 1 hour: Key auto-deleted
Next request: Cache miss, hit DB

Simple but:
❌ Data stale for up to 1 hour
❌ After update: Old data served until TTL
❌ No immediate consistency
```

**EXPLICIT INVALIDATION:**

```
When data changes:
def update_user(user_id, data):
    # Update DB
    db.update(user_id, data)
    
    # Invalidate cache
    cache.delete(f"user:{user_id}")
    
    return updated

Next request:
  ├─ Cache miss (invalidated)
  └─ Fetch fresh from DB

Pros:
✅ Immediate consistency
✅ No stale data

Cons:
❌ More cache misses
❌ Coordination needed
❌ Complex in distributed systems
```

**CACHE VERSIONING:**

```
Instead of deleting: Change key version

Data: user:123 → Alice
Version 1: cache key = "user:123:v1"

After update:
Version 2: cache key = "user:123:v2"

Code:
def get_user(user_id):
    version = db.get_user_version(user_id)
    cache_key = f"user:{user_id}:v{version}"
    
    user = cache.get(cache_key)
    if not user:
        user = db.query(user_id)
        cache.set(cache_key, user, ttl=86400)  # 1 day
    
    return user

Benefits:
✅ No deletion needed
✅ Old versions auto-expire (TTL)
✅ No thundering herd
```

### Distributed Cache Challenges

**THUNDERING HERD:**

```
Cache key expires at exact moment:

T=0: 1000 servers all check cache
T=0.001: All cache misses (expired!)
T=0.002: All 1000 hit database simultaneously
T=0.003: Database overloaded, crashes!

Solution: Stagger expiry times
cache.set(key, value, ttl=3600 + random(0, 300))
└─ TTL: 60-65 minutes (random)
└─ Expirations spread out
└─ No thundering herd
```

**CACHE STAMPEDE:**

```
Cache miss on popular key:

Cache miss for "product:bestseller"
  ├─ Query hits database
  ├─ Slow query (10 seconds)
  └─ During those 10 seconds...

Meanwhile: 100 more requests for same key
  ├─ All cache misses
  ├─ All hit database
  ├─ Database doing same query 100 times!
  └─ Database overloaded

Solution: Lock pattern
if not cache.get(key):
    if cache.lock(key):  # Acquire lock
        value = expensive_query()
        cache.set(key, value)
        cache.unlock(key)
    else:  # Someone else has lock
        wait_for_lock()  # Wait for their result
        return cache.get(key)  # Use their cached value
```

**CACHE ASIDE WITH DELETION:**

```
PROBLEM: Cache-aside + deletion = stale reads

1. Read user:123 from cache ✗ MISS
2. Query database
3. Another server: DELETE user:123 (user updated)
4. Store old data in cache
5. Result: Stale data in cache!

SOLUTION: Check DB timestamp
cache.set(key, value, metadata={
    'timestamp': db.get_timestamp(),
    'version': db.get_version()
})

On read:
db_version = db.get_version(key)
cached_version = cache.get_version(key)
if db_version != cached_version:
    # Stale, refresh
    value = db.query(key)
    cache.set(key, value)
```

---

## 🐍 Python Code Example

### ❌ Without Distributed Cache (Slow)

```python
# ===== WITHOUT DISTRIBUTED CACHE =====

from flask import Flask
import psycopg2

app = Flask(__name__)
db_conn = psycopg2.connect("dbname=mydb")

@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    """Every request hits database"""
    
    cursor = db_conn.cursor()
    
    # Query database
    cursor.execute(f'SELECT * FROM users WHERE id = {user_id}')
    user = cursor.fetchone()
    
    return {'user': user}

# Problem:
# ❌ 1 million requests/second
# ❌ All hit database
# ❌ Database can't handle
# ❌ Users see timeouts
```

### ✅ Local Cache (Helps One Server)

```python
# ===== LOCAL CACHE (NOT DISTRIBUTED) =====

from flask import Flask
import psycopg2
from functools import lru_cache

app = Flask(__name__)
db_conn = psycopg2.connect("dbname=mydb")

local_cache = {}  # In-process cache

@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    """Local cache in each server"""
    
    # Check local cache
    if user_id in local_cache:
        print(f"Local cache hit for user {user_id}")
        return {'user': local_cache[user_id], 'source': 'local_cache'}
    
    # Cache miss
    cursor = db_conn.cursor()
    cursor.execute(f'SELECT * FROM users WHERE id = {user_id}')
    user = cursor.fetchone()
    
    # Store in local cache
    local_cache[user_id] = user
    
    return {'user': user, 'source': 'database'}

# Problem:
# ❌ Server 1 cache: {user:123: Alice}
# ❌ Server 2 cache: empty!
# ❌ If request goes to Server 2: Cache miss
# ❌ Only ~20% hit rate with 5 servers
```

### ✅ Distributed Cache (Shared Across Servers)

```python
# ===== DISTRIBUTED CACHE (REDIS) =====

from flask import Flask
import psycopg2
import redis
import json
import time

app = Flask(__name__)
db_conn = psycopg2.connect("dbname=mydb")

# Connect to Redis (shared)
cache = redis.Redis(host='redis-cluster', port=6379, decode_responses=True)

@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    """Distributed cache shared by all servers"""
    
    cache_key = f"user:{user_id}"
    
    # Check distributed cache
    cached = cache.get(cache_key)
    if cached:
        print(f"Cache hit for user {user_id}")
        return {'user': json.loads(cached), 'source': 'cache'}
    
    # Cache miss: Hit database
    print(f"Cache miss for user {user_id}, querying DB")
    cursor = db_conn.cursor()
    cursor.execute(f'SELECT * FROM users WHERE id = {user_id}')
    user = cursor.fetchone()
    
    # Store in distributed cache (1 hour TTL)
    cache.setex(cache_key, 3600, json.dumps(user))
    
    return {'user': user, 'source': 'database'}

# Benefits:
# ✅ ALL servers share same cache
# ✅ Server 1 cache hit: Server 2 benefits
# ✅ ~80% hit rate with 5 servers
# ✅ Database load drops 5x
```

### ✅ Production Distributed Cache (Advanced)

```python
# ===== PRODUCTION DISTRIBUTED CACHE =====

from flask import Flask
import redis
from redis.cluster import RedisCluster
import json
import hashlib
import time

app = Flask(__name__)

# Redis Cluster (multiple nodes)
cache_cluster = RedisCluster.from_url('redis://redis-cluster:6379')

class DistributedCacheManager:
    """Production-grade distributed cache"""
    
    def __init__(self, cache, db_conn):
        self.cache = cache
        self.db = db_conn
        self.local_cache = {}  # L1 cache
    
    def get_user(self, user_id):
        """Get user with multi-level caching"""
        
        cache_key = f"user:{user_id}"
        version_key = f"user:{user_id}:version"
        
        # L1: Local cache
        if user_id in self.local_cache:
            cached_user, timestamp = self.local_cache[user_id]
            if time.time() - timestamp < 60:  # Valid for 1 minute
                return cached_user, "L1_LOCAL_CACHE"
        
        # L2: Distributed cache
        cached = self.cache.get(cache_key)
        if cached:
            user = json.loads(cached)
            # Store in L1 for next request
            self.local_cache[user_id] = (user, time.time())
            return user, "L2_DISTRIBUTED_CACHE"
        
        # L3: Database
        cursor = self.db.cursor()
        cursor.execute(f'SELECT * FROM users WHERE id = {user_id}')
        user = cursor.fetchone()
        
        # Store in L2 (distributed)
        self.cache.setex(cache_key, 3600, json.dumps(user))
        
        # Store in L1 (local)
        self.local_cache[user_id] = (user, time.time())
        
        return user, "L3_DATABASE"
    
    def update_user(self, user_id, data):
        """Update user with cache invalidation"""
        
        cache_key = f"user:{user_id}"
        
        # Update database (source of truth)
        cursor = self.db.cursor()
        cursor.execute(f'UPDATE users SET data=%s WHERE id=%s', (json.dumps(data), user_id))
        self.db.commit()
        
        # Invalidate L2 cache (distributed)
        self.cache.delete(cache_key)
        
        # Invalidate L1 cache (local)
        if user_id in self.local_cache:
            del self.local_cache[user_id]
        
        return {"status": "updated"}
    
    def batch_get_users(self, user_ids):
        """Batch get (reduce latency)"""
        
        cache_keys = [f"user:{uid}" for uid in user_ids]
        
        # Batch get from cache
        cached_values = self.cache.mget(cache_keys)
        
        results = {}
        missing_ids = []
        
        for i, user_id in enumerate(user_ids):
            if cached_values[i]:
                results[user_id] = json.loads(cached_values[i])
            else:
                missing_ids.append(user_id)
        
        # Batch query for missing
        if missing_ids:
            cursor = self.db.cursor()
            placeholders = ','.join(['%s'] * len(missing_ids))
            cursor.execute(f'SELECT * FROM users WHERE id IN ({placeholders})', 
                         missing_ids)
            for user in cursor.fetchall():
                results[user['id']] = user
                # Cache it
                self.cache.set(f"user:{user['id']}", json.dumps(user), 3600)
        
        return results

# Usage
cache_mgr = DistributedCacheManager(cache_cluster, db_conn)

@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    user, source = cache_mgr.get_user(user_id)
    return {'user': user, 'source': source}

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    return cache_mgr.update_user(user_id, request.json)
```

---

## 💡 Mini Project: "Build Distributed Cache System"

### Phase 1: Redis Setup ⭐

**Requirements:**
- Single Redis instance
- Basic cache-aside pattern
- TTL management
- Hit/miss tracking

---

### Phase 2: Cluster & Replication ⭐⭐

**Requirements:**
- Redis cluster (multiple nodes)
- Replication for failover
- Consistent hashing
- Failover handling

---

### Phase 3: Advanced (Multi-Tier) ⭐⭐⭐

**Requirements:**
- L1 local cache
- L2 distributed cache
- L3 database
- Cache warming
- Stale-while-revalidate

---

## ⚖️ Cache Comparison

| Aspect | Local Cache | Distributed Cache |
|--------|------------|------------------|
| **Latency** | < 1ms | 1-10ms |
| **Scope** | Per server | Across servers |
| **Size** | Limited (memory) | Large (100GB+) |
| **Consistency** | Server-local | Global |
| **Scaling** | Doesn't scale | Scales well |
| **Failure** | One server | Replicated |

---

## ❌ Common Mistakes

### Mistake 1: Cache Everything

```python
# ❌ Cache all database queries
cache.set(query, result, 3600)

# Problem: Cold cache (useless first hour)
# Also: Memory explosion (cache fills with rarely-used data)

# ✅ Cache strategically
# Cache: User profiles, posts (frequently accessed)
# Don't cache: Admin queries, reports (rarely accessed)
```

### Mistake 2: No Cache Invalidation

```python
# ❌ Set cache, never delete
cache.set("user:123", alice_data)
# User updates profile (but cache not updated!)
# Old data served forever

# ✅ Invalidate on update
def update_user(user_id, data):
    db.update(user_id, data)
    cache.delete(f"user:{user_id}")  # Invalidate!
```

### Mistake 3: Single Cache Node

```python
# ❌ One Redis server
redis_server = Redis(host='single-server')
# If server dies: No cache! (cascading failures)

# ✅ Redis cluster with replication
redis_cluster = RedisCluster(nodes=[...])
# If one node dies: Others survive
```

---

## 📚 Additional Resources

**Redis:**
- [Redis Documentation](https://redis.io/docs/)
- [Redis Cluster](https://redis.io/docs/management/scaling/)
- [Redis Patterns](http://redis-raftv.github.io/Patterns/)

**Memcached:**
- [Memcached Documentation](https://memcached.org/)
- [Memcached Consistent Hashing](https://www.last.fm/user/RJ/journal/2007/04/10/rj_and_memcached_breaking_a_little)

**Caching Strategies:**
- [Cache Invalidation](https://en.wikipedia.org/wiki/Cache_invalidation)
- [Cache Patterns](https://docs.microsoft.com/en-us/azure/architecture/patterns/cache-aside)

---

## 🎯 Before You Leave

**Can you answer these?**

1. **Why not just use local cache on each server?**
   - Answer: Inconsistent view, high miss rate, database overloaded

2. **What's cache-aside pattern?**
   - Answer: Check cache, if miss hit DB and populate cache

3. **What's the main challenge in distributed caching?**
   - Answer: Cache invalidation (ensuring consistency)

4. **How does Redis Cluster scale?**
   - Answer: Partition data via hashing, multiple nodes handle partitions

5. **What's thundering herd problem?**
   - Answer: Multiple servers querying DB simultaneously when cache expires

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **Engineer:** "Let's add caching to reduce database load!"
>
> **After 1 month:** "Why are users seeing stale data?"
>
> **After 2 months:** "We now have cache invalidation bugs."
>
> **After 3 months:** "Sometimes we're faster, sometimes slower?"
>
> **Senior Engineer:** "Welcome to distributed caching, where the only certainty is that your cache will be wrong." 💀

---

[← Back to Main](../README.md) | [Previous: Microservices vs Monoliths](27-microservices-monoliths.md) | [Next: Event-Driven Architecture →](29-event-driven-architecture.md)

---

**Last Updated:** November 11, 2025  
**Difficulty:** ⭐⭐⭐ Intermediate-Advanced (consistency challenges)  
**Time to Read:** 27 minutes  
**Time to Implement:** 5-8 hours per phase  

---

*Distributed caching: Making your system faster and your problems more complex, simultaneously.* 🚀