# 17. Load Balancers (L4, L7)

Load balancers are like bouncers at a nightclub: they stand at the door and decide which server gets the next customer. When they're working, no one notices. When they fail, everyone complains about the line wrapping around the block. 🚪

[← Back to Main](../README.md) | [Previous: File Storage](16-file-storage.md) | [Reverse Proxy (Nginx, HAProxy)](18-reverse-proxy.md)

---

## 🎯 Quick Summary

**Load Balancers** distribute incoming traffic across multiple backend servers to prevent any single server from being overwhelmed. They work at different layers: Layer 4 (TCP/UDP, fast) for raw traffic, Layer 7 (HTTP, smart) for application-aware routing. Popular options: Nginx, HAProxy, AWS ELB, Azure Load Balancer. They're essential for scaling: they multiply your capacity and provide failover.

Think of it as: **Load Balancer = Traffic Cop for Your Servers**

---

## 🌟 Beginner Explanation

### Without Load Balancer (Single Server)

```
┌─────────────────────┐
│   Single Server     │
│  (Handles all requests)
└─────────────────────┘
   ↑     ↑     ↑     ↑
 User1 User2 User3 User4

Problems:
❌ Server gets 100% of load
❌ If server crashes: ALL users down
❌ Can't scale (still one server)
❌ Server CPU at 100%
❌ Slow for everyone (queued requests)

Scenario: Traffic spike
└─ Server crashes
└─ Website down
└─ Users angry 😡
```

### With Load Balancer (Multiple Servers)

```
                ┌─────────────────────┐
                │  LOAD BALANCER      │
                │  (Traffic Cop)      │
                └─────────────────────┘
                 ↑     ↑     ↑     ↑
              User1  User2  User3  User4
                 ↓     ↓     ↓     ↓
        ┌────────┴─────┬─────┴────────┐
        ↓              ↓              ↓
    ┌────────┐    ┌────────┐    ┌────────┐
    │Server 1│    │Server 2│    │Server 3│
    │(25%)   │    │(25%)   │    │(25%)   │
    └────────┘    └────────┘    └────────┘

Traffic distributed:
├─ User1 → Server 1
├─ User2 → Server 2
├─ User3 → Server 3
├─ User4 → Server 1 (round-robin)

Benefits:
✅ Each server handles 25% of load
✅ If Server 1 dies: Users routed to 2,3
✅ Can scale horizontally (add servers)
✅ Faster response (less queuing)
✅ High availability
```

### Load Balancer Algorithms

```
ROUND-ROBIN:
Request 1 → Server 1
Request 2 → Server 2
Request 3 → Server 3
Request 4 → Server 1 (loop back)

Simple, fair distribution
Problem: Doesn't account for server capacity

LEAST CONNECTIONS:
Server 1: 10 active connections
Server 2: 5 active connections ← send next request here
Server 3: 8 active connections

Smarter: Send to least busy server

WEIGHTED:
Server 1: capacity 100, weight 2
Server 2: capacity 50, weight 1

Send 2 requests to Server 1 for every 1 to Server 2
Useful: Different server sizes

IP HASH:
Hash of client IP determines server
Same client always hits same server
Useful: Session affinity (but problematic!)
```

---

## 🔬 Advanced Explanation

### OSI Layer Overview

```
APPLICATION LAYER (Layer 7):
├─ HTTP, HTTPS, DNS
├─ Can read/understand application data
├─ Routes based on URL, hostname, headers
├─ Examples: Nginx, HAProxy, AWS ALB

TRANSPORT LAYER (Layer 4):
├─ TCP, UDP
├─ Can't read application data
├─ Routes based on IP/port only
├─ Very fast (hardware-based)
├─ Examples: AWS NLB, F5 BigIP
```

### Layer 4 (L4) Load Balancer

```
TCP/UDP LEVEL:

Input:
├─ Client IP: 192.168.1.100:12345
├─ Destination IP: 10.0.0.1:80
└─ Protocol: TCP

Load Balancer:
├─ Looks at: source IP, dest IP, port
├─ Decides: which backend server?
├─ Forwards packet

Output:
├─ Client packet to Backend Server 1:9001
└─ Maintains connection mapping

Pros:
✅ Ultra-fast (hardware acceleration)
✅ Handles millions of connections
✅ Protocol agnostic (works with any protocol)

Cons:
❌ No application-level logic
❌ Can't inspect HTTP headers
❌ Can't route by URL
```

**L4 Routing Decision:**

```
┌──────────────┐
│ L4 Load LB   │
│              │
│ Client IP    │
│ Dest IP      │
│ Port         │ → Hash/match to backend
│              │
└──────────────┘

Example:
src_ip: 192.168.1.100
hash(192.168.1.100) % 3 = 1
└─ Send to Backend Server 1
```

### Layer 7 (L7) Load Balancer

```
HTTP/APPLICATION LEVEL:

Input:
GET /api/users HTTP/1.1
Host: api.example.com
User-Agent: Chrome
Authorization: Bearer token123
Content-Type: application/json

Load Balancer:
├─ Reads: URL path, hostname, headers, body
├─ Decides: which backend based on content?
├─ Forwards request

Routing options:
├─ GET /api/users → Backend 1
├─ GET /api/products → Backend 2
├─ POST /api/* → Backend 3
├─ Host: auth.example.com → Backend 4
└─ Header: "X-Premium: true" → Backend 5 (premium servers)

Pros:
✅ Intelligent routing
✅ Content-based routing
✅ URL-based routing
✅ Header-based routing
✅ Can rate limit per path

Cons:
❌ Must decrypt HTTPS
❌ More CPU intensive
❌ Slower than L4
❌ Only for HTTP(S)
```

**L7 Routing Decision:**

```
┌──────────────────────┐
│ L7 Load LB           │
│                      │
│ Reads entire request │
│ ├─ URL: /api/users   │
│ ├─ Host: api.ex.com  │
│ ├─ Headers           │
│ └─ Body              │
│                      │
│ Decision engine:     │
│ IF url == /api/users │
│   → Backend API-1    │
│ IF url == /images    │
│   → Backend Media-1  │
│ ELSE                 │
│   → Backend Default  │
└──────────────────────┘
```

### Health Checks

```
PROBLEM: Server crashes, LB still sends traffic

SOLUTION: Health checks

L4 Health Check:
├─ TCP ping to backend:9001
├─ If no response: Mark server down
├─ Stop sending traffic
├─ Try again periodically
├─ When healthy: Restore traffic

L7 Health Check:
├─ HTTP GET /healthz
├─ Expects 200 OK response
├─ If fails or slow: Mark down
├─ Check query params, headers, body
├─ Custom health logic possible

Example:

Server healthy:
GET /healthz → 200 OK ✅
└─ LB sends traffic

Server overloaded:
GET /healthz → 503 Service Unavailable
└─ LB stops sending traffic
└─ Routes to healthy servers

Server crashed:
Connection refused
└─ LB immediately stops traffic
```

### Session Affinity (Sticky Sessions)

```
PROBLEM: User logged into Server 1, session stored in memory

Request 1: → Server 1 (login, create session)
Request 2: → Server 2 (NO SESSION! User logged out!)

SOLUTION 1: Sticky Sessions (L4/L7)

All requests from same client → Same server
├─ Client IP hash → Server 1
├─ All requests → Server 1
└─ Session preserved

Problem: If Server 1 dies, all users from that IP logged out

SOLUTION 2: Shared Session Store

├─ All servers share Redis session cache
├─ User logs in: Session stored in Redis
├─ Request routed anywhere: Session fetched from Redis
└─ All servers access same session

Better solution! (if possible)
```

### Failover & Redundancy

```
SINGLE LB (Single Point of Failure):

┌──────────────┐
│  Load        │
│  Balancer    │ ← Crashes! All requests fail!
└──────────────┘

SOLUTION: HA (High Availability)

┌──────────────┐         ┌──────────────┐
│  LB Primary  │ ←─────→ │  LB Backup   │
│  (Active)    │  Heartbeat (Standby)   │
└──────────────┘         └──────────────┘

Primary fails:
├─ Backup detects failure
├─ Backup becomes active
├─ VIP (Virtual IP) now points to backup
├─ Traffic continues 💪

Used by: HAProxy, Nginx with keepalived, AWS multi-AZ
```

---

## 🐍 Python Code Example

### ❌ Without Load Balancer (Single Server)

```python
# ===== WITHOUT LOAD BALANCER =====

from http.server import HTTPServer, BaseHTTPRequestHandler
import time

class SingleServerHandler(BaseHTTPRequestHandler):
    """Single server handling all requests"""
    
    def do_GET(self):
        """Handle GET request"""
        # Simulate work
        time.sleep(0.1)  # 100ms to process
        
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Response from single server\n')
    
    def log_message(self, format, *args):
        pass  # Suppress logs

# Single server
print("=== WITHOUT LOAD BALANCER ===\n")
print("Single server at localhost:8000")
print("Send 10 sequential requests (takes ~1 second)")
print("If server crashes: ALL requests fail!")

# In practice:
# server = HTTPServer(('0.0.0.0', 8000), SingleServerHandler)
# server.serve_forever()
```

### ✅ Simple Load Balancer (Round-Robin)

```python
# ===== SIMPLE LOAD BALANCER =====

import socket
import threading
import time
from collections import deque

class SimpleLoadBalancer:
    """Simple L4 load balancer with round-robin"""
    
    def __init__(self, listen_port=8000):
        self.listen_port = listen_port
        self.backends = []
        self.current_index = 0
        self.backend_index = 0
    
    def add_backend(self, host, port):
        """Add backend server"""
        self.backends.append({
            'host': host,
            'port': port,
            'healthy': True,
            'connections': 0
        })
    
    def select_backend_round_robin(self):
        """Select backend using round-robin"""
        if not self.backends:
            return None
        
        # Find next healthy backend
        attempts = 0
        while attempts < len(self.backends):
            backend = self.backends[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.backends)
            
            if backend['healthy']:
                return backend
            
            attempts += 1
        
        return None
    
    def select_backend_least_connections(self):
        """Select backend with least connections"""
        if not self.backends:
            return None
        
        # Find healthy backend with least connections
        healthy = [b for b in self.backends if b['healthy']]
        if not healthy:
            return None
        
        return min(healthy, key=lambda b: b['connections'])
    
    def health_check(self):
        """Periodically check backend health"""
        while True:
            for backend in self.backends:
                try:
                    # Try to connect
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    sock.connect((backend['host'], backend['port']))
                    sock.close()
                    backend['healthy'] = True
                except:
                    backend['healthy'] = False
            
            time.sleep(5)  # Check every 5 seconds
    
    def get_stats(self):
        """Get load balancer statistics"""
        healthy = sum(1 for b in self.backends if b['healthy'])
        return {
            'total_backends': len(self.backends),
            'healthy': healthy,
            'unhealthy': len(self.backends) - healthy,
            'backends': self.backends
        }

# Usage
print("=== SIMPLE LOAD BALANCER ===\n")

lb = SimpleLoadBalancer(listen_port=8000)

# Add 3 backend servers
lb.add_backend('localhost', 8001)
lb.add_backend('localhost', 8002)
lb.add_backend('localhost', 8003)

# Start health checks
health_thread = threading.Thread(target=lb.health_check, daemon=True)
health_thread.start()

# Simulate request routing
print("Routing 10 requests:\n")
for i in range(10):
    backend = lb.select_backend_round_robin()
    if backend:
        print(f"Request {i+1} → {backend['host']}:{backend['port']}")
    else:
        print(f"Request {i+1} → No healthy backend!")

# Stats
stats = lb.get_stats()
print(f"\nStats: {stats['healthy']}/{stats['total_backends']} backends healthy")
```

### ✅ Production Load Balancer (L7 with Routing)

```python
# ===== PRODUCTION L7 LOAD BALANCER =====

import re
from dataclasses import dataclass
from typing import List, Dict, Callable

@dataclass
class Route:
    """Routing rule"""
    pattern: str  # URL pattern
    backend_group: str  # Backend group name
    priority: int = 0

class L7LoadBalancer:
    """Production-grade Layer 7 load balancer"""
    
    def __init__(self):
        self.backends: Dict[str, List[dict]] = {}
        self.routes: List[Route] = []
        self.current_backend_index: Dict[str, int] = {}
    
    def add_backend_group(self, group_name: str, backends: List[dict]):
        """Add group of backends"""
        self.backends[group_name] = backends
        self.current_backend_index[group_name] = 0
    
    def add_route(self, pattern: str, backend_group: str, priority: int = 0):
        """Add routing rule"""
        route = Route(pattern, backend_group, priority)
        self.routes.append(route)
        # Sort by priority
        self.routes.sort(key=lambda r: -r.priority)
    
    def select_backend(self, group_name: str) -> dict:
        """Select backend from group (round-robin)"""
        if group_name not in self.backends:
            return None
        
        backends = self.backends[group_name]
        if not backends:
            return None
        
        # Round-robin within group
        idx = self.current_backend_index.get(group_name, 0)
        backend = backends[idx]
        self.current_backend_index[group_name] = (idx + 1) % len(backends)
        
        return backend
    
    def route_request(self, method: str, path: str, host: str, 
                     headers: dict) -> dict:
        """Route request based on L7 criteria"""
        
        # Check routes in priority order
        for route in self.routes:
            # Pattern matching
            if re.match(route.pattern, path):
                backend = self.select_backend(route.backend_group)
                return {
                    'backend': backend,
                    'route': route.pattern,
                    'group': route.backend_group
                }
        
        # Default: if no routes matched, use 'default' group
        backend = self.select_backend('default')
        return {
            'backend': backend,
            'route': 'default',
            'group': 'default'
        }

# Usage
print("=== PRODUCTION L7 LOAD BALANCER ===\n")

lb = L7LoadBalancer()

# Define backend groups
api_backends = [
    {'host': 'api1.internal', 'port': 8001},
    {'host': 'api2.internal', 'port': 8001},
    {'host': 'api3.internal', 'port': 8001}
]

media_backends = [
    {'host': 'media1.internal', 'port': 8002},
    {'host': 'media2.internal', 'port': 8002}
]

default_backends = [
    {'host': 'default1.internal', 'port': 8003},
    {'host': 'default2.internal', 'port': 8003}
]

lb.add_backend_group('api', api_backends)
lb.add_backend_group('media', media_backends)
lb.add_backend_group('default', default_backends)

# Add routing rules (priority: higher first)
lb.add_route(r'^/api/.*', 'api', priority=10)
lb.add_route(r'^/media/.*', 'media', priority=10)
lb.add_route(r'^/static/.*', 'media', priority=9)

# Route some requests
test_requests = [
    ('GET', '/api/users', 'api.example.com', {}),
    ('GET', '/api/products', 'api.example.com', {}),
    ('GET', '/media/image.jpg', 'cdn.example.com', {}),
    ('GET', '/static/style.css', 'cdn.example.com', {}),
    ('GET', '/home', 'example.com', {}),
    ('GET', '/about', 'example.com', {}),
]

print("Request routing:\n")
for method, path, host, headers in test_requests:
    routing = lb.route_request(method, path, host, headers)
    backend = routing['backend']
    if backend:
        print(f"{method:4} {path:20} → {backend['host']}:{backend['port']} "
              f"(route: {routing['route']})")
    else:
        print(f"{method:4} {path:20} → No backend available!")

# Output shows intelligent routing based on URL path
```

---

## 💡 Mini Project: "Build a Load Balancer"

### Phase 1: Simple Round-Robin ⭐

**Requirements:**
- Accept connections on port 8000
- Route to multiple backends
- Round-robin algorithm
- Basic health checks
- No persistence

---

### Phase 2: Advanced (L7 Routing) ⭐⭐

**Requirements:**
- L7 routing based on URL
- Health checks
- Connection tracking
- Session affinity
- Statistics

---

### Phase 3: Enterprise (HA, Monitoring) ⭐⭐⭐

**Requirements:**
- High availability (dual LB)
- Advanced health checks
- Metrics/monitoring
- Rate limiting
- DDoS protection

---

## ⚖️ L4 vs L7 Comparison

| Feature | L4 | L7 |
|---------|----|----|
| **Speed** | Ultra-fast ⚡ | Slower |
| **Throughput** | Millions/sec | Hundreds/sec |
| **Content Awareness** | None | Full ✅ |
| **URL Routing** | ❌ | ✅ |
| **Header Routing** | ❌ | ✅ |
| **HTTPS Decrypt** | ❌ | Yes (overhead) |
| **Session Affinity** | Hard | Easy |
| **Use Case** | High-traffic, same backend | API, microservices |

---

## 🎯 When to Use Each

```
USE L4 WHEN:
✅ Ultra-high throughput needed
✅ Non-HTTP protocols (TCP, UDP)
✅ All traffic goes to same backends
✅ Gaming, messaging, video
✅ 10M+ RPS

USE L7 WHEN:
✅ Routing logic needed
✅ HTTP APIs
✅ Microservices
✅ Content-based routing
✅ Rate limiting needed
✅ Less than 1M RPS

USE BOTH (L4 + L7):
✅ L4 in front (initial distribution)
✅ L7 behind (application-aware)
✅ Best of both worlds
```

---

## ❌ Common Mistakes

### Mistake 1: Single Load Balancer

```python
# ❌ LB is single point of failure
┌──────────┐
│    LB    │ ← If this fails, all down!
└──────────┘

# ✅ HA Load Balancers
┌──────────┐  ┌──────────┐
│ LB (A)   │←→│ LB (B)   │ ← Automatic failover
└──────────┘  └──────────┘
```

### Mistake 2: No Health Checks

```python
# ❌ Send traffic to dead servers
# Server crashes
# LB still sends traffic
# Users see timeouts

# ✅ Active health checks
# Every 5 seconds: Can you respond?
# No? Remove from pool immediately
```

### Mistake 3: Poor Algorithm Choice

```python
# ❌ Round-robin with unequal servers
# Server 1 (64GB RAM): Gets 33% traffic
# Server 2 (8GB RAM): Gets 33% traffic
# Server 2 crashes under load!

# ✅ Use least-connections or weighted
# Server 1: 2x weight
# Server 2: 1x weight
# Proportional to capacity
```

# 🚀 **FINAL SUMMARY — L4 & L7 Load Balancers (Instagram Example)**


# 📌 **1. Why Load Balancers Exist**

No single server or process can handle millions of users.

So companies use:

* **L4 Load Balancers** → handle TCP connections
* **L7 Load Balancers** → handle HTTP requests

Both are needed because they solve **different problems**.

---

# 📌 **2. What is L4 Load Balancer (Layer 4 - Transport Layer)**

### It works at:

* IP
* Port
* TCP / UDP packets

### It does **NOT** understand:

* URL
* Headers
* Cookies
* JSON

### Its job:

* Handle HUGE number of TCP connections (millions per second)
* Distribute connections to L7 balancers

### Think of it like:

**A traffic cop who sees only cars, not what is inside them.**

---

# 📌 **3. What is L7 Load Balancer (Layer 7 - Application Layer)**

### It understands:

* URL (like `/feed/timeline/`)
* HTTP headers
* Cookies
* JWT tokens
* Request body

### Its job:

* HTTPS termination (decrypt)
* Routing logic
* Rate limiting
* Caching
* A/B testing
* Security (WAF)
* Forward request to correct microservice

### Think of it like:

**A receptionist who reads your file and decides which room you go to.**

---

# 📌 **4. Why L4 Balances L7**

* L7 is heavy (decrypt, read URL, parse headers)
* L7 cannot handle millions of connections
* So we put many L7 proxies (100–500)
* L4 distributes connections to these L7 proxies

### Final chain:

```
Client → L4 → L7 → Microservices
```

---

# 📌 **5. Why We Need MULTIPLE L4 and MULTIPLE L7**

### Multiple L4:

* To handle 200M Indian users
* To avoid single point of failure
* For scaling
* For global traffic distribution

### Multiple L7:

* Each L7 can handle only a limited amount
* They need horizontal scaling
* They do heavy HTTP tasks

---

# 📌 **6. Where They Live Physically (Instagram)**

You → Jio/Airtel → Nearest Meta Edge POP → Instagram Datacenter.

Instagram has L4 and L7 in **Edge POPs**, closest to you.

Example for India:

* Mumbai
* Chennai
* Hyderabad
* Singapore backup

---

# 📌 **7. Full Instagram Practical Flow (From Your Phone in India)**

### Step 1 — You open Instagram

Your app sends:

```
GET https://i.instagram.com/api/v1/feed/timeline/
```

### Step 2 — DNS chooses nearest Instagram POP

Jaipur → routed to **Mumbai** POP.

### Step 3 — Request hits **L4 LOAD BALANCER**

Handles:

* TCP handshake
* SYN flood protection
* Millions of connections

It chooses one L7 proxy.

### Step 4 — Request goes to **L7 LOAD BALANCER**

L7:

* Decrypts HTTPS
* Reads URL
* Checks cookies/auth
* Applies rate limits
* Decides microservice

Sees:

```
/api/v1/feed/timeline/
```

Routes to Feed Service.

### Step 5 — Feed Service (in Singapore DC)

Calls:

* ranking service
* ads engine
* story service
* user service
* ML recommendation engine

Builds your feed.

### Step 6 — Response returns:

```
Feed → L7 → L4 → You
```

Your Instagram feed loads.

---

# 📌 **8. What Happens If One Layer Is Removed?**

### ❌ If L4 is removed:

* All traffic goes directly to L7
* L7 overloads and crashes
* Instagram down globally

### ❌ If L7 is removed:

* No routing based on URL
* No rate limiting
* No HTTPS termination
* No microservices
* App won’t work

### ❌ If both removed:

* Traffic goes directly to backend
* Backend instantly dies
* Total outage

---

# 📌 **9. One-line Definitions to Remember**

### **L4 Load Balancer**

“Distributes TCP connections. Fast. Blind. Scales massively.”

### **L7 Load Balancer**

“Understands HTTP. Routes intelligently. Does security + logic.”

### **Instagram Flow**

You → L4 (distribute connections) → L7 (smart routing) → Feed service → You.

---

# 📌 **10. The Perfect Mental Diagram to Remember**

```
You (India)
    ↓
Internet
    ↓
🎯 L4 Load Balancers (10–50 per region)
    ↓
🎯 L7 Load Balancers / Proxies (100–500)
    ↓
Feed / Story / DM Microservices
    ↓
DB, Cache, ML systems
    ↓
Back to L7 → L4 → You
```


---

## 📚 Additional Resources

**Load Balancers:**
- [Nginx](https://nginx.org/) - Most popular
- [HAProxy](http://www.haproxy.org/) - Powerful
- [AWS ELB/ALB/NLB](https://aws.amazon.com/elasticloadbalancing/)
- [Azure Load Balancer](https://azure.microsoft.com/en-us/products/load-balancer/)

**Learning:**
- [Introduction to Load Balancing](https://www.digitalocean.com/community/tutorials/an-introduction-to-haproxy-and-load-balancing-concepts)
- [nginx LB Tutorial](https://docs.nginx.com/nginx/admin-guide/load-balancer/)

---

## 🎯 Before You Leave

**Can you answer these?**

1. **What's the main purpose of a load balancer?**
   - Answer: Distribute traffic across multiple servers

2. **What's the difference between L4 and L7?**
   - Answer: L4 = fast, TCP/IP only; L7 = smart, HTTP-aware

3. **What's a health check?**
   - Answer: Periodic test to verify backend is healthy

4. **What's session affinity?**
   - Answer: Route same client always to same server

5. **Why do you need HA for load balancers?**
   - Answer: LB itself is single point of failure

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **Startup:** "We don't need a load balancer. One server can handle everything!"
>
> **3 months later (viral moment):** Traffic spike! Server crashes!
>
> **CEO:** "Why didn't we load balance?"
>
> **Engineer:** "You said it was a waste of money..."
>
> **Site:** *is down* 💀

---

[← Back to Main](../README.md) | [Previous: File Storage](16-file-storage.md) | [Reverse Proxy (Nginx, HAProxy)](18-reverse-proxy.md)

---

**Last Updated:** November 10, 2025  
**Difficulty:** ⭐⭐⭐ Intermediate-Advanced (networking concepts)  
**Time to Read:** 26 minutes  
**Time to Build LB:** 4-6 hours per phase  

---

*Load balancers: Turning "which server?" into "all of them!" in milliseconds.* 🚀