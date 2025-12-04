# 42. Rate Limiting (Security)

Rate limiting stops people from abusing your API. User makes 1000 requests per second? Blocked! Brute force attack with 10 million login attempts? Blocked! Then legitimate traffic spike hits and you block paying customers too. Oops. Rate limiting is like security, but it also blocks the people you want. Fun times! 🚦⚠️

[← Back to Main](../README.md) | [Previous: Authentication & Authorization](41-auth-oauth-jwt.md) | [Next: SSL/TLS & HTTPS](43-ssl-tls-https.md)

---

## 🎯 Quick Summary

**Rate Limiting** restricts request frequency per user/IP to prevent abuse. Stops brute force attacks, DDoS, resource exhaustion. Algorithms: token bucket (smooth), sliding window (flexible), leaky bucket (steady). Redis commonly used (fast lookups). GitHub API: 60 requests/minute (unauthenticated), 5000/hour (authenticated). AWS limits everything. Trade-off: legitimate traffic may be blocked, complexity in distributed systems, fairness issues.

Think of it as: **Rate Limiting = Traffic Cop**

---

## 🌟 Beginner Explanation

### Why Rate Limiting?

```
SCENARIO 1: Brute Force Attack

Attacker:
├─ Tries password: attempt1
├─ Wrong, tries: attempt2
├─ Wrong, tries: attempt3
├─ ... (10 million attempts)
└─ Password cracked (maybe)

Without rate limiting:
├─ System processes all 10M requests
├─ Database under load
├─ Legitimate users slow down
├─ Attack succeeds (eventually)

With rate limiting:
├─ Allow 5 attempts per minute
├─ 6th attempt: Blocked (rate limit)
├─ Attacker can only try 300 times per hour
├─ After 1 hour: Account locked
└─ Attack fails! ✓


SCENARIO 2: Accidental Spike

Bug in client code:
├─ Sends 100 requests instead of 1
├─ Client repeats bug millions of times
├─ Server under attack (accidentally!)

Without rate limiting:
├─ Server crashes
├─ Everyone affected
├─ Revenue lost

With rate limiting:
├─ After request limit hit
├─ Additional requests: Blocked
├─ Client gets 429 (Too Many Requests)
├─ Fix the bug
├─ Traffic resumes
└─ Server stays healthy! ✓


SCENARIO 3: DDoS Attack

Attacker:
├─ 10,000 bots, each sending 1000 req/sec
├─ Total: 10M requests/second
└─ System can't handle

Without rate limiting:
├─ Server tries to process all
├─ CPU exhausted
├─ Memory exhausted
├─ Crashes
└─ Complete outage

With rate limiting:
├─ Each IP limited to 100 req/sec
├─ 10,000 bots × 100 = 1M req/sec
├─ Still too much!
├─ But mitigates worst attacks
└─ Combined with IP blocking: More protection
```

### Rate Limiting Algorithms

```
TOKEN BUCKET (Most common):

Bucket capacity: 100 tokens
Refill rate: 10 tokens per second

User makes requests:
├─ Request 1: Take 1 token (99 left)
├─ Request 2: Take 1 token (98 left)
├─ ... (50 requests)
├─ Request 50: Take 1 token (50 left)
├─ Time passes: 5 seconds
├─ Refill: +50 tokens (100 total)
├─ Request 51: Take 1 token (99 left)
└─ Continue...

Burst allowed:
├─ If user inactive for 10 seconds
├─ Bucket fills to max (100)
├─ User can do 100 requests instantly
├─ (Bursty traffic OK)

Good for:
✅ Smooth traffic
✅ Allows bursts
✅ Fair allocation
✅ Simple implementation


SLIDING WINDOW:

Window: Last 60 seconds
Limit: 100 requests per minute

Timestamp tracking:
├─ T=0s: Request (count=1)
├─ T=5s: Request (count=2)
├─ T=10s: Request (count=3)
├─ T=55s: Request (count=4)
├─ T=60s: Request (count=5)
├─ T=61s: Oldest request (T=0s) expires
│  └─ Remove from window
├─ T=61s: Current window (T=1-61s, count=4)
├─ T=61s: New request (count=5)
└─ ...

Exact measurement but storage-heavy
(Must store timestamp of each request)


LEAKY BUCKET:

Queue of requests
Leak rate: 10 requests per second

User sends requests:
├─ Request 1: Queue (queue size=1)
├─ Request 2: Queue (queue size=2)
├─ Request 3: Queue (queue size=3)
├─ ... (100 requests)
├─ Request 100: Queue (queue size=100)
├─ Request 101: Overflow! Dropped (rate limit)

Processing:
├─ 1 request processed per 100ms
├─ After 1 second: 10 processed
├─ Queue steadily empties
└─ Smooth, constant rate

Good for:
✅ Steady processing
✅ Prevents bursts
✅ Fair allocation
✅ Queue-based
```

### Implementation

```
SIMPLE RATE LIMITING (In-Memory):

```python
from collections import defaultdict
from time import time

class RateLimiter:
    def __init__(self, max_requests=100, window=60):
        self.max_requests = max_requests  # 100 requests
        self.window = window              # per 60 seconds
        self.requests = defaultdict(list)  # Track requests per user
    
    def is_allowed(self, user_id):
        now = time()
        window_start = now - self.window
        
        # Remove old requests outside window
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if req_time > window_start
        ]
        
        # Check if under limit
        if len(self.requests[user_id]) < self.max_requests:
            self.requests[user_id].append(now)
            return True
        
        return False  # Rate limited

Problems:
❌ In-memory (lost on restart)
❌ Single server only
❌ Doesn't work with multiple servers
❌ High memory usage

```

REDIS-BASED (Production):

```python
import redis

class RedisRateLimiter:
    def __init__(self, redis_client, max_requests=100, window=60):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window = window
    
    def is_allowed(self, user_id):
        key = f"rate_limit:{user_id}"
        
        # Increment request counter
        current = self.redis.incr(key)
        
        # Set expiration on first request
        if current == 1:
            self.redis.expire(key, self.window)
        
        # Check if over limit
        return current <= self.max_requests

Benefits:
✅ Distributed (works across servers)
✅ Fast (Redis in-memory)
✅ Persistent
✅ Industry standard
```

---

## 🔬 Advanced Explanation

### Distributed Rate Limiting

```
PROBLEM: Multiple servers

User makes requests:
├─ Request 1: Server A
├─ Request 2: Server B
├─ Request 3: Server C
├─ ... (100 requests to different servers)

Each server thinks:
├─ "Only got 33 requests, under limit!"
└─ Total: 99 (allowed)

But actually: User sent 100+ requests!
Rate limit broken! ❌


SOLUTION: Centralized Counter (Redis)

All servers share Redis:
├─ Server A: Check Redis counter
├─ Server B: Check Redis counter
├─ Server C: Check Redis counter

Request 1: incr(user_123) = 1
Request 2: incr(user_123) = 2
Request 3: incr(user_123) = 3
...
Request 100: incr(user_123) = 100
Request 101: incr(user_123) = 101 → BLOCKED

Global counter! ✓


RACE CONDITIONS:

Without atomic operations:
├─ Server A: Read counter (99)
├─ Server B: Read counter (99)
├─ Server A: Increment to 100, Write (allowed)
├─ Server B: Increment to 100, Write (allowed!)
└─ Both allowed when should block!

With atomic Redis operations:
├─ Server A: INCR (atomic)
├─ Server B: INCR (atomic)
├─ Redis handles ordering
└─ One returns 100, one returns 101 (blocked)
```

### Fairness & Distributed Rate Limiting

```
PROBLEM: Fair allocation

Multiple users, shared rate limit:
├─ User A: 50 requests/sec
├─ User B: 50 requests/sec
├─ Total allowed: 100 requests/sec

If User A sends 100 requests:
├─ All blocked (over individual limit)
└─ User B can send 100 (gets full limit) ✓

But what if limit is global (100 total)?
├─ User A sends 100
├─ User B can send 0
└─ Unfair! User A hogged all

SOLUTION: Per-user limit

Each user gets: 100 requests/sec
Total across all users: Unlimited (if they share)

User A: Limited to 100
User B: Limited to 100
User C: Limited to 100
...
Fairness: Guaranteed ✓


PRIORITY-BASED RATE LIMITING:

VIP user: 1000 requests/sec
Regular user: 100 requests/sec
Free user: 10 requests/sec

Implementation:
├─ Check user tier
├─ Apply appropriate limit
├─ VIP doesn't block regular
└─ Regular doesn't block free
```

### Strategies

```
STRATEGY 1: User-Based (Per-User Limit)

Limit applies to: Individual user account

Example:
├─ alice@example.com: 1000 requests/hour
├─ bob@example.com: 1000 requests/hour
├─ charlie@example.com: 1000 requests/hour

Each user independent


STRATEGY 2: IP-Based (Per-IP Limit)

Limit applies to: IP address

Example:
├─ 192.168.1.1: 1000 requests/hour
├─ 192.168.1.2: 1000 requests/hour

Problem:
❌ Behind proxy: All users from same IP!
❌ NAT networks: Multiple users same IP


STRATEGY 3: API Key-Based

Limit applies to: API key

Example:
├─ API key abc123: 100 requests/sec
├─ API key xyz789: 50 requests/sec

Good for: Service-to-service communication


STRATEGY 4: Endpoint-Based

Different limits per endpoint:

Example:
├─ GET /users: 1000 requests/hour
├─ POST /orders: 100 requests/hour
├─ DELETE /users: 10 requests/hour

Protect expensive operations ✓


STRATEGY 5: Cost-Based (Weighted)

Different operations cost different:

Example:
├─ GET /users (cost=1): 1000 requests
├─ POST /orders (cost=5): 200 requests (uses 1000 budget)
├─ ML prediction (cost=100): 10 requests (uses 1000 budget)

Fair allocation ✓
```

---

## 🐍 Python Code Example

### ❌ Without Rate Limiting (Vulnerable)

```python
# ===== WITHOUT RATE LIMITING =====

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/login', methods=['POST'])
def login():
    """Login endpoint - no rate limiting"""
    
    username = request.json.get('username')
    password = request.json.get('password')
    
    # Brute force attack possible!
    # Attacker can try millions of passwords
    
    user = verify_credentials(username, password)
    if user:
        return jsonify({'token': create_token(user)})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

# Problem:
# ❌ No rate limiting
# ❌ Brute force attacks possible
# ❌ Can try 10M passwords/hour
# ❌ No protection
```

### ✅ With Rate Limiting (Token Bucket)

```python
# ===== WITH RATE LIMITING =====

from flask import Flask, request, jsonify
import redis
from time import time

app = Flask(__name__)
redis_client = redis.Redis(host='localhost', port=6379)

class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, redis, max_tokens=10, refill_rate=1):
        self.redis = redis
        self.max_tokens = max_tokens  # 10 login attempts
        self.refill_rate = refill_rate  # 1 per second
    
    def is_allowed(self, user_id):
        """Check if request is allowed"""
        
        key = f"rate_limit:{user_id}"
        
        # Get current tokens (or initialize)
        tokens = float(self.redis.get(key) or self.max_tokens)
        
        # Get last update time
        last_update_key = f"rate_limit_ts:{user_id}"
        last_update = float(self.redis.get(last_update_key) or time())
        
        now = time()
        elapsed = now - last_update
        
        # Refill tokens: +1 per second
        tokens = min(
            self.max_tokens,
            tokens + (elapsed * self.refill_rate)
        )
        
        # Update timestamp
        self.redis.set(last_update_key, now)
        
        if tokens >= 1:
            # Allow request, consume 1 token
            self.redis.set(key, tokens - 1)
            return True
        else:
            # Rate limited
            return False

# Initialize rate limiter
limiter = RateLimiter(redis_client, max_tokens=10, refill_rate=1)

@app.route('/api/login', methods=['POST'])
def login():
    """Login endpoint with rate limiting"""
    
    username = request.json.get('username')
    
    # Check rate limit per user
    if not limiter.is_allowed(username):
        return jsonify({'error': 'Too many login attempts'}), 429
    
    password = request.json.get('password')
    user = verify_credentials(username, password)
    
    if user:
        return jsonify({'token': create_token(user)})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

# Benefits:
# ✅ Brute force protection (10 attempts/10 seconds)
# ✅ Distributed (Redis-backed)
# ✅ Token bucket algorithm
# ✅ Fair and smooth
```

### ✅ Production Rate Limiter (Advanced)

```python
# ===== PRODUCTION RATE LIMITER =====

from functools import wraps
from time import time
import redis

class AdvancedRateLimiter:
    """Production-grade rate limiter with multiple strategies"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.limits = {}  # Define limits per endpoint
    
    def set_limit(self, endpoint, max_requests, window_seconds, by='user'):
        """Configure rate limit"""
        
        self.limits[endpoint] = {
            'max_requests': max_requests,
            'window': window_seconds,
            'by': by  # 'user', 'ip', 'api_key'
        }
    
    def get_key(self, endpoint, identifier):
        """Generate Redis key"""
        return f"rate_limit:{endpoint}:{identifier}"
    
    def check_limit(self, endpoint, identifier):
        """Check if request is allowed"""
        
        if endpoint not in self.limits:
            return True  # No limit set
        
        limit_config = self.limits[endpoint]
        key = self.get_key(endpoint, identifier)
        
        # Use sliding window counter
        now = int(time())
        window_start = now - limit_config['window']
        
        # Get all requests in window (remove old ones)
        self.redis.zremrangebyscore(key, 0, window_start)
        
        # Count requests in current window
        count = self.redis.zcard(key)
        
        if count < limit_config['max_requests']:
            # Allow request
            self.redis.zadd(key, {str(now): now})
            self.redis.expire(key, limit_config['window'])
            return True
        else:
            # Rate limited
            return False
    
    def rate_limit_by_user(self, endpoint):
        """Decorator for rate limiting by user"""
        
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                # Get user from request
                user_id = get_current_user_id()  # Implementation specific
                
                if not self.check_limit(endpoint, user_id):
                    return jsonify({'error': 'Rate limit exceeded'}), 429
                
                return f(*args, **kwargs)
            
            return decorated
        
        return decorator
    
    def rate_limit_by_ip(self, endpoint):
        """Decorator for rate limiting by IP"""
        
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                ip = request.remote_addr
                
                if not self.check_limit(endpoint, ip):
                    return jsonify({'error': 'Rate limit exceeded'}), 429
                
                return f(*args, **kwargs)
            
            return decorated
        
        return decorator

# Usage
app = Flask(__name__)
redis_client = redis.Redis(host='localhost')
limiter = AdvancedRateLimiter(redis_client)

# Configure limits
limiter.set_limit('login', max_requests=5, window_seconds=60)
limiter.set_limit('api_call', max_requests=100, window_seconds=3600)
limiter.set_limit('ml_predict', max_requests=10, window_seconds=3600)

@app.route('/api/login', methods=['POST'])
@limiter.rate_limit_by_user('login')
def login():
    """Login with per-user rate limiting"""
    # Implementation
    pass

@app.route('/api/call', methods=['GET'])
@limiter.rate_limit_by_ip('api_call')
def api_call():
    """API endpoint with per-IP rate limiting"""
    # Implementation
    pass

@app.route('/api/ml/predict', methods=['POST'])
@limiter.rate_limit_by_user('ml_predict')
def ml_predict():
    """ML prediction with user-based limiting"""
    # Implementation
    pass

# Benefits:
# ✅ Multiple strategies
# ✅ Per-endpoint limits
# ✅ Decorators for easy application
# ✅ Production-ready
# ✅ Distributed (Redis)
```

---

## 💡 Mini Project: "Build Rate Limiter"

### Phase 1: Basic Limiter ⭐

**Requirements:**
- Token bucket algorithm
- Per-user limiting
- Simple Redis backend
- HTTP 429 responses

---

### Phase 2: Advanced Limiter ⭐⭐

**Requirements:**
- Multiple strategies (user, IP, API key)
- Per-endpoint limits
- Sliding window
- Distributed setup

---

### Phase 3: Production Ready ⭐⭐⭐

**Requirements:**
- Weighted costs
- Priority tiers (VIP/regular/free)
- Monitoring & metrics
- DDoS protection integration

---

## ⚖️ Rate Limiting Algorithms

| Algorithm | Burst | Fairness | Storage | Accuracy |
|-----------|-------|----------|---------|----------|
| **Token Bucket** | High | Good | Low | Good |
| **Sliding Window** | None | Excellent | High | Excellent |
| **Leaky Bucket** | None | Good | Low | Good |
| **Fixed Window** | High | Fair | Very Low | Fair |

---

## ❌ Common Mistakes

### Mistake 1: Rate Limit Only By User

```python
# ❌ Only per-user
limiter.is_allowed(user_id)
# But: One user can create many accounts!

# ✅ Multiple limits
limiter.is_allowed(user_id)    # Per user
limiter.is_allowed(ip_address) # Per IP
limiter.is_allowed(api_key)    # Per API key
# Multiple layers of protection
```

### Mistake 2: No Gradual Backoff

```python
# ❌ Block immediately at limit
if count >= limit:
    return 429
# Harsh, no warning

# ✅ Warn before blocking
if count >= limit * 0.8:
    add_retry_after_header()
if count >= limit:
    return 429
```

### Mistake 3: Distributed Inconsistency

```python
# ❌ Counter only in-memory
requests_per_user = {}
requests_per_user[user] = requests_per_user.get(user, 0) + 1
# Restart server: Counter reset!

# ✅ Persistent Redis
redis.incr(f"limit:{user}")
redis.expire(key, window)
# Survives restarts
```

---

## 📚 Additional Resources

**Algorithms:**
- [Token Bucket](https://en.wikipedia.org/wiki/Token_bucket)
- [Leaky Bucket](https://en.wikipedia.org/wiki/Leaky_bucket)
- [Rate Limiting Strategies](https://stripe.com/blog/rate-limiters)

**Tools:**
- [Redis](https://redis.io/)
- [Nginx rate limiting](https://nginx.org/en/docs/http/ngx_http_limit_req_module.html)
- [API Gateway rate limiting](https://docs.aws.amazon.com/apigateway/)

---

## 🎯 Before You Leave

**Can you answer these?**

1. **Token bucket vs sliding window?**
   - Answer: Token bucket allows bursts; sliding window exact

2. **Why rate limit?**
   - Answer: Prevent brute force, DDoS, resource exhaustion

3. **Distributed rate limiting?**
   - Answer: Use centralized Redis, not in-memory

4. **Per-user vs per-IP limiting?**
   - Answer: Per-user for accounts; per-IP for attackers

5. **What HTTP status for rate limit?**
   - Answer: 429 (Too Many Requests)

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **Attacker:** "Let me brute force this login 10 million times"
>
> **Rate Limiter:** "5 attempts per minute"
>
> **Attacker:** "That's not fair!"
>
> **Rate Limiter:** "It's not supposed to be fair to attackers"
>
> **Legitimate User:** "I tried 6 times, why am I blocked?"
>
> **Rate Limiter:** "Oops, collateral damage" 😅

---

[← Back to Main](../README.md) | [Previous: Authentication & Authorization](41-auth-oauth-jwt.md) | [Next: SSL/TLS & HTTPS](43-ssl-tls-https.md)

---

**Last Updated:** November 11, 2025  
**Difficulty:** ⭐⭐⭐ Intermediate-Advanced (security)  
**Time to Read:** 24 minutes  
**Time to Implement:** 4-6 hours per phase  

---

*Rate Limiting: Stopping abuse by knowing when to say no.* 🚀