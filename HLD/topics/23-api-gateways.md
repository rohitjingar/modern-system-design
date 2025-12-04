# 23. API Gateways

An API gateway is like a nightclub bouncer who also checks IDs, enforces dress codes, limits drinks per person, logs who's coming and going, routes VIPs to the best section, and somehow also manages the coat check. It's either the best system decision you've ever made or the single point of failure that will ruin your Saturday night. 🎩

[← Back to Main](../README.md) | [Previous: Rate Limiting](22-rate-limiting.md) | [Service Discovery](24-service-discovery.md)

---

## 🎯 Quick Summary

**API Gateways** are the front door to your microservices: they authenticate, rate limit, route, transform, cache, and log all API requests. Kong, AWS API Gateway, Nginx, Traefik are popular. Without them: every service handles security, routing, logging (duplicated work). With them: centralized control, consistent behavior, security boundary. Single point of contact for clients, intelligent distribution to backend services.

Think of it as: **API Gateway = Intelligent Receptionist for Your APIs**

---

## 🌟 Beginner Explanation

### Before API Gateway (Chaos)

```
┌────────────────────────────────────────────┐
│  Multiple Clients                          │
└────────────────────────────────────────────┘
    ↓↓↓↓↓↓↓
┌──────────┐  ┌──────────┐  ┌──────────┐
│User Svc  │  │Order Svc │  │Payment   │
│ ├─ Auth  │  │ ├─ Auth  │  │ ├─ Auth  │
│ ├─ Rate  │  │ ├─ Rate  │  │ ├─ Rate  │
│ └─ Log   │  │ └─ Log   │  │ └─ Log   │
└──────────┘  └──────────┘  └──────────┘

Problems:
❌ Each service does auth (duplicated code)
❌ Each service does rate limiting (inconsistent)
❌ Each service does logging (inconsistent)
❌ Clients need to know all service URLs
❌ Security scattered across services
❌ Hard to change auth globally
```

### With API Gateway (Organized)

```
┌────────────────────────────────────────────┐
│  Clients (talk to ONE URL)                 │
└────────────────────────────────────────────┘
            ↓
┌────────────────────────────────────────────┐
│  API GATEWAY (central point)               │
│ ├─ Authentication (once!)                  │
│ ├─ Rate Limiting (global!)                 │
│ ├─ Request Logging (centralized!)          │
│ ├─ Routing (to correct service)            │
│ ├─ Caching (common responses)              │
│ └─ Response Transform (JSON → XML)         │
└────────────────────────────────────────────┘
    ↓↓↓↓↓↓↓
┌──────────┐  ┌──────────┐  ┌──────────┐
│User Svc  │  │Order Svc │  │Payment   │
│(no auth) │  │(no auth) │  │(no auth) │
│(simple!) │  │(simple!) │  │(simple!) │
└──────────┘  └──────────┘  └──────────┘

Benefits:
✅ Single authentication layer
✅ Consistent rate limiting
✅ Centralized logging
✅ Services don't know about clients
✅ Easy security updates
✅ Services focus on business logic
```

### API Gateway Responsibilities

```
INCOMING REQUEST:
Client → GET /api/users/123

API Gateway DOES:

1. AUTHENTICATION:
   ├─ Extract token from header
   ├─ Validate token
   └─ Who is this user?

2. RATE LIMITING:
   ├─ Check: Is user under limit?
   ├─ Update counter
   └─ Reject if over

3. ROUTING:
   ├─ Parse path: /api/users/123
   ├─ Decide: This goes to User Service
   └─ Route to correct backend

4. TRANSFORMATION (optional):
   ├─ Modify headers
   ├─ Add X-User-ID header
   └─ Add trace ID for logging

5. FORWARDING:
   ├─ Send to User Service: GET /123 (simplified)
   ├─ Wait for response

6. RESPONSE PROCESSING:
   ├─ Receive: {"id": 123, "name": "Alice"}
   ├─ Cache (if appropriate)
   ├─ Log: user_id=123, status=200
   └─ Return to client

OUTGOING RESPONSE:
Client ← {"id": 123, "name": "Alice"}
```

---

## 🔬 Advanced Explanation

### API Gateway Architecture

```
SINGLE API GATEWAY (Simple):

Internet
  ↓
API Gateway (single instance)
  ├→ User Service
  ├→ Order Service
  ├→ Payment Service

Problem: Single point of failure!
If gateway down: All APIs down


LOAD-BALANCED API GATEWAYS (HA):

Internet
  ↓
Load Balancer
  ├→ API Gateway 1
  ├→ API Gateway 2
  ├→ API Gateway 3 (stateless!)

Then:
  ├→ User Service
  ├→ Order Service
  ├→ Payment Service

Benefits:
✅ Multiple gateways (no single failure)
✅ Gateways are stateless (replaceable)
✅ Scale horizontally
```

### Routing Strategies

**PATH-BASED ROUTING:**

```
GET /api/users/123
→ User Service

GET /api/orders/456
→ Order Service

GET /api/payments/789
→ Payment Service

Configuration:
/api/users/* → user-service:8001
/api/orders/* → order-service:8002
/api/payments/* → payment-service:8003
```

**HOSTNAME-BASED ROUTING:**

```
users.api.example.com/123
→ User Service

orders.api.example.com/456
→ Order Service

Configuration:
users.api.example.com → user-service:8001
orders.api.example.com → order-service:8002
```

**METHOD + PATH ROUTING:**

```
POST /api/users
→ User Service (create)

GET /api/users/123
→User Service (read)

PUT /api/users/123
→ User Service (update)

DELETE /api/users/123
→ User Service (delete)
```

**WEIGHTED ROUTING (Canary Deployment):**

```
GET /api/users

Route 90% to version 1.0
Route 10% to version 2.0 (new, testing)

After 1 week (if stable):
Route 100% to version 2.0

Benefits:
✅ Test new version with real traffic
✅ Rollback easy (if issues)
✅ No downtime
```

### Advanced Features

**REQUEST/RESPONSE TRANSFORMATION:**

```
Client sends: {"user_id": "alice"}
API Gateway translates to: {"user": "alice"}
Backend expects: {"user": "alice"}

Use case: Migrate API format without changing services

Example (XML → JSON):
Client sends: <user>alice</user>
API Gateway converts to: {"user": "alice"}
Backend receives: {"user": "alice"}
```

**HEADER MANIPULATION:**

```
Incoming request:
GET /api/users/123
Authorization: Bearer token-xyz
User-Agent: Mobile/1.0

API Gateway ADDS:
X-User-ID: 42
X-Request-ID: req-abc123
X-Forwarded-Proto: https
X-Real-IP: 203.0.113.45

Forwarded to backend:
GET /api/users/123
X-User-ID: 42 ← Added!
X-Request-ID: req-abc123 ← Added!
X-Forwarded-Proto: https
X-Real-IP: 203.0.113.45
```

**RESPONSE CACHING:**

```
Request 1: GET /api/users/123
→ Call backend
→ Backend takes 200ms
→ Response: 200ms
→ Cache in API Gateway (TTL: 60s)

Request 2: GET /api/users/123 (within 60s)
→ Cache hit!
→ Response: 1ms (cached!)
→ Never hits backend

After 60s:
Request 3: GET /api/users/123
→ Cache expired
→ Call backend again
→ Response: 200ms
```

**REQUEST AGGREGATION:**

```
Client requests: GET /api/dashboard?user=123

API Gateway realizes it needs:
├─ User profile from User Service
├─ Recent orders from Order Service
├─ Account balance from Payment Service

API Gateway does:
├─ Parallel requests to all 3 services
├─ Aggregates responses
└─ Returns to client in ONE response

Result:
Single request → 3 services in parallel
User gets: {user, orders, balance} in one call
```

### Gateway vs Load Balancer

```
LOAD BALANCER:
├─ Level: Transport (L4) or Network (L7)
├─ Job: Distribute traffic
├─ Knows: IP, port, basic routing
├─ Used: 3 backend servers, pick one

API GATEWAY:
├─ Level: Application
├─ Job: API-specific logic
├─ Knows: Auth, rate limits, transformations
├─ Used: Route to correct microservice, enforce policy

TOGETHER:
External → Load Balancer → Gateway → Services
         (distribute)      (route & policy)
```

---

## 🐍 Python Code Example

### ❌ Without API Gateway (Direct Access)

```python
# ===== WITHOUT API GATEWAY =====

from flask import Flask, jsonify, request
import requests

# Client talks directly to each service
user_service_url = "http://user-service:8001"
order_service_url = "http://order-service:8002"
payment_service_url = "http://payment-service:8003"

# PROBLEM: Client must know all URLs!
# PROBLEM: Client does auth itself!
# PROBLEM: Client rate limits itself (doesn't enforce)

def get_user(user_id):
    """Client calls User Service directly"""
    # No authentication check!
    # No rate limiting!
    response = requests.get(f"{user_service_url}/users/{user_id}")
    return response.json()

def get_orders(user_id):
    """Client calls Order Service directly"""
    response = requests.get(f"{order_service_url}/orders?user={user_id}")
    return response.json()

# Problems:
# ❌ Client knows internal URLs
# ❌ No central auth
# ❌ Each service does auth separately
# ❌ No rate limiting at gateway
# ❌ Hard to monitor
```

### ✅ Simple API Gateway

```python
# ===== SIMPLE API GATEWAY =====

from flask import Flask, jsonify, request
import requests
from functools import wraps
import time

app = Flask(__name__)

# Backend services
SERVICES = {
    'users': 'http://user-service:8001',
    'orders': 'http://order-service:8002',
    'payments': 'http://payment-service:8003'
}

# Simple auth (token)
VALID_TOKENS = {'token-123', 'token-456'}

def authenticate(f):
    """Authentication middleware"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if token not in VALID_TOKENS:
            return jsonify({"error": "Unauthorized"}), 401
        
        return f(*args, **kwargs)
    
    return decorated

class RateLimiter:
    """Simple rate limiter"""
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, user_token):
        now = time.time()
        if user_token not in self.requests:
            self.requests[user_token] = []
        
        # Remove old requests (outside 1 minute window)
        self.requests[user_token] = [
            t for t in self.requests[user_token]
            if now - t < 60
        ]
        
        # Limit: 100 req/min
        if len(self.requests[user_token]) < 100:
            self.requests[user_token].append(now)
            return True
        return False

limiter = RateLimiter()

@app.route('/api/<service>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@authenticate
def gateway_route(service, path):
    """Route requests to correct backend service"""
    
    # Rate limiting
    token = request.headers.get('Authorization')
    if not limiter.is_allowed(token):
        return jsonify({"error": "Rate limit exceeded"}), 429
    
    # Routing
    if service not in SERVICES:
        return jsonify({"error": "Service not found"}), 404
    
    backend_url = f"{SERVICES[service]}/{path}"
    
    # Forward request
    try:
        response = requests.request(
            method=request.method,
            url=backend_url,
            json=request.get_json(),
            params=request.args,
            headers={
                'X-Forwarded-User': token,
                'X-Request-ID': request.headers.get('X-Request-ID', 'unknown')
            }
        )
        
        return jsonify(response.json()), response.status_code
    
    except Exception as e:
        return jsonify({"error": str(e)}), 503

# Usage:
# Client: GET /api/users/123
#         Authorization: Bearer token-123
# → Gateway authenticates
# → Gateway rate limits
# → Gateway routes to User Service
# → Returns response
```

### ✅ Production API Gateway

```python
# ===== PRODUCTION API GATEWAY =====

from flask import Flask, jsonify, request, Response
import requests
from functools import wraps
import time
import json
from datetime import datetime
import hashlib

app = Flask(__name__)

class ProductionAPIGateway:
    """Production-grade API gateway"""
    
    def __init__(self):
        self.services = {
            'users': {'url': 'http://user-service:8001', 'timeout': 5},
            'orders': {'url': 'http://order-service:8002', 'timeout': 10},
            'payments': {'url': 'http://payment-service:8003', 'timeout': 15}
        }
        
        self.cache = {}  # Simple cache
        self.request_log = []
    
    def authenticate(self, token):
        """Authenticate request"""
        # In production: check against database
        valid_tokens = {'token-123', 'token-456'}
        return token in valid_tokens
    
    def rate_limit(self, user_id):
        """Check rate limit"""
        # In production: use Redis for distributed
        key = f"rate_limit:{user_id}"
        # Simplified: allow all in demo
        return True
    
    def should_cache(self, method, path):
        """Decide if response should be cached"""
        # Cache GET requests only
        if method != 'GET':
            return False
        
        # Don't cache certain paths
        if 'search' in path or 'dynamic' in path:
            return False
        
        return True
    
    def get_cache_key(self, method, path, query_string):
        """Generate cache key"""
        key_str = f"{method}:{path}?{query_string}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def log_request(self, user_id, method, path, status, latency):
        """Log request"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'method': method,
            'path': path,
            'status': status,
            'latency_ms': int(latency * 1000)
        }
        self.request_log.append(log_entry)
    
    def route_request(self, service, path, method, data):
        """Route and process request"""
        
        # Extract auth
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '')
        
        # 1. AUTHENTICATE
        if not self.authenticate(token):
            return jsonify({"error": "Unauthorized"}), 401
        
        # 2. RATE LIMIT
        user_id = token.split('-')[0]  # Simplified user extraction
        if not self.rate_limit(user_id):
            return jsonify({"error": "Rate limit exceeded"}), 429
        
        # 3. CHECK CACHE
        cache_key = self.get_cache_key(method, path, str(request.args))
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            return jsonify(cached_data), 200
        
        # 4. ROUTE TO SERVICE
        if service not in self.services:
            return jsonify({"error": "Service not found"}), 404
        
        service_config = self.services[service]
        backend_url = f"{service_config['url']}/{path}"
        
        # 5. FORWARD REQUEST
        start = time.time()
        try:
            response = requests.request(
                method=method,
                url=backend_url,
                json=data,
                params=request.args,
                headers={
                    'X-User-ID': user_id,
                    'X-Request-ID': request.headers.get('X-Request-ID', 'unknown'),
                    'X-Forwarded-For': request.remote_addr,
                    'X-Forwarded-Proto': 'https'
                },
                timeout=service_config['timeout']
            )
            
            latency = time.time() - start
            response_data = response.json()
            
            # 6. CACHE RESPONSE
            if self.should_cache(method, path):
                self.cache[cache_key] = response_data
            
            # 7. LOG REQUEST
            self.log_request(user_id, method, path, response.status_code, latency)
            
            return jsonify(response_data), response.status_code
        
        except requests.Timeout:
            self.log_request(user_id, method, path, 504, time.time() - start)
            return jsonify({"error": "Service timeout"}), 504
        
        except Exception as e:
            self.log_request(user_id, method, path, 503, time.time() - start)
            return jsonify({"error": "Service unavailable"}), 503

gateway = ProductionAPIGateway()

@app.route('/api/<service>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def gateway(service, path):
    """API Gateway endpoint"""
    return gateway.route_request(
        service,
        path,
        request.method,
        request.get_json()
    )

# Benefits:
# ✅ Centralized authentication
# ✅ Rate limiting
# ✅ Request caching
# ✅ Routing to services
# ✅ Request logging
# ✅ Error handling
```

---

## 💡 Mini Project: "Build an API Gateway"

### Phase 1: Basic Routing ⭐

**Requirements:**
- Route requests to backends
- Basic authentication
- Simple logging
- Error handling

---

### Phase 2: Advanced Features ⭐⭐

**Requirements:**
- Rate limiting
- Request caching
- Header transformation
- Health checks
- Monitoring

---

### Phase 3: Production (HA, Scaling) ⭐⭐⭐

**Requirements:**
- Multiple gateway instances
- Request aggregation
- Canary deployments
- Load balancing
- Distributed rate limiting

---

## ⚖️ API Gateway Solutions Comparison

| Solution | Type | Cost | Setup | Features |
|----------|------|------|-------|----------|
| **Kong** | Open source | Low | Medium | Very complete |
| **AWS API Gateway** | Managed | Medium | Very Low | AWS ecosystem |
| **Nginx** | Open source | Low | Medium | Powerful, minimal |
| **Traefik** | Open source | Low | Low | Cloud native |
| **Tyk** | Open source/SaaS | Low/Medium | Low | Developer-friendly |

---

## 🎯 When to Use API Gateway

```
✅ USE WHEN:
- Multiple microservices
- External APIs needed
- Auth centralization desired
- Rate limiting required
- Monitoring/logging needed
- API versioning needed
- Request transformation needed

❌ LESS CRITICAL WHEN:
- Single monolithic app
- Internal APIs only
- Simple architecture
- No auth requirements
```

---

## ❌ Common Mistakes

### Mistake 1: Single Point of Failure

```python
# ❌ Single gateway
Internet → API Gateway → Services
             (if down: all fail!)

# ✅ Load-balanced gateways
Internet → Load Balancer
           ├→ API Gateway 1
           ├→ API Gateway 2
           ├→ API Gateway 3
           → Services
```

### Mistake 2: Gateway Too Smart

```python
# ❌ Gateway does everything
# - Authentication
# - Authorization
# - Business logic
# - Data transformation
# Gateway becomes bottleneck!

# ✅ Gateway does infrastructure
# - Auth (standard JWT, OAuth)
# - Rate limiting
# - Routing
# - Logging
# Services do business logic
```

### Mistake 3: No Caching

```python
# ❌ Every request hits backend
# Unnecessary load on services

# ✅ Cache common requests
# GET /api/users/123 (cacheable)
# POST /api/orders (not cacheable)
# Reduce backend load
```

---

## 📚 Additional Resources

**API Gateway Platforms:**
- [Kong](https://konghq.com/)
- [AWS API Gateway](https://aws.amazon.com/api-gateway/)
- [Nginx](https://www.nginx.com/)
- [Traefik](https://traefik.io/)

**Learning:**
- [API Gateway Pattern](https://microservices.io/patterns/apigateway.html)
- [API Gateway Design](https://aws.amazon.com/blogs/compute/api-gateway-best-practices/)

---

## 🎯 Before You Leave

**Can you answer these?**

1. **What's the main purpose of an API gateway?**
   - Answer: Centralize API management (auth, routing, rate limiting)

2. **Why are gateways stateless?**
   - Answer: Can scale horizontally behind load balancer

3. **What are common gateway responsibilities?**
   - Answer: Auth, rate limiting, routing, caching, logging

4. **What's path-based routing?**
   - Answer: Route based on URL path (/api/users → User Service)

5. **When should you NOT use a gateway?**
   - Answer: Simple monolith, no external APIs, no cross-cutting concerns

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **DevOps:** "Add an API gateway."
>
> **Developer:** "But we only have 3 services."
>
> **DevOps:** "Now you have 4."
>
> **Developer:** "That didn't help."
>
> **DevOps:** "Wait till you have 20 services."
>
> **Developer (later):** "Why didn't we add this sooner?" 🤦

---

[← Back to Main](../README.md) | [Previous: Rate Limiting](22-rate-limiting.md) | [Service Discovery](24-service-discovery.md)

---

**Last Updated:** November 11, 2025  
**Difficulty:** ⭐⭐⭐ Intermediate-Advanced (microservices)  
**Time to Read:** 25 minutes  
**Time to Build Gateway:** 4-7 hours per phase  

---

*API Gateways: The best business decision you make before your architecture becomes chaos.* 🚀