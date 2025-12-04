# 14. Content Delivery Networks (CDNs)

 CDNs are how we deliver content so fast that users in Australia get data faster than the person sitting next to the server. Geography is just a suggestion. 🌍⚡

[← Back to Main](../README.md) | [Previous: Caching](13-caching.md) | [Next: Data Modeling →](15-data-modeling.md)

---

## 🎯 Quick Summary

**Content Delivery Networks (CDNs)** cache and distribute content geographically so users get data from servers near them. Instead of all users hitting your origin server (slow), they hit edge servers worldwide (fast). CDNs are essential for global scale: Cloudflare, AWS CloudFront, Akamai, Fastly. They reduce latency, bandwidth costs, and server load.

Think of it as: **CDN = Cache Servers Spread Globally**

---

## 🌟 Beginner Explanation

### Without CDN (Centralized)

```
Origin Server in USA

User in USA:
├─ Request travels 10ms to USA
├─ Processes
├─ Response travels 10ms back
└─ Total: ~100ms (fast) ✅

User in Australia:
├─ Request travels 150ms to USA 🐢
├─ Processes
├─ Response travels 150ms back
└─ Total: ~600ms (SLOW!) 😱

User in Europe:
├─ Request travels 90ms to USA
├─ Processes
├─ Response travels 90ms back
└─ Total: ~300ms (slow)

Problem: Everyone waits for USA server!
```

### With CDN (Distributed)

```
Origin Server (USA) + Edge Servers Worldwide

User in USA:
├─ Connects to USA edge server (closest)
├─ Gets content locally: 50ms ✅
└─ Fast!

User in Australia:
├─ Connects to Australia edge server (closest)
├─ Gets content locally: 50ms ✅
└─ Also fast! (was 600ms without CDN)

User in Europe:
├─ Connects to Europe edge server (closest)
├─ Gets content locally: 50ms ✅
└─ Also fast! (was 300ms without CDN)

Benefit:
- Everyone gets ~50ms response time
- Network geography doesn't matter
- Origin server rarely hit
```

### How CDN Works

```
First request from user in Australia:

1. User: "Get file.jpg"
2. Router: "You're in Australia, go to Sydney edge server"
3. Sydney edge server: "Don't have file.jpg, ask origin"
4. Sydney → Origin (150ms to USA)
5. Origin: Sends file.jpg
6. Sydney: Caches file locally
7. Sydney: Responds to user (50ms)
8. Total: ~200ms

Next request from ANY user in Australia:

1. User: "Get file.jpg"
2. Router: "Sydney edge has this!"
3. Sydney: Responds immediately ✅ (50ms)
4. Total: 50ms

Origin server only hit ONCE, not 1 million times!
```

---

## 🔬 Advanced Explanation

### CDN Architecture

**TRADITIONAL SERVER (Origin Only):**

```
┌─────────────────────────┐
│   Origin Server (USA)   │
│  - Stores everything    │
│  - Handles all requests │
│  - Overloaded!          │
└─────────────────────────┘
         ↑ ↑ ↑ ↑
    All users hit here
```

**CDN ARCHITECTURE (Distributed):**

```
┌──────────────┐
│ Origin (USA) │ ← Master copy (served when cache miss)
└──────────────┘
       ↑
       │ (replicate to edge when needed)
       │
    ┌──┴───┬────────┬────────┬────────┐
    │      │        │        │        │
┌───▼─┐ ┌──▼──┐ ┌──▼──┐ ┌───▼──┐ ┌──▼──┐
│ NY  │ │ LA  │ │ LON │ │ SYD  │ │ TOK │
│Edge │ │Edge │ │Edge │ │Edge  │ │Edge │
└─────┘ └─────┘ └─────┘ └──────┘ └─────┘

Each edge server:
├─ Caches popular content
├─ Serves nearby users
├─ If cache miss: Fetches from origin
└─ If cache hit: Serves instantly
```

### CDN Types

**PUSH CDN:**

```
You control what gets cached

Push to CDN:
├─ Upload file1.jpg to CDN
├─ Upload file2.jpg to CDN
├─ CDN propagates to all edges

Pros:
✅ Control exactly what's cached
✅ Guaranteed to have content
✅ Good for large files

Cons:
❌ Manual work
❌ Wastes bandwidth (cache rarely used files)
❌ Scaling issues (how many files?)
```

**PULL CDN:**

```
CDN automatically caches when requested

First request for file.jpg:
├─ User: Gets from origin (slow)
├─ CDN: "This is popular, cache it"
├─ CDN: Caches at all edges

Next requests:
├─ Users: Get from edge (fast)

Pros:
✅ Automatic (no manual work)
✅ Only cache popular content
✅ Scales automatically

Cons:
❌ First request slow (cache miss)
❌ Can't guarantee content
```

### CDN Routing

**ANYCAST ROUTING:**

```
All edge servers have SAME IP address

User in Australia:
├─ DNS resolves example.com
├─ Gets "1.2.3.4" (anycast IP)
├─ Network routes to NEAREST edge server
├─ (Sydney edge also has 1.2.3.4)
└─ Request reaches Sydney server ✅

User in USA:
├─ DNS resolves example.com
├─ Gets "1.2.3.4" (same IP!)
├─ Network routes to NEAREST edge server
├─ (USA edge has 1.2.3.4)
└─ Request reaches USA server ✅

Magic: Same IP, different servers!
```

**GEO-ROUTING (Via DNS):**

```
DNS returns different IPs based on location

User in Australia:
├─ DNS query: "Where's example.com?"
├─ DNS sees: Requesting from Australia
├─ DNS returns: Sydney edge IP (1.2.3.4)
├─ User hits Sydney edge ✅

User in USA:
├─ DNS query: "Where's example.com?"
├─ DNS sees: Requesting from USA
├─ DNS returns: USA edge IP (5.6.7.8)
├─ User hits USA edge ✅

DNS routing based on geography
```

### Cache Invalidation

**PROBLEM: Old content cached**

```
file.jpg v1 cached everywhere
You upload file.jpg v2
Users still see v1 (old)

How to fix?
```

**SOLUTION 1: TTL (Time To Live)**

```
Cache-Control: max-age=3600  ← Expires in 1 hour

After 1 hour:
├─ Edge cache expires
├─ Next request: Fetch new version
├─ All users get v2

But: Old version served for 1 hour
```

**SOLUTION 2: Purge/Flush**

```
Admin: "Flush cache for file.jpg"

CDN:
├─ Deletes file.jpg from all edges
├─ Next request: Fetches from origin
├─ All users get v2

But: Purge takes time (seconds to propagate)
```

**SOLUTION 3: Cache Busting (Filename)**

```
Version 1: file.jpg
Version 2: file-v2.jpg

Both exist in cache:
├─ file.jpg → v1
├─ file-v2.jpg → v2

No purge needed! Just point to new filename

Pros: Instant
Cons: Old files accumulate

Used by: Web apps, build systems
```

**SOLUTION 4: Versioning Headers**

```
Response header:
ETag: "abc123"  ← Version identifier

Browser: "Do you have abc123?"
CDN: "Yes, here's latest"

Version changes:
ETag: "abc124"  ← Different!

Browser: "Do you have abc124?"
CDN: "No, fetch from origin"

Efficient: Only fetch if changed
```

### CDN Performance

**EDGE CACHING:**

```
Popular assets cached at edges

Video file (500MB):
├─ Without CDN: Origin serves every time
├─ Bandwidth: 1M users × 500MB = 500TB! 💥
├─ Cost: HUGE 💸
├─ Latency: Variable (network dependent)

With CDN:
├─ First user hits origin (500MB once)
├─ Cached at edge
├─ Next 999K users: All hit edge (instant)
├─ Bandwidth: ~500MB + 1M × (a few KB) = 501MB
├─ Cost: 1000x cheaper! 💰
├─ Latency: Consistent (same edge)
```

**COMPRESSION:**

```
CDN compresses content on the fly

HTML file: 100KB
Gzip compression: 20KB (80% reduction!)

Browser: Accepts gzip
CDN: Compresses and sends 20KB
Browser: Decompresses to 100KB

User gets: 5x faster download!
```

### Performance Metrics

```
TTFB (Time To First Byte):
├─ Time until first response byte arrives
├─ Without CDN: 100-300ms (network + origin)
├─ With CDN: 10-50ms (edge server)
└─ Improvement: 5-10x faster

DCP (Dominant Content Paint):
├─ When user sees most content
├─ Huge improvement with CDN
└─ Impacts user satisfaction heavily

TTL (Time To Live):
├─ How long content cached
├─ Too short: Frequent cache misses
├─ Too long: Old content served
└─ Balance needed
```

---

## 🐍 Python Code Example

### ❌ Without CDN (All from Origin)

```python
# ===== WITHOUT CDN (SLOW) =====

import time

class OriginServer:
    """Single origin server"""
    
    def __init__(self):
        self.files = {
            "index.html": "HTML content",
            "style.css": "CSS content",
            "script.js": "JavaScript content",
            "image.jpg": "Image binary data"
        }
        self.request_count = 0
    
    def get_file(self, filename, user_location):
        """Serve file (always from origin)"""
        self.request_count += 1
        
        # Simulate network latency based on location
        latencies = {
            "USA": 10,
            "Australia": 150,
            "Europe": 100,
            "Asia": 120
        }
        
        latency = latencies.get(user_location, 50)
        time.sleep(latency / 1000)  # Simulate network delay
        
        return self.files.get(filename)

# Usage
print("=== WITHOUT CDN ===\n")

origin = OriginServer()

# Simulate 100 requests from different locations
locations = ["USA", "Australia", "Europe", "Asia"] * 25  # 100 total

start = time.time()
for i, location in enumerate(locations):
    file_data = origin.get_file("image.jpg", location)
    if (i + 1) % 25 == 0:
        elapsed = time.time() - start
        print(f"{i+1} requests: {elapsed:.2f}s")

total_time = time.time() - start
print(f"\nTotal: {total_time:.2f}s")
print(f"Avg latency: {total_time/100*1000:.0f}ms")
print(f"Origin received: {origin.request_count} requests 😰")

# Output:
# 100 requests: ~10-15 seconds
# Every request hits origin!
```

### ✅ With CDN (Cached at Edges)

```python
# ===== WITH CDN (FAST) =====

import time
from collections import defaultdict

class EdgeServer:
    """Edge server (cache)"""
    
    def __init__(self, location, latency_to_origin=150):
        self.location = location
        self.cache = {}  # filename → content
        self.latency_to_origin = latency_to_origin
        self.request_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get_file(self, filename, origin_server):
        """Get file (from cache if available)"""
        self.request_count += 1
        
        # Simulate local latency
        local_latency = 10
        
        # Check cache
        if filename in self.cache:
            # Cache hit!
            self.cache_hits += 1
            time.sleep(local_latency / 1000)
            return self.cache[filename]
        
        # Cache miss - fetch from origin
        self.cache_misses += 1
        time.sleep(self.latency_to_origin / 1000)  # Network to origin
        
        # Get from origin
        content = origin_server.get_file(filename, self.location)
        
        # Cache it
        self.cache[filename] = content
        
        # Return (already waited for network)
        return content
    
    def get_stats(self):
        return {
            "location": self.location,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": self.cache_hits / self.request_count * 100 if self.request_count > 0 else 0
        }

class CDN:
    """Content Delivery Network"""
    
    def __init__(self, origin_server):
        self.origin = origin_server
        self.edges = {
            "USA": EdgeServer("USA", latency_to_origin=10),
            "Australia": EdgeServer("Australia", latency_to_origin=150),
            "Europe": EdgeServer("Europe", latency_to_origin=100),
            "Asia": EdgeServer("Asia", latency_to_origin=120)
        }
    
    def get_file(self, filename, user_location):
        """Get file from nearest edge"""
        edge = self.edges.get(user_location, self.edges["USA"])
        return edge.get_file(filename, self.origin)
    
    def get_stats(self):
        return {edge.location: edge.get_stats() for edge in self.edges.values()}

# Usage
print("=== WITH CDN ===\n")

origin = OriginServer()
cdn = CDN(origin)

# Simulate 100 requests
locations = ["USA", "Australia", "Europe", "Asia"] * 25

start = time.time()
for i, location in enumerate(locations):
    file_data = cdn.get_file("image.jpg", location)
    if (i + 1) % 25 == 0:
        elapsed = time.time() - start
        print(f"{i+1} requests: {elapsed:.2f}s")

total_time = time.time() - start
print(f"\nTotal: {total_time:.2f}s")
print(f"Avg latency: {total_time/100*1000:.0f}ms")

# Stats
print("\n=== CDN Statistics ===")
stats = cdn.get_stats()
for location, data in stats.items():
    print(f"{location}: {data['cache_hits']} hits, {data['cache_misses']} misses, "
          f"hit rate: {data['hit_rate']:.0f}%")

# Output:
# With CDN: ~2-3 seconds total
# Most requests served from cache!
# Huge speedup vs origin-only
```

### ✅ Production CDN Integration

```python
# ===== PRODUCTION CDN =====

class ProductionCDN:
    """Production-grade CDN with real providers"""
    
    def __init__(self):
        self.providers = {
            "cloudflare": "https://cloudflare.com/cdn",
            "cloudfront": "https://cloudfront.amazonaws.com",
            "akamai": "https://akamai.com",
            "fastly": "https://fastly.com"
        }
    
    def push_content(self, content, path, ttl=3600):
        """Push content to CDN"""
        # In real usage: Call CDN API
        # cdn.api.push(content, path, ttl)
        
        return {
            "path": path,
            "ttl": ttl,
            "status": "pushed",
            "url": f"https://cdn.example.com{path}"
        }
    
    def purge_cache(self, path):
        """Purge specific path from all edges"""
        # In real usage: Call CDN API
        # cdn.api.purge(path)
        
        return {
            "path": path,
            "status": "purged",
            "message": "Cache cleared from all edge servers"
        }
    
    def get_stats(self, path=None):
        """Get CDN statistics"""
        return {
            "cache_hit_ratio": 0.92,
            "avg_latency": 45,
            "bandwidth_saved": "65%",
            "requests": 10_000_000
        }

# Usage in application
cdn = ProductionCDN()

# Push initial content
result = cdn.push_content(
    content="<html>...</html>",
    path="/index.html",
    ttl=3600
)
print(f"Pushed: {result['url']}")

# After update, purge cache
cdn.purge_cache("/index.html")

# Check stats
stats = cdn.get_stats()
print(f"Cache hit ratio: {stats['cache_hit_ratio']*100:.0f}%")
```

---

## 💡 Mini Project: "Build a Mini CDN"

### Phase 1: Simple Edge Cache ⭐

**Requirements:**
- Single origin server
- 3-4 edge servers
- Cache hits/misses tracking
- Request routing

---

### Phase 2: Distributed (Multiple Edges) ⭐⭐

**Requirements:**
- Multiple geographic regions
- Cache invalidation
- Statistics tracking
- TTL management

---

### Phase 3: Enterprise (Full CDN) ⭐⭐⭐

**Requirements:**
- Real provider integration
- Performance monitoring
- DDoS protection
- Analytics dashboard

---

## ⚖️ CDN Services Comparison

| Feature | Cloudflare | AWS CloudFront | Akamai | Fastly |
|---------|-----------|----------------|--------|--------|
| **Speed** | Ultra-fast | Very fast | Enterprise | Ultra-fast |
| **Global Coverage** | 250+ cities | 600+ edges | Extensive | Many regions |
| **Ease of Use** | Very easy | Medium | Complex | Easy |
| **Cost** | Cheap | Medium | Expensive | Medium |
| **DDoS Protection** | Built-in | Optional | Yes | Basic |
| **Best For** | SMB/Startups | AWS users | Large Enterprise | High Performance |
| **Support** | Good | Good | Enterprise | Good |

---

## 🎯 When to Use CDN

```
✅ USE CDN WHEN:
- Content served globally
- Media files (images, videos)
- Static assets (CSS, JS)
- Download speed critical
- Geographic diversity needed
- Bandwidth costs high

❌ LESS BENEFIT WHEN:
- All users in one region
- Dynamic content only
- Personalized per-user
- Real-time data needed
- Private/authenticated content
```

---

## ❌ Common Mistakes

### Mistake 1: Only Caching Popular Content

```python
# ❌ Cache only top 10% of content
# Everything else goes to origin

# ✅ Cache liberally
# Cache everything, let CDN purge rarely used
# Better to cache then evict
```

### Mistake 2: Wrong TTL

```python
# ❌ TTL too short (1 minute)
# Cache misses constantly
# No performance benefit

# ❌ TTL too long (1 year)
# Stale content forever
# Users see old data

# ✅ Balance based on content
# Static assets: 1 year + cache busting
# Dynamic: 1 hour
# User profile: 1 minute
```

### Mistake 3: Not Purging Old Content

```python
# ❌ Deploy v2, old v1 still cached
# Users see mix of old/new (broken!)

# ✅ Always purge on deploy
# Or use cache busting (new filenames)
```

---

## 📚 Additional Resources

**CDN Providers:**
- [Cloudflare](https://www.cloudflare.com/)
- [AWS CloudFront](https://aws.amazon.com/cloudfront/)
- [Akamai](https://www.akamai.com/)
- [Fastly](https://www.fastly.com/)

**Learning:**
- [CDN Basics - Medium](https://medium.com/cdnjs/what-is-a-cdn-and-how-does-it-work-2e8e6e7b4f4)
- [CDN vs Cache - Cloudflare Blog](https://www.cloudflare.com/learning/cdn/what-is-a-cdn/)

---

## 🎯 Before You Leave

**Can you answer these?**

1. **What's the main advantage of using a CDN?**
   - Answer: Serve content from servers near users (lower latency)

2. **What's the difference between PUSH and PULL CDN?**
   - Answer: Push = you upload; Pull = auto-cache on access

3. **What's anycast routing?**
   - Answer: Same IP routes to nearest server

4. **Why is cache invalidation hard?**
   - Answer: Need to purge from all edge servers

5. **What's cache busting?**
   - Answer: Changing filenames to force fresh fetch

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **User in Australia:** "Why is Netflix so fast here?"
>
> **Netflix:** "We have a server in Sydney."
>
> **User in USA:** "Why is Netflix so fast here too?"
>
> **Netflix:** "We have a server in LA."
>
> **User in Europe:** "Why is Netflix so fast here?"
>
> **Netflix:** "We have servers... everywhere. We're watching you." 👁️

---

[← Back to Main](../README.md) | [Previous: Caching](13-caching.md) | [Next: Data Modeling →](15-data-modeling.md)

---

**Last Updated:** November 10, 2025  
**Difficulty:** ⭐⭐ Beginner-Intermediate (geographic concepts)  
**Time to Read:** 24 minutes  
**Time to Build Mini CDN:** 3-5 hours per phase  

---

*CDN: How to be in 200+ places at once without actually being there.* 🚀