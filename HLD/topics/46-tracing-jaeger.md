# 46. Distributed Tracing (Jaeger, OpenTelemetry)

A user clicks a button. 50 services get involved. Request goes through: API gateway, auth service, database, cache, message queue, payment processor, analytics, logging, monitoring... One service is slow. Which one? You don't know. You have logs from all 50. You have metrics from all 50. But no trace showing which one actually broke the chain. Distributed tracing: finally understanding what your microservices are doing! 🔍🐛

[← Back to Main](../README.md) | [Previous: Metrics](45-metrics-prometheus.md) | [Next: URL Shortener](../case-studies/47-url-shortener.md)

---

## 🎯 Quick Summary

**Distributed Tracing** tracks requests across multiple services. **Trace** follows one request through system (spans = service calls). **Jaeger** collects and visualizes traces. **OpenTelemetry** standard for instrumentation. Uber created Jaeger. Traces show: latency bottlenecks, service dependencies, failure paths. Trade-off: overhead (adds latency), storage (massive), sampling (miss rare issues). Essential for microservices debugging.

Think of it as: **Distributed Tracing = Request Journey Map**

---

## 🌟 Beginner Explanation

### Problem: Debugging Microservices

```
SCENARIO: User reports "checkout is slow"

Monolith (Old):
├─ GET /checkout
├─ Server processes
├─ Returns response
└─ Look at logs, see problem

Microservices (Now):
├─ GET /checkout → API Gateway
├─ → Auth Service (slow?)
├─ → Order Service (slow?)
├─ → Payment Service (slow?)
├─ → Inventory Service (slow?)
├─ → Notification Service (slow?)
└─ Response returned

Which one is slow?
├─ Check logs from Auth? Unclear
├─ Check logs from Order? Unclear
├─ Check logs from Payment? Unclear
├─ Check metrics? All look OK
└─ No idea which is bottleneck!

SOLUTION: Distributed Trace

One trace request_id=abc123:
├─ Gateway: 10ms
├─ Auth: 5ms
├─ Order: 50ms ← BOTTLENECK!
├─ Payment: 10ms
├─ Inventory: 5ms
├─ Notification: 10ms
└─ Total: 90ms

Immediately see: Order service is slow!
```

### Trace Structure

```
TRACE (Request_ID = abc123):
└─ Root Span: GET /checkout (0-100ms)
   ├─ Child: Auth Service (5-10ms)
   │  ├─ Check token: 2ms
   │  ├─ Query cache: 2ms
   │  └─ Return result: 1ms
   │
   ├─ Child: Order Service (40-60ms) ← SLOW
   │  ├─ Create order: 20ms
   │  ├─ Query database: 35ms ← SLOWEST
   │  └─ Validate: 5ms
   │
   ├─ Child: Payment Service (10-25ms)
   │  ├─ Process payment: 15ms
   │  └─ Confirm: 5ms
   │
   └─ Child: Notification (5-15ms)
      └─ Send email: 10ms

SPAN (Individual operation):
├─ Trace_ID: abc123 (parent request)
├─ Span_ID: auth_001 (unique to this call)
├─ Parent_Span_ID: root (who called this)
├─ Service: auth-service
├─ Operation: check_token
├─ Start: 5ms
├─ Duration: 10ms
├─ Tags: token_valid=true, cache_hit=true
├─ Logs: ["Started", "Cache hit", "Returned"]
└─ Status: OK

TAGS vs LOGS:

Tags (Structured):
├─ Key-value pairs
├─ user_id = 123
├─ cache_hit = true
├─ error_code = null
└─ Queryable

Logs (Unstructured):
├─ Text messages
├─ "Starting operation"
├─ "Querying database"
├─ "Operation complete"
└─ Not queryable
```

### Trace Propagation

```
REQUEST WITH TRACE CONTEXT:

Client → API Gateway:
├─ Header: X-Trace-ID: abc123
├─ Header: X-Span-ID: gateway_001
└─ Header: X-Parent-Span-ID: null

API Gateway → Auth Service:
├─ Header: X-Trace-ID: abc123 (same!)
├─ Header: X-Span-ID: auth_001 (new!)
├─ Header: X-Parent-Span-ID: gateway_001 (who called)
└─ Headers passed through!

Auth Service → Cache:
├─ Header: X-Trace-ID: abc123 (same!)
├─ Header: X-Span-ID: cache_001
├─ Header: X-Parent-Span-ID: auth_001
└─ Same trace through whole request!

Result: One trace_id follows entire request!
```

### Sampling

```
PROBLEM: Too many traces

Your system:
├─ 1 million requests/second
├─ Each generates 1 trace
├─ 86.4 billion traces/day

Storage:
├─ Each trace: ~10KB
├─ 86.4B × 10KB = 864 TB/day!
├─ Storage: Impossible
└─ Costs: Astronomical

SOLUTION: Sampling

Sample 1 in 100:
├─ Trace 1% of requests
├─ Store: 864GB/day (vs 864TB)
├─ Cost: 100x reduction!

Sampling strategies:

Uniform sampling:
├─ Trace 1% of all requests
├─ Fast requests: Maybe traced
├─ Slow requests: Maybe not traced
└─ Issue: Miss rare slow requests!

Adaptive sampling:
├─ Slow requests (> 100ms): Always trace
├─ Normal requests (< 100ms): Trace 10%
├─ Ensures: Slow requests captured
└─ Better!

Error sampling:
├─ Errors: Always trace
├─ Success: Trace 1%
└─ Debug errors, understand normal flow
```

---

## 🔬 Advanced Explanation

### OpenTelemetry Standard

```
PROBLEM: Too many tracing standards

Before OpenTelemetry:
├─ Jaeger (Uber)
├─ Zipkin (Twitter)
├─ DataDog (proprietary)
├─ New Relic (proprietary)
├─ AWS X-Ray (AWS)
└─ Different formats, hard to switch!

SOLUTION: OpenTelemetry

Unified standard:
├─ One instrumentation
├─ Multiple backends
├─ Switch without code change!

Architecture:

Application
├─ Uses OpenTelemetry SDK
├─ Generates traces/metrics/logs
└─ Sends to Collector

Collector (OTel Collector)
├─ Receives data
├─ Processes/filters/samples
├─ Sends to backend

Backend
├─ Jaeger
├─ Datadog
├─ Honeycomb
├─ GCP Cloud Trace
└─ Any OTel-compatible backend

Benefit:
✅ No vendor lock-in
✅ Switch backends easily
✅ Standard format
✅ Industry standard
```

### Trace Analysis

```
LATENCY BREAKDOWN:

Request timeline:
│
├─ Gateway: 5ms (overhead)
├─ Auth: 10ms (token check)
├─ Order: 50ms (main work)
│  ├─ Validate: 5ms
│  ├─ DB Query: 40ms ← SLOWEST!
│  └─ Save: 5ms
├─ Payment: 15ms
└─ Notify: 5ms

Total: 85ms

Analysis:
├─ Where is latency? DB Query (40ms = 47%)
├─ Can we optimize? Cache results?
├─ Can we parallelize? Payment + Notify?
└─ Expected: 80ms → Actual: 85ms → Close!

ERROR TRACING:

Request:
├─ Gateway: OK
├─ Auth: OK
├─ Order: OK
├─ Payment: ERROR ❌
│  └─ Exception: "Card declined"
├─ Notify: SKIPPED (due to error)
└─ Response: 402 (Payment required)

Trace shows:
├─ Where error occurred: Payment service
├─ What error: Card declined
├─ When: 50ms into request
├─ Which service to debug: Payment
└─ Fast root cause analysis!
```

---

## 🐍 Python Code Example

### ❌ Without Tracing (No Visibility)

```python
# ===== NO DISTRIBUTED TRACING =====

from flask import Flask
import requests

app = Flask(__name__)

@app.route('/checkout', methods=['POST'])
def checkout():
    """Checkout - no tracing"""
    
    # Call auth service
    auth_resp = requests.get('http://auth-service/verify')
    
    # Call order service
    order_resp = requests.post('http://order-service/create', json=request.json)
    
    # Call payment service
    payment_resp = requests.post('http://payment-service/process')
    
    # Combine responses
    return {'status': 'success'}

# Problems:
# ❌ No trace following request
# ❌ No visibility into service calls
# ❌ Can't see which service is slow
# ❌ Logs from each service not correlated
```

### ✅ With Basic Tracing (Manual)

```python
# ===== BASIC TRACING =====

from flask import Flask, request
import requests
import uuid

app = Flask(__name__)

@app.route('/checkout', methods=['POST'])
def checkout():
    """Checkout with basic tracing"""
    
    # Create trace ID
    trace_id = str(uuid.uuid4())
    span_id = 'checkout_001'
    
    print(f"[{trace_id}] Starting checkout")
    
    # Call auth service (pass trace context)
    headers = {
        'X-Trace-ID': trace_id,
        'X-Span-ID': 'auth_001',
        'X-Parent-Span-ID': span_id
    }
    auth_resp = requests.get('http://auth-service/verify', headers=headers)
    print(f"[{trace_id}] Auth complete")
    
    # Call order service
    headers['X-Span-ID'] = 'order_001'
    order_resp = requests.post('http://order-service/create', json=request.json, headers=headers)
    print(f"[{trace_id}] Order complete")
    
    # Call payment service
    headers['X-Span-ID'] = 'payment_001'
    payment_resp = requests.post('http://payment-service/process', headers=headers)
    print(f"[{trace_id}] Payment complete")
    
    print(f"[{trace_id}] Checkout finished")
    
    return {'status': 'success', 'trace_id': trace_id}

# Benefits:
# ✅ Can correlate logs via trace_id
# ✓ Not ideal (manual, error-prone)
```

### ✅ With OpenTelemetry (Production)

```python
# ===== OPENTELEMETRY TRACING =====

from flask import Flask, request
import requests
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

app = Flask(__name__)

# Configure Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name='localhost',
    agent_port=6831,
)

# Set up tracing
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Auto-instrument Flask and requests
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

tracer = trace.get_tracer(__name__)

@app.route('/checkout', methods=['POST'])
def checkout():
    """Checkout with automatic tracing"""
    
    with tracer.start_as_current_span("checkout") as span:
        # Set tags
        span.set_attribute("user_id", request.json.get('user_id'))
        span.set_attribute("amount", request.json.get('amount'))
        
        # These calls are automatically traced!
        # OpenTelemetry intercepts requests
        
        auth_resp = requests.get('http://auth-service/verify')
        order_resp = requests.post('http://order-service/create', json=request.json)
        payment_resp = requests.post('http://payment-service/process')
        
        span.set_attribute("status", "success")
        
        return {'status': 'success'}

# Benefits:
# ✅ Automatic tracing of requests
# ✅ Automatic span creation
# ✅ Zero overhead (sampling)
# ✅ Easy context propagation
# ✅ Production-ready
```

### ✅ Custom Spans (Advanced)

```python
# ===== CUSTOM SPANS =====

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
import time

tracer = trace.get_tracer(__name__)

def slow_database_query(query):
    """Database query with tracing"""
    
    with tracer.start_as_current_span("db_query") as span:
        # Record parameters
        span.set_attribute("query", query)
        span.set_attribute("db", "postgres")
        
        try:
            start = time.time()
            
            # Execute query
            result = execute_query(query)
            
            duration = time.time() - start
            span.set_attribute("duration_ms", duration * 1000)
            span.set_attribute("rows", len(result))
            
            # Add event log
            span.add_event("query_complete")
            
            return result
        
        except Exception as e:
            # Record error
            span.set_attribute("error", True)
            span.set_attribute("error.type", type(e).__name__)
            span.set_attribute("error.message", str(e))
            span.set_status(Status(StatusCode.ERROR, str(e)))
            
            raise

def create_order(user_id, items):
    """Create order with multiple spans"""
    
    with tracer.start_as_current_span("create_order") as root_span:
        root_span.set_attribute("user_id", user_id)
        root_span.set_attribute("items_count", len(items))
        
        # Validate
        with tracer.start_as_current_span("validate_items"):
            validate_items(items)
        
        # Query inventory
        with tracer.start_as_current_span("check_inventory"):
            for item in items:
                with tracer.start_as_current_span("check_item"):
                    check_stock(item)
        
        # Save to database
        with tracer.start_as_current_span("save_order"):
            order_id = slow_database_query(
                f"INSERT INTO orders (user_id, items) VALUES ({user_id}, '{items}')"
            )
        
        root_span.set_attribute("order_id", order_id)
        
        return order_id

# Trace visualization in Jaeger:
#
# create_order (root)
# ├─ validate_items (5ms)
# ├─ check_inventory (30ms)
# │  ├─ check_item (item1) (10ms)
# │  ├─ check_item (item2) (10ms)
# │  └─ check_item (item3) (10ms)
# └─ save_order (45ms)
#    └─ db_query (40ms) ← slowest!
#
# Total: 80ms
```

---

## 💡 Mini Project: "Build Tracing System"

### Phase 1: Basic Tracing ⭐

**Requirements:**
- Manual trace context propagation
- Jaeger setup
- View traces in Jaeger UI
- Multiple spans per request

---

### Phase 2: OpenTelemetry ⭐⭐

**Requirements:**
- Auto-instrumentation
- Custom spans
- Error tracking
- Performance metrics

---

### Phase 3: Production Ready ⭐⭐⭐

**Requirements:**
- Sampling strategies
- Multiple backends
- Trace correlation with logs
- Alert on slow traces

---

## ⚖️ Observability Pillars Complete

| Pillar | Tool | Use Case |
|--------|------|----------|
| **Metrics** | Prometheus | Trending, alerting |
| **Logs** | ELK, Loki | Debugging, events |
| **Traces** | Jaeger | Performance, dependencies |

---

## ❌ Common Mistakes

### Mistake 1: No Sampling

```python
# ❌ Trace 100% of requests
# Storage explodes, costs astronomical

# ✅ Intelligent sampling
# Sample slow requests: 100%
# Sample normal: 10%
# Sample errors: 100%
```

### Mistake 2: Not Propagating Context

```python
# ❌ Trace context lost at service boundary
request_to_other_service()  # No trace context!

# ✅ Propagate headers
headers = {
    'X-Trace-ID': trace_id,
    'X-Span-ID': span_id,
    'X-Parent-Span-ID': parent_span_id
}
request_to_other_service(headers=headers)
```

### Mistake 3: Too Many Spans

```python
# ❌ Create span for every operation
with tracer.start_span("increment_i"): i += 1
with tracer.start_span("increment_j"): j += 1
# Creates thousands of spans!

# ✅ Only span important operations
with tracer.start_span("main_loop"):
    for i in range(1000):
        i += 1  # Don't span this
```

---

## 📚 Additional Resources

**Jaeger:**
- [Jaeger](https://www.jaegertracing.io/)
- [Jaeger Tutorial](https://medium.com/jaegertracing/jaeger-tracing-tutorial-fbb1e3fc5faf)

**OpenTelemetry:**
- [OpenTelemetry](https://opentelemetry.io/)
- [OTel Python SDK](https://opentelemetry.io/docs/instrumentation/python/)

**Tracing:**
- [Distributed Tracing](https://opentracing.io/)
- [Trace Context](https://www.w3.org/TR/trace-context/)

---

## 🎯 Before You Leave

**Can you answer these?**

1. **Trace vs span?**
   - Answer: Trace is request; span is service call

2. **Why trace context propagation?**
   - Answer: Correlate across service boundaries

3. **Sampling strategies?**
   - Answer: Uniform, adaptive, error-based

4. **OpenTelemetry benefit?**
   - Answer: Vendor-neutral standard, switch backends

5. **When to use tracing vs logging?**
   - Answer: Tracing for path; logging for details

**If you got these right, you're ready for real systems!** ✅

---

## 🤣 Closing Thoughts

> **Microservices:** "I call 50 other services!"
>
> **Request:** "Where am I?"
>
> **Microservices:** "No idea, could be anywhere"
>
> **Distributed Trace:** "Found you!"
>
> **Request:** "Finally! Who was slow?"
>
> **Distributed Trace:** "Database, but we already knew that"
>
> **Everyone:** "At least now we can prove it!" 📊

---

[← Back to Main](../README.md) | [Previous: Metrics](45-metrics-prometheus.md) | [Next: URL Shortener](../case-studies/47-url-shortener.md)

---

**Last Updated:** November 11, 2025  
**Difficulty:** ⭐⭐⭐⭐ Advanced (observability/microservices)  
**Time to Read:** 26 minutes  
**Time to Implement:** 5-8 hours per phase  

---

*Distributed Tracing: Finally understanding what your microservices are doing.* 🚀