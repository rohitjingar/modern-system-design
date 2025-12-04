# 31. Data Pipelines & Stream Processing

Batch processing is like doing laundry once a week: you pile everything up and process it all at once. Stream processing is like washing each sock individually as soon as it gets dirty. One is efficient but slow. The other is real-time but exhausting. You'll end up doing both because your users want instant results and your servers need breaks. 🧦⚡

[← Back to Main](../README.md) | [Previous: CQRS](30-cqrs.md) | [Next: Edge Computing →](32-edge-computing.md)

---

## 🎯 Quick Summary

**Data Pipelines** move data from source to destination, transforming it along the way (ETL: Extract, Transform, Load). **Stream Processing** processes data in real-time as it arrives (events, logs, metrics). Batch: processes daily/hourly (Hadoop, Spark). Stream: processes immediately (Kafka Streams, Flink, Spark Streaming). Netflix uses pipelines for analytics. Uber uses streams for real-time pricing. Trade-off: batch is simpler, stream is complex but real-time.

Think of it as: **Batch = Process Later, Stream = Process Now**

---

## 🌟 Beginner Explanation

### Batch vs Stream Processing

**BATCH PROCESSING (Process in Bulk):**

```
Scenario: Daily analytics report

00:00 (midnight): Collect all day's data
├─ 1 million user events
├─ 500k transactions
├─ 2 million page views
└─ Store in data lake

01:00: Start batch job
├─ Read all data
├─ Aggregate by user
├─ Calculate metrics
├─ Write to analytics DB
└─ Takes 2 hours

03:00: Report ready
├─ Users see yesterday's data
├─ 3-hour delay acceptable
└─ Efficient processing

Pros:
✅ Simple to build
✅ Efficient (process once)
✅ Easy to debug
✅ Cheap (off-peak hours)

Cons:
❌ Not real-time (hours delay)
❌ All or nothing (if fails: reprocess all)
❌ High latency (wait for batch)
```

**STREAM PROCESSING (Process Immediately):**

```
Scenario: Real-time fraud detection

User makes payment:
├─ Event: payment.initiated
├─ Stream processor receives immediately
├─ Check: Is amount > $10,000?
├─ Check: Is user in risky country?
├─ Check: Has user paid before?
├─ Decision: Approve or block
└─ Result in < 100ms

Every event processed individually
No waiting for batch

Pros:
✅ Real-time (< 1 second)
✅ Immediate results
✅ Actionable insights now

Cons:
❌ Complex (stateful processing)
❌ Expensive (always running)
❌ Hard to debug (distributed)
```

### Data Pipeline Architecture

```
DATA PIPELINE (ETL):

EXTRACT (Get data):
├─ Source 1: Application database
├─ Source 2: User logs
├─ Source 3: External API
├─ Source 4: File uploads
└─ Extract every hour

TRANSFORM (Clean & process):
├─ Parse JSON
├─ Filter invalid records
├─ Join with user table
├─ Aggregate metrics
├─ Denormalize
└─ Enrich with metadata

LOAD (Store):
├─ Destination: Data warehouse (Snowflake, BigQuery)
├─ Or: Data lake (S3)
├─ Or: Analytics DB (ClickHouse)
└─ Ready for queries

Example: E-Commerce

Extract:
├─ Orders from PostgreSQL
├─ Clicks from log files
├─ User data from API

Transform:
├─ Join orders + clicks
├─ Calculate: conversion rate
├─ Filter: valid orders only
├─ Aggregate: by day/product

Load:
├─ Write to data warehouse
└─ Business analysts query
```

### Stream Processing Flow

```
STREAM PROCESSING (Real-Time):

Event Source:
├─ User clicks (millions/sec)
├─ Transactions (thousands/sec)
├─ IoT sensors (billions/sec)
└─ Logs (terabytes/day)

Stream Processor:
├─ Kafka Streams
├─ Apache Flink
├─ Spark Streaming
└─ Processes each event

Operations:
├─ Filter (remove invalid)
├─ Map (transform)
├─ Aggregate (count, sum)
├─ Join (with other streams)
├─ Window (time-based grouping)
└─ Output to sink

Sink:
├─ Database (write results)
├─ Dashboard (update metrics)
├─ Alerts (trigger notifications)
└─ Another stream (chaining)

Example: Twitter Trending Topics

Input: Tweets (stream)
Process:
├─ Filter hashtags
├─ Count per hashtag (5 min window)
├─ Rank top 10
├─ Update every 5 minutes
Output: Trending topics dashboard
```

---

## 🔬 Advanced Explanation

### Batch Processing Deep Dive

```
HADOOP MAPREDUCE (Classic Batch):

Job: Count words in 1TB of logs

Map Phase (Parallel):
├─ Split file into 1000 chunks
├─ Each chunk: 1GB
├─ Map task per chunk
├─ Output: (word, 1) pairs

Mapper 1: Chunk 1
├─ "hello world" → (hello, 1), (world, 1)

Mapper 2: Chunk 2
├─ "hello again" → (hello, 1), (again, 1)

... 1000 mappers total

Shuffle (Group by key):
├─ All (hello, 1) pairs go to Reducer 1
├─ All (world, 1) pairs go to Reducer 2
└─ Network transfer (expensive!)

Reduce Phase (Aggregate):
├─ Reducer 1: Sum all (hello, 1) → (hello, 5000)
├─ Reducer 2: Sum all (world, 1) → (world, 3000)
└─ Write to HDFS

Result: Word counts
Time: 30 minutes for 1TB

Limitations:
❌ High latency (minutes to hours)
❌ No incremental results
❌ Must reprocess all data if fails
```

**SPARK (Modern Batch):**

```
Spark improves on Hadoop:

In-Memory Processing:
├─ Cache data in RAM (not disk)
├─ 10-100x faster than Hadoop
└─ Reuse cached data

Lazy Evaluation:
├─ Build execution plan
├─ Optimize before running
└─ Execute only when needed

DAG (Directed Acyclic Graph):
├─ Multiple stages
├─ Pipeline transformations
├─ Efficient execution plan

Example: Word count in Spark
data = spark.read.text("hdfs://logs")
words = data.flatMap(lambda line: line.split(" "))
counts = words.groupBy("word").count()
counts.write.parquet("hdfs://output")

Result: 10x faster than Hadoop
```

### Stream Processing Deep Dive

```
KAFKA STREAMS (Real-Time):

Topology: Sequence of processing nodes

Source → Processor → Processor → Sink
(read)   (filter)    (aggregate)  (write)

Example: Real-time analytics

Input: User clicks
├─ Event: {user_id, page, timestamp}
├─ 10,000 events/sec

Processor 1: Filter
├─ Keep only product page clicks
├─ Output: 3,000 events/sec

Processor 2: Window
├─ Group by 5-minute window
├─ Count clicks per product
├─ Output: {product_id, count, window}

Processor 3: Aggregate
├─ Maintain running totals
├─ Update dashboard
└─ Output: Real-time counts

Sink: Write to database
├─ Update product_views table
└─ Visible immediately

State Management:
├─ Kafka Streams maintains state
├─ Stored in RocksDB (local)
├─ Backed up to Kafka (distributed)
└─ Recovers on failure
```

**WINDOWING (Time-Based Aggregation):**

```
TUMBLING WINDOW (Fixed, Non-Overlapping):

Window size: 5 minutes
├─ Window 1: 00:00-00:05 (closed)
├─ Window 2: 00:05-00:10 (closed)
├─ Window 3: 00:10-00:15 (active)
└─ Each event in exactly one window

Events:
├─ 00:01: user_id=1 → Window 1
├─ 00:04: user_id=2 → Window 1
├─ 00:06: user_id=3 → Window 2
├─ 00:09: user_id=1 → Window 2
└─ 00:11: user_id=2 → Window 3

Aggregate:
├─ Window 1: 2 events
├─ Window 2: 2 events
└─ Window 3: 1 event (so far)

SLIDING WINDOW (Overlapping):

Window size: 5 minutes, Slide: 1 minute
├─ Window 1: 00:00-00:05
├─ Window 2: 00:01-00:06 (overlaps W1)
├─ Window 3: 00:02-00:07 (overlaps W2)
└─ Event can be in multiple windows

Event at 00:03:
├─ In Window 1 (00:00-00:05)
├─ In Window 2 (00:01-00:06)
├─ In Window 3 (00:02-00:07)
└─ Counted 3 times!

SESSION WINDOW (Activity-Based):

Gap: 30 minutes of inactivity
├─ User active: Extend window
├─ User inactive 30 min: Close window
└─ Dynamic window size

User 1:
├─ 00:00: Event (start session)
├─ 00:10: Event (extend)
├─ 00:15: Event (extend)
├─ 00:45: No activity (30 min gap)
└─ Session closed: 00:00-00:15 (15 min)

User 2:
├─ 00:00: Event
├─ 01:00: Event (gap > 30 min)
└─ Two sessions: 00:00, 01:00
```

### Lambda Architecture (Batch + Stream)

```
LAMBDA ARCHITECTURE (Best of Both):

Problem: Need both real-time AND accuracy

Solution: Run batch AND stream in parallel

BATCH LAYER (Accurate):
├─ Process all historical data
├─ Run daily (comprehensive)
├─ Accurate but slow
└─ Output: Batch view

SPEED LAYER (Real-Time):
├─ Process recent data only
├─ Run continuously
├─ Fast but approximate
└─ Output: Real-time view

SERVING LAYER (Merge):
├─ Query = Batch view + Real-time view
├─ Real-time: Last 24 hours
├─ Batch: Everything older
└─ Combined result

Example: Page view counts

Batch (accurate):
├─ Count page views from all logs
├─ Run once per day
└─ Result: 1,000,000 views (yesterday)

Stream (real-time):
├─ Count page views in last hour
├─ Run continuously
└─ Result: 500 views (last hour)

Query:
├─ Total views = 1,000,000 + 500
└─ Result: 1,000,500 views

Benefits:
✅ Accuracy (batch)
✅ Low latency (stream)
✅ Fault tolerance (recompute from batch)
```

---

## 🐍 Python Code Example

### ❌ Without Pipeline (Manual Processing)

```python
# ===== WITHOUT PIPELINE (MANUAL) =====

import psycopg2
import json

# Manual data processing (no pipeline)
def process_orders_manually():
    """Process orders one by one (slow)"""
    
    # Connect to database
    conn = psycopg2.connect("dbname=shop")
    cursor = conn.cursor()
    
    # Get all orders
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    
    # Process each order
    for order in orders:
        # Transform
        order_data = {
            'order_id': order[0],
            'user_id': order[1],
            'amount': order[2],
            'status': order[3]
        }
        
        # Write to analytics (manually)
        print(f"Processing order: {order_data}")
    
    print(f"Processed {len(orders)} orders")

# Problems:
# ❌ No reusability
# ❌ No parallelism
# ❌ No error handling
# ❌ Not scalable
# ❌ Manual execution
```

### ✅ Batch Processing Pipeline (Apache Spark)

```python
# ===== BATCH PROCESSING PIPELINE (SPARK) =====

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, count, avg, window

# Initialize Spark
spark = SparkSession.builder \
    .appName("OrderAnalytics") \
    .getOrCreate()

class BatchPipeline:
    """Batch processing pipeline"""
    
    def __init__(self):
        self.spark = spark
    
    def extract(self):
        """Extract: Read data from sources"""
        
        # Read from database
        orders = self.spark.read \
            .format("jdbc") \
            .option("url", "jdbc:postgresql://localhost/shop") \
            .option("dbtable", "orders") \
            .load()
        
        # Read from log files
        logs = self.spark.read \
            .json("hdfs://logs/user_activity/*.json")
        
        return orders, logs
    
    def transform(self, orders, logs):
        """Transform: Clean and aggregate"""
        
        # Filter valid orders
        valid_orders = orders.filter(col("status") == "completed")
        
        # Aggregate: Total revenue by day
        daily_revenue = valid_orders \
            .groupBy("date") \
            .agg(
                sum("amount").alias("total_revenue"),
                count("*").alias("order_count"),
                avg("amount").alias("avg_order_value")
            )
        
        # Join with user activity logs
        enriched = valid_orders.join(
            logs,
            valid_orders.user_id == logs.user_id,
            "left"
        )
        
        return daily_revenue, enriched
    
    def load(self, daily_revenue, enriched):
        """Load: Write to destination"""
        
        # Write to data warehouse
        daily_revenue.write \
            .mode("overwrite") \
            .parquet("hdfs://warehouse/daily_revenue")
        
        # Write to analytics database
        enriched.write \
            .format("jdbc") \
            .option("url", "jdbc:postgresql://localhost/analytics") \
            .option("dbtable", "order_analytics") \
            .mode("append") \
            .save()
    
    def run(self):
        """Run entire pipeline"""
        print("Starting batch pipeline...")
        
        # ETL
        orders, logs = self.extract()
        daily_revenue, enriched = self.transform(orders, logs)
        self.load(daily_revenue, enriched)
        
        print("Pipeline completed!")

# Run pipeline
pipeline = BatchPipeline()
pipeline.run()

# Benefits:
# ✅ Parallel processing (distributed)
# ✅ Fault tolerance (Spark)
# ✅ Scalable (add more nodes)
# ✅ Reusable (run daily)
```

### ✅ Stream Processing (Kafka Streams)

```python
# ===== STREAM PROCESSING (KAFKA STREAMS) =====

from kafka import KafkaConsumer, KafkaProducer
import json
from collections import defaultdict
from datetime import datetime, timedelta

class StreamProcessor:
    """Real-time stream processing"""
    
    def __init__(self):
        # Kafka consumer
        self.consumer = KafkaConsumer(
            'user_clicks',
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        # Kafka producer (output)
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        # State (in-memory window)
        self.window_state = defaultdict(int)
        self.window_size = timedelta(minutes=5)
    
    def process_event(self, event):
        """Process single event"""
        
        # Extract fields
        user_id = event.get('user_id')
        page = event.get('page')
        timestamp = datetime.fromisoformat(event.get('timestamp'))
        
        # Filter: Only product pages
        if not page.startswith('/product/'):
            return None
        
        # Transform: Extract product_id
        product_id = page.split('/')[-1]
        
        # Aggregate: Count clicks per product (5-min window)
        window_key = f"{product_id}:{timestamp.strftime('%Y%m%d%H%M')}"
        self.window_state[window_key] += 1
        
        # Emit aggregated result
        result = {
            'product_id': product_id,
            'click_count': self.window_state[window_key],
            'window_start': timestamp.isoformat(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return result
    
    def start(self):
        """Start stream processing"""
        print("Starting stream processor...")
        
        for message in self.consumer:
            # Process event
            event = message.value
            result = self.process_event(event)
            
            if result:
                # Publish result
                self.producer.send('product_clicks', value=result)
                print(f"Processed: {result}")

# Run stream processor
processor = StreamProcessor()
processor.start()

# Benefits:
# ✅ Real-time (< 1 second latency)
# ✅ Continuous processing
# ✅ Stateful (maintains windows)
# ✅ Scalable (add more consumers)
```

### ✅ Production Pipeline (Airflow + Spark)

```python
# ===== PRODUCTION PIPELINE (AIRFLOW) =====

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

# Define DAG
default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2025, 11, 1),
    'email': ['alerts@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'daily_analytics_pipeline',
    default_args=default_args,
    description='Daily analytics ETL pipeline',
    schedule_interval='0 1 * * *',  # Run at 1 AM daily
    catchup=False
)

# Task 1: Extract from database
def extract_orders(**context):
    """Extract orders from database"""
    from pyspark.sql import SparkSession
    
    spark = SparkSession.builder.appName("Extract").getOrCreate()
    
    orders = spark.read \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://localhost/shop") \
        .option("dbtable", "orders") \
        .option("user", "readonly") \
        .load()
    
    # Save to HDFS
    orders.write.parquet("hdfs://staging/orders", mode="overwrite")
    
    return "Extracted {} orders".format(orders.count())

extract_task = PythonOperator(
    task_id='extract_orders',
    python_callable=extract_orders,
    dag=dag
)

# Task 2: Transform data
def transform_orders(**context):
    """Transform and aggregate"""
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col, sum, count
    
    spark = SparkSession.builder.appName("Transform").getOrCreate()
    
    orders = spark.read.parquet("hdfs://staging/orders")
    
    # Aggregate
    analytics = orders \
        .groupBy("user_id") \
        .agg(
            count("*").alias("order_count"),
            sum("amount").alias("total_spent")
        )
    
    # Save
    analytics.write.parquet("hdfs://staging/analytics", mode="overwrite")
    
    return "Transformed {} users".format(analytics.count())

transform_task = PythonOperator(
    task_id='transform_orders',
    python_callable=transform_orders,
    dag=dag
)

# Task 3: Load to warehouse
load_task = BashOperator(
    task_id='load_to_warehouse',
    bash_command='spark-submit load_to_warehouse.py',
    dag=dag
)

# Task 4: Update dashboard
def update_dashboard(**context):
    """Refresh dashboard"""
    import requests
    
    response = requests.post('http://dashboard/api/refresh')
    return f"Dashboard updated: {response.status_code}"

dashboard_task = PythonOperator(
    task_id='update_dashboard',
    python_callable=update_dashboard,
    dag=dag
)

# Define dependencies
extract_task >> transform_task >> load_task >> dashboard_task

# Benefits:
# ✅ Scheduled execution (daily)
# ✅ Error handling (retries)
# ✅ Monitoring (emails)
# ✅ Dependencies (task order)
# ✅ Production-ready
```

---

## 💡 Mini Project: "Build Data Pipeline"

### Phase 1: Simple Batch Pipeline ⭐

**Requirements:**
- Extract from CSV
- Transform (clean, aggregate)
- Load to database
- Schedule with cron

---

### Phase 2: Spark Pipeline ⭐⭐

**Requirements:**
- Distributed processing
- Multiple data sources
- Complex transformations
- Partitioned output

---

### Phase 3: Real-Time Stream ⭐⭐⭐

**Requirements:**
- Kafka stream processing
- Windowed aggregations
- State management
- Fault tolerance

---

## ⚖️ Batch vs Stream Comparison

| Aspect | Batch | Stream |
|--------|-------|--------|
| **Latency** | Hours | Seconds |
| **Complexity** | Simple | Complex |
| **Cost** | Low | High |
| **Use Case** | Reports | Real-time |
| **Volume** | Large | Continuous |
| **Debugging** | Easy | Hard |
| **Fault Tolerance** | Retry | Checkpointing |

---

## ❌ Common Mistakes

### Mistake 1: No Idempotency

```python
# ❌ Pipeline not idempotent
def process():
    orders = read_orders()
    analytics.insert(orders)  # Duplicate on rerun!

# ✅ Idempotent pipeline
def process():
    orders = read_orders()
    analytics.upsert(orders)  # Safe to rerun
```

### Mistake 2: No Backpressure

```python
# ❌ Consume faster than process
while True:
    event = consume()
    process(event)  # If slow: Queue fills, OOM!

# ✅ Backpressure handling
while queue.size() < MAX:
    event = consume()
    queue.add(event)
```

### Mistake 3: No Monitoring

```python
# ❌ No visibility into pipeline
process_data()

# ✅ Monitor metrics
metrics.gauge('pipeline.processed', count)
metrics.gauge('pipeline.latency', latency)
```

---

## 📚 Additional Resources

**Batch:**
- [Apache Spark](https://spark.apache.org/)
- [Apache Airflow](https://airflow.apache.org/)

**Stream:**
- [Apache Kafka](https://kafka.apache.org/)
- [Apache Flink](https://flink.apache.org/)
- [Kafka Streams](https://kafka.apache.org/documentation/streams/)

---


## 🎯 Before You Leave

**Can you answer these?**

1. **What's ETL?**
   - Answer: Extract, Transform, Load

2. **Batch vs stream?**
   - Answer: Batch = process later; Stream = process now

3. **What's windowing?**
   - Answer: Time-based grouping of events

4. **What's Lambda architecture?**
   - Answer: Batch + stream together

5. **When to use stream processing?**
   - Answer: Real-time requirements (fraud, alerts, monitoring)

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **Engineer:** "Let's process data in real-time!"
>
> **Manager:** "Why not batch at night?"
>
> **Engineer:** "Users want instant results!"
>
> **Manager:** "Build both then"
>
> **Engineer:** "Now I have two problems" 😅

---

[← Back to Main](../README.md) | [Previous: CQRS](30-cqrs.md) | [Next: Edge Computing →](32-edge-computing.md)

---

**Last Updated:** November 11, 2025  
**Difficulty:** ⭐⭐⭐⭐ Advanced (distributed systems)  
**Time to Read:** 28 minutes  
**Time to Implement:** 6-10 hours per phase  

---

*Data pipelines: Moving data from A to B while transforming it into C. Simple, right?* 🚀