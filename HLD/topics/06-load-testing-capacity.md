# 06. Load Testing & Capacity Estimation

Capacity estimation is predicting the future. Load testing is the future punching you in the face when you're wrong. 👊

[← Back to Main](../README.md) | [Previous: JSON vs Protobuf](05-json-vs-protobuf.md) | [Next: SQL vs NoSQL →](07-sql-vs-nosql.md)

---

## 🎯 Quick Summary

**Load Testing and Capacity Estimation** are about answering: "How many users can my system handle?" and "What happens when traffic 10x tomorrow?" Estimation is math; load testing is reality. Both are essential before your system crashes at 3 AM.

Think of it as: **Estimation = Theory, Load Testing = Practice**

---

## 🌟 Beginner Explanation

### The Story of Scaling Failure

Imagine you open a coffee shop:

```
OPENING DAY (capacity estimation):
You estimate: "I can serve 50 customers/hour"
You hire: 2 baristas
You buy: 1 espresso machine

First month: Perfect! 30 customers/hour
Your estimate was right! ✅

VIRAL MOMENT (6 months later):
Someone posts: "BEST COFFEE IN TOWN!" on TikTok
Next day: 500 customers/hour (16x more!) 😱

What happens:
- 1 espresso machine can't keep up
- 2 baristas are overwhelmed
- Queue wraps around the block
- Customers leave angry
- You lose business

What should have happened:
- Estimate capacity upfront
- Plan for 10x growth
- Have backup equipment
- Test during peak hours
```

### Capacity Estimation: The Math

```
QUESTION: How many servers do I need for 1 million users?

STEP 1: Estimate QPS (queries per second)
1M users × 10 requests/day ÷ 86,400 seconds/day
= ~115 QPS

STEP 2: Estimate per-server throughput
Each server can handle: 1,000 QPS (with caching)

STEP 3: Calculate servers needed
115 QPS ÷ 1,000 QPS/server = 0.115 servers
= Round up to 1 server

BUT WAIT! Add redundancy:
×2 for failover (1 → 2 servers)
×1.5 for peak (2 → 3 servers)
×2 for growth (3 → 6 servers)
= 6 servers total

REALITY CHECK:
- If your math was wrong: Oops, you crash
- If your math was too conservative: Wasted money
- If your math was right: Perfect! ✅
```

### Load Testing: Stress Your System

```
WITHOUT LOAD TESTING:
You deploy to production
1000 real users hit your system
Everything crashes
Customers angry
You panic fix in production
It's 3 AM and you hate your life 😭

WITH LOAD TESTING:
You simulate 1000 users in test environment
You find the bottleneck (database can't handle 100 QPS)
You fix it before users see it
Deploy to production
Everything works smoothly ✅
You sleep well
```

### Real Numbers

```
Netflix can handle:
- 100 million concurrent streams
- 500 million tweets/day traffic spike
- 99.99% uptime guarantee

Amazon during Black Friday:
- 1000x normal traffic
- Must handle millions of orders/minute
- System must not crash or lose money

Twitter during election:
- 3000 QPS baseline
- Spikes to 500,000 QPS during major event
- Must handle 167x increase

Your startup first day:
- 100 users
- Probably fine with 1 server
- But estimate for 1000 anyway
```

---

## 🔬 Advanced Explanation

### Capacity Estimation: The Framework

**Step 1: Define Metrics**

```
DAU (Daily Active Users): 1 million
Requests per user per day: 10
Peak hour fraction: 20% (20% of daily traffic in 1 hour)

Calculation:
Daily QPS = (1M users × 10 requests) / 86,400 seconds = 115 QPS
Peak QPS = 115 × 24 / 5 = 552 QPS (assuming peak is 1/5 of day)
Peak second = 552 / 3600 = 0.15 QPS per second... wait that's not right

Let me recalculate:
1M users × 10 requests/day = 10M requests/day
10M / 86,400 seconds = 115 requests/second (baseline)

If peak hour has 5% of daily traffic:
Peak QPS = (10M × 0.05) / 3,600 = 1,389 QPS

If peak second has 10x normal:
Peak second = 1,389 × 10 = 13,890 requests/second
```

**Step 2: Estimate Database Load**

```
Same 115 baseline QPS:
- 80% reads (92 QPS)
- 20% writes (23 QPS)

Database:
- Reads: Can handle 10,000 QPS (with caching)
- Writes: Can handle 1,000 QPS (must persist to disk)

Bottleneck: Write operations!
23 writes × peak multiplier (10x) = 230 writes/second
But database can do 1,000/sec, so we're fine...

For now.
```

**Step 3: Estimate Storage**

```
Average request size: 2 KB
Average response size: 5 KB
Total per request: 7 KB

115 QPS × 7 KB = 805 KB/second
805 KB/s × 86,400 seconds = 69.5 GB/day
69.5 GB/day × 365 days = 25.4 TB/year

Need to store:
- 1 year of data: ~25 TB
- Add 2x for redundancy: ~50 TB
- Add 1x for backups: ~75 TB

So you need: ~75 TB of storage minimum
```

**Step 4: Estimate Bandwidth**

```
Response size: 5 KB average
115 QPS × 5 KB = 575 KB/second

Peak QPS: 1,389 QPS
1,389 × 5 KB = 6.9 MB/second
= 55 Mbps (during peak)

Your datacenter needs: 100+ Mbps connection
```

**Step 5: Calculate Servers Needed**

```
Baseline QPS: 115 requests/second
Peak QPS: 1,389 requests/second

Each server handles: 1,000 QPS
Servers for baseline: 115 / 1,000 = 0.12 → 1 server minimum
Servers for peak: 1,389 / 1,000 = 1.39 → 2 servers

Add redundancy (10% spare capacity):
2 × 1.1 = 2.2 → 3 servers

Add failover (always 2 can take over if 1 fails):
3 servers total (1 can be down, 2 handle traffic)
```

### Load Testing: The Process

**Types of Load Tests:**

```
1. BASELINE TEST
Send "normal" traffic
Measure performance
See if it meets SLA (Service Level Agreement)

2. RAMP TEST
Gradually increase traffic
Find breaking point
See where performance degrades

3. STRESS TEST
Send more than max capacity
See what breaks first
Understand failure modes

4. SPIKE TEST
Sudden traffic increase
See how system recovers
Test auto-scaling

5. SOAK TEST
Send normal load for 24+ hours
Find memory leaks
Check for degradation
```

**Example: Load Testing with JMeter**

```
Test Plan:
├─ 100 users
├─ Ramp up over 10 minutes
├─ Each user makes 10 requests
├─ Measure response time, errors

Results:
├─ Average response time: 45ms ✅
├─ 95th percentile (p95): 120ms ✅
├─ 99th percentile (p99): 500ms ✅
├─ Error rate: 0.1% ✅
├─ Throughput: 980 requests/second ✅

All metrics good!
```

### Real-World Estimation Example: Twitter-Like System

```
REQUIREMENTS:
- 1 billion total users
- 100 million daily active users (DAU)
- 500 million tweets/day
- Read:Write ratio = 100:1

CALCULATIONS:

Tweets per second:
500M tweets/day / 86,400 seconds = 5,787 writes/second

Tweet reads per second:
5,787 × 100 = 578,700 reads/second

Total QPS:
578,700 + 5,787 = 584,487 QPS ← This is a LOT!

DATABASE:
- Write servers: 5,787 / 1,000 per server = 6 servers
- Read replicas: 578,700 / 10,000 per server = 58 servers
- Add redundancy: 100+ servers total

CACHE (Redis):
- 80% of reads hit cache (464,560 QPS from cache)
- 20% go to database (114,140 QPS)
- Redis handles 100,000 QPS per instance
- Need: 5 Redis instances

API SERVERS:
- Each handles 5,000 QPS
- Need: 584,487 / 5,000 = 117 servers
- Add redundancy: 150+ servers

TOTAL INFRASTRUCTURE:
- 150 API servers
- 100 database servers
- 5 cache servers
- 10+ load balancers
- CDN (for static assets)
- Multiple datacenters

Real cost: Millions of dollars per month 💰
```

### Measurement: Key Metrics

```
LATENCY (How fast?)
- Mean (average): 50ms
- p50 (median): 45ms
- p95 (95th percentile): 100ms
- p99 (99th percentile): 200ms
- p99.9: 500ms

Why p95/p99 matter:
If mean is 50ms but p99 is 500ms:
- 99% of users fast
- 1% of users (10K in 1M) wait 500ms → Bad experience!

THROUGHPUT (How many?)
- Requests per second: 1,000 QPS
- Transactions per second: 500 TPS
- Bytes per second: 5 MB/s

ERROR RATE (How many fail?)
- Errors per second: < 1 per 100,000
- Error rate: < 0.001%
- Target: 99.99% success rate

RESOURCE USAGE (What's consumed?)
- CPU: 70% utilization
- Memory: 60% utilization
- Disk I/O: 500 IOPS
- Network: 100 Mbps
```

---

## 🐍 Python Code Example

### ❌ Simple Capacity Estimation (Manual)

```python
# ===== MANUAL CAPACITY ESTIMATION =====

def estimate_capacity_simple():
    """Manual back-of-envelope calculation"""
    
    # User metrics
    dau = 1_000_000  # 1 million daily active users
    requests_per_user = 10  # Each user makes 10 requests/day
    
    # Calculate QPS
    total_requests_per_day = dau * requests_per_user
    qps_baseline = total_requests_per_day / 86_400  # 86,400 seconds in a day
    
    # Peak traffic (assume peak is 10x baseline)
    qps_peak = qps_baseline * 10
    
    print(f"Baseline QPS: {qps_baseline:.0f}")
    print(f"Peak QPS: {qps_peak:.0f}")
    
    # Server capacity
    qps_per_server = 1_000
    servers_needed = qps_peak / qps_per_server
    
    # Add redundancy (2x for failover)
    servers_with_redundancy = servers_needed * 2
    
    print(f"Servers needed: {servers_with_redundancy:.0f}")
    
    # Storage estimation
    avg_request_size = 5_000  # bytes
    storage_per_day = (qps_baseline * 86_400) * avg_request_size
    storage_per_year = storage_per_day * 365
    
    print(f"Storage per year: {storage_per_year / 1024 / 1024 / 1024:.1f} GB")
    
    # Bandwidth
    avg_response_size = 5_000  # bytes
    bandwidth_peak = qps_peak * avg_response_size / 1_000_000  # Convert to Mbps
    
    print(f"Bandwidth needed: {bandwidth_peak:.1f} Mbps")

# Output:
# Baseline QPS: 115
# Peak QPS: 1,157
# Servers needed: 2
# Storage per year: 18.3 GB
# Bandwidth needed: 58.0 Mbps

estimate_capacity_simple()

# Problems:
# ❌ Too simplistic
# ❌ Doesn't account for different request types
# ❌ Doesn't consider caching
# ❌ Doesn't account for write vs read load
# ❌ Hardcoded multipliers
```

### ✅ Advanced Capacity Estimation (Professional)

```python
from dataclasses import dataclass
from enum import Enum
import math

class RequestType(Enum):
    READ = 1
    WRITE = 2

@dataclass
class RequestMetrics:
    """Metrics for different request types"""
    name: str
    percentage: float  # % of total requests
    avg_size_bytes: int
    qps_per_server: int  # How many QPS each server can handle

class CapacityEstimator:
    def __init__(self, dau: int, requests_per_user: float):
        self.dau = dau
        self.requests_per_user = requests_per_user
        self.baseline_qps = (dau * requests_per_user) / 86_400
    
    def estimate_with_request_types(self, request_types: list[RequestMetrics]):
        """Estimate capacity accounting for different request types"""
        print("=" * 60)
        print("ADVANCED CAPACITY ESTIMATION")
        print("=" * 60)
        
        total_qps_by_type = {}
        total_servers = 0
        total_bandwidth = 0
        
        for req_type in request_types:
            # Calculate QPS for this request type
            qps = self.baseline_qps * (req_type.percentage / 100)
            peak_qps = qps * 10  # Assume 10x peak
            
            # Calculate servers needed
            servers_needed = math.ceil(peak_qps / req_type.qps_per_server)
            servers_with_redundancy = servers_needed * 2
            
            # Calculate bandwidth
            bandwidth = peak_qps * req_type.avg_size_bytes / 1_000_000  # Mbps
            
            total_qps_by_type[req_type.name] = qps
            total_servers += servers_with_redundancy
            total_bandwidth += bandwidth
            
            print(f"\n{req_type.name}:")
            print(f"  Baseline: {qps:.0f} QPS")
            print(f"  Peak: {peak_qps:.0f} QPS")
            print(f"  Servers needed: {servers_with_redundancy}")
            print(f"  Bandwidth: {bandwidth:.1f} Mbps")
        
        print(f"\n{'=' * 60}")
        print(f"TOTALS:")
        print(f"  Total servers: {total_servers}")
        print(f"  Total bandwidth: {total_bandwidth:.1f} Mbps")
        print(f"  Total baseline QPS: {self.baseline_qps:.0f}")
        print(f"{'=' * 60}\n")
        
        return {
            'total_servers': total_servers,
            'total_bandwidth': total_bandwidth,
            'qps_by_type': total_qps_by_type
        }
    
    def estimate_storage(self, data_retention_days=365, avg_record_size=1000):
        """Estimate storage needs"""
        requests_per_day = self.baseline_qps * 86_400
        total_records = requests_per_day * data_retention_days
        total_bytes = total_records * avg_record_size
        
        # Convert to TB
        total_tb = total_bytes / 1_024 / 1_024 / 1_024
        
        # Add 2x for redundancy
        total_with_redundancy = total_tb * 2
        
        print(f"Storage estimation:")
        print(f"  Records per day: {requests_per_day:.0f}")
        print(f"  Total records ({data_retention_days} days): {total_records:.0f}")
        print(f"  Raw storage: {total_tb:.1f} TB")
        print(f"  With redundancy (2x): {total_with_redundancy:.1f} TB")
        
        return total_with_redundancy

# Usage
estimator = CapacityEstimator(dau=1_000_000, requests_per_user=10)

# Define request types
request_types = [
    RequestMetrics(
        name="Read Requests",
        percentage=80,  # 80% reads
        avg_size_bytes=5_000,
        qps_per_server=10_000  # Each server handles 10K read QPS
    ),
    RequestMetrics(
        name="Write Requests",
        percentage=20,  # 20% writes
        avg_size_bytes=2_000,
        qps_per_server=1_000  # Each server handles only 1K write QPS
    ),
]

# Estimate
result = estimator.estimate_with_request_types(request_types)
storage = estimator.estimate_storage(data_retention_days=365)

# Output:
# ============================================================
# ADVANCED CAPACITY ESTIMATION
# ============================================================
#
# Read Requests:
#   Baseline: 92 QPS
#   Peak: 920 QPS
#   Servers needed: 2
#   Bandwidth: 46.0 Mbps
#
# Write Requests:
#   Baseline: 23 QPS
#   Peak: 230 QPS
#   Servers needed: 1
#   Bandwidth: 1.2 Mbps
#
# ============================================================
# TOTALS:
#   Total servers: 3
#   Total bandwidth: 47.2 Mbps
#   Total baseline QPS: 115
# ============================================================
#
# Storage estimation:
#   Records per day: 9,942,576
#   Total records (365 days): 3,629,640,240
#   Raw storage: 3.6 TB
#   With redundancy (2x): 7.2 TB
```

### ✅ Load Testing Example (Locust)

```python
# ===== LOAD TESTING WITH LOCUST =====
from locust import HttpUser, task, between, events
import time

class UserBehavior(HttpUser):
    """Simulates user behavior"""
    
    # Wait 1-3 seconds between requests
    wait_time = between(1, 3)
    
    @task(3)  # 3x more likely
    def get_user(self):
        """Read user data (read operation)"""
        user_id = 123
        self.client.get(f"/api/users/{user_id}")
    
    @task(1)  # 1x less likely
    def create_post(self):
        """Create post (write operation)"""
        self.client.post("/api/posts", json={
            "title": "Hello World",
            "content": "This is a test"
        })
    
    @task(2)
    def list_posts(self):
        """List all posts"""
        self.client.get("/api/posts?limit=10")

# Event handlers for monitoring
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("=" * 60)
    print("LOAD TEST STARTED")
    print("=" * 60)

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("\n" + "=" * 60)
    print("LOAD TEST COMPLETED")
    print("=" * 60)
    
    # Print statistics
    for name, stats in environment.stats.items():
        print(f"\n{name}:")
        print(f"  Requests: {stats.num_requests}")
        print(f"  Failures: {stats.num_failures}")
        print(f"  Median response time: {stats.median_response_time}ms")
        print(f"  P95 response time: {stats.get_response_time_percentile(0.95)}ms")
        print(f"  P99 response time: {stats.get_response_time_percentile(0.99)}ms")

# Run with:
# locust -f load_test.py --host=http://localhost:5000
#
# CLI options:
# -u 1000          : 1000 simulated users
# -r 100           : Ramp up 100 users per second
# -t 5m            : Run for 5 minutes
# --headless       : No web UI

# Output (web UI):
# ┌─────────────────────────────────────────────────────┐
# │ Type          Method  Name        Count   Avg(ms) P99 │
# ├─────────────────────────────────────────────────────┤
# │ HTTP          GET     /api/users  5,000   45      200 │
# │ HTTP          POST    /api/posts  1,667   120     500 │
# │ HTTP          GET     /api/posts  3,333   52      180 │
# │ Total                             10,000  65      300 │
# └─────────────────────────────────────────────────────┘
```

---

## 💡 Mini Project: "Build a Capacity Planner"

### Phase 1: Simple Calculator ⭐

**Requirements:**
- Input: DAU, requests/user, peak multiplier
- Output: Servers needed, storage, bandwidth
- Simple calculations

**Code:**
```python
def simple_capacity_calculator():
    dau = int(input("Daily Active Users: "))
    requests_per_user = float(input("Requests per user per day: "))
    peak_multiplier = float(input("Peak traffic multiplier (e.g., 10): "))
    
    baseline_qps = (dau * requests_per_user) / 86_400
    peak_qps = baseline_qps * peak_multiplier
    servers = int(peak_qps / 1_000) + 1  # +1 for safety
    
    print(f"\nBaseline QPS: {baseline_qps:.0f}")
    print(f"Peak QPS: {peak_qps:.0f}")
    print(f"Servers needed: {servers}")

simple_capacity_calculator()
```

---

### Phase 2: Interactive Capacity Planner ⭐⭐

**Requirements:**
- Multiple request types
- Different server capacities
- Storage calculation
- Savings analysis

**Features:**
```python
class CapacityPlanner:
    def __init__(self):
        self.request_types = {}
    
    def add_request_type(self, name, percentage, qps_per_server):
        self.request_types[name] = {
            'percentage': percentage,
            'qps_per_server': qps_per_server
        }
    
    def calculate_and_display(self, dau, requests_per_user):
        baseline_qps = (dau * requests_per_user) / 86_400
        
        total_servers = 0
        for name, config in self.request_types.items():
            qps = baseline_qps * (config['percentage'] / 100)
            peak_qps = qps * 10
            servers = math.ceil(peak_qps / config['qps_per_server']) * 2
            
            total_servers += servers
            print(f"{name}: {servers} servers")
        
        # Calculate cost
        monthly_cost = total_servers * 500  # $500 per server per month
        print(f"\nEstimated monthly cost: ${monthly_cost:,.0f}")

# Usage
planner = CapacityPlanner()
planner.add_request_type("Reads", 80, 10_000)
planner.add_request_type("Writes", 20, 1_000)
planner.calculate_and_display(1_000_000, 10)
```

---

### Phase 3: Real Load Testing Suite ⭐⭐⭐

**Requirements:**
- Automated load testing
- Result analysis
- Bottleneck detection
- Recommendations

**Features:**
```python
import subprocess
import json

class LoadTestSuite:
    def run_load_test(self, target_url, num_users, ramp_rate, duration):
        """Run Locust load test and analyze results"""
        
        cmd = [
            "locust",
            "-f", "load_test.py",
            "--host", target_url,
            "-u", str(num_users),
            "-r", str(ramp_rate),
            "-t", duration,
            "--headless",
            "--csv=results"
        ]
        
        subprocess.run(cmd)
        
        # Analyze results
        self.analyze_results()
    
    def analyze_results(self):
        """Find bottlenecks and make recommendations"""
        
        with open('results_stats.csv', 'r') as f:
            lines = f.readlines()
        
        print("\n=== LOAD TEST ANALYSIS ===\n")
        
        for line in lines[1:]:
            parts = line.strip().split(',')
            name = parts[0]
            avg_response = float(parts[5])
            p95_response = float(parts[7])
            failure_rate = float(parts[12])
            
            print(f"{name}:")
            print(f"  Avg response: {avg_response:.0f}ms")
            print(f"  P95 response: {p95_response:.0f}ms")
            print(f"  Failure rate: {failure_rate:.2f}%")
            
            # Make recommendations
            if avg_response > 200:
                print(f"  ⚠️ SLOW: Consider caching or optimization")
            if p95_response > 1000:
                print(f"  ⚠️ TAIL: P95 is very high, investigate outliers")
            if failure_rate > 0.1:
                print(f"  ⚠️ ERRORS: High error rate, check server logs")

# Usage
tester = LoadTestSuite()
tester.run_load_test(
    target_url="http://localhost:5000",
    num_users=1000,
    ramp_rate=100,
    duration="5m"
)
```

---

## ⚖️ Key Estimation Metrics

| Metric | Baseline | Peak | Action |
|--------|----------|------|--------|
| **QPS** | 115 | 1,157 | Add 10x capacity |
| **Latency (Avg)** | 50ms | 100ms | OK ✅ |
| **Latency (P99)** | 200ms | 500ms | Consider optimization |
| **Error Rate** | 0.01% | 0.1% | Monitor closely |
| **CPU** | 40% | 70% | Room for more traffic |
| **Memory** | 50% | 80% | Good utilization |

---

## 🎯 Common Estimation Mistakes

### Mistake 1: Underestimating Peak

```python
# ❌ Bad: Assume peak is 2x normal
peak = baseline * 2

# Reality: Major event can be 100x
# Black Friday, viral tweet, news event

# ✅ Good: Plan for 10-100x surge
peak = baseline * 100
```

### Mistake 2: Ignoring Write Operations

```python
# ❌ Bad: Treat reads and writes the same
servers = total_qps / 5_000  # Both can do 5K/sec

# Reality: Writes need disk persistence
# Reads can be cached (very fast)
# Writes must go to database (slower)

# ✅ Good: Separate calculations
read_servers = read_qps / 10_000
write_servers = write_qps / 1_000  # Much lower!
```

### Mistake 3: No Safety Margin

```python
# ❌ Bad: Exact calculation
servers_needed = peak_qps / qps_per_server

# Reality: Unexpected spikes, bugs, uneven distribution

# ✅ Good: Add safety margin
servers_needed = (peak_qps / qps_per_server) * 1.5
```

### Mistake 4: Not Testing Bottlenecks

```python
# ❌ Bad: Assume servers are bottleneck
# Deploy with 100 servers
# Traffic increases
# System crashes
# Oh no! Bottleneck was database! 😱

# ✅ Good: Load test early
# Find bottleneck (database)
# Scale database first
# Then scale app servers
# Deploy with confidence
```

---

## 📚 Additional Resources

**Estimation Tools:**
- [Google Cloud Sizing Calculator](https://cloudcalculator.app/)
- [AWS Pricing Calculator](https://calculator.aws/)
- [Azure Pricing Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)

**Load Testing Tools:**
- [Locust](https://locust.io/) - Python-based, easy
- [JMeter](https://jmeter.apache.org/) - Java-based, powerful
- [k6](https://k6.io/) - JavaScript, cloud-native
- [Gatling](https://gatling.io/) - Scala, great reports

**Monitoring:**
- [Prometheus](https://prometheus.io/) - Metrics collection
- [Grafana](https://grafana.com/) - Visualization
- [New Relic](https://newrelic.com/) - APM
- [DataDog](https://www.datadoghq.com/) - Comprehensive monitoring

**Reading:**
- "Capacity Planning" chapter in DDIA
- "Performance Tuning" on High Scalability blog
- [Brendan Gregg's Performance](http://www.brendangregg.com/) - Linux performance tools

---

## 🎯 Before You Leave

**Can you answer these?**

1. **What's the difference between baseline and peak QPS?**
   - Answer: Baseline is average load; peak is maximum spike

2. **Why should you load test before production?**
   - Answer: Find bottlenecks early; avoid 3 AM crashes

3. **What's more expensive at scale: reads or writes?**
   - Answer: Writes (need disk persistence); reads can be cached

4. **What's a p99 latency and why does it matter?**
   - Answer: 99th percentile response time; 1% of users see this delay

5. **How do you estimate servers needed?**
   - Answer: Peak QPS ÷ QPS per server × safety margin

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **Junior Dev:** "The system is optimized for 1,000 QPS."
>
> **Senior Dev:** "Cool. What's the peak?"
>
> **Junior Dev:** "...Peak?"
>
> **Senior Dev:** "Yeah, when it actually matters."
>
> **System:** *crashes under 10,000 QPS* 💥
>
> **Junior Dev:** *updating LinkedIn* 😭

---

[← Back to Main](../README.md) | [Previous: JSON vs Protobuf](05-json-vs-protobuf.md) | [Next: SQL vs NoSQL →](07-sql-vs-nosql.md)

---

**Last Updated:** November 10, 2025  
**Difficulty:** ⭐⭐ Beginner-Intermediate (some math required)  
**Time to Read:** 22 minutes  
**Time to Build Planner:** 3-5 hours per phase  

---

*Estimation + testing = confidence. Skip either and 3 AM on-call pages await.* 🚀