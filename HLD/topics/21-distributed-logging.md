# 21. Distributed Logging & Monitoring

Monitoring is how you find out your system is broken. Logging is how you figure out which part broke and why. Together, they're like a detective investigating a crime scene, except the scene is constantly on fire and you're underwater. 🔍🔥

[← Back to Main](../README.md) | [Pub/Sub Systems](20-pubsub-systems.md) | [Rate Limiting & Throttling](22-rate-limiting.md)

---

## 🎯 Quick Summary

**Distributed Logging & Monitoring** is how you see what's happening in production systems at scale. Logging captures detailed events (what happened), Monitoring watches metrics (health status). ELK Stack, Datadog, Splunk, Prometheus, Grafana are industry standard. Without them: you're flying blind. With them: you catch issues before users notice. Essential for reliability, performance debugging, compliance, and post-mortems.

Think of it as: **Logging = What Happened, Monitoring = How We're Doing**

---

## 🌟 Beginner Explanation

### Logs vs Metrics

**LOGS (What Happened):**

```
User logs in: 2025-11-10 18:30:45.123 [INFO] user=alice password=correct
User makes purchase: 2025-11-10 18:31:02.456 [INFO] order=12345 amount=$50
Server error: 2025-11-10 18:31:15.789 [ERROR] db_connection_timeout after 30s

Details:
├─ Timestamp
├─ Level (INFO, WARN, ERROR)
├─ Message
├─ Context (user_id, request_id, etc)

Useful for: Debugging, auditing, understanding sequences
Problem: Massive volume (1 million logs/second possible)
```

**METRICS (How We're Doing):**

```
CPU Usage: 45%
Memory: 2.5GB / 8GB
Requests/second: 1000
Error Rate: 0.5%
Latency (p99): 250ms
Disk: 80% full

Details:
├─ Single number (gauge, counter, histogram)
├─ Timestamped
├─ Aggregated (not every event)
└─ Queryable

Useful for: Health status, trends, alerting
Problem: Lose detail (1000 reqs/sec = 1 data point)
```

### Single Server vs Distributed

**SINGLE SERVER (Logs):**

```
Server1: All logs in /var/log/app.log

Problem:
├─ Server crashes: Logs gone (if not backed up)
├─ Disk fills: Logs stop writing
├─ Can't search easily
├─ No real-time view
```

**DISTRIBUTED (Logs Centralized):**

```
Server1 → Log Collector → Central Log Storage (Elasticsearch)
Server2 → Log Collector → Central Log Storage
Server3 → Log Collector → Central Log Storage
...
Server100 → Log Collector → Central Log Storage

Then:
Dashboards, Search, Alerts all read from central storage

Benefits:
✅ One place to search all logs
✅ Survives server crashes
✅ Real-time search
✅ Build dashboards
✅ Set alerts
```

### The Stack

```
LOGGING STACK:

App → Logs → Log Collector → Message Queue → Storage → Search/Dashboard

Example (ELK):
App → Logback/Winston → Fluentd → Kafka → Elasticsearch → Kibana

Example (Cloud):
App → CloudWatch → CloudWatch Logs → CloudWatch Insights

Example (SaaS):
App → Datadog Agent → Datadog → Datadog Dashboard
```

---

## 🔬 Advanced Explanation

### Centralized Logging Architecture

**LOG COLLECTION PATTERN:**

```
┌─────────────────────────────────────────────┐
│ Application Servers                          │
├─────────────────────────────────────────────┤
│ App1: stdout/stderr, files                  │
│ App2: stdout/stderr, files                  │
│ App3: stdout/stderr, files                  │
└─────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────┐
│ Log Collection Agents                        │
├─────────────────────────────────────────────┤
│ Fluentd/Logstash/Filebeat (on each server) │
│ - Read logs from files                      │
│ - Parse/transform                           │
│ - Send to central storage                   │
└─────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────┐
│ Central Storage                              │
├─────────────────────────────────────────────┤
│ Elasticsearch / S3 / BigQuery                │
│ - Indexed for fast search                   │
│ - Retention policy (30 days, etc)          │
│ - Replicated (multiple copies)              │
└─────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────┐
│ Query/Visualization                         │
├─────────────────────────────────────────────┤
│ Kibana / Splunk / Datadog                   │
│ - Search logs by any field                  │
│ - Create dashboards                         │
│ - Set alerts                                │
│ - Generate reports                          │
└─────────────────────────────────────────────┘
```

### Structured Logging

**UNSTRUCTURED LOGS (Hard to Search):**

```
2025-11-10 18:30:45 User alice successfully authenticated and created order 12345 for $50 with 5 items from NY
```

Problems:
- Can't easily search "orders over $100"
- Can't aggregate "orders by region"
- Hard to parse programmatically

**STRUCTURED LOGS (JSON, Easy to Search):**

```json
{
  "timestamp": "2025-11-10T18:30:45Z",
  "level": "INFO",
  "event": "order_created",
  "user_id": "alice",
  "order_id": 12345,
  "amount": 50,
  "currency": "USD",
  "items_count": 5,
  "region": "NY",
  "request_id": "req-xyz789"
}
```

Benefits:
✅ Query: `amount > 100 AND region = "NY"`
✅ Aggregate: `sum(amount) GROUP BY region`
✅ Easy to parse
✅ Add new fields without breaking

### Monitoring: Metrics

**TYPES OF METRICS:**

```
1. GAUGE (Current value)
   └─ CPU usage: 45%
   └─ Memory: 2.5GB
   └─ Active connections: 1000

2. COUNTER (Only increases)
   └─ Total requests: 1,000,000
   └─ Total errors: 500
   └─ Total bytes sent: 10TB

3. HISTOGRAM (Distribution)
   └─ Request latency: p50=50ms, p95=100ms, p99=250ms
   └─ Response sizes: min=10B, max=10MB, avg=500KB

4. RATE (Per time unit)
   └─ Requests per second: 1000
   └─ Errors per minute: 5
   └─ Bytes per second: 10MB
```

**METRIC COLLECTION:**

```
Application emits metrics:
│
├─ Prometheus scrapes (pulls):
│  └─ Every 15 seconds hit /metrics endpoint
│  └─ Prometheus stores in time-series DB
│
└─ Push model:
   └─ App sends to collector
   └─ Collector aggregates
   └─ Storage ingests

Visualization:
Prometheus → Grafana (pretty dashboards)
```

### Alerting

**SIMPLE ALERT:**

```
Alert Rule: CPU > 80% for 5 minutes
└─ IF avg(cpu_usage, 5min) > 80%
   └─ THEN send to on_call

Trigger:
├─ 18:00 CPU hits 82%
├─ Alert fires at 18:05 (5 min threshold)
├─ PagerDuty wakes up on-call
├─ Slack: "HIGH CPU on server-1"
├─ On-call investigates
```

**COMPLEX ALERT (Composition):**

```
Alert Rule: High Error Rate + High Latency
└─ IF (error_rate > 5%) AND (p99_latency > 1s) for 2 min
   └─ THEN page on-call

Reason: Combination indicates real issue
- Just high latency? Could be GC pause
- Just high errors? Could be one broken endpoint
- Both? System overloaded, need to scale!
```

### Tracing in Distributed Systems

**PROBLEM: Request spans multiple servers**

```
User Request: GET /user/123/orders

Server A: Handle request
├─ Call Server B for user data

Server B: Fetch user
├─ Call Server C for user details
├─ Call Server D for address

Server C: Return user details

Server D: Return address

Server B: Aggregate, return

Server A: Call Server E for orders

Server E: Return orders

Server A: Aggregate, return to user

Total latency: 500ms
Which part was slow? Unknown without tracing!
```

**SOLUTION: Distributed Tracing**

```
Generate trace_id = "trace-xyz789"

Pass trace_id through all services:
├─ Server A: span-1 (0-500ms) [calls B, E]
│  ├─ Server B: span-2 (10-200ms) [calls C, D]
│  │  ├─ Server C: span-3 (15-50ms)
│  │  └─ Server D: span-4 (55-180ms)
│  └─ Server E: span-5 (250-480ms)

Visualization (Jaeger, Zipkin):
Shows exact timing, which service was slow, dependencies

Result:
├─ Server E took 230ms (bottleneck!)
├─ Server D took 125ms (also slow)
├─ Fix these and total latency drops
```

---

## 🐍 Python Code Example

### ❌ Without Logging (Blind)

```python
# ===== WITHOUT LOGGING (BLIND) =====

import time

def process_order(order_id):
    """Process order without logging"""
    
    # Silent failures - no visibility!
    user = get_user(order_id)
    
    # If this fails: No log, just exception
    amount = calculate_price(user)
    
    # If slow: No indication why
    charge_credit_card(amount)
    
    # If fails: Silent
    send_confirmation_email(user)
    
    return True

# Problem:
# ❌ Order failed 3 hours ago
# ❌ User complained
# ❌ Can't find logs (they don't exist)
# ❌ Can't reproduce issue
# ❌ Spending hours debugging
```

### ✅ Simple Logging (File-based)

```python
# ===== SIMPLE LOGGING (FILE-BASED) =====

import logging
import json
from datetime import datetime

# Setup logging to file
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def process_order(order_id):
    """Process order with basic logging"""
    
    try:
        logging.info(f"Processing order {order_id}")
        
        user = get_user(order_id)
        logging.info(f"User retrieved: {user.id}")
        
        amount = calculate_price(user)
        logging.info(f"Price calculated: ${amount}")
        
        charge_credit_card(amount)
        logging.info(f"Payment charged: ${amount}")
        
        send_confirmation_email(user)
        logging.info(f"Confirmation email sent to {user.email}")
        
        logging.info(f"Order {order_id} completed successfully")
        return True
    
    except Exception as e:
        logging.error(f"Order {order_id} failed: {e}")
        return False

# Benefits:
# ✅ Can see what happened
# ✅ Error context
# ✅ Timeline of events

# Problems:
# ❌ Only on this server
# ❌ Hard to search across servers
# ❌ Manual parsing
# ❌ Log file grows unbounded
```

### ✅ Production Logging (Structured, Centralized)

```python
# ===== PRODUCTION LOGGING =====

import json
import sys
from datetime import datetime
from typing import Dict, Any
import uuid

class StructuredLogger:
    """Structured logging for distributed systems"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.request_id = None
    
    def set_request_id(self, request_id: str):
        """Set request_id for tracing"""
        self.request_id = request_id
    
    def log(self, level: str, event: str, **kwargs):
        """Log structured event as JSON"""
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "level": level,
            "event": event,
            "request_id": self.request_id,
        }
        
        # Add custom fields
        log_entry.update(kwargs)
        
        # Output as JSON (goes to stdout → collected centrally)
        print(json.dumps(log_entry))
    
    def info(self, event: str, **kwargs):
        self.log("INFO", event, **kwargs)
    
    def error(self, event: str, **kwargs):
        self.log("ERROR", event, **kwargs)
    
    def warning(self, event: str, **kwargs):
        self.log("WARNING", event, **kwargs)

class OrderService:
    """Order service with structured logging"""
    
    def __init__(self):
        self.logger = StructuredLogger("order-service")
    
    def process_order(self, order_id: int, user_id: str):
        """Process order with structured logging"""
        
        # Set request tracking
        request_id = str(uuid.uuid4())
        self.logger.set_request_id(request_id)
        
        self.logger.info(
            "order_processing_started",
            order_id=order_id,
            user_id=user_id
        )
        
        try:
            # Get user
            user = self.get_user(user_id)
            self.logger.info(
                "user_retrieved",
                user_id=user_id,
                user_name=user.get("name")
            )
            
            # Calculate price
            amount = self.calculate_price(user, order_id)
            self.logger.info(
                "price_calculated",
                amount=amount,
                currency="USD"
            )
            
            # Charge card
            charge_result = self.charge_credit_card(amount)
            self.logger.info(
                "payment_charged",
                amount=amount,
                transaction_id=charge_result.get("id")
            )
            
            # Send email
            self.send_confirmation_email(user)
            self.logger.info(
                "confirmation_email_sent",
                user_email=user.get("email")
            )
            
            # Success
            self.logger.info(
                "order_completed",
                order_id=order_id,
                total_amount=amount
            )
            
            return True
        
        except Exception as e:
            self.logger.error(
                "order_processing_failed",
                error_type=type(e).__name__,
                error_message=str(e),
                order_id=order_id
            )
            return False
    
    def get_user(self, user_id: str):
        # Mock implementation
        return {"id": user_id, "name": "Alice", "email": "alice@example.com"}
    
    def calculate_price(self, user, order_id):
        return 50.00
    
    def charge_credit_card(self, amount):
        return {"id": "txn-123", "status": "success"}
    
    def send_confirmation_email(self, user):
        pass

# Usage
print("=== STRUCTURED LOGGING ===\n")

service = OrderService()
service.process_order(order_id=12345, user_id="alice")

# Output (JSON, easily parsed):
# {"timestamp": "2025-11-10T18:30:45Z", "service": "order-service", 
#  "level": "INFO", "event": "order_processing_started", ...}
# {"timestamp": "2025-11-10T18:30:46Z", "service": "order-service",
#  "level": "INFO", "event": "user_retrieved", ...}
```

### ✅ Monitoring & Metrics

```python
# ===== MONITORING & METRICS =====

import time
from dataclasses import dataclass
from typing import Dict

@dataclass
class MetricsCollector:
    """Collect and expose metrics"""
    
    def __init__(self):
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, list] = {}
    
    def increment_counter(self, name: str, value: int = 1):
        """Increment counter"""
        self.counters[name] = self.counters.get(name, 0) + value
    
    def set_gauge(self, name: str, value: float):
        """Set gauge value"""
        self.gauges[name] = value
    
    def record_histogram(self, name: str, value: float):
        """Record value for histogram"""
        if name not in self.histograms:
            self.histograms[name] = []
        self.histograms[name].append(value)
    
    def get_prometheus_metrics(self) -> str:
        """Export in Prometheus format"""
        output = []
        
        # Counters
        for name, value in self.counters.items():
            output.append(f"{name} {value}")
        
        # Gauges
        for name, value in self.gauges.items():
            output.append(f"{name} {value}")
        
        # Histograms (simplified)
        for name, values in self.histograms.items():
            if values:
                p50 = sorted(values)[len(values)//2]
                p99 = sorted(values)[int(len(values)*0.99)]
                output.append(f"{name}_p50 {p50}")
                output.append(f"{name}_p99 {p99}")
        
        return "\n".join(output)

class MonitoredOrderService:
    """Order service with metrics"""
    
    def __init__(self, metrics: MetricsCollector):
        self.metrics = metrics
    
    def process_order(self, order_id, amount):
        """Process with metrics"""
        
        start = time.time()
        
        try:
            # Process order
            time.sleep(0.1)  # Simulate work
            
            # Track metrics
            self.metrics.increment_counter("orders_processed")
            self.metrics.increment_counter("revenue", int(amount))
            
        except Exception as e:
            self.metrics.increment_counter("orders_failed")
            raise
        
        finally:
            # Always record latency
            elapsed = (time.time() - start) * 1000  # ms
            self.metrics.record_histogram("order_processing_time_ms", elapsed)

# Usage
print("=== MONITORING ===\n")

metrics = MetricsCollector()
service = MonitoredOrderService(metrics)

# Process orders
for i in range(5):
    service.process_order(f"order-{i}", 50 + i*10)

# Export metrics
print(metrics.get_prometheus_metrics())

# Output:
# orders_processed 5
# revenue 300
# order_processing_time_ms_p50 100
# order_processing_time_ms_p99 110
```

---

## 💡 Mini Project: "Build a Monitoring System"

### Phase 1: Simple Logging ⭐

**Requirements:**
- Structured JSON logging
- Log levels (INFO, WARN, ERROR)
- Request ID tracking
- File output

---

### Phase 2: Centralized ⭐⭐

**Requirements:**
- Collect from multiple servers
- Central storage (Elasticsearch)
- Search interface
- Basic dashboards
- Retention policy

---

### Phase 3: Full Stack ⭐⭐⭐

**Requirements:**
- Metrics collection
- Alerting rules
- Distributed tracing
- Grafana dashboards
- PagerDuty integration

---

## ⚖️ Logging Solutions Comparison

| Solution | Type | Cost | Setup | Scale |
|----------|------|------|-------|-------|
| **ELK Stack** | Self-hosted | Low | Medium | High |
| **Splunk** | Enterprise | High | High | Very High |
| **Datadog** | SaaS | Medium | Low | Very High |
| **CloudWatch** | AWS | Medium | Very Low | High |
| **Grafana** | Self-hosted | Low | Medium | High |

---

## ❌ Common Mistakes

### Mistake 1: Logging Everything

```python
# ❌ Log every variable
for i in range(1000000):
    logger.info(f"Processing item {i}")
    # 1 million log lines!
    # Storage overflows, becomes unmanageable

# ✅ Log important events
for i in range(1000000):
    if i % 10000 == 0:
        logger.info(f"Progress: {i}/1000000")
    # Only 100 log lines, still informative
```

### Mistake 2: Unstructured Logs

```python
# ❌ Unstructured
logger.info("User alice processed order 12345 for 50 dollars")
# Can't search: amount > 100
# Can't aggregate by user

# ✅ Structured
logger.info("order_processed", user="alice", order_id=12345, amount=50)
# Can search and aggregate easily
```

### Mistake 3: No Retention Policy

```python
# ❌ Store logs forever
# 1000 servers × 1GB/day = 1TB/day!
# After 1 year: 365TB = $365,000

# ✅ Set retention policy
# Keep 30 days in hot storage (search)
# Archive to cold storage after 30 days (cheap)
# Delete after 1 year (or comply with retention laws)
```

---

## 📚 Additional Resources

**ELK Stack:**
- [Elasticsearch](https://www.elastic.co/)
- [Kibana](https://www.elastic.co/kibana)
- [Logstash](https://www.elastic.co/logstash)

**Monitoring:**
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)
- [Datadog](https://www.datadoghq.com/)

**Tracing:**
- [Jaeger](https://www.jaegertracing.io/)
- [Zipkin](https://zipkin.io/)


---

## 🎯 Before You Leave

**Can you answer these?**

1. **What's the difference between logs and metrics?**
   - Answer: Logs = detailed events; Metrics = health status

2. **Why centralize logs?**
   - Answer: Search across servers, survive crashes, real-time visibility

3. **What's structured logging?**
   - Answer: JSON format for easy parsing and querying

4. **What's distributed tracing?**
   - Answer: Follow request through multiple services

5. **What's a good retention policy?**
   - Answer: Hot (30 days searchable), cold (365 days archived), delete after

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **Manager:** "Why is the system slow?"
>
> **Engineer:** "I don't know, no monitoring."
>
> **Manager:** "Add monitoring!"
>
> **Engineer (3 hours later):** "The problem is us adding monitoring."
>
> **Manager:** "..."
>
> **Engineer:** "Yeah, log collection was 40% of CPU." 💀

---

[← Back to Main](../README.md) | [Pub/Sub Systems](20-pubsub-systems.md) | [Rate Limiting & Throttling](22-rate-limiting.md)

---

**Last Updated:** November 10, 2025  
**Difficulty:** ⭐⭐ Beginner-Intermediate (operations)  
**Time to Read:** 26 minutes  
**Time to Build System:** 4-7 hours per phase  

---

*Monitoring: The only thing between "everything's fine" and "it's been down for 6 hours."* 🚀