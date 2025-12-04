# 36. Circuit Breakers

A circuit breaker is like an electrical circuit: when current (requests) gets too high, it trips the switch (stops traffic). Except in distributed systems, when you trip the switch, everything downstream breaks too. So you add circuit breakers to those too. Then those trip, breaking things further. Eventually your entire system is a cascade of circuit breakers. But hey, at least it's not melting down! 🔌💥

[← Back to Main](../README.md) | [Previous: Failover & Replication Strategies](35-failover-replication.md) | [Next: Retry & Backoff Mechanisms →](37-retry-backoff.md)

---

## 🎯 Quick Summary

**Circuit Breaker** stops traffic to failing services to prevent cascading failures. When service A calls service B and B is failing, circuit breaker opens, stops traffic to B, allows B to recover. States: closed (normal), open (stop traffic), half-open (test recovery). Prevents timeout storms, resource exhaustion, cascading failures. Netflix's Hystrix popularized it. Essential in microservices. Trade-off: complexity, additional latency (checking circuit state).

Think of it as: **Circuit Breaker = Emergency Stop Button**

---

## 🌟 Beginner Explanation

### Problem: Cascading Failures

```
SCENARIO: Service B crashes

Service A → Service B (database)
  ├─ B crashes
  ├─ A keeps calling B
  ├─ A waits for timeout: 30 seconds
  ├─ A exhausts thread pool
  ├─ A slows down
  └─ Now A also appears broken!

Service C → Service A
  ├─ A is slow (threads busy waiting)
  ├─ C gets slow response (or timeout)
  ├─ C's thread pool fills
  └─ C also appears broken!

Service D → Service C
  ├─ C is slow
  └─ D cascades down too!

Result: Chain reaction!
├─ B crashes
├─ A breaks
├─ C breaks
├─ D breaks
└─ Everything down!


SOLUTION: Circuit Breaker

Service A → Service B (with circuit breaker)

Scenario:
├─ B crashes
├─ A detects failures
├─ Circuit breaker: OPEN (stop calling!)
├─ A returns error immediately (no timeout wait)
├─ A's threads available
├─ A keeps working
└─ Doesn't cascade!

Service C → Service A
├─ A is responsive (threads freed)
├─ C works normally
└─ No cascade!
```

### Circuit Breaker States

```
CLOSED (Normal operation):
├─ Service working normally
├─ Requests flow through
├─ Success rate > 95%
└─ Circuit breaker: CLOSED (allowing traffic)

Scenario:
├─ 100 requests
├─ 99 succeed
├─ 1 fails
└─ 99% success → CLOSED

Open (Failing):
├─ Service failing badly
├─ Circuit breaker: OPEN (blocking traffic!)
├─ Requests rejected immediately
├─ No timeout wait
└─ Gives service time to recover

Scenario:
├─ 10 requests
├─ 8 fail
├─ 2 succeed
└─ 20% success → OPEN!

Half-Open (Recovery test):
├─ Service been down for a while
├─ Time to test if recovered
├─ Circuit breaker: HALF-OPEN (allow some traffic)
├─ Send test request
├─ If succeeds: CLOSED (recovered!)
├─ If fails: OPEN (still broken)
└─ Controlled recovery testing


STATE TRANSITIONS:

CLOSED → OPEN
├─ Failure threshold exceeded
├─ Example: 5 failures in last 20 requests
└─ Condition: failureRate > 50%

OPEN → HALF-OPEN
├─ Timeout reached
├─ Example: been open for 30 seconds
└─ Condition: time.since(open_time) > timeout

HALF-OPEN → CLOSED
├─ Test request succeeds
├─ Service appears recovered
└─ Condition: test_request.success()

HALF-OPEN → OPEN
├─ Test request fails
├─ Service still broken
├─ Reset timeout
└─ Condition: test_request.fail()
```

### Implementation Pattern

```
REQUEST FLOW WITH CIRCUIT BREAKER:

1. Check circuit state
   ├─ CLOSED? → Continue
   ├─ OPEN? → Fail immediately
   └─ HALF-OPEN? → Allow 1 request

2. If CLOSED or HALF-OPEN:
   ├─ Call downstream service
   ├─ If success:
   │  ├─ Record success
   │  ├─ Update state if needed
   │  └─ Return result
   ├─ If failure:
   │  ├─ Record failure
   │  ├─ Check threshold
   │  ├─ If threshold exceeded: OPEN
   │  └─ Return error

3. If OPEN:
   ├─ Reject request immediately
   ├─ Return error
   ├─ No downstream call made
   └─ Check if timeout reached
      ├─ If yes: HALF-OPEN
      └─ If no: Stay OPEN

Example thresholds:
├─ Failure rate > 50%: OPEN
├─ Min requests to check: 5
├─ Timeout before retry: 30 seconds
└─ Max requests in HALF-OPEN: 3
```

---

## 🔬 Advanced Explanation

### Failure Detection

```
FAILURE CRITERIA:

What causes circuit to open?

Option 1: Failure Rate
├─ Last 20 requests
├─ 10 fail
├─ Failure rate: 50%
├─ Threshold: 50%
└─ → OPEN

Option 2: Error Count
├─ Last 100 requests
├─ 15 fail
├─ Error count: 15
├─ Threshold: 10
└─ → OPEN

Option 3: Response Time
├─ Last 5 requests
├─ Average: 2 seconds
├─ Threshold: 1 second
└─ → OPEN (slow = failing)

Option 4: Exception Type
├─ IOException: → COUNT (network issue)
├─ TimeoutException: → COUNT (slow)
├─ BusinessException: → IGNORE (not circuit issue)
└─ Circuit cares only about technical failures


SLIDING WINDOW:

Track failures in window:

Bucket 0 (0-10s):   3 failures
Bucket 1 (10-20s):  2 failures
Bucket 2 (20-30s):  5 failures
Bucket 3 (30-40s):  1 failure

Total last 40s: 11 failures

Over 40 seconds = 11/X failures
If > 50%: OPEN

Window slides:
├─ Every 10 seconds
├─ New bucket added
├─ Old bucket dropped
└─ Always track last 40 seconds
```

### Fallback Strategies

```
WHEN CIRCUIT OPENS (Fallback options):

Option 1: Fail Fast
├─ Circuit open
├─ Return error immediately
├─ {"error": "Service unavailable"}
└─ User sees error (but server responsive)

Option 2: Cached Response
├─ Circuit open
├─ Return last known good response
├─ Stale but better than error
└─ User might see old data

Example:
├─ User list cached 1 hour ago
├─ Service down now
├─ Return cached list
└─ User happy (outdated list better than error)

Option 3: Default Value
├─ Circuit open
├─ Return safe default
├─ Example: Empty list instead of error
└─ Graceful degradation

Option 4: Another Service
├─ Circuit open on primary
├─ Try secondary service
├─ If secondary also down: Fallback
└─ Reduces complete failure

Example:
├─ Primary database down
├─ Try read-only replica
├─ If replica down: Return cache
└─ Multi-level fallback

Option 5: Reject Gracefully
├─ Circuit open
├─ Queue request for later
├─ Retry when recovered
└─ Eventual consistency


BULKHEAD PATTERN (Isolation):

Without bulkheads:
├─ One service (A) calls another (B)
├─ B fails
├─ A's thread pool exhausted
├─ A can't serve other requests
└─ A cascades down

With bulkheads:
├─ Service A has dedicated thread pools:
│  ├─ Pool 1: For B calls (10 threads)
│  ├─ Pool 2: For C calls (10 threads)
│  ├─ Pool 3: For D calls (10 threads)
│  └─ Pool 4: For local work (20 threads)
├─ B fails
├─ Pool 1 exhausted (stuck)
├─ Pools 2, 3, 4 still available
├─ A still serves requests to C, D
└─ Isolated failure (doesn't cascade!)
```

---

## 🐍 Python Code Example

### ❌ Without Circuit Breaker (Cascading Failure)

```python
# ===== WITHOUT CIRCUIT BREAKER =====

import requests
import time

def call_downstream_service(user_id):
    """Call downstream service (no circuit breaker)"""
    
    try:
        # Call downstream
        response = requests.get(
            f'http://user-service:8000/users/{user_id}',
            timeout=30  # 30 second timeout
        )
        return response.json()
    
    except requests.exceptions.Timeout:
        # Service is slow/down
        # We wait 30 seconds!
        # Thread blocked for 30 seconds
        return None
    except requests.exceptions.ConnectionError:
        return None

# Problem:
# ❌ Service down
# ❌ We wait 30 seconds for timeout
# ❌ Thread blocked
# ❌ If many requests: All threads blocked
# ❌ Service appears broken
# ❌ Cascading failure
```

### ✅ With Circuit Breaker (Protected)

```python
# ===== WITH CIRCUIT BREAKER =====

import requests
import time
from datetime import datetime, timedelta
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # Normal
    OPEN = "open"          # Failing (stop traffic)
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    """Circuit breaker pattern"""
    
    def __init__(self, 
                 failure_threshold=5,
                 recovery_timeout=30,
                 expected_exception=Exception):
        
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
    
    def call(self, func, *args, **kwargs):
        """Execute function through circuit breaker"""
        
        # Check state
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                print("Circuit breaker: HALF_OPEN (testing recovery)")
            else:
                # Still open, reject immediately
                raise Exception("Circuit breaker is OPEN")
        
        try:
            # Call function
            result = func(*args, **kwargs)
            
            # Success
            self._on_success()
            return result
        
        except self.expected_exception as e:
            # Failure
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle success"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        print("✓ Circuit breaker: CLOSED (recovered)")
    
    def _on_failure(self):
        """Handle failure"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        print(f"✗ Failure #{self.failure_count}")
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            print(f"Circuit breaker: OPEN (stopping traffic)")
    
    def _should_attempt_reset(self):
        """Should try to recover?"""
        if not self.last_failure_time:
            return False
        
        elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return elapsed > self.recovery_timeout

# Usage
breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=10
)

def get_user(user_id):
    """Get user with circuit breaker protection"""
    
    def call_service():
        response = requests.get(
            f'http://user-service:8000/users/{user_id}',
            timeout=5  # Shorter timeout
        )
        return response.json()
    
    try:
        return breaker.call(call_service)
    except Exception as e:
        # Circuit open or service down
        print(f"Error: {e}")
        return {"error": "Service unavailable"}

# Behavior:
# Request 1: Service down → Failure #1
# Request 2: Service down → Failure #2
# Request 3: Service down → Failure #3 → OPEN
# Request 4: Circuit open → Rejected immediately (no timeout wait!)
# Request 5: Circuit open → Rejected immediately
# ... wait 10 seconds ...
# Request 6: Circuit HALF_OPEN → Try again
# Request 6 succeeds: Circuit CLOSED (recovered!)

# Benefits:
# ✅ Fail fast (no 30s timeout wait)
# ✅ Prevents cascading failure
# ✅ Allows recovery time
```

### ✅ Production Circuit Breaker (Advanced)

```python
# ===== PRODUCTION CIRCUIT BREAKER =====

from collections import deque
from threading import Lock
import requests

class AdvancedCircuitBreaker:
    """Production-grade circuit breaker"""
    
    def __init__(self,
                 name,
                 failure_threshold=0.5,  # 50% failure rate
                 min_requests=5,  # Need 5+ requests to judge
                 recovery_timeout=60,
                 max_half_open_requests=3):
        
        self.name = name
        self.failure_threshold = failure_threshold
        self.min_requests = min_requests
        self.recovery_timeout = recovery_timeout
        self.max_half_open_requests = max_half_open_requests
        
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
        self.half_open_requests = 0
        
        # Sliding window (last 20 requests)
        self.request_history = deque(maxlen=20)
        self.lock = Lock()
    
    def call(self, url, timeout=5):
        """Make HTTP request through circuit breaker"""
        
        with self.lock:
            # Check state
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_requests = 0
                    print(f"[{self.name}] Circuit: HALF_OPEN")
                else:
                    raise Exception(f"[{self.name}] Circuit: OPEN")
            
            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_requests >= self.max_half_open_requests:
                    raise Exception(f"[{self.name}] HALF_OPEN max requests reached")
                self.half_open_requests += 1
        
        try:
            # Make request
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            
            # Success
            with self.lock:
                self.request_history.append(True)
                self._update_state()
                if self.state == CircuitState.HALF_OPEN:
                    self.state = CircuitState.CLOSED
                    print(f"[{self.name}] Circuit: CLOSED (recovered)")
            
            return response.json()
        
        except Exception as e:
            # Failure
            with self.lock:
                self.request_history.append(False)
                self.last_failure_time = datetime.utcnow()
                self._update_state()
            
            raise
    
    def _update_state(self):
        """Check if should open circuit"""
        
        if len(self.request_history) < self.min_requests:
            return  # Not enough data
        
        failures = sum(1 for success in self.request_history if not success)
        failure_rate = failures / len(self.request_history)
        
        if failure_rate > self.failure_threshold:
            if self.state != CircuitState.OPEN:
                self.state = CircuitState.OPEN
                print(f"[{self.name}] Circuit: OPEN (failure rate {failure_rate:.1%})")
    
    def _should_attempt_reset(self):
        """Should try to recover?"""
        if not self.last_failure_time:
            return False
        
        elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return elapsed > self.recovery_timeout

# Usage
user_breaker = AdvancedCircuitBreaker("user-service")
order_breaker = AdvancedCircuitBreaker("order-service")

def get_user(user_id):
    try:
        return user_breaker.call(f'http://user-service:8000/users/{user_id}')
    except Exception:
        return {"error": "User service unavailable"}

def get_orders(user_id):
    try:
        return order_breaker.call(f'http://order-service:8000/orders/{user_id}')
    except Exception:
        return {"error": "Order service unavailable"}

# Benefits:
# ✅ Failure rate tracking (not just count)
# ✅ Sliding window (last 20 requests)
# ✅ Configurable thresholds
# ✅ Thread-safe (locks)
# ✅ Production-ready
```

---

## 💡 Mini Project: "Build Circuit Breaker"

### Phase 1: Basic Circuit Breaker ⭐

**Requirements:**
- Three states (closed, open, half-open)
- Failure counting
- Timeout-based reset
- Simple implementation

---

### Phase 2: Advanced (Metrics) ⭐⭐

**Requirements:**
- Failure rate tracking
- Sliding window
- Thread-safe
- Metrics/monitoring

---

### Phase 3: Production (Full) ⭐⭐⭐

**Requirements:**
- Multiple breakers
- Fallback strategies
- Bulkhead isolation
- Distributed tracing

---

## ⚖️ Circuit Breaker States

| State | Allows Traffic | Waits for Timeout | Tests Recovery |
|-------|---|---|---|
| **CLOSED** | ✅ Yes | ❌ No | ❌ No |
| **OPEN** | ❌ No | ✅ Yes | ❌ No |
| **HALF-OPEN** | ⚠️ Limited | ❌ No | ✅ Yes |

---

## ❌ Common Mistakes

### Mistake 1: Circuit Never Resets

```python
# ❌ No timeout, circuit stays open forever
if self.failure_count >= 5:
    self.state = "open"
    # Never checks if should try again!

# ✅ Include timeout
if self.failure_count >= 5:
    self.state = "open"
    self.open_time = now()
    
# Later:
if (now - open_time) > 60 seconds:
    self.state = "half_open"
```

### Mistake 2: All Exceptions Treated Same

```python
# ❌ Timeout = Bad network vs User doesn't exist
# Both are failures?
try:
    result = call_service()
except Exception:
    failure_count += 1

# ✅ Distinguish exception types
try:
    result = call_service()
except (TimeoutException, ConnectionError):
    failure_count += 1  # Circuit issue
except ValueError:
    pass  # Business logic error, not circuit issue
```

### Mistake 3: No Fallback

```python
# ❌ Circuit opens, user sees error
if circuit.is_open():
    raise Exception("Service down")

# ✅ Provide fallback
if circuit.is_open():
    return cached_data or default_value
```

---

## 📚 Additional Resources

**Circuit Breaker:**
- [Pattern Overview](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Hystrix](https://github.com/Netflix/Hystrix) (Netflix's library)
- [Resilience4j](https://resilience4j.readme.io/) (Modern Java)

**Related:**
- [Bulkhead Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/bulkhead)
- [Retry Patterns](37-retry-backoff.md)

---

## 🎯 Before You Leave

**Can you answer these?**

1. **What's a circuit breaker?**
   - Answer: Stops traffic to failing services

2. **What are the three states?**
   - Answer: Closed (normal), Open (failing), Half-Open (testing)

3. **When does circuit open?**
   - Answer: When failure rate exceeds threshold

4. **When does it try to recover?**
   - Answer: After timeout, enters Half-Open

5. **Why not just retry forever?**
   - Answer: Prevents cascading failure, gives service time to recover

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **Service A:** "Service B is failing!"
>
> **Circuit Breaker:** "I'll stop calling it"
>
> **Service A:** "Good idea!"
>
> **Service B (silently dying):** "Why is nobody calling me?"
>
> **Service B (after 60 seconds):** "I fixed it!"
>
> **Circuit Breaker:** "Let me test... yep! CLOSED!"
>
> **Service A:** "Welcome back, buddy!" 💚

---

[← Back to Main](../README.md) | [Previous: Failover & Replication Strategies](35-failover-replication.md) | [Next: Retry & Backoff Mechanisms →](37-retry-backoff.md)

---

**Last Updated:** November 11, 2025  
**Difficulty:** ⭐⭐⭐⭐ Advanced (reliability patterns)  
**Time to Read:** 26 minutes  
**Time to Implement:** 4-6 hours per phase  

---

*Circuit Breakers: Protecting your services from each other's failures, one trip at a time.* 🚀