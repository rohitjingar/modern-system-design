# 18. Reverse Proxy (Nginx, HAProxy)

A reverse proxy is a server that pretends to be your server so your real server can hide in the shadows like a hermit crab. You talk to the proxy, it talks to the real server. Everyone's happy except when the proxy crashes, then everything's chaos. 🦞

[← Back to Main](../README.md) | [Previous: Load Balancers](17-load-balancers.md) | [Next: Message Queues →](19-message-queues.md)

---

## 🎯 Quick Summary

**Reverse Proxies** sit between clients and backend servers, appearing as the server to clients. They handle SSL termination, compression, caching, URL rewriting, and more. Nginx and HAProxy are industry standard. They're lighter than load balancers (different purpose) and essential for production systems. Every major website uses them: Netflix, Google, Amazon all use Nginx.

Think of it as: **Reverse Proxy = Shield & Helper for Your Server**

---

## 🌟 Beginner Explanation

### Forward Proxy vs Reverse Proxy

**FORWARD PROXY (VPN/Proxy):**

```
Client uses forward proxy to reach external server

Client → Forward Proxy → External Server

Example: VPN
├─ Your IP hidden (proxy IP shown)
├─ Access blocked websites
├─ Company monitors traffic

Used by: Clients wanting privacy/access
```

**REVERSE PROXY:**

```
External client connects through reverse proxy to server

Client → Reverse Proxy → Your Backend Server

Example: Nginx in front of Apache
├─ Client thinks it's talking to server
├─ Server stays hidden
├─ Proxy handles SSL, caching, etc

Used by: Servers needing protection/performance
```

### What Reverse Proxy Does

```
WITHOUT REVERSE PROXY:

Client
  ↓ (port 443, HTTP/2, TLS 1.3)
  ↓ (must negotiate SSL)
  ↓ (compression needed)
Backend Server
  ├─ Decrypt HTTPS
  ├─ Handle compression
  ├─ Serve request
  └─ Encrypt response (slow!)

Problems:
❌ Backend handles SSL (CPU intensive)
❌ Compression overhead
❌ Cache misses (everything fresh)
❌ No protection (DDoS hits server directly)
```

**WITH REVERSE PROXY:**

```
Client
  ↓ (port 443, HTTP/2, TLS 1.3)
  ↓ (proxy handles SSL)
Nginx Reverse Proxy
  ├─ Terminate SSL (move decryption here)
  ├─ Compress response (if needed)
  ├─ Cache common responses
  ├─ Handle DDoS
  ├─ Rewrite URLs
  └─ Forward to backend (HTTP, unencrypted, internal)
Backend Server
  ├─ Receive HTTP (no SSL overhead)
  ├─ Serve request
  └─ Send response (simple HTTP)

Benefits:
✅ Backend CPU freed (no SSL)
✅ Compression handled at edge
✅ Caching at proxy
✅ DDoS protection
✅ Hidden backend (security)
```

### Proxy vs Load Balancer

```
LOAD BALANCER:
├─ Routes across MULTIPLE servers
├─ Only cares about distribution
├─ Doesn't process request
├─ Example: Send to backend1 or backend2

REVERSE PROXY:
├─ Can route across multiple servers OR single server
├─ Processes the request (decrypt, compress, cache)
├─ Modifies headers, rewrites URLs
├─ Example: Decrypt, cache, modify, then forward

Relationship:
└─ Often used TOGETHER
   LB in front (picks server)
   Reverse proxy on each server (process request)
```

---

## 🔬 Advanced Explanation

### Reverse Proxy Capabilities

**SSL/TLS TERMINATION:**

```
PROBLEM: SSL decryption is CPU-intensive

Request from client:
GET /api/users HTTP/1.1
(encrypted with TLS 1.3, AES-256-GCM)

Backend must:
1. Decrypt payload (CPU: 10ms)
2. Parse request
3. Process
4. Encrypt response (CPU: 10ms)

SOLUTION: Terminate SSL at proxy

Client → Nginx (decrypt here) → Backend (HTTP, no SSL)

Benefits:
✅ Backend can be simple HTTP (faster)
✅ Proxy handles SSL (optimize once, not per request)
✅ Backend CPU freed (20% improvement!)
✅ Easy SSL updates (change proxy, not all servers)
```

**COMPRESSION:**

```
PROBLEM: Large responses waste bandwidth

Backend generates 1MB HTML
Client is on mobile (slow network)

SOLUTION: Proxy compresses

Backend → Nginx (compresses: 1MB → 100KB)
          ↓
Client receives 100KB (10x reduction!)
Browser decompresses to 1MB

Gzip compression:
├─ HTML: 80% reduction
├─ JSON: 60% reduction
├─ Images: No compression (already compressed)

Nginx decides:
├─ Only compress > 1KB responses
├─ Skip images/video (waste CPU)
├─ Gzip level 6 (balance CPU vs compression)
```

**CACHING:**

```
REQUEST 1:
Client → Nginx (cache miss)
         → Backend (slow, 200ms)
         → Nginx (cache response)
         → Client

Time: 200ms + network latency

REQUEST 2 (same URL, within TTL):
Client → Nginx (cache hit!)
         → Client

Time: 10ms + network latency

Nginx decides:
├─ Cache GET requests? YES
├─ Cache POST requests? NO (state change)
├─ Cache headers: Cache-Control: max-age=3600
├─ TTL: If header says cache 1 hour, do it
└─ If no header: Use default policy
```

**URL REWRITING:**

```
INCOMING REQUEST:
GET /api/v1/users HTTP/1.1

Nginx rule:
if ($uri ~ ^/api/v1/(.*)) {
  set $backend_path /api/$1;
}

FORWARDED TO BACKEND:
GET /api/users HTTP/1.1

Benefit: Decouple frontend URL from backend URL
```

**HEADER MANIPULATION:**

```
INCOMING REQUEST:
GET /api/users HTTP/1.1
User-Agent: Chrome
X-Real-IP: unknown

Nginx adds/modifies:
├─ X-Real-IP: 203.0.113.45 (client's real IP)
├─ X-Forwarded-For: 203.0.113.45
├─ X-Forwarded-Proto: https
├─ X-Forwarded-Host: example.com

FORWARDED TO BACKEND:
GET /api/users HTTP/1.1
User-Agent: Chrome
X-Real-IP: 203.0.113.45 ← Added by proxy!
X-Forwarded-For: 203.0.113.45
X-Forwarded-Proto: https
X-Forwarded-Host: example.com

Backend knows:
└─ Client's real IP (not proxy IP)
└─ Original protocol & host
```

**RATE LIMITING:**

```
PROBLEM: Client sends 1000 requests/second

SOLUTION: Nginx rate limits

limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

Effect:
├─ Request 1-10: Allowed
├─ Request 11: 429 Too Many Requests (rate limited!)
├─ Request 12-20: Queued (wait)
└─ After 1 second: Process more

Protects backend from:
├─ Aggressive clients
├─ Bot attacks
├─ Resource exhaustion
```

### Nginx vs HAProxy

```
NGINX:
├─ Web server + reverse proxy + LB
├─ Very fast (async, low memory)
├─ Easier config
├─ Popular (everyone uses it)
├─ Community support huge
├─ Good for HTTP(S)
└─ Examples: Netflix, Dropbox, WordPress

HAProxy:
├─ Load balancer + reverse proxy
├─ Lower latency (dedicated LB)
├─ Advanced health checks
├─ Better for high-concurrency
├─ Steeper learning curve
├─ Good for both L4 and L7
└─ Examples: GitHub, Airbnb, Reddit
```

### Connection Pooling

```
PROBLEM: Create new connection per request (slow)

Request 1:
Client → LB → Nginx → Backend1
          └─ Create TCP connection (3-way handshake: 10ms)
          └─ Send request
          └─ Close connection

Request 2 (different backend):
Client → LB → Nginx → Backend2
          └─ Create TCP connection (10ms again!)
          └─ Send request
          └─ Close connection

Total: 20ms just for connections!

SOLUTION: Connection pooling

Nginx maintains pool:
├─ Backend1: 10 connections (keep-alive)
├─ Backend2: 10 connections (keep-alive)
├─ Backend3: 10 connections (keep-alive)

Request 1 → Reuse Backend1 connection (1ms)
Request 2 → Reuse Backend2 connection (1ms)
Request 3 → Reuse Backend1 connection (1ms)

Benefit:
✅ No handshake overhead
✅ ~10x faster backend connections
✅ Lower latency
```

---

## 🐍 Python Code Example

### ❌ Without Reverse Proxy (Backend Exposed)

```python
# ===== WITHOUT REVERSE PROXY =====

from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import os

class DirectBackendHandler(BaseHTTPRequestHandler):
    """Backend exposed directly to internet"""
    
    def do_GET(self):
        """Handle request"""
        # Backend must handle SSL decryption (slow!)
        # Backend must handle compression (overhead!)
        # Backend must handle all requests (not specialized)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        
        # Large response (for compression demo)
        response = "<html><body>" + "x" * 100000 + "</body></html>"
        
        self.end_headers()
        self.wfile.write(response.encode())

# Setup SSL (on backend directly - CPU intensive!)
# context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# context.load_cert_chain('cert.pem', 'key.pem')
# server = HTTPServer(('0.0.0.0', 443), DirectBackendHandler, ssl_context=context)

# Problems:
# ❌ Backend handles SSL (CPU hot)
# ❌ No compression
# ❌ No caching
# ❌ Exposed to DDoS
# ❌ No URL rewriting
# ❌ Hard to upgrade (SSL config on backend)
```

### ✅ Simple Reverse Proxy (Python)

```python
# ===== SIMPLE REVERSE PROXY =====

import socket
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
from urllib.parse import urljoin

class SimpleReverseProxyHandler(BaseHTTPRequestHandler):
    """Simple reverse proxy implementation"""
    
    BACKEND_URL = 'http://localhost:8001'  # Internal backend
    
    def do_GET(self):
        """Handle GET requests"""
        # Construct backend URL
        full_backend_url = urljoin(self.BACKEND_URL, self.path)
        
        try:
            # Forward request to backend
            req = urllib.request.Request(
                full_backend_url,
                headers={'User-Agent': 'ReverseProxy/1.0'}
            )
            
            with urllib.request.urlopen(req) as response:
                status = response.status
                headers = dict(response.headers)
                body = response.read()
            
            # Send response back to client
            self.send_response(status)
            
            # Forward headers (except hop-by-hop)
            for key, value in headers.items():
                if key.lower() not in ['connection', 'transfer-encoding']:
                    self.send_header(key, value)
            
            self.end_headers()
            self.wfile.write(body)
        
        except Exception as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(b'Bad Gateway')
    
    def log_message(self, format, *args):
        pass  # Suppress logs

# Usage
print("=== SIMPLE REVERSE PROXY ===\n")
print("Proxy listening on port 8000")
print("Forwarding to backend on port 8001")

# Start proxy
# server = HTTPServer(('0.0.0.0', 8000), SimpleReverseProxyHandler)
# server.serve_forever()
```

### ✅ Production Reverse Proxy (Features)

```python
# ===== PRODUCTION REVERSE PROXY =====

import urllib.request
import urllib.error
import gzip
import hashlib
from io import BytesIO
from urllib.parse import urljoin, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta
import time

class ProductionReverseProxy:
    """Production-grade reverse proxy features"""
    
    def __init__(self):
        self.backend_url = 'http://localhost:8001'
        self.cache = {}  # Simple in-memory cache
        self.rate_limit = {}  # IP → request count
        self.rate_limit_threshold = 100  # requests per minute
    
    def should_cache(self, method, headers, status):
        """Decide if response should be cached"""
        
        # Only cache GET requests
        if method != 'GET':
            return False
        
        # Only cache successful responses
        if status != 200:
            return False
        
        # Check Cache-Control header
        cache_control = headers.get('Cache-Control', '')
        if 'no-cache' in cache_control or 'no-store' in cache_control:
            return False
        
        return True
    
    def get_cache_ttl(self, headers):
        """Extract TTL from Cache-Control header"""
        cache_control = headers.get('Cache-Control', '')
        
        if 'max-age=' in cache_control:
            max_age = int(cache_control.split('max-age=')[1].split(',')[0])
            return max_age
        
        return 300  # Default 5 minutes
    
    def compress_response(self, body, encoding='gzip'):
        """Compress response"""
        
        # Don't compress small responses
        if len(body) < 1000:
            return body, None
        
        if encoding == 'gzip':
            compressed = BytesIO()
            with gzip.GzipFile(fileobj=compressed, mode='wb') as gz:
                gz.write(body)
            return compressed.getvalue(), 'gzip'
        
        return body, None
    
    def rate_limit_check(self, client_ip):
        """Check if client is rate limited"""
        
        now = time.time()
        key = client_ip
        
        # Clean old entries
        if key in self.rate_limit:
            timestamp, count = self.rate_limit[key]
            
            # If over 1 minute old, reset
            if now - timestamp > 60:
                self.rate_limit[key] = (now, 0)
            else:
                # Check if exceeded
                if count >= self.rate_limit_threshold:
                    return True
                
                # Increment count
                self.rate_limit[key] = (timestamp, count + 1)
        else:
            # First request from this IP
            self.rate_limit[key] = (now, 1)
        
        return False
    
    def rewrite_headers(self, original_headers, client_ip, protocol, host):
        """Add/modify headers for backend"""
        
        modified = dict(original_headers)
        
        # Add client information
        modified['X-Real-IP'] = client_ip
        modified['X-Forwarded-For'] = client_ip
        modified['X-Forwarded-Proto'] = protocol
        modified['X-Forwarded-Host'] = host
        
        return modified
    
    def forward_request(self, method, path, headers, body, client_ip):
        """Forward request to backend with all optimizations"""
        
        # Rate limiting
        if self.rate_limit_check(client_ip):
            return {
                'status': 429,
                'body': b'Too Many Requests',
                'headers': {}
            }
        
        # Cache lookup
        cache_key = f"{method}:{path}"
        if cache_key in self.cache:
            cached_data, exp_time = self.cache[cache_key]
            if time.time() < exp_time:
                return {
                    'status': 200,
                    'body': cached_data,
                    'headers': {'X-Cache': 'HIT'}
                }
            else:
                del self.cache[cache_key]
        
        # Build backend request
        full_url = urljoin(self.backend_url, path)
        parsed = urlparse(full_url)
        
        # Rewrite headers
        rewritten_headers = self.rewrite_headers(
            headers, client_ip, 'https', parsed.hostname
        )
        
        try:
            # Make request
            req = urllib.request.Request(
                full_url,
                data=body,
                headers=rewritten_headers,
                method=method
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                status = response.status
                resp_headers = dict(response.headers)
                resp_body = response.read()
            
            # Compression
            body_to_send, encoding = self.compress_response(resp_body)
            if encoding:
                resp_headers['Content-Encoding'] = encoding
            
            # Cache if appropriate
            if self.should_cache(method, resp_headers, status):
                ttl = self.get_cache_ttl(resp_headers)
                self.cache[cache_key] = (body_to_send, time.time() + ttl)
                resp_headers['X-Cache'] = 'MISS'
            
            return {
                'status': status,
                'body': body_to_send,
                'headers': resp_headers
            }
        
        except urllib.error.HTTPError as e:
            return {
                'status': e.code,
                'body': b'Gateway Error',
                'headers': {}
            }
        except Exception as e:
            return {
                'status': 502,
                'body': b'Bad Gateway',
                'headers': {}
            }

# Usage
proxy = ProductionReverseProxy()

# Simulate request
result = proxy.forward_request(
    method='GET',
    path='/api/users',
    headers={'User-Agent': 'Client/1.0'},
    body=None,
    client_ip='203.0.113.45'
)

print(f"Status: {result['status']}")
print(f"Headers: {result['headers']}")
print(f"Body size: {len(result['body'])} bytes")
```

---

## 💡 Mini Project: "Build a Reverse Proxy"

### Phase 1: Simple Forwarding ⭐

**Requirements:**
- Accept connections on port 8000
- Forward to backend on port 8001
- Pass headers through
- Return responses

---

### Phase 2: With Features ⭐⭐

**Requirements:**
- SSL termination (HTTPS)
- Compression
- Caching
- Rate limiting
- Header rewriting

---

### Phase 3: Production (HA, Monitoring) ⭐⭐⭐

**Requirements:**
- Multiple backends
- Health checks
- Connection pooling
- Metrics/monitoring
- Graceful shutdown

---

## ⚖️ Common Reverse Proxy Tasks

| Task | How |
|------|-----|
| **SSL Termination** | Proxy handles HTTPS, backend HTTP |
| **Compression** | Gzip responses before sending |
| **Caching** | Store common responses |
| **Rate Limiting** | Limit requests per client |
| **URL Rewriting** | Change path before forwarding |
| **Load Balancing** | Distribute across backends |
| **Header Injection** | Add X-Real-IP, etc |
| **Request Logging** | Log all requests |

---

## ❌ Common Mistakes

### Mistake 1: No Connection Pooling

```
# ❌ New connection per request
# Handshake overhead: 10ms × 1000 requests = 10 seconds!

# ✅ Pool connections
# Reuse connections: 1ms × 1000 requests = 1 second
# 10x improvement!
```

### Mistake 2: Caching POST Requests

```python
# ❌ Cache POST (state change!)
cache[url] = response

# POST /transfer (transfer $100)
# POST /transfer (cached response! "already transferred")
# User confused: transferred twice?

# ✅ Only cache safe methods (GET, HEAD)
if method in ['GET', 'HEAD']:
    cache[url] = response
```

### Mistake 3: Missing Hop-by-Hop Headers

```python
# ❌ Forward all headers
for key, value in headers.items():
    send_header(key, value)

# Some headers break proxying:
# - Connection
# - Transfer-Encoding
# - Upgrade

# ✅ Skip hop-by-hop headers
skip_headers = {'connection', 'transfer-encoding', 'upgrade'}
for key, value in headers.items():
    if key.lower() not in skip_headers:
        send_header(key, value)
```

# 🗺️ **1. Where are Instagram’s Backend Data Centers? (Exact Locations)**

Instagram (Meta) runs its **backend microservices** in **large Meta-owned data centers**, not in PoPs.

For Asia (including India) the backend is mostly in:

### ✔ **Singapore Data Center (Primary for Asia)**

* This is where your feed is generated
* Where ML ranking happens
* Where your profile data lives
* Where images/videos metadata is stored

### ✔ **US Data Centers (Backup / Additional capacity)**

* Prineville, Oregon
* Altoona, Iowa
* Forest City, North Carolina
* Luleå, Sweden (Meta European DC)

Your traffic *from India* usually hits:

👉 **India PoP → Singapore Backend → India PoP → You**

Only some rare cases go to **US**.

---

# 🧩 **2. What’s Inside These Backend Data Centers?**

These are **massive** buildings with:

* Hundreds of thousands of servers
* Storage servers
* ML GPU clusters
* Microservices clusters
* Redis / Memcache clusters
* Kafka streams
* Internal routing fabric
* Internal LB systems

Think of it like a **city of servers**.

This is where the actual **backend code runs**.

---

# 🏗️ **3. Where is Instagram backend CODE hosted?**

Instagram backend is built primarily using:

* **Python (Django legacy)**
* **Hack/PHP (Meta’s HHVM platform)**
* **C++ for critical services**
* **Java, Go, Rust for some microservices**

This code runs on:

### ✔ Containers (similar to Docker)

### ✔ Orchestration (similar to Kubernetes but Meta built its own)

### ✔ Thousands of servers grouped into clusters

Each microservice runs on **hundreds of servers**.

Example:

```
Feed Service → 500 servers
Stories Service → 300 servers
DM Service → 400 servers
Media Service → 1000 servers
Ads Service → 1000+ servers
Notification Service → 200 servers
User Profile Service → 150 servers
```

---

# 🎨 **4. Where is Instagram Frontend CODE hosted?**

Instagram has 2 frontends:

## **A) Mobile Apps (Android/iOS)**

The frontend code is inside the mobile app binary, downloaded from:

* Google Play Store
* Apple App Store

When you open the Instagram app, all UI code already exists on your phone.

UI code → calls backend APIs.

---

## **B) Instagram Web (instagram.com)**

These static files are hosted on:

### ✔ CDNs (Meta Global CDN)

* HTML
* CSS
* JS
* Images
* Static assets

CDNs are placed globally in many cities (including India PoPs).

CDN = super fast static content delivery.

---

# 🔄 **5. How do backend microservices talk to each other?**

Inside the Singapore data center, microservices communicate using:

### ✔ **Thrift RPC** (Meta’s internal gRPC-like system)

### ✔ **Service Mesh**

### ✔ **Load Balancers**

### ✔ **Memcache / Redis**

### ✔ **Kafka Streams**

### ✔ **Internal TCP LBs**

A single request to `/feed/timeline` causes:

```
Feed Service
  → Ranking Service
  → Graph Service
  → User Service
  → Media Service
  → Ads Service
  → Stories Service
  → Cache Service
  → Notifications Service
```

10–20 microservice calls (minimum) happen to build your feed.

---

# 🔁 **6. COMPLETE FLOW: From Your Phone → Backend → Back to You**

Let’s stitch it all together.

---

## **STEP 1: You open Instagram (India)**

Your app calls:

```
GET https://i.instagram.com/api/v1/feed/timeline/
```

---

## **STEP 2: DNS → You get the IP of nearest Instagram PoP**

Likely **Mumbai**.

---

## **STEP 3: Request hits L4 Load Balancer (Mumbai PoP)**

* Handles TCP
* Spreads load
* Sends to L7

---

## **STEP 4: Request hits L7 Reverse Proxy (Mumbai PoP)**

This is where Instagram *first* understands your HTTP request.

L7 does:

* SSL/TLS decryption
* Reads URL `/feed/timeline`
* Reads headers
* Rate limits
* Authentication verification
* Routing logic

Then it routes the request to…

---

## **STEP 5: L7 forwards request to Singapore Data Center**

Why Singapore?
Close to India + Meta’s main Asia DC.

---

## **STEP 6: Inside Singapore DC → Feed Microservice handles your request**

Feed service does:

* Rank your posts
* Mix ads
* Fetch stories preview
* Check user relationships
* ML predictions
* Build the final feed list
* Talk to many other microservices

This is where the **real backend work** happens.

---

## **STEP 7: Back-end generates the response**

something like:

```json
{
  "items": [...],
  "stories": [...],
  "ads": [...],
  "suggestions": [...]
}
```

---

## **STEP 8: Response goes back**

```
Feed Service → Reverse Proxy (Singapore) → PoP Reverse Proxy (Mumbai) → You
```

Reverse proxy compresses it (gzip/br), adds cache headers, etc.

---

## **STEP 9: Your app receives JSON → renders the UI**

The images/videos are loaded from **CDN servers** in PoPs.

Done.

---

# 🧠 **7. Where is EVERYTHING hosted?**

### ✔ Frontend app

→ YOUR PHONE (Android/iOS)

### ✔ Web frontend

→ Meta Global CDN (including India PoPs)

### ✔ L4 load balancers

→ India PoPs (Mumbai, Chennai, Hyderabad)

### ✔ L7 load balancers / Reverse proxy

→ India PoPs

### ✔ Backend microservices

→ Singapore + US data centers

### ✔ Data storage (DB, media metadata)

→ Singapore + US DCs

### ✔ Image/video files

→ Distributed storage + edge caches in PoPs

---

# 🎯 **8. Interview-ready explanation (simple but impressive)**

*Use this in system design interviews:*

> “Instagram uses global PoPs near users (like Mumbai) with L4 and L7 load balancers.
> Your mobile app sends requests to the PoP L7, which terminates SSL, performs routing, caching, security checks, and then forwards the request to backend microservices running in Meta’s Singapore and US data centers.
> These microservices communicate internally using RPC, caches, and service mesh.
> The feed is built in the backend and returned through the reverse proxy and L4 back to the user.
> Static assets come from CDN caches in PoPs, while the backend logic happens in large central data centers.”

This answer sounds EXACTLY like a backend engineer at Meta.


---

## 📚 Additional Resources

**Nginx:**
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Nginx as Reverse Proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [Nginx Configuration Best Practices](https://www.nginx.com/resources/wiki/)

**HAProxy:**
- [HAProxy Documentation](http://www.haproxy.org/)
- [HAProxy Configuration](https://www.haproxy.com/documentation)


---

## 🎯 Before You Leave

**Can you answer these?**

1. **What's a reverse proxy?**
   - Answer: Server that forwards requests to backend servers

2. **Why use SSL termination?**
   - Answer: Move encryption overhead from backend to proxy

3. **What's connection pooling?**
   - Answer: Reuse connections to avoid handshake overhead

4. **Why compress responses?**
   - Answer: Reduce bandwidth usage (80% for HTML)

5. **Why not cache POST requests?**
   - Answer: POST modifies state, can't cache state changes

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **Developer:** "My backend is slow!"
>
> **DevOps:** "Add a reverse proxy."
>
> **Developer:** "Won't that add overhead?"
>
> **DevOps:** "It'll be 10x faster because it handles SSL."
>
> **Developer:** *measures* "Wow, actually 10x faster!"
>
> **DevOps:** "Reverse proxies are magic." ✨

---

[← Back to Main](../README.md) | [Previous: Load Balancers](17-load-balancers.md) | [Next: Message Queues →](19-message-queues.md)

---

**Last Updated:** November 10, 2025  
**Difficulty:** ⭐⭐⭐ Intermediate-Advanced (infrastructure)  
**Time to Read:** 25 minutes  
**Time to Build Proxy:** 4-6 hours per phase  

---

*Reverse proxies: Making backends look fast by doing the hard work themselves.* 🚀