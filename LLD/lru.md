# LRU

Let’s break down a classic backend interview scenario: **Implementing an LRU (Least Recently Used) Cache**, focusing on real-world requirements (high performance, correct eviction, suitability for web API or database result caching).

We’ll use actual data structures—no drama, no boredom!

***

## 1. **Bad Example: Cache With List-Based Eviction**

Suppose you need a fast in-memory cache, but you naively use a list for ordering:

```python
class BadLRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.entries = {}    # key -> value
        self.order = []      # order of keys (oldest to newest)

    def get(self, key):
        if key in self.entries:
            self.order.remove(key)
            self.order.append(key)
            return self.entries[key]
        return None

    def put(self, key, value):
        if key in self.entries:
            self.order.remove(key)
        elif len(self.entries) == self.capacity:
            oldest = self.order.pop(0)
            del self.entries[oldest]
        self.entries[key] = value
        self.order.append(key)
```

**Problems:**

- **Inefficient (`list.remove` \& `pop(0)` are O(N)):** For large caches, performance tanks.
- **Not thread-safe:** Race conditions galore.
- **Misses edge cases:** Duplicate keys, not robust in production.

**Humour Break:**
> “Your cache’s eviction strategy is as slow as customer support on a holiday weekend.”

***

## 2. **Good Example: LRU With OrderedDict (Production-Style Pythonic)**

**The optimal pattern uses a doubly-linked list or `OrderedDict`—O(1) put/get/evict operations.**

### Python Implementation

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()   # key-value pairs, oldest first

    def get(self, key):
        if key not in self.cache:
            print(f"[LRU] Miss for key: {key}")
            return None
        # Move key to end (most recently used)
        self.cache.move_to_end(key)
        print(f"[LRU] Hit for key: {key}")
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            # Update value, move to end
            self.cache.move_to_end(key)
            self.cache[key] = value
            print(f"[LRU] Updated key: {key}")
        else:
            if len(self.cache) >= self.capacity:
                oldest = next(iter(self.cache))
                del self.cache[oldest]
                print(f"[LRU] Evicted key: {oldest}")
            self.cache[key] = value
            print(f"[LRU] Inserted key: {key}")

    def __repr__(self):
        # For debugging, show order from least to most recently used
        return f"LRUCache({list(self.cache.items())})"

# --- Usage Example: Typical Interview Questions ---
cache = LRUCache(3)
cache.put('A', 10)
cache.put('B', 20)
cache.put('C', 30)

print(cache.get('A'))  # Hit: A
cache.put('D', 40)     # Evicts B
print(cache.get('B'))  # Miss
print(cache)           # ['C', 'A', 'D']
```


### **Why Is This Better?**

- **O(1) Operations:** Put/get/evict happen in constant time.
- **Robust for production:** Can easily add TTL, thread safety, or statistics.
- **Debuggable and extensible:** Add logging, cache metrics, expiration as needed.

**Humour Break:**
> “The only thing your LRU cache doesn’t evict is your boss’s Friday deploy schedule.”

***

## 3. **Real-World Backend Applications**

- **Web API response caches:** Speed up repeated requests.
- **DB query result caches:** Avoid slow, redundant queries.
- **Image/asset caching:** For CDN, backend media platforms.
- **Microservices:** Cross-service data caching (user/session objects, configs).

**Popular frameworks:**

- Redis LRU eviction policy
- Python functools.lru_cache
- Django/Flask/Celery built-in cache backends

***

## 4. **Scaling Beyond the Simple LRU**

- Add **TTL (time-to-live)** for cache expiry.
- Integrate with **Observer/Stats** for monitoring hits/misses and performance.
- Build distributed versions using consistent hashing/partitioning.
- Thread-safe and async wrappers for production systems.

***

## **Summary**

- **Bad Example:** List-based cache—slow, error-prone, not scalable.
- **Good Example:** OrderedDict/doubly-linked list—blazing fast, robust, production-ready.
- **Real-World Use:** Backend, database, asset, microservices cache.


