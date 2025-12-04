# 44. Logging, Monitoring, and Alerting

You deploy to production. Everything works perfectly. Then you get paged at 3 AM. "The system is down!" You check logs. Nothing. You check metrics. All look fine. You check alerts. Silent. Turns out: logging broke, metrics weren't being collected, and alerts were misconfigured. The only working monitoring was angry customers calling support. Welcome to observability! 🔥📊

[← Back to Main](../README.md) | [Previous: SSL/TLS & HTTPS](43-ssl-tls-https.md) | [Next: Metrics (Prometheus, Grafana) →](45-metrics-prometheus.md)

---

## 🎯 Quick Summary

**Logging** records events (errors, requests, debugging info). **Monitoring** tracks system health (CPU, memory, latency). **Alerting** notifies when problems occur (page engineers). Together = Observability. **ELK Stack** (Elasticsearch, Logstash, Kibana) for logs. **Prometheus + Grafana** for metrics. **PagerDuty** for alerts. Netflix generates petabytes of logs daily. Google uses similar systems. Trade-off: storage (massive), alert fatigue (too many alerts), cost (infrastructure).

Think of it as: **Logging = History, Monitoring = Now, Alerting = Action**

---

## 🌟 Beginner Explanation

### Three Pillars of Observability

```
LOGS (What happened?):

Application logs:
├─ 2025-11-30 10:00:01 INFO: User 123 logged in
├─ 2025-11-30 10:00:05 DEBUG: Query took 45ms
├─ 2025-11-30 10:00:10 ERROR: Payment failed - card declined
├─ 2025-11-30 10:00:15 WARN: Rate limit approaching
└─ Text-based, timestamped events

Use cases:
├─ Debugging: "Why did this user's order fail?"
├─ Audit: "Who deleted this record?"
├─ Investigation: "What happened before the crash?"
└─ Root cause analysis

Levels:
├─ DEBUG: Detailed info for developers
├─ INFO: General informational messages
├─ WARN: Warning, something might be wrong
├─ ERROR: Error occurred, but app continues
└─ FATAL: Critical error, app crashed


METRICS (How is it performing?):

System metrics:
├─ CPU usage: 45%
├─ Memory usage: 2.1 GB / 8 GB
├─ Disk I/O: 150 MB/s
├─ Network: 50 Mbps
└─ Quantitative measurements

Application metrics:
├─ Requests per second: 3,500
├─ Error rate: 0.5%
├─ P99 latency: 120ms
├─ Active users: 10,000
└─ Business metrics

Use cases:
├─ Performance: "Is the system slow?"
├─ Capacity: "Do we need more servers?"
├─ Trending: "Is traffic growing?"
└─ SLA monitoring: "Are we meeting our target?"


ALERTS (What needs attention?):

Alert conditions:
├─ CPU > 80% for 5 minutes → Alert
├─ Error rate > 1% → Alert
├─ Latency > 500ms → Alert
├─ Disk space < 10% → Alert
└─ Service down → Alert

Alert channels:
├─ PagerDuty: Wake up on-call engineer
├─ Slack: Team notification
├─ Email: Non-urgent issues
├─ SMS: Critical only
└─ Phone call: Emergency

Use cases:
├─ Incident response: "System is down, fix it!"
├─ Proactive: "Disk filling up, add space"
├─ SLA breach: "Latency too high, investigate"
└─ Security: "Unusual activity detected"
```

### Log Aggregation

```
PROBLEM: Logs scattered across servers

Without aggregation:
├─ Server 1: /var/log/app.log
├─ Server 2: /var/log/app.log
├─ Server 3: /var/log/app.log
├─ ... (100 servers)
└─ Must SSH to each server to read logs!

Debugging:
├─ User reports error at 10:05 AM
├─ Which server handled it? Unknown
├─ SSH to server 1: grep "error" app.log
├─ SSH to server 2: grep "error" app.log
├─ ... repeat 100 times
└─ Takes hours!


SOLUTION: Centralized logging (ELK Stack)

Architecture:
├─ Server 1 → Logs → Filebeat → Logstash
├─ Server 2 → Logs → Filebeat → Logstash
├─ Server 3 → Logs → Filebeat → Logstash
├─ Logstash: Parse, filter, enrich
├─ Elasticsearch: Store, index logs
└─ Kibana: Search, visualize logs

Query:
├─ Search: "ERROR" AND timestamp:[10:04 TO 10:06]
├─ Results: All errors across all servers
├─ Found: Server 47 had the error
├─ Time: < 1 second!
└─ Fast debugging!


ELK STACK:

Elasticsearch:
├─ Stores logs as documents
├─ Full-text search (fast!)
├─ Scales horizontally
└─ Think: Google for logs

Logstash:
├─ Collects logs from servers
├─ Parses: Extract fields from text
├─ Filters: Enrich with metadata
├─ Sends to Elasticsearch
└─ Think: Log processing pipeline

Kibana:
├─ Web UI for searching logs
├─ Create dashboards
├─ Visualize trends
├─ Set up alerts
└─ Think: UI for Elasticsearch
```

### Monitoring & Metrics

```
PROMETHEUS WORKFLOW:

1. Application exposes metrics:
   GET /metrics
   Returns:
   ├─ requests_total{path="/api"} 1000
   ├─ request_duration_seconds 0.045
   ├─ memory_bytes 1000000
   └─ errors_total{code="500"} 5

2. Prometheus scrapes metrics:
   ├─ Every 15 seconds (configurable)
   ├─ From all targets
   ├─ Stores in time-series database
   └─ Can query historical data

3. Grafana visualizes:
   ├─ Dashboard: CPU, memory, requests
   ├─ Graphs: Time-series charts
   ├─ Real-time updates
   └─ Team views health at a glance

4. Alertmanager alerts:
   ├─ Rule: cpu_usage > 80 for 5m
   ├─ Fires: When condition true
   ├─ Notifies: PagerDuty, Slack, email
   └─ Engineers respond


GRAFANA DASHBOARD:

Panel 1: Request Rate
├─ Query: rate(requests_total[5m])
├─ Shows: Requests per second
├─ Graph type: Line chart
└─ Updates: Every 5 seconds

Panel 2: Error Rate
├─ Query: rate(errors_total[5m]) / rate(requests_total[5m])
├─ Shows: Error percentage
├─ Graph type: Line chart
├─ Alert: If > 1%

Panel 3: Latency (P99)
├─ Query: histogram_quantile(0.99, request_duration_seconds_bucket)
├─ Shows: 99th percentile latency
├─ Graph type: Line chart
└─ Alert: If > 500ms

Panel 4: Active Users
├─ Query: active_users
├─ Shows: Current logged-in users
├─ Graph type: Gauge
└─ Business metric
```

### Alert Best Practices

```
GOOD ALERT:

Alert: High Error Rate
├─ Condition: error_rate > 1% for 5 minutes
├─ Severity: Critical
├─ Notification: PagerDuty (page on-call)
├─ Runbook: Link to debugging steps
├─ Context: Which service, what time
└─ Actionable: Clear what to fix

Result:
✅ Engineer knows what's wrong
✅ Has steps to fix it
✅ Can resolve quickly


BAD ALERT:

Alert: Something is wrong
├─ Condition: Unknown
├─ Severity: Unknown
├─ Notification: Email to everyone
├─ Runbook: None
├─ Context: None
└─ Not actionable

Result:
❌ Engineer confused
❌ No idea what to fix
❌ Wastes time investigating
❌ Alert fatigue (ignore future alerts)


ALERT FATIGUE:

Problem:
├─ Too many alerts (50/day)
├─ Most are false positives
├─ Engineers ignore alerts
├─ Real issue: Missed!
└─ System down for hours

Solution:
├─ Fewer, better alerts
├─ Only alert on actionable issues
├─ Group similar alerts
├─ Escalation policies
└─ Regular review and tuning
```

---

## 🔬 Advanced Explanation

### Structured Logging

```
UNSTRUCTURED LOGGING (Bad):

Log entry:
"User 123 logged in from IP 192.168.1.1 at 10:00:01"

Problems:
├─ Text parsing required
├─ Hard to query (regex)
├─ Inconsistent format
├─ No metadata
└─ Slow searches


STRUCTURED LOGGING (Good):

Log entry (JSON):
{
  "timestamp": "2025-11-30T10:00:01Z",
  "level": "INFO",
  "message": "User logged in",
  "user_id": 123,
  "ip_address": "192.168.1.1",
  "session_id": "abc123",
  "trace_id": "xyz789"
}

Benefits:
✅ Easy to parse
✅ Fast queries (indexed fields)
✅ Consistent format
✅ Rich metadata
✅ Correlation (trace_id)

Query examples:
├─ Find all logs for user_id=123
├─ Find all logs from IP=192.168.1.1
├─ Find all logs with trace_id=xyz789
└─ Fast and precise!
```

### Log Sampling

```
PROBLEM: Too many logs

High-traffic service:
├─ 10,000 requests/second
├─ Each request: 5 log lines
├─ Total: 50,000 logs/second
├─ Per day: 4.3 billion logs
├─ Storage: 4.3 TB/day (uncompressed)
└─ Cost: Astronomical!


SOLUTION: Intelligent sampling

Strategy 1: Sample by percentage
├─ Log 10% of requests
├─ Storage: 430 GB/day
├─ Cost: 90% reduction
└─ Issue: Miss rare errors

Strategy 2: Sample by error
├─ Log all errors (100%)
├─ Log 10% of success (sample)
├─ Storage: Low
├─ Benefit: Catch all problems!
└─ Recommended

Strategy 3: Adaptive sampling
├─ Slow requests (>100ms): Log 100%
├─ Normal requests: Log 10%
├─ Fast requests (<10ms): Log 1%
└─ Optimal balance
```

### Distributed Tracing Integration

```
CORRELATION: Logs + Traces

Request flow:
├─ API Gateway (trace_id=abc123)
│  └─ Log: "Request received" (trace_id=abc123)
├─ Auth Service (trace_id=abc123, span_id=auth_001)
│  └─ Log: "Token validated" (trace_id=abc123)
├─ Order Service (trace_id=abc123, span_id=order_001)
│  └─ Log: "Order created" (trace_id=abc123)
└─ Payment Service (trace_id=abc123, span_id=pay_001)
   └─ Log: "Payment processed" (trace_id=abc123)

Benefit:
├─ Trace shows: Which services involved
├─ Logs show: What happened in each
├─ Combined: Complete picture
└─ Fast debugging!

Search:
├─ Query logs: trace_id=abc123
├─ Returns: All logs for this request
├─ Across all services
└─ Full story!
```

---

## 🐍 Python Code Example

### ❌ Without Proper Logging

```python
# ===== NO LOGGING =====

from flask import Flask

app = Flask(__name__)

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create order - no logging"""
    
    try:
        order = process_order(request.json)
        return {'order_id': order.id}
    except Exception as e:
        # Silent failure!
        return {'error': 'Failed'}, 500

# Problems:
# ❌ No logs
# ❌ Can't debug issues
# ❌ No visibility
# ❌ No metrics
```

### ✅ With Structured Logging

```python
# ===== WITH STRUCTURED LOGGING =====

from flask import Flask, request
import logging
import json
from datetime import datetime

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

class StructuredLogger:
    """Structured JSON logger"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def log(self, level, message, **kwargs):
        """Log structured JSON"""
        
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message,
            **kwargs
        }
        
        self.logger.log(
            getattr(logging, level),
            json.dumps(log_entry)
        )

structured_logger = StructuredLogger(logger)

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create order with logging"""
    
    user_id = request.json.get('user_id')
    
    structured_logger.log(
        'INFO',
        'Order creation started',
        user_id=user_id,
        endpoint='/api/orders',
        method='POST'
    )
    
    try:
        start_time = time.time()
        
        order = process_order(request.json)
        
        duration = time.time() - start_time
        
        structured_logger.log(
            'INFO',
            'Order created successfully',
            user_id=user_id,
            order_id=order.id,
            duration_ms=duration * 1000
        )
        
        return {'order_id': order.id}
    
    except Exception as e:
        structured_logger.log(
            'ERROR',
            'Order creation failed',
            user_id=user_id,
            error=str(e),
            error_type=type(e).__name__
        )
        
        return {'error': 'Failed'}, 500

# Log output (JSON):
# {"timestamp": "2025-11-30T10:00:01Z", "level": "INFO", 
#  "message": "Order created successfully", "user_id": 123, 
#  "order_id": 456, "duration_ms": 45.2}

# Benefits:
# ✅ Structured JSON logs
# ✅ Easy to parse and query
# ✅ Rich metadata
# ✅ Production-ready
```

### ✅ Production Observability Stack

```python
# ===== PRODUCTION OBSERVABILITY =====

from flask import Flask, request
import logging
from prometheus_client import Counter, Histogram, generate_latest
from opentelemetry import trace
import json

app = Flask(__name__)

# Structured logging
structured_logger = StructuredLogger(logging.getLogger(__name__))

# Prometheus metrics
requests_total = Counter(
    'requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'request_duration_seconds',
    'Request duration',
    ['endpoint']
)

# OpenTelemetry tracing
tracer = trace.get_tracer(__name__)

class ObservabilityMiddleware:
    """Complete observability: logs + metrics + traces"""
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        """Wrap request with observability"""
        
        # Start trace
        with tracer.start_as_current_span("http_request") as span:
            trace_id = span.get_span_context().trace_id
            
            # Log request start
            structured_logger.log(
                'INFO',
                'Request received',
                method=environ['REQUEST_METHOD'],
                path=environ['PATH_INFO'],
                trace_id=format(trace_id, '032x')
            )
            
            # Track metrics
            start_time = time.time()
            
            def custom_start_response(status, headers):
                # Extract status code
                status_code = int(status.split()[0])
                
                # Record metrics
                duration = time.time() - start_time
                request_duration.labels(
                    endpoint=environ['PATH_INFO']
                ).observe(duration)
                
                requests_total.labels(
                    method=environ['REQUEST_METHOD'],
                    endpoint=environ['PATH_INFO'],
                    status=status_code
                ).inc()
                
                # Log completion
                structured_logger.log(
                    'INFO',
                    'Request completed',
                    method=environ['REQUEST_METHOD'],
                    path=environ['PATH_INFO'],
                    status=status_code,
                    duration_ms=duration * 1000,
                    trace_id=format(trace_id, '032x')
                )
                
                return start_response(status, headers)
            
            return self.app(environ, custom_start_response)

# Apply middleware
app.wsgi_app = ObservabilityMiddleware(app.wsgi_app)

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

# Benefits:
# ✅ Logs: Structured JSON with trace_id
# ✅ Metrics: Prometheus-compatible
# ✅ Traces: Distributed tracing
# ✅ Complete observability
# ✅ Production-ready
```

---

## 💡 Mini Project: "Build Observability"

### Phase 1: Logging ⭐

**Requirements:**
- Structured logging (JSON)
- Log levels (DEBUG, INFO, ERROR)
- Log aggregation (ELK)
- Search and filter

---

### Phase 2: Monitoring ⭐⭐

**Requirements:**
- Prometheus metrics
- Grafana dashboards
- Real-time visualization
- Historical trending

---

### Phase 3: Complete Stack ⭐⭐⭐

**Requirements:**
- Logs + Metrics + Traces
- Alert rules (Alertmanager)
- PagerDuty integration
- Runbooks and documentation

---

## ⚖️ Observability Tools

| Tool | Purpose | Pros | Cons |
|------|---------|------|------|
| **ELK Stack** | Logging | Powerful search | Complex setup |
| **Prometheus** | Metrics | Time-series | Storage limits |
| **Jaeger** | Tracing | Distributed | Overhead |
| **Datadog** | All-in-one | Easy | Expensive |

---

## ❌ Common Mistakes

### Mistake 1: Logging Everything

```python
# ❌ Log every operation
for i in range(1000):
    logger.info(f"Processing item {i}")
# Generates 1000 logs (spam!)

# ✅ Log milestones
logger.info(f"Processing {len(items)} items")
# Process items...
logger.info(f"Processing complete")
```

### Mistake 2: No Alert Runbooks

```python
# ❌ Alert without context
Alert: "CPU high"
# What do I do?

# ✅ Alert with runbook
Alert: "CPU high - Check process consuming CPU, 
        restart if necessary. Runbook: wiki.com/cpu-runbook"
```

### Mistake 3: Ignoring Log Storage Costs

```python
# ❌ Keep all logs forever
# Storage grows infinitely
# Costs explode

# ✅ Retention policy
# Keep 30 days in hot storage
# Archive 90 days in cold storage
# Delete after 1 year
```

---

## 📚 Additional Resources

**Logging:**
- [ELK Stack](https://www.elastic.co/elk-stack)
- [Structured Logging](https://www.structuredlogging.com/)

**Monitoring:**
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)

**Alerting:**
- [PagerDuty](https://www.pagerduty.com/)
- [Alert Best Practices](https://docs.pagerduty.com/docs/best-practices)


---

## 🎯 Before You Leave

**Can you answer these?**

1. **Logs vs metrics vs traces?**
   - Answer: Logs = what happened; Metrics = how performing; Traces = request path

2. **Why structured logging?**
   - Answer: Easy to parse, query, and analyze

3. **Alert fatigue?**
   - Answer: Too many alerts, engineers ignore them

4. **ELK Stack components?**
   - Answer: Elasticsearch, Logstash, Kibana

5. **Good alert characteristics?**
   - Answer: Actionable, has runbook, provides context

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **3 AM Page:** "System is down!"
>
> **Engineer:** Checks logs → Empty
>
> **Engineer:** Checks metrics → All good
>
> **Engineer:** Checks alerts → Silent
>
> **Engineer:** "How do I even debug this?"
>
> **Boss:** "That's why we pay you the big bucks!"
>
> **Engineer:** "I need better observability..." 😤

---

[← Back to Main](../README.md) | [Previous: SSL/TLS & HTTPS](43-ssl-tls-https.md) | [Next: Metrics (Prometheus, Grafana) →](45-metrics-prometheus.md)

---

**Last Updated:** November 30, 2025  
**Difficulty:** ⭐⭐⭐ Intermediate-Advanced (operations)  
**Time to Read:** 25 minutes  
**Time to Implement:** 6-10 hours per phase  

---

*Logging, Monitoring, and Alerting: Know what's happening before your users tell you.* 🚀