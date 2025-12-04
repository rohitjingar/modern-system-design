# 34. Heartbeats & Health Checks

A heartbeat is a service saying "I'm alive!" every few seconds. Health checks verify the heartbeat. It's like having a friend text you "still alive?" every 10 seconds. Sounds annoying, but when they stop texting, you know something's wrong. Distributed systems: where paranoia is a feature. 💓🔍

[← Back to Main](../README.md) | [Previous: Database Optimization](33-database-optimization.md) | [Next: Failover & Replication Strategies →](35-failover-replication.md)

---

## 🎯 Quick Summary

**Heartbeats** are periodic signals from services indicating they're alive. **Health Checks** verify service is functioning correctly. Without them: dead services still appear alive (no detection). With them: detect failures in seconds, trigger automatic recovery. Kubernetes uses readiness/liveness probes. Netflix monitors 100k+ services continuously. Used everywhere production systems run. Simple but essential: enables automatic failover, prevents requests to dead instances, improves availability.

Think of it as: **Heartbeats = Proof of Life**

---

## 🌟 Beginner Explanation

### Problem: Dead Services

```
SCENARIO: Service crashes, nobody knows

T=0: Order Service crashes
├─ User still tries to place order
├─ Load balancer routes to dead service
├─ Connection timeout (30 seconds!)
├─ User frustrated
└─ Order fails

T=30: Timeout finally detected
├─ Load balancer removes service
├─ Next user's order: Routes to alive service
└─ But first user lost!

PROBLEM:
❌ 30-second delay to detect failure
❌ Users hit dead service first
❌ Manual investigation needed
❌ No automatic recovery
```

**SOLUTION: Heartbeats & Health Checks**

```
T=0: Order Service crashes
├─ Stops sending heartbeats
└─ Also fails health checks

T=5: Health check fails
├─ Load balancer detects immediately
├─ Removes from rotation
└─ No more traffic sent there

T=5.1: User tries to place order
├─ Load balancer: Only sends to healthy services
├─ Order succeeds
└─ User happy!

BENEFITS:
✅ 5-second detection (vs 30)
✅ Automatic recovery
✅ Users never hit dead service
✅ Minimal impact
```

### Heartbeat Types

```
HEARTBEAT (Service says "I'm alive"):

Simple ping:
└─ Server: "TCP connection successful"
└─ Cost: Low
└─ Detects: Network/crash only

HTTP endpoint:
└─ GET /healthz → 200 OK
└─ Cost: Low (HTTP request)
└─ Detects: Service running

Application check:
└─ Checks: Can connect to database?
└─ Checks: Queues < threshold?
└─ Checks: Memory < 80%?
└─ Cost: Medium (real checks)
└─ Detects: Actual problems

Business logic check:
└─ Checks: Can query user?
└─ Checks: Can create order?
└─ Checks: All dependencies working?
└─ Cost: High (real operations)
└─ Detects: Everything broken


HEALTH CHECK LEVELS:

Liveness Probe (Is it alive?):
└─ Is process running?
└─ GET /alive → 200 OK
└─ If fails: Kill container, restart
└─ Default: < 30 seconds

Readiness Probe (Can it handle traffic?):
└─ Is it ready to serve?
└─ GET /ready → 200 OK (if dependencies OK)
└─ If fails: Remove from load balancer
└─ Default: < 10 seconds

Startup Probe (Did it start correctly?):
└─ Did initialization succeed?
└─ GET /startup → 200 OK (if ready)
└─ If fails for too long: Kill container
└─ Default: < 60 seconds
```

### Architecture

```
HEARTBEAT SYSTEM:

Service (Order Service):
├─ Sending heartbeat: Every 5 seconds
│  └─ Endpoint: GET /heartbeat
│     └─ Returns: {status: "alive", timestamp: now}
│
├─ Responding to health checks: Every 10 seconds
│  ├─ Endpoint: GET /health
│  ├─ Checks:
│  │  ├─ Database connected? ✅
│  │  ├─ Cache working? ✅
│  │  ├─ Dependencies reachable? ✅
│  │  └─ Memory < 80%? ✅
│  └─ Returns: {status: "healthy"}
│
└─ Failing scenario:
   ├─ Database crashes
   ├─ Next health check fails
   │  └─ GET /health → {status: "unhealthy", reason: "DB down"}
   └─ Load balancer detects

Load Balancer:
├─ Health check interval: 10 seconds
├─ For each backend service:
│  ├─ Sends: GET /health
│  ├─ Expects: 200 OK
│  ├─ If OK: "healthy" → keep traffic
│  ├─ If fails: "unhealthy" → remove traffic
│  └─ If fails 3 times: "down" → manual investigation
│
└─ Updates routing:
   ├─ Only send traffic to healthy services
   ├─ Skip dead services
   └─ Automatic failover

Monitoring System:
├─ Tracks health checks over time
├─ Alerts on failures
├─ Restarts services if needed
└─ Sends notifications
```

---

## 🔬 Advanced Explanation

### Health Check Strategy

```
ENDPOINT /health (Application Health):

GET /health

Checks performed:
1. Database connectivity (5ms)
   ├─ Query: SELECT 1
   ├─ If fails: "unhealthy"
   └─ Otherwise: continue

2. Cache connectivity (5ms)
   ├─ Ping Redis
   ├─ If fails: "unhealthy"
   └─ Otherwise: continue

3. Dependency health (10ms)
   ├─ Check upstream services
   ├─ If fails: "degraded" (not unhealthy)
   └─ Otherwise: continue

4. Resource utilization (2ms)
   ├─ Memory: < 80%?
   ├─ Disk: < 90%?
   ├─ Connections: < max?
   └─ If fails: "unhealthy"

Total time: ~22ms

Response:
├─ Healthy: 200 OK
├─ Degraded: 200 OK (but marked degraded)
└─ Unhealthy: 503 Service Unavailable


ENDPOINT /liveness (Just alive?):

GET /liveness

Checks performed:
1. Process running? Yes
2. Not in crash loop? Yes
3. No deadlock? Yes

Total time: < 5ms

Response:
├─ Alive: 200 OK
└─ Dead: (no response)

Why minimal?
❌ If too complex: Probe itself fails
❌ If too slow: Timeout before completing
❌ Keep it simple: Just check process state
```

### Failure Detection

```
FAILURE DETECTION WORKFLOW:

Healthy service:
├─ T=0: Health check → 200 OK
├─ T=10: Health check → 200 OK
├─ T=20: Health check → 200 OK
└─ Status: Healthy ✅

Service degrading:
├─ T=0: Health check → 200 OK
├─ T=10: Health check → 200 OK
├─ T=20: Health check → 503 (unhealthy)
├─ Action: Mark unhealthy (but give retry chance)
├─ T=30: Health check → 503 (still bad)
├─ Action: Remove from load balancer
└─ Status: Unhealthy ❌

Service recovering:
├─ T=0: Health check → 503 (unhealthy)
├─ T=10: Health check → 503 (still bad)
├─ T=20: Health check → 200 OK (recovered!)
├─ Action: Mark as recovering
├─ T=30: Health check → 200 OK
├─ Action: Add back to load balancer
└─ Status: Healthy ✅

FAILURE MODES:

Partial Failure:
├─ Service A: healthy
├─ Service B: unhealthy (timeout)
├─ Service C: healthy
└─ Load balancer: Routes around B

Network Partition:
├─ Service reachable locally
├─ Health check can't reach database (network down)
├─ Marked unhealthy (cascading failure)
└─ But service actually fine!
   └─ Solution: Distinguish network vs app failure

Cascading Failure:
├─ Service A fails
├─ Service B depends on A
├─ B's health checks fail
├─ B removed from rotation
├─ Service C depends on B
├─ C's health checks fail
├─ C removed from rotation
└─ Entire chain fails!
   └─ Solution: Circuit breakers (Topic 36)
```

### Kubernetes Probes

```
KUBERNETES HEALTH CHECKS:

apiVersion: v1
kind: Pod
metadata:
  name: order-service
spec:
  containers:
  - name: app
    image: order-service:1.0
    
    # Startup Probe (initialization)
    startupProbe:
      httpGet:
        path: /startup
        port: 8000
      initialDelaySeconds: 0
      periodSeconds: 10
      timeoutSeconds: 3
      failureThreshold: 30  # Fail if 30 failures
    
    # Liveness Probe (is it alive?)
    livenessProbe:
      httpGet:
        path: /alive
        port: 8000
      initialDelaySeconds: 30  # Wait 30s before first check
      periodSeconds: 10  # Check every 10s
      timeoutSeconds: 5  # Timeout after 5s
      failureThreshold: 3  # Kill if 3 failures
    
    # Readiness Probe (ready for traffic?)
    readinessProbe:
      httpGet:
        path: /ready
        port: 8000
      initialDelaySeconds: 10
      periodSeconds: 5  # Check every 5s (more frequent)
      timeoutSeconds: 3
      failureThreshold: 2  # Remove if 2 failures

Flow:
1. Container starts
2. Startup probe runs until success (or 30 failures)
3. Once started: Readiness probe checks if ready
4. If ready: Traffic sent
5. If readiness fails: Traffic removed (but pod not killed)
6. If liveness fails: Pod killed (restart)
```

---

## 🐍 Python Code Example

### ❌ Without Health Checks (No Failure Detection)

```python
# ===== WITHOUT HEALTH CHECKS =====

from flask import Flask

app = Flask(__name__)

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create order endpoint"""
    
    try:
        # Create order in database
        order = db.create_order(request.json)
        return {'order_id': order.id}
    except Exception as e:
        return {'error': str(e)}, 500

# Problems:
# ❌ No health checks
# ❌ If database crashes: Service still accepts requests
# ❌ Load balancer doesn't know service is broken
# ❌ Requests timeout waiting for database
# ❌ No automatic recovery
```

### ✅ Basic Health Checks

```python
# ===== BASIC HEALTH CHECKS =====

from flask import Flask, jsonify
import psycopg2
import redis
from datetime import datetime

app = Flask(__name__)

# Simulate dependencies
db = psycopg2.connect("dbname=shop")
cache = redis.Redis(host='localhost')

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create order endpoint"""
    
    try:
        order = db.create_order(request.json)
        return {'order_id': order.id}
    except Exception as e:
        return {'error': str(e)}, 500

# Health check endpoints
@app.route('/health', methods=['GET'])
def health_check():
    """Full health check"""
    
    checks = {
        'database': check_database(),
        'cache': check_cache(),
        'memory': check_memory(),
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # If any check fails: Return 503
    if not all(checks.values()):
        return jsonify(checks), 503
    
    return jsonify(checks), 200

@app.route('/alive', methods=['GET'])
def liveness_probe():
    """Liveness probe (just alive?)"""
    
    # Minimal check: Is process running?
    return {'status': 'alive'}, 200

@app.route('/ready', methods=['GET'])
def readiness_probe():
    """Readiness probe (ready for traffic?)"""
    
    # Check if dependencies available
    if not check_database():
        return {'status': 'not_ready', 'reason': 'database'}, 503
    
    if not check_cache():
        return {'status': 'not_ready', 'reason': 'cache'}, 503
    
    return {'status': 'ready'}, 200

def check_database():
    """Check if database is reachable"""
    try:
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        return True
    except:
        return False

def check_cache():
    """Check if cache is reachable"""
    try:
        cache.ping()
        return True
    except:
        return False

def check_memory():
    """Check if memory usage is acceptable"""
    import psutil
    
    memory_percent = psutil.virtual_memory().percent
    return memory_percent < 80

# Benefits:
# ✅ Load balancer can detect failures
# ✅ Automatic traffic removal from unhealthy
# ✅ Fast detection (every 10 seconds)
# ✅ Enables automatic recovery
```

### ✅ Production Health Checks (Kubernetes-Ready)

```python
# ===== PRODUCTION HEALTH CHECKS =====

from flask import Flask, jsonify
import psycopg2
import redis
import time
from datetime import datetime, timedelta
import threading

app = Flask(__name__)

# Dependencies
db = psycopg2.connect("dbname=shop")
cache = redis.Redis(host='localhost')

# Startup state
startup_time = None
initialization_complete = False

def initialize():
    """Initialization that must succeed before serving traffic"""
    
    global startup_time, initialization_complete
    
    startup_time = datetime.utcnow()
    
    try:
        # Run initialization tasks
        print("Initializing...")
        
        # Connect to database
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        print("✓ Database connected")
        
        # Load configuration
        config = cache.get('app:config')
        if not config:
            raise Exception("Config not loaded")
        print("✓ Configuration loaded")
        
        # Warm up cache
        print("✓ Cache warmed")
        
        initialization_complete = True
        print("✓ Initialization complete")
        
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        initialization_complete = False

# Run initialization on startup
initialize()

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create order endpoint"""
    
    if not initialization_complete:
        return {'error': 'Service not ready'}, 503
    
    try:
        order = db.create_order(request.json)
        return {'order_id': order.id}
    except Exception as e:
        return {'error': str(e)}, 500

# Kubernetes startup probe
@app.route('/startup', methods=['GET'])
def startup_probe():
    """Kubernetes startup probe"""
    
    if not initialization_complete:
        return {'status': 'starting'}, 503
    
    # Check if initialization took too long (> 5 minutes)
    init_duration = (datetime.utcnow() - startup_time).total_seconds()
    if init_duration > 300:
        return {'status': 'initialization_timeout'}, 503
    
    return {'status': 'started'}, 200

# Kubernetes liveness probe
@app.route('/alive', methods=['GET'])
def liveness_probe():
    """Kubernetes liveness probe"""
    
    # Minimal: Just check if process running
    # This endpoint should almost never fail
    
    return {'status': 'alive'}, 200

# Kubernetes readiness probe
@app.route('/ready', methods=['GET'])
def readiness_probe():
    """Kubernetes readiness probe"""
    
    checks = {}
    
    # 1. Initialization complete
    if not initialization_complete:
        checks['initialization'] = False
        return jsonify(checks), 503
    
    checks['initialization'] = True
    
    # 2. Database healthy
    try:
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        checks['database'] = True
    except:
        checks['database'] = False
        return jsonify(checks), 503
    
    # 3. Cache healthy
    try:
        cache.ping()
        checks['cache'] = True
    except:
        # Cache failure: degraded, not unhealthy
        checks['cache'] = False
        # Don't fail readiness, just mark degraded
    
    # 4. Queues not backlogged
    try:
        queue_length = cache.llen('task_queue')
        checks['queue_length'] = queue_length
        
        if queue_length > 10000:
            # Too backlogged, can't handle traffic
            return jsonify(checks), 503
    except:
        pass
    
    return jsonify(checks), 200

# Full health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Full health check (for monitoring)"""
    
    health = {
        'status': 'healthy',
        'checks': {}
    }
    
    # Database check
    try:
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        health['checks']['database'] = 'ok'
    except Exception as e:
        health['checks']['database'] = f'error: {e}'
        health['status'] = 'unhealthy'
    
    # Cache check
    try:
        cache.ping()
        health['checks']['cache'] = 'ok'
    except Exception as e:
        health['checks']['cache'] = f'error: {e}'
        health['status'] = 'degraded'  # Not fatal
    
    # Memory check
    import psutil
    mem_percent = psutil.virtual_memory().percent
    health['checks']['memory_percent'] = mem_percent
    if mem_percent > 90:
        health['status'] = 'unhealthy'
    
    # Disk check
    disk_percent = psutil.disk_usage('/').percent
    health['checks']['disk_percent'] = disk_percent
    if disk_percent > 95:
        health['status'] = 'unhealthy'
    
    health['timestamp'] = datetime.utcnow().isoformat()
    
    status_code = 200 if health['status'] == 'healthy' else 503
    return jsonify(health), status_code

# Benefits:
# ✅ Kubernetes-ready (startup, liveness, readiness)
# ✅ Graceful initialization
# ✅ Detailed health information
# ✅ Production monitoring
```

---

## 💡 Mini Project: "Implement Health Check System"

### Phase 1: Basic Health Checks ⭐

**Requirements:**
- /health endpoint
- Database connectivity check
- Simple readiness probe
- Load balancer integration

---

### Phase 2: Advanced Checks ⭐⭐

**Requirements:**
- Multiple probe types (startup, liveness, readiness)
- Detailed health information
- Metrics tracking
- Alert thresholds

---

### Phase 3: Production Monitoring ⭐⭐⭐

**Requirements:**
- Kubernetes integration
- Distributed health checks
- Dependency tracking
- Automatic recovery triggers

---

## ⚖️ Health Check Comparison

| Type | Frequency | Timeout | Action on Fail |
|------|-----------|---------|----------------|
| **Liveness** | Every 30s | 5s | Kill & restart |
| **Readiness** | Every 10s | 3s | Remove from LB |
| **Startup** | Every 10s | 5s | Kill after 30 failures |
| **Custom** | Every 60s | 10s | Alert |

---

## ❌ Common Mistakes

### Mistake 1: Health Check Too Complex

```python
# ❌ Health check runs expensive query
@app.route('/health')
def health():
    result = db.query("SELECT * FROM large_table WHERE complex_condition")
    return {'status': 'ok'}
# If query slow: Health check timeout! (cascading failure)

# ✅ Simple health check
@app.route('/health')
def health():
    cursor = db.cursor()
    cursor.execute("SELECT 1")
    return {'status': 'ok'}
# Fast, reliable, can't fail
```

### Mistake 2: Health Check Has Side Effects

```python
# ❌ Health check modifies data
@app.route('/health')
def health():
    db.insert('health_check_log', {'timestamp': now()})
    return {'status': 'ok'}
# Every 10 seconds: Writes to database! (log table explodes)

# ✅ Health check read-only
@app.route'/health')
def health():
    db.query("SELECT 1")  # Read-only
    return {'status': 'ok'}
```

### Mistake 3: Health Check Catches All Exceptions

```python
# ❌ Hides real errors
@app.route('/health')
def health():
    try:
        check_everything()
    except:
        return {'status': 'ok'}  # Always says OK!

# ✅ Let failures propagate
@app.route('/health')
def health():
    check_critical()  # Let fail if error
    check_optional()  # Catch and warn
    return {'status': 'ok'}
```

---

## 📚 Additional Resources

**Health Checks:**
- [Kubernetes Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Health Check Best Practices](https://aws.amazon.com/blogs/architecture/best-practices-for-application-health-checks/)

**Tools:**
- [Prometheus Monitoring](https://prometheus.io/)
- [Kubernetes Events](https://kubernetes.io/docs/tasks/debug-application-cluster/debug-cluster/)


---

## 🎯 Before You Leave

**Can you answer these?**

1. **What's a heartbeat?**
   - Answer: Periodic signal showing service is alive

2. **What's difference between liveness and readiness?**
   - Answer: Liveness = alive (restart if fails); Readiness = ready for traffic (remove if fails)

3. **When to use startup probe?**
   - Answer: When initialization takes time

4. **Why keep health checks simple?**
   - Answer: Complex checks fail, causing cascading failures

5. **What's failure threshold?**
   - Answer: Number of failures before declaring unhealthy

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **Service:** "I just crashed!"
>
> **Health Check:** "Are you alive?"
>
> **Service:** "..."
>
> **Health Check:** "No response = you're dead"
>
> **Kubernetes:** "KILL IT AND RESTART IT!"
>
> **Service (restarted):** "I'm alive now!"
>
> **Health Check:** "Welcome back, buddy" 💚

---

[← Back to Main](../README.md) | [Previous: Database Optimization](33-database-optimization.md) | [Next: Failover & Replication Strategies →](35-failover-replication.md)

---

**Last Updated:** November 11, 2025  
**Difficulty:** ⭐⭐⭐ Intermediate-Advanced (reliability)  
**Time to Read:** 25 minutes  
**Time to Implement:** 4-6 hours per phase  

---

*Heartbeats & Health Checks: Teaching your system to check if its organs are still working.* 🚀