# 22. Rate Limiting & Throttling

Rate limiting is your bouncer saying "Sorry, we're at capacity." Throttling is saying "Slow down, you're going too fast." Together they're your system's way of saying "Please stop breaking me." Developers ignore both and then wonder why their API melts. 🚫

[← Back to Main](../README.md) | [Previous: Distributed Logging](21-distributed-logging.md) | [Next: API Gateways →](23-api-gateways.md)

---

## 🎯 Quick Summary

**Rate Limiting & Throttling** protect systems from overload: rate limiting blocks requests exceeding a threshold, throttling delays them. Essential for APIs: prevent abuse, ensure fair resource sharing, maintain performance under load. Strategies: token bucket, sliding window, leaky bucket. Implemented at: API gateway, application, database levels. Without them: single malicious user can take down entire service. With them: graceful degradation under load.

Think of it as: **Rate Limiting = No Entry, Throttling = Slow Down**

---

## 🌟 Beginner Explanation

### The Concert Analogy

**WITHOUT RATE LIMITING:**

```
Concert venue (1000 capacity)

No door policy:
├─ 5000 people try to enter
├─ Everyone crowds the door
├─ Stampede! 💥
├─ 50 people injured
├─ Event cancelled
└─ Everyone angry

Without limits: System overwhelmed, everyone suffers!
```

**WITH RATE LIMITING:**

```
Concert venue with bouncer:

Bouncer says:
├─ "Sorry, we're full!"
├─ Only 1000 people allowed
├─ Excess wait outside
├─ No stampede
├─ Everyone inside enjoys concert
└─ Queue outside moves as people leave

With limits: System healthy, fair experience!
```

### Rate Limiting vs Throttling

**RATE LIMITING (Reject/Block):**

```
API: "Max 1000 requests per hour"

Request 1-1000: OK ✅
Request 1001: "429 Too Many Requests" ❌
Request 1002: "429 Too Many Requests" ❌

Behavior: Hard rejection
Cost: Immediate feedback, no buffering
Used: Protect from abuse, ensure SLA
```

**THROTTLING (Slow Down/Queue):**

```
API: "Process at max 100 requests/second"

Requests 1-100: Process immediately
Requests 101-200: Queue (wait)
Requests 201-300: Queue (wait)

Behavior: Delay instead of reject
Cost: Buffering, increases latency
Used: Gradual degradation, fair sharing
```

### Who Gets Limited?

```
GLOBAL LIMIT:
├─ All users share 10,000 req/hour
├─ One user burns through fast
├─ Others starved
└─ Problem: Fair sharing

PER-USER LIMIT:
├─ Each user: 1000 req/hour
├─ Power user: 1000 req/hour
├─ Other users: 1000 req/hour each
└─ Solution: Fair sharing

TIERED LIMITS:
├─ Free tier: 100 req/hour
├─ Pro tier: 10,000 req/hour
├─ Enterprise: Unlimited
└─ Solution: Monetization!
```

---

## 🔬 Advanced Explanation

### Rate Limiting Algorithms

**TOKEN BUCKET (Most Popular):**

```
How it works:

┌─────────────────────┐
│  Token Bucket       │
│  Capacity: 100      │
│  Current: 85 tokens │
└─────────────────────┘

Refill rate: 10 tokens/second

Request arrives:
├─ Cost: 1 token
├─ If tokens available: Process request, remove token
├─ If no tokens: Reject/queue request

Timeline:
├─ T=0s: 85 tokens, request arrives
│        Process (84 tokens left)
├─ T=0.1s: 86 tokens (refilled)
├─ T=1s: 95 tokens (refilled 10)
├─ T=1.1s: 94 tokens (request processed)

Benefits:
✅ Handles bursts (capacity buffer)
✅ Smooth rate limiting
✅ Fair distribution
✅ Simple to implement

Cost: Requires background refill
```

# SLIDING WINDOW

Track requests in **the last 1 hour (past only)**

---

### **Initial State**

Window size: **1 hour**
Limit: **1000 requests/hour**

```
Current Time = 19:00
Window = 18:00 → 19:00 (last 1 hour)
Requests in this window = 850


┌──────────────────────────────────┐
│   18:00 ─────────────── 19:00     │
│   [#########.............]        │
│   Count = 850 requests            │
└──────────────────────────────────┘
```
Still under 1000 → all good.

---

# ⭐ **New Request at 18:50 (Correct Handling)**

At time **18:50**, window becomes:

```
Window = 17:50 → 18:50
```

We drop all requests older than 17:50.

Let’s say the user made:

* 700 requests before 17:50 → OUTSIDE window
* 150 requests between 17:50–18:50 → INSIDE window

So:

```
Request count in current window = 150
Limit = 1000 → OK
Allow request
```

✔ **Request at 18:50 = ALLOWED**

---

# ⭐ **New Request at 19:50 (Correct Handling)**

At time **19:50**, window becomes:

```
Window = 18:50 → 19:50
```

All requests before 18:50 drop out.

Let’s say:

* 250 requests happened between 18:50–19:50

So:

```
Request count = 250
Limit = 1000 → OK
Allow request
```

✔ **Request at 19:50 = ALLOWED**

---

Sliding Window ALWAYS checks:

```
Window = NOW − 1 hour → NOW
```

Never NOW → NOW + 1 hour
Never future timestamps
Never shifts forward

---

# ⚠️ **Issues with Sliding Window**

* Must store ALL request timestamps → high memory usage
* Boundary situations cause uneven limiting
* Does NOT protect against short bursts (spikes)


---


# LEAKY BUCKET

Imagine you have a **bucket with a small hole at the bottom**.

* Water = **incoming requests**
* Hole = **processing speed**
* Bucket size = **maximum buffer**

Water can pour in **fast**,
but it only leaks out **at a fixed, constant rate**.

If too much water pours in and bucket overflows → **extra water is rejected**.

This is EXACTLY how Leaky Bucket works.



**Leaky Bucket Diagram Explained**

```
Requests pouring in (fast)
     ↓  ↓  ↓  ↓  ↓ 
┌────────────────────────┐
│     BUCKET              │
│  ~~~~~~~~ requests      │  <-- fills up quickly
│  ~~~~~~~~               │
└───────────┬────────────┘
            │ leak
            ↓
         100 req/sec
```



# ⭐ **Given Example:**

### **Requests coming in**: 1000 per second

(very high, crazy speed)

### **Bucket capacity**: 1000

(max number of requests we can temporarily store)

### **Leak rate**: 100 per second

(max processing speed — fixed)



# ⭐ **What happens step-by-step:**

### 🔵 Step 1: Requests pour in fast (1000/sec)

They fill up the bucket.

### 🟢 Step 2: The bucket leaks at a steady rate (100/sec)

Processing is **smooth**, not jumpy.

### 🔴 Step 3: Bucket gets full (capacity = 1000)

Any request beyond capacity → **rejected** immediately.



# 🧠 **Why does Leaky Bucket exist?**

Because systems MUST keep **output rate stable**.

Imagine:

* Server can only handle 100 requests/sec
* But users can send 1000 requests/sec

Without a bucket → system crashes
With bucket → system absorbs some burst



# 🏎️ **REAL-LIFE ANALOGY (PERFECT EXAMPLE)**

Imagine a toll booth on a highway:

* Cars arrive FAST (1000 cars/minute)
* Only **one gate**, allows 100 cars/minute → fixed speed
* Cars queue up before the gate (the bucket)

If the queue becomes too long → cars are turned away.

This is **Leaky Bucket**.



# ✔️ **OUTPUT RATE IS ALWAYS CONSTANT**

Even if input spikes randomly:

* 200/sec → output stays 100/sec
* 5/sec → output stays 100/sec (idle)
* 1000/sec → output stays 100/sec

This prevents:

* DB overload
* API crashes
* Network congestion



# 🔥 **Where is Leaky Bucket used?**

Primarily in **network traffic shaping**, like:

* Routers
* Switches
* ISPs
* Linux kernel

Why?
Because network devices prefer **smooth, predictable traffic**.



# ⭐ **Leaky Bucket vs Token Bucket (Very Important Difference)**

| Feature        | Token Bucket  | Leaky Bucket    |
| -------------- | ------------- | --------------- |
| Allows bursts? | YES           | NO              |
| Output rate    | Variable      | Constant        |
| Good for       | Rate limiting | Traffic shaping |
| Used by        | APIs          | Networks        |

**Token Bucket = burst-friendly**
**Leaky Bucket = burst-smoothed**


# ✔️ **LEAKY BUCKET SUMMARY (memorize this)**

> **Requests enter bucket fast → leak out slowly at a fixed rate.
> If bucket overflows → new requests are rejected.**

---


# Where to Rate Limit

**API GATEWAY (Layer 1 - First Line):**

```
┌─────────┐
│ Client  │
└────┬────┘
     ↓
┌─────────────────────┐
│ API Gateway         │
│ Rate Limiter HERE   │ ← Check quota
│ → Check: 1000/hour? │
└────┬────────────────┘
     ↓ (only if within quota)
┌─────────────────────┐
│ Application Server  │
└─────────────────────┘

Benefits:
✅ Centralized control
✅ Protects entire backend
✅ Catches abuse early
✅ Easy to modify limits

Examples: Nginx, AWS API Gateway
```

**APPLICATION LEVEL (Layer 2):**

```
┌─────────────────────┐
│ API Gateway         │
└────┬────────────────┘
     ↓ (all requests)
┌─────────────────────┐
│ Application         │
│ Rate Limiter HERE   │ ← Per-endpoint limits
│ /api/search: 10/sec │
│ /api/upload: 1/sec  │
└─────────────────────┘

Benefits:
✅ Granular per-endpoint
✅ Custom per-service logic
✅ Can share state in memory

Examples: Guava RateLimiter, Bucket4j
```

**DATABASE LEVEL (Layer 3):**

```
┌─────────────────────┐
│ Application         │
└────┬────────────────┘
     ↓ (all queries)
┌─────────────────────┐
│ Database            │
│ Connection Pool: 10 │ ← Limits concurrent
│ Queue Size: 100     │ ← Buffers excess
└─────────────────────┘

Benefits:
✅ Prevents DB overload
✅ Automatic connection management
✅ Queue for fairness

Examples: JDBC connection pool
```

### Quota Types

**HARD QUOTA (Reject):**

```
Limit: 1000 requests/hour

Request 1-1000: ✅ Success
Request 1001: ❌ 429 Too Many Requests

User hits limit: Completely blocked
Behavior: Strict
Used: Free tier, prevent abuse
```

**SOFT QUOTA (Alert):**

```
Limit: 1000 requests/hour
Alert at: 90% (900 requests)

900 requests: Warning email
  "You've used 90% of your quota"

1000 requests: Limit hit, further requests blocked

Used: Premium users, gradual degradation
```

**BURST QUOTA:**

```
Sustained: 100 req/sec
Burst: 500 req/sec for 10 seconds

Normal traffic: 100/sec
Traffic spike: Can go to 500/sec for 10s
After 10s: Back to 100/sec

Used: Handle traffic spikes fairly
```

### Distributed Rate Limiting

**PROBLEM: Multiple Servers**

```
Rate Limit: 1000 requests/hour

Server 1 (in-memory counter):
├─ 500 requests counted

Server 2 (in-memory counter):
├─ 500 requests counted

Load balancer routes randomly:
├─ Client 1 → Server 1 (counts)
├─ Client 1 → Server 2 (counts separately!)
└─ Total: 1000 counted, but 1000 allowed on EACH!

Result: 2000 requests allowed (should be 1000!)
├─ Rate limit bypassed! 😱
└─ System overloaded
```

**SOLUTION: Centralized Counter**

```
All servers share Redis counter:

Server 1: Check Redis (300), increment → 301
Server 2: Check Redis (300), increment → 302
Server 3: Check Redis (300), increment → 303

Centralized Redis:
└─ True count: 303 (correct!)

When count hits 1000:
└─ All servers reject, regardless of which one receives request

Result:
✅ Consistent limiting across all servers
✅ True distributed rate limiting
```

---

## 🐍 Python Code Example

### ❌ Without Rate Limiting (Vulnerable)

```python
# ===== WITHOUT RATE LIMITING =====

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/search', methods=['GET'])
def search():
    """Search API with no rate limiting"""
    
    query = request.args.get('q', '')
    
    # Expensive operation
    results = expensive_search(query)
    
    return jsonify(results)

def expensive_search(query):
    # Simulate complex search (1 second)
    time.sleep(1)
    return {"results": f"Results for {query}"}

# Problem:
# ❌ User sends 10,000 requests simultaneously
# ❌ All processed (server slows to crawl)
# ❌ Other users affected
# ❌ Malicious DDoS attack possible
```

### ✅ Simple Rate Limiting (Per-Process)

```python
# ===== SIMPLE RATE LIMITING (IN-MEMORY) =====

from flask import Flask, jsonify, request
from collections import defaultdict
import time

app = Flask(__name__)

class RateLimiter:
    """Simple token bucket rate limiter"""
    
    def __init__(self, rate: int, per: int = 60):
        """
        rate: max requests
        per: per N seconds
        """
        self.rate = rate
        self.per = per
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request from client is allowed"""
        
        now = time.time()
        
        # Remove old requests (outside window)
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < self.per
        ]
        
        # Check if at limit
        if len(self.requests[client_id]) < self.rate:
            # Allow request
            self.requests[client_id].append(now)
            return True
        else:
            # Reject request
            return False

limiter = RateLimiter(rate=10, per=60)  # 10 req/min

@app.route('/api/search', methods=['GET'])
def search():
    """Search API with rate limiting"""
    
    client_id = request.remote_addr
    
    if not limiter.is_allowed(client_id):
        return jsonify({"error": "Rate limit exceeded"}), 429
    
    query = request.args.get('q', '')
    results = expensive_search(query)
    
    return jsonify(results)

# Benefits:
# ✅ Simple to implement
# ✅ Works per-server
# ✅ No external dependencies

# Problems:
# ❌ Only works on single server
# ❌ Memory grows with users
# ❌ Not distributed
```

### ✅ Production Rate Limiting (Distributed)

```python
# ===== PRODUCTION RATE LIMITING (REDIS) =====

import redis
import time
from typing import Tuple

class DistributedRateLimiter:
    """Redis-backed rate limiter (distributed)"""
    
    def __init__(self, redis_client, rate: int, per: int = 60):
        self.redis = redis_client
        self.rate = rate
        self.per = per
    
    def is_allowed(self, client_id: str) -> Tuple[bool, dict]:
        """Check if request allowed and return stats"""
        
        key = f"rate_limit:{client_id}"
        now = time.time()
        window = now - self.per
        
        # Remove old requests (before window)
        self.redis.zremrangebyscore(key, 0, window)
        
        # Count requests in window
        request_count = self.redis.zcard(key)
        
        if request_count < self.rate:
            # Allow request
            self.redis.zadd(key, {str(now): now})
            self.redis.expire(key, self.per)
            
            return True, {
                "limit": self.rate,
                "remaining": self.rate - request_count - 1,
                "reset_in": self.per
            }
        else:
            # Reject request
            oldest = float(self.redis.zrange(key, 0, 0, withscores=True)[0][1])
            reset_in = int(oldest + self.per - now)
            
            return False, {
                "limit": self.rate,
                "remaining": 0,
                "reset_in": reset_in
            }

# Usage
redis_client = redis.Redis(host='localhost', port=6379)
limiter = DistributedRateLimiter(
    redis_client,
    rate=100,  # 100 requests
    per=60     # per 60 seconds
)

@app.route('/api/search', methods=['GET'])
def search():
    """Search API with distributed rate limiting"""
    
    client_id = request.remote_addr
    allowed, stats = limiter.is_allowed(client_id)
    
    response_headers = {
        'X-RateLimit-Limit': str(stats['limit']),
        'X-RateLimit-Remaining': str(stats['remaining']),
        'X-RateLimit-Reset': str(int(time.time()) + stats['reset_in'])
    }
    
    if not allowed:
        return (
            jsonify({"error": "Rate limit exceeded"}),
            429,
            response_headers
        )
    
    query = request.args.get('q', '')
    results = expensive_search(query)
    
    return jsonify(results), 200, response_headers

# Benefits:
# ✅ Distributed across servers
# ✅ Consistent rate limiting
# ✅ Survives server restarts
# ✅ Includes response headers (client can see remaining quota)
```

### ✅ Advanced: Tiered Rate Limiting

```python
# ===== TIERED RATE LIMITING =====

class TieredRateLimiter:
    """Different limits for different user tiers"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        
        # Define tiers
        self.tiers = {
            'free': {'rate': 100, 'per': 3600},      # 100/hour
            'pro': {'rate': 10000, 'per': 3600},     # 10k/hour
            'enterprise': {'rate': float('inf'), 'per': 3600}  # Unlimited
        }
    
    def get_user_tier(self, user_id: str) -> str:
        """Get user's subscription tier"""
        # In real system: fetch from database
        return 'free'  # Default
    
    def is_allowed(self, user_id: str) -> Tuple[bool, dict]:
        """Check if request allowed"""
        
        tier = self.get_user_tier(user_id)
        limits = self.tiers[tier]
        
        # If unlimited: always allow
        if limits['rate'] == float('inf'):
            return True, {"tier": tier, "limit": "unlimited"}
        
        # Otherwise: standard rate limiting
        key = f"rate_limit:{user_id}"
        now = time.time()
        window = now - limits['per']
        
        # Count requests
        self.redis.zremrangebyscore(key, 0, window)
        request_count = self.redis.zcard(key)
        
        if request_count < limits['rate']:
            self.redis.zadd(key, {str(now): now})
            self.redis.expire(key, limits['per'])
            return True, {
                "tier": tier,
                "limit": limits['rate'],
                "remaining": limits['rate'] - request_count - 1
            }
        else:
            return False, {
                "tier": tier,
                "limit": limits['rate'],
                "remaining": 0
            }

# Usage
tiered_limiter = TieredRateLimiter(redis_client)

@app.route('/api/search', methods=['GET'])
def search():
    """Search with tiered rate limiting"""
    
    user_id = get_user_id(request)  # From auth
    allowed, stats = tiered_limiter.is_allowed(user_id)
    
    if not allowed:
        return jsonify({"error": "Rate limit exceeded"}), 429
    
    # Process request
    return jsonify({"results": "..."})

# Benefits:
# ✅ Monetization (free vs paid)
# ✅ Different limits per tier
# ✅ Enterprise: unlimited
```

---

## 💡 Mini Project: "Build a Rate Limiter"

### Phase 1: Simple Algorithm ⭐

**Requirements:**
- Token bucket implementation
- Per-client limits
- In-memory storage
- Response headers
- Basic metrics

---

### Phase 2: Distributed ⭐⭐

**Requirements:**
- Redis backend
- Multiple servers
- Consistent limits
- Tiered limits
- Request tracking

---

### Phase 3: Production ⭐⭐⭐

**Requirements:**
- Multiple algorithms (bucket, sliding window, leaky)
- Dynamic limit updates
- Analytics dashboard
- Abuse detection
- Graceful degradation

---

## ⚖️ Rate Limiting Algorithms Comparison

| Algorithm | Burst Handling | Complexity | Memory | Best For |
|-----------|---|---|---|---|
| **Token Bucket** | ✅ Yes | Low | Low | General purpose |
| **Sliding Window** | ❌ No | Medium | Medium | Strict limits |
| **Leaky Bucket** | ✅ Yes | Low | Low | Smooth output |
| **Fixed Window** | ❌ No | Very Low | Very Low | Simple |

---

## 🎯 When to Use Rate Limiting

```
✅ USE WHEN:
- Public APIs (prevent abuse)
- Limited resources (DB connections)
- Cost control (expensive operations)
- Fair resource sharing
- DDoS protection
- Free tier users
- Prevent runaway scripts

❌ LESS CRITICAL WHEN:
- Internal APIs (trusted)
- Unlimited resources
- Single user (no contention)
```

---

## ❌ Common Mistakes

### Mistake 1: Only Global Limits

```python
# ❌ Single global limit
limit = 10000  # per hour total

# One user burns it all
# Others starved

# ✅ Per-user limits
limit_per_user = 1000  # per hour each
# Fair for all
```

### Mistake 2: Synchronous Rate Limiting

```python
# ❌ Check limit for every request (slow)
for request in incoming_requests:
    if check_limit_in_db(user):  # Database query!
        process(request)

# Performance dies under load

# ✅ Use local cache or Redis
if rate_limiter.is_allowed(user):
    process(request)  # In-memory, fast
```

### Mistake 3: No Response Headers

```python
# ❌ No indication of remaining quota
response = jsonify({"data": "..."})
return response

# User confused: how many left?
# Client can't optimize

# ✅ Include headers
response.headers['X-RateLimit-Remaining'] = str(remaining)
response.headers['X-RateLimit-Reset'] = str(reset_time)
return response
```

---

## 📚 Additional Resources

**Libraries:**
- [Guava RateLimiter](https://guava.dev/) (Java)
- [Bucket4j](https://github.com/vladimir-bukhtoyarov/bucket4j) (Java)
- [Flask-Limiter](https://flask-limiter.readthedocs.io/) (Python)
- [express-rate-limit](https://github.com/nfriedly/express-rate-limit) (Node.js)

**Reading:**
- [API Rate Limiting](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)
- [Token Bucket Algorithm](https://en.wikipedia.org/wiki/Token_bucket)



---

## 🎯 Before You Leave

**Can you answer these?**

1. **What's the difference between rate limiting and throttling?**
   - Answer: Rate limiting rejects; throttling delays

2. **How does token bucket work?**
   - Answer: Refills tokens at fixed rate, reject when empty

3. **Why distributed rate limiting?**
   - Answer: Single server limits can be bypassed across multiple servers

4. **What response headers should you include?**
   - Answer: X-RateLimit-Limit, Remaining, Reset

5. **When to rate limit at API gateway vs application?**
   - Answer: Gateway for global; Application for per-endpoint

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **User:** "Why did my request get rejected?"
>
> **API:** "You exceeded rate limit."
>
> **User:** "But I only sent 1 request!"
>
> **API:** "Yeah, per microsecond." ⚡

---

[← Back to Main](../README.md) | [Previous: Distributed Logging](21-distributed-logging.md) | [Next: API Gateways →](23-api-gateways.md)

---

**Last Updated:** November 11, 2025  
**Difficulty:** ⭐⭐ Beginner-Intermediate (algorithm understanding)  
**Time to Read:** 24 minutes  
**Time to Build Limiter:** 3-6 hours per phase  

---

*Rate limiting: How to say "no more!" without breaking the API.* 🚀