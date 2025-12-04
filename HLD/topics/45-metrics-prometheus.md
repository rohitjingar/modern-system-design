# 45. Metrics (Prometheus, Grafana)

You need to know what's happening in your system, so you collect metrics. You collect so many metrics that you run out of storage. So you delete old metrics. Then the one time you need historical data? Gone. You invent compression schemes. Still not enough. You build sophisticated sampling. Now you have no data when things go wrong. Metrics: helping you understand nothing in excruciating detail! 📊😤

[← Back to Main](../README.md) | [Previous: Logging, Monitoring & Observability](44-logging-monitoring-alerting.md) | [Next: Tracing (Jaeger, OpenTelemetry)](46-tracing-jaeger.md)

---

## 🎯 Quick Summary

**Metrics** are quantitative measurements (CPU, memory, latency, errors). **Prometheus** scrapes time-series data every 15 seconds. **Grafana** visualizes metrics in dashboards. Netflix generates billions of metrics daily. Google uses similar systems internally. Metrics enable: alerting (CPU > 80%), trending (traffic growing), debugging (what changed?). Trade-off: storage (massive), cardinality explosion (too many labels), staleness (15s delay). Essential for production visibility.

Think of it as: **Metrics = System Heartbeat**

---

## 🌟 Beginner Explanation

### Types of Metrics

```
COUNTER (Always increasing):

Request counter:
├─ T=0: requests_total = 1000
├─ T=1: requests_total = 1001
├─ T=2: requests_total = 1005
├─ T=3: requests_total = 1010
└─ Only goes up (or resets on restart)

Uses:
├─ Total requests
├─ Total errors
├─ Total bytes sent
└─ Can only increase

Useful for:
├─ Rate calculation (requests/sec = delta/time)
├─ Error counting
├─ Tracking work done


GAUGE (Can go up or down):

Memory usage:
├─ T=0: memory_bytes = 1,000,000,000
├─ T=1: memory_bytes = 1,100,000,000 (↑ increased)
├─ T=2: memory_bytes = 900,000,000 (↓ decreased)
├─ T=3: memory_bytes = 950,000,000 (↑ increased again)
└─ Goes up and down freely

Uses:
├─ Current memory
├─ Current connections
├─ Current queue length
└─ Can be any value

Useful for:
├─ Current state
├─ Capacity tracking
├─ Resource utilization


HISTOGRAM (Distribution of values):

Request latency:
├─ Bucket < 10ms: 500 requests
├─ Bucket < 50ms: 4,500 requests
├─ Bucket < 100ms: 4,800 requests
├─ Bucket < 500ms: 4,950 requests
├─ Bucket < 1000ms: 4,999 requests
└─ Bucket < inf: 5000 requests

Useful for:
├─ Percentiles (p50, p99, p999)
├─ Understanding distribution
├─ Alerting on slowness


SUMMARY (Histogram alternative):

Request latency (quantiles):
├─ p50 (median): 45ms
├─ p90: 120ms
├─ p99: 450ms
├─ p99.9: 850ms
├─ Total count: 5000
└─ Total sum: 225,000ms

Difference from histogram:
├─ Histogram: Calculated by client
├─ Summary: Calculated by server
└─ Both allow percentile calculation
```

### Prometheus Architecture

```
SCRAPING (Pull model):

Prometheus server:
├─ Every 15 seconds (configurable)
├─ Scrapes each target
├─ GET http://target:9090/metrics
├─ Receives metrics text format
├─ Stores in time-series database
└─ Repeat forever

Target (application):
├─ Exports metrics endpoint
├─ GET /metrics returns:
│  ├─ requests_total{path="/api"} 1000
│  ├─ request_duration_seconds 0.045
│  ├─ memory_bytes 1000000
│  └─ ... more metrics
└─ Prometheus scrapes it

Storage:
├─ Time-series database (on disk)
├─ Fast query for ranges
├─ Stores: (metric, labels, timestamp, value)
└─ Default: 15 days retention

Query:
├─ PromQL (Prometheus Query Language)
├─ SELECT requests_total WHERE path="/api"
├─ Returns: Time series of values
└─ Grafana visualizes


PUSH MODEL (Alternative):

Some systems push metrics (instead of pull):
├─ Application sends data
├─ To: Metrics aggregator
├─ Every: 1 minute (or batched)

Push example:
├─ Datadog
├─ CloudWatch
├─ InfluxDB
└─ (Pull is more common)

Prometheus uses PULL (not push)
```

### PromQL (Query Language)

```
BASIC QUERIES:

Get all CPU usage:
├─ cpu_usage_percent
└─ Returns: All CPU metrics

Filter by label:
├─ cpu_usage_percent{host="server1"}
└─ Returns: CPU only for server1

Multiple labels:
├─ requests_total{path="/api", method="GET"}
└─ Returns: GET requests to /api


AGGREGATION:

Sum across instances:
├─ sum(requests_total)
└─ Returns: Total requests across all servers

Average:
├─ avg(request_duration_seconds)
└─ Returns: Average latency

Percentile:
├─ histogram_quantile(0.99, request_duration_seconds_bucket)
└─ Returns: P99 latency


TIME RANGE:

Last 5 minutes:
├─ requests_total[5m]
└─ Returns: Time series for last 5 minutes

Rate calculation:
├─ rate(requests_total[5m])
└─ Returns: Requests per second

Increase over time:
├─ increase(requests_total[1h])
└─ Returns: How many requests in last hour


ALERTING QUERIES:

Alert if CPU > 80%:
├─ cpu_usage_percent > 80
└─ Triggers: Alert when true

Alert if error rate > 1%:
├─ (rate(errors_total[5m]) / rate(requests_total[5m])) > 0.01
└─ Triggers: If error rate exceeds 1%
```

---

## 🔬 Advanced Explanation

### Cardinality Explosion

```
WHAT IS CARDINALITY?

Each unique combination of label values = 1 metric

Example:
├─ Metric: request_duration
├─ Labels: path, method, status, host

Values:
├─ path: 100 endpoints
├─ method: 5 values (GET, POST, PUT, DELETE, PATCH)
├─ status: 20 values (200, 201, 400, 401, 403, 404, 500, etc)
├─ host: 50 servers

Total cardinality:
├─ 100 × 5 × 20 × 50 = 500,000 metrics!
└─ For ONE metric type!

Problem:
├─ Storage explodes
├─ Query performance degrades
├─ RAM usage increases
└─ Prometheus slows down


PREVENTION:

1. Limit labels:
   ├─ Don't label everything
   ├─ Only label what you need
   └─ Avoid customer_id as label (infinite values!)

2. Use static labels:
   ├─ Put const values elsewhere
   ├─ Or aggregate server-side
   └─ Don't expose as labels

3. Monitor cardinality:
   ├─ Track number of metrics
   ├─ Alert if growing too fast
   └─ Investigate new labels
```

### Storage & Retention

```
STORAGE CALCULATION:

Disk space per metric:
├─ Timestamp: 8 bytes
├─ Value: 8 bytes
├─ Total: ~16 bytes per data point

Scrape interval: 15 seconds
Data points per metric per day:
├─ 24 hours × 60 min × 60 sec / 15 sec = 5,760 data points
├─ Per day per metric

If you have 10,000 metrics:
├─ 10,000 metrics × 5,760 points = 57.6M points/day
├─ 57.6M × 16 bytes = 921 MB/day
├─ 921 MB × 365 days = 336 GB/year!

With 1TB storage:
├─ 1000 GB / 336 GB per year = ~3 years

RETENTION STRATEGIES:

Default (15 days):
├─ Store: 15 days of high-resolution
├─ Delete: Older data

Tiered storage:
├─ Hot: 15 days (15 second resolution)
├─ Warm: 90 days (1 minute resolution)
├─ Cold: Archive (downsampled)

Downsampling:
├─ After 7 days: Reduce resolution
├─ Keep: 1 point per minute (was 4/min)
├─ 75% storage savings!
└─ Good for: Trending, still lose detail
```

### Grafana Dashboards

```
DASHBOARD TYPES:

Real-time (Live):
├─ Update: Every refresh (1-5 seconds)
├─ Retention: Current state
├─ Use: Current issues, active debugging
└─ Example: CPU, memory NOW

Time-series (Historical):
├─ Update: As data comes in
├─ Retention: Full history
├─ Use: Trending, capacity planning
└─ Example: CPU over last week

Heatmap:
├─ Shows: Distribution over time
├─ X-axis: Time
├─ Y-axis: Value range
├─ Color: Frequency
└─ Use: Latency distribution

Table:
├─ Shows: Raw data
├─ Sortable: By any column
├─ Use: Detailed investigation
└─ Example: Top N queries
```

---

## 🐍 Python Code Example

### ❌ Without Metrics (No Visibility)

```python
# ===== NO METRICS =====

from flask import Flask

app = Flask(__name__)

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create order - no metrics"""
    
    try:
        order = process_order(request.json)
        return {'order_id': order.id}
    except Exception as e:
        print(f"Error: {e}")  # Logging only!
        return {'error': 'Failed'}, 500

# Problems:
# ❌ No metrics
# ❌ No visibility into performance
# ❌ Can't see traffic patterns
# ❌ Can't alert on issues
# ❌ Debugging: Logs only (slow)
```

### ✅ With Prometheus Metrics

```python
# ===== WITH PROMETHEUS METRICS =====

from flask import Flask
from prometheus_client import Counter, Histogram, Gauge, generate_latest

app = Flask(__name__)

# Define metrics
requests_total = Counter(
    'requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration_seconds = Histogram(
    'request_duration_seconds',
    'HTTP request duration',
    ['endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 5.0)
)

orders_processing = Gauge(
    'orders_processing',
    'Orders currently being processed'
)

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create order with metrics"""
    
    orders_processing.inc()  # Increment gauge
    
    start_time = time.time()
    
    try:
        order = process_order(request.json)
        
        # Record success
        duration = time.time() - start_time
        request_duration_seconds.labels(endpoint='/api/orders').observe(duration)
        requests_total.labels(
            method='POST',
            endpoint='/api/orders',
            status='201'
        ).inc()
        
        return {'order_id': order.id}, 201
    
    except Exception as e:
        # Record error
        duration = time.time() - start_time
        request_duration_seconds.labels(endpoint='/api/orders').observe(duration)
        requests_total.labels(
            method='POST',
            endpoint='/api/orders',
            status='500'
        ).inc()
        
        return {'error': str(e)}, 500
    
    finally:
        orders_processing.dec()  # Decrement gauge

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus scrapes this endpoint"""
    
    return generate_latest()

# Benefits:
# ✅ Visibility into traffic
# ✅ Performance metrics
# ✅ Error tracking
# ✅ Prometheus compatible
```

### ✅ Production Metrics (Advanced)

```python
# ===== PRODUCTION METRICS =====

from prometheus_client import (
    Counter, Histogram, Gauge, Summary,
    generate_latest, CollectorRegistry,
    start_http_server
)
from functools import wraps
import time

class MetricsCollector:
    """Production-grade metrics collection"""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        self._setup_metrics()
    
    def _setup_metrics(self):
        """Define all metrics"""
        
        # Request metrics
        self.requests_total = Counter(
            'requests_total',
            'Total requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.request_duration = Histogram(
            'request_duration_seconds',
            'Request duration',
            ['endpoint'],
            buckets=(0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0),
            registry=self.registry
        )
        
        # Business metrics
        self.orders_created = Counter(
            'orders_created_total',
            'Orders created',
            ['status'],  # pending, completed, failed
            registry=self.registry
        )
        
        self.order_value = Histogram(
            'order_value_dollars',
            'Order values',
            buckets=(10, 50, 100, 500, 1000, 5000),
            registry=self.registry
        )
        
        # System metrics
        self.db_connections = Gauge(
            'db_connections_active',
            'Active database connections',
            registry=self.registry
        )
        
        self.cache_hits = Counter(
            'cache_hits_total',
            'Cache hits',
            registry=self.registry
        )
        
        self.cache_misses = Counter(
            'cache_misses_total',
            'Cache misses',
            registry=self.registry
        )
    
    def track_request(self, endpoint):
        """Decorator to track HTTP requests"""
        
        def decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                start = time.time()
                
                try:
                    result = f(*args, **kwargs)
                    status = result[1] if isinstance(result, tuple) else 200
                    return result
                
                finally:
                    duration = time.time() - start
                    method = request.method
                    
                    self.request_duration.labels(endpoint=endpoint).observe(duration)
                    self.requests_total.labels(
                        method=method,
                        endpoint=endpoint,
                        status=status
                    ).inc()
            
            return wrapped
        
        return decorator
    
    def get_metrics(self):
        """Return metrics in Prometheus format"""
        
        return generate_latest(self.registry)

# Usage
metrics = MetricsCollector()

@app.route('/api/orders', methods=['POST'])
@metrics.track_request('/api/orders')
def create_order():
    """Create order with automatic metrics"""
    
    order = process_order(request.json)
    
    # Track business metric
    metrics.orders_created.labels(status='completed').inc()
    metrics.order_value.observe(order.total_value)
    
    return {'order_id': order.id}

@app.route('/metrics', methods=['GET'])
def prometheus_metrics():
    """Prometheus scrapes here"""
    
    return metrics.get_metrics()

# Start metrics server (optional, on different port)
if __name__ == '__main__':
    start_http_server(8000)  # Metrics on :8000
    app.run(port=5000)       # App on :5000

# Benefits:
# ✅ Comprehensive metrics
# ✅ Business metrics tracked
# ✅ System metrics tracked
# ✅ Automatic request tracking
# ✅ Production-ready
```

---

## 💡 Mini Project: "Build Metrics Dashboard"

### Phase 1: Basic Metrics ⭐

**Requirements:**
- Prometheus setup
- Collect basic metrics (requests, latency, errors)
- Prometheus queries
- Basic alerting

---

### Phase 2: Grafana Dashboard ⭐⭐

**Requirements:**
- Grafana visualization
- Multi-panel dashboard
- Real-time updates
- Historical trending

---

### Phase 3: Production Setup ⭐⭐⭐

**Requirements:**
- Multi-service monitoring
- Custom business metrics
- Alert rules
- Retention policies

---

## ⚖️ Metrics vs Logs vs Traces

| Aspect | Metrics | Logs | Traces |
|--------|---------|------|--------|
| **Data** | Numbers | Text | Spans |
| **Storage** | Small | Large | Medium |
| **Query** | Fast | Slow | Medium |
| **Purpose** | Trending | Debugging | Path tracking |

---

## ❌ Common Mistakes

### Mistake 1: Cardinality Explosion

```python
# ❌ Label per user (infinite cardinality!)
requests_total.labels(user_id=user_id).inc()
# Creates 1 metric per user = MILLIONS

# ✅ Pre-aggregate or summarize
requests_total.labels(endpoint='/api').inc()
# Only a few endpoints = manageable
```

### Mistake 2: Too Short Retention

```python
# ❌ Keep only 1 day of data
# Can't see weekly trends

# ✅ Keep historical data (or downsample)
# 15 days high resolution
# 90 days downsampled
# Enables trend analysis
```

### Mistake 3: Forgetting Business Metrics

```python
# ❌ Only system metrics (CPU, memory)
# Can't see business impact

# ✅ Track business metrics too
# Orders created
# Revenue
# User signups
# Both system AND business
```

---

## 📚 Additional Resources

**Prometheus:**
- [Prometheus](https://prometheus.io/)
- [PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)

**Grafana:**
- [Grafana](https://grafana.com/)
- [Dashboard Templates](https://grafana.com/grafana/dashboards/)

**Metrics:**
- [Metrics Design](https://prometheus.io/docs/practices/instrumentation/)
- [Cardinality](https://prometheus.io/docs/prometheus/latest/querying/cardinality/)


---

## 🎯 Before You Leave

**Can you answer these?**

1. **Counter vs gauge?**
   - Answer: Counter only up; gauge up/down

2. **Cardinality explosion?**
   - Answer: Too many label combinations = storage explosion

3. **Prometheus pull vs push?**
   - Answer: Prometheus pulls metrics from targets

4. **PromQL aggregation?**
   - Answer: sum, avg, rate, histogram_quantile

5. **When to use metrics vs logs?**
   - Answer: Metrics for trends; logs for debugging

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **Engineer:** "I'll just add a few metrics for debugging"
>
> **Later:** 50 metrics per endpoint
>
> **Even later:** 100 metrics per endpoint
>
> **Much later:** MILLIONS of metrics
>
> **Prometheus:** "Storage full!"
>
> **Engineer:** "I'll add cardinality limits"
>
> **Then:** All queries return "too many metrics"
>
> **Everyone:** "Metrics: helping you see nothing" 📊

---

[← Back to Main](../README.md) | [Previous: Logging, Monitoring & Observability](44-logging-monitoring-observability.md) | [Next: Tracing (Jaeger, OpenTelemetry)](46-tracing-jaeger.md)

---

**Last Updated:** November 11, 2025  
**Difficulty:** ⭐⭐⭐ Intermediate-Advanced (observability)  
**Time to Read:** 26 minutes  
**Time to Implement:** 4-7 hours per phase  

---

*Metrics: Turning data into understanding, one dashboard at a time.* 🚀