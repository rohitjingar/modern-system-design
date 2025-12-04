# 33. Database Optimization Techniques

You optimize your database: queries now run in 100ms instead of 1 second. Congrats, you've optimized 1% of the problem. The other 99% is still bad application design, missing indexes, N+1 queries, and developers not understanding SQL. But hey, at least you can say you optimized the database. 🗄️💨

[← Back to Main](../README.md) | [Previous: Edge Computing](32-edge-computing.md) | [Next: Heartbeats & Health Checks →](34-heartbeats-health-checks.md)

---

## 🎯 Quick Summary

**Database Optimization** improves query performance and reduces resource usage. Techniques: indexing (B-tree, hash), query optimization (explain plans, joins), denormalization (trading storage for speed), partitioning (distribute data), replication (read scaling), caching (memory). Most impact: right indexes, query tuning. Medium: denormalization, partitioning. Least: tweaking server config. Netflix uses heavy caching + denormalization. Amazon optimizes millions of queries/second. Trade-off: complexity, storage, consistency.

Think of it as: **Database Optimization = Making Databases Not Slow**

---

## 🌟 Beginner Explanation

### Query Performance Basics

```
SLOW QUERY (Bad):

SELECT * FROM orders
WHERE user_id = 123
    AND created_at > '2025-01-01'

Database: "Scan entire orders table (10M rows)"
├─ Check every row
├─ Is user_id = 123? 
├─ Is created_at > 2025-01-01?
├─ Keep matching rows
└─ Time: 30 seconds!

Problem:
❌ Full table scan (10M rows checked)
❌ No index on user_id
❌ Database does unnecessary work


FAST QUERY (Good):

CREATE INDEX idx_user_created 
ON orders(user_id, created_at)

SELECT * FROM orders
WHERE user_id = 123
    AND created_at > '2025-01-01'

Database: "Use index (B-tree)"
├─ Jump to user_id=123 section (via index)
├─ Find created_at > 2025-01-01 (via index)
├─ Return matching rows
└─ Time: 10ms!

Benefit:
✅ Index skips 9.9M rows
✅ B-tree lookup (logarithmic)
✅ 3000x faster!
```

### Index Types

```
B-TREE INDEX (Most Common):

Ordered structure:
       [M]
      /   \
    [G]   [T]
   / \   / \
  [A][K][P][V]

Insert: 50, 10, 30, 20, 5
Index becomes sorted, balanced tree

Lookup user_id=50:
├─ Start at root
├─ Is 50 < M? Yes, go left
├─ Is 50 < G? No, go right
├─ Is 50 = K? Yes, found!
└─ Time: O(log n) - very fast

Good for: Range queries, sorting, equality
NOT good for: Full-text search


HASH INDEX:

Hash function: hash(key) → bucket position

Insert: user_id=123 → hash(123)=45 → Store at bucket 45

Lookup user_id=123:
├─ hash(123) = 45
├─ Check bucket 45
├─ Found!
└─ Time: O(1) - instant

Good for: Exact match, equality
NOT good for: Range queries, sorting


BITMAP INDEX:

Column value: gender
├─ M (Male)
├─ F (Female)

Bitmap:
├─ M_bitmap: 1, 0, 1, 1, 0 (rows with M)
├─ F_bitmap: 0, 1, 0, 0, 1 (rows with F)

Query: gender=M AND age > 30
├─ Use M_bitmap (which rows have M)
├─ Use age_bitmap (which rows > 30)
├─ AND them together
└─ Get matching rows instantly

Good for: Low cardinality (few values)
NOT good for: High cardinality (many values)
```

### Common Optimization Techniques

```
TECHNIQUE 1: Add Indexes

SELECT * FROM orders WHERE user_id = 123
├─ Without index: 5 seconds (scan all)
├─ With index: 10ms (lookup)
└─ 500x improvement!

Rule of thumb:
├─ Add index on WHERE columns
├─ Add index on JOIN columns
├─ Add index on ORDER BY columns
├─ But not too many! (write slowdown)


TECHNIQUE 2: Denormalization

Normalized (3 tables):
users (id, name)
orders (id, user_id)
order_items (order_id, item_id, quantity)

Query:
SELECT users.name, COUNT(orders.id)
FROM users
JOIN orders ON users.id = orders.user_id
GROUP BY users.name

Problem:
└─ Multiple joins needed

Denormalized (1 table):
orders_summary (user_name, order_count)

Query:
SELECT user_name, order_count
FROM orders_summary

Benefit:
└─ Single table, instant!

Trade-off:
├─ More storage (redundancy)
├─ Update complexity (update multiple places)
├─ But read is fast!


TECHNIQUE 3: Partitioning

Large table: events (1 billion rows)

Partitioned by date:
events_2025_01 (rows from Jan)
events_2025_02 (rows from Feb)
...
events_2025_12 (rows from Dec)

Query: events WHERE date >= '2025-06-01'
├─ Only scan June, July... Dec tables
├─ Skip Jan-May entirely
└─ 7x faster (scan 7 months instead of 12)


TECHNIQUE 4: Archiving

events table (1 billion rows, huge, slow)

Archive (keep only recent):
events table (100M recent rows, fast)
events_archive (900M old rows, cold storage)

Query: events WHERE date >= '2025-01-01'
├─ Query recent events (fast)
├─ If need old: Query archive (slow but rare)

Benefit:
├─ Fast queries for recent data
├─ Old data still available (if needed)
└─ Hot storage reduced 10x
```

---

## 🔬 Advanced Explanation

### Query Execution Plans

```
EXPLAIN PLAN (See what database does):

SELECT o.*, u.name
FROM orders o
JOIN users u ON o.user_id = u.id
WHERE o.created_at > '2025-01-01'

EXPLAIN shows:
┌──────────────────────────────────┐
│ Seq Scan on orders o (cost=0..1000)
├──────────────────────────────────┤
│ Filter: created_at > '2025-01-01'
└──────────────────────────────────┘
           ↓
┌──────────────────────────────────┐
│ Hash Join (cost=100..2000)       │
├──────────────────────────────────┤
│ Hash Cond: o.user_id = u.id     │
└──────────────────────────────────┘
           ↓
┌──────────────────────────────────┐
│ Seq Scan on users u (cost=0..500)│
└──────────────────────────────────┘

Problem:
❌ Seq Scan on orders (scans all!)
❌ Should use index on created_at
❌ Missing index on user_id join

Solution:
CREATE INDEX idx_orders_created ON orders(created_at)
CREATE INDEX idx_orders_user ON orders(user_id)

After optimization:
┌──────────────────────────────────┐
│ Index Scan (cost=0..50)          │
│ Using idx_orders_created         │
└──────────────────────────────────┘
           ↓
┌──────────────────────────────────┐
│ Hash Join (cost=50..200)         │
└──────────────────────────────────┘

Result: 1000ms → 10ms (100x faster!)
```

### N+1 Query Problem

The **N+1 Query Problem** is a common database performance anti-pattern where an application executes **1 initial query + N additional queries** (hence "N+1"), when the same data could be retrieved with just 1 or 2 queries.

## How It Happens

**Scenario:** You want to display a list of users and their associated orders.

### ❌ Bad Approach (N+1 Problem)

```python
# 1. Fetch all users (1 query)
users = db.query("SELECT * FROM users")

# 2. For each user, fetch their orders (N queries)
for user in users:
    orders = db.query("SELECT * FROM orders WHERE user_id = ?", user.id)
    print(f"{user.name}: {len(orders)} orders")
```

**Result:** If you have 100 users, this executes **101 queries**:
- 1 query to get all users
- 100 queries (one per user) to get each user's orders

### ✅ Good Approach (Solved)

```python
# Fetch all data with a JOIN (1 or 2 queries)
results = db.query("""
    SELECT u.*, o.*
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
""")

# Process in application code
# Or use eager loading in ORMs
```

**Result:** Just **1-2 queries** total, regardless of how many users you have.

## Common Causes

1. **ORM Lazy Loading** - ORMs like SQLAlchemy, Hibernate, or ActiveRecord load related data on-demand
2. **Looping with Queries** - Manually querying inside loops
3. **GraphQL Resolvers** - Each field resolver making separate database calls

## Real-World Example

```javascript
// Express.js with Sequelize ORM
// ❌ N+1 Problem
app.get('/users', async (req, res) => {
    const users = await User.findAll(); // 1 query
    
    for (let user of users) {
        user.orders = await Order.findAll({ 
            where: { userId: user.id } 
        }); // N queries!
    }
    
    res.json(users);
});

// ✅ Fixed with Eager Loading
app.get('/users', async (req, res) => {
    const users = await User.findAll({
        include: [Order] // 1 query with JOIN
    });
    
    res.json(users);
});
```

## How to Detect

- Enable database query logging and count queries per request
- Use monitoring tools like **New Relic**, **Datadog**, or **Rails Bullet gem**
- Watch for patterns where query count scales with data size

## Solutions

1. **Eager Loading** - Load all related data upfront with JOINs
2. **Batch Loading** - Use DataLoader pattern (popular in GraphQL)
3. **Query Optimization** - Use subqueries or CTEs
4. **Caching** - Cache frequently accessed relationships

The N+1 problem can turn a millisecond query into a multi-second bottleneck, especially with large datasets or high latency database connections.

### Caching at Database Layer

```
QUERY CACHING:

SELECT COUNT(*) FROM active_users

First request:
├─ Query database
├─ Count: 1,000,000
├─ Cache result
└─ Time: 5 seconds

Second request (1 second later):
├─ Return from cache
├─ Count: 1,000,000
└─ Time: 1ms

When data changes:
├─ Clear cache
├─ Next query: Re-cache

TTL-based cache:
cache_ttl = 60 seconds
├─ If < 60s old: Serve cache
├─ If > 60s old: Refresh
├─ Stale data OK? Use TTL
└─ Strong consistency needed? No cache


MATERIALIZED VIEWS:

Expensive query:
SELECT user_id, COUNT(*) as order_count
FROM orders
GROUP BY user_id

Run once per day:
CREATE MATERIALIZED VIEW user_order_counts AS
SELECT user_id, COUNT(*) as order_count
FROM orders
GROUP BY user_id

Query now:
SELECT * FROM user_order_counts WHERE user_id = 123

Result: 1ms (pre-calculated!)
Trade-off: 1-day stale data
```

### Connection Pooling

```
PROBLEM: Many connections

100 web servers, each opens database connection
├─ 100 connections
├─ Each uses resources
├─ Database: "I can handle 1000"

But at peak:
├─ 1000 connections
├─ Database max reached
├─ New connections: Queue/fail
├─ Application hangs


SOLUTION: Connection Pooling

Web servers share pool:
Connection Pool (10 connections)
    ├─ 10 actual database connections
    └─ Shared across 100 web servers

Request 1: Take connection from pool
Request 2: Take connection from pool
...
Request 10: Wait for available connection
Request 11: Still waiting...
Request 10 done: Return connection to pool
Request 11: Use returned connection

Benefits:
✅ Fewer database connections (limited)
✅ Reuse connections (cheaper)
✅ Web servers don't crash if DB overloaded
✅ Graceful degradation
```

---

## 🐍 Python Code Example

### ❌ Unoptimized Database Access

```python
# ===== UNOPTIMIZED DATABASE ACCESS =====

import psycopg2

conn = psycopg2.connect("dbname=shop")
cursor = conn.cursor()

# Problem 1: N+1 Query
def get_user_orders_slow(user_id):
    """Inefficient: N+1 query problem"""
    
    # Query 1: Get user
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    
    # Query 2+N: Get each order individually
    cursor.execute("SELECT * FROM orders WHERE user_id=%s", (user_id,))
    orders = cursor.fetchall()
    
    # For each order, get items
    order_items = {}
    for order in orders:
        cursor.execute("SELECT * FROM order_items WHERE order_id=%s", (order[0],))
        order_items[order[0]] = cursor.fetchall()
    
    return user, orders, order_items

# Total: 1 + N + N queries (wasteful!)


# Problem 2: No indexes (full scan)
def search_orders_slow(status):
    """No index on status: slow scan"""
    cursor.execute("SELECT * FROM orders WHERE status=%s", (status,))
    return cursor.fetchall()
    # Scans entire table even though only 1% match!


# Problem 3: Missing connections pooling
def get_data():
    """New connection each time: expensive"""
    conn = psycopg2.connect("dbname=shop")  # New connection!
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM data")
    return cursor.fetchall()
    # Each call: open new connection, close after

# Problems:
# ❌ N+1 queries
# ❌ No indexes (full scans)
# ❌ No connection pooling
# ❌ No caching
```

### ✅ Optimized Database Access

```python
# ===== OPTIMIZED DATABASE ACCESS =====

from psycopg2.extras import execute_values
import psycopg2.pool

# Connection Pool (reuse connections)
connection_pool = psycopg2.pool.SimpleConnectionPool(
    1, 20,  # min, max connections
    "dbname=shop user=reader"
)

# Cache layer
cache = {}

def get_db_connection():
    """Get connection from pool"""
    return connection_pool.getconn()

def release_db_connection(conn):
    """Return connection to pool"""
    connection_pool.putconn(conn)

# Optimization 1: Batch queries (join)
def get_user_orders_fast(user_id):
    """Efficient: Single join query"""
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Single query with joins (not N+1!)
        cursor.execute("""
            SELECT u.*, o.*, oi.*
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE u.id = %s
        """, (user_id,))
        
        rows = cursor.fetchall()
        
        # Reconstruct objects from rows
        user = parse_user(rows[0])
        orders = {}
        for row in rows:
            if row[X] not in orders:  # order_id
                orders[row[X]] = parse_order(row)
        
        return user, orders
    
    finally:
        release_db_connection(conn)

# Total: 1 query (3000x faster!)


# Optimization 2: Add indexes
def create_indexes():
    """Create indexes on common queries"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Index on status (for status queries)
        cursor.execute("""
            CREATE INDEX idx_orders_status 
            ON orders(status)
        """)
        
        # Index on user_id (for joins)
        cursor.execute("""
            CREATE INDEX idx_orders_user_id 
            ON orders(user_id)
        """)
        
        # Compound index (for both conditions)
        cursor.execute("""
            CREATE INDEX idx_orders_user_status 
            ON orders(user_id, status)
        """)
        
        conn.commit()
    
    finally:
        release_db_connection(conn)


# Optimization 3: Caching
def get_user_cached(user_id):
    """Cache results"""
    
    cache_key = f"user:{user_id}"
    
    # Check cache
    if cache_key in cache:
        return cache[cache_key]
    
    # Cache miss: Query database
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        user = cursor.fetchone()
        
        # Store in cache (1 hour TTL)
        cache[cache_key] = user
        
        return user
    
    finally:
        release_db_connection(conn)


# Optimization 4: Batch operations
def insert_orders_fast(orders):
    """Batch insert (not loop)"""
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Batch insert
        execute_values(
            cursor,
            """
            INSERT INTO orders (user_id, amount, status)
            VALUES %s
            """,
            [(o['user_id'], o['amount'], o['status']) for o in orders]
        )
        
        conn.commit()
    
    finally:
        release_db_connection(conn)

# Benefits:
# ✅ Connection pooling (reuse)
# ✅ Batch queries (not N+1)
# ✅ Indexes (fast lookups)
# ✅ Caching (in-memory)
# ✅ Batch inserts (fast writes)
```

### ✅ Production Database Optimization

```python
# ===== PRODUCTION DATABASE OPTIMIZATION =====

from datetime import datetime, timedelta
import redis

class DatabaseOptimizer:
    """Production-grade database optimization"""
    
    def __init__(self):
        self.pool = psycopg2.pool.ThreadedConnectionPool(
            5, 50, "dbname=shop"
        )
        self.redis = redis.Redis(host='cache', port=6379)
    
    def get_user(self, user_id):
        """Get user with caching"""
        
        cache_key = f"user:{user_id}"
        
        # Try cache
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Query database
        conn = self.pool.getconn()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, email, created_at 
                FROM users 
                WHERE id = %s
            """, (user_id,))
            
            result = cursor.fetchone()
            if result:
                user = {
                    'id': result[0],
                    'name': result[1],
                    'email': result[2],
                    'created_at': result[3].isoformat()
                }
                
                # Cache for 1 hour
                self.redis.setex(
                    cache_key,
                    3600,
                    json.dumps(user)
                )
                
                return user
        
        finally:
            self.pool.putconn(conn)
    
    def bulk_get_users(self, user_ids):
        """Get multiple users efficiently"""
        
        conn = self.pool.getconn()
        try:
            cursor = conn.cursor()
            
            # Single query for all users
            placeholders = ','.join(['%s'] * len(user_ids))
            cursor.execute(f"""
                SELECT id, name, email 
                FROM users 
                WHERE id IN ({placeholders})
            """, user_ids)
            
            results = {}
            for row in cursor.fetchall():
                results[row[0]] = {
                    'id': row[0],
                    'name': row[1],
                    'email': row[2]
                }
            
            return results
        
        finally:
            self.pool.putconn(conn)
    
    def get_user_stats(self, user_id):
        """Get materialized view (pre-calculated)"""
        
        # Pre-calculated view (updated hourly)
        conn = self.pool.getconn()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, order_count, total_spent, last_order
                FROM user_stats_view
                WHERE user_id = %s
            """, (user_id,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'order_count': result[1],
                    'total_spent': result[2],
                    'last_order': result[3]
                }
        
        finally:
            self.pool.putconn(conn)

# Benefits:
# ✅ Connection pooling
# ✅ Redis caching
# ✅ Batch queries
# ✅ Materialized views
# ✅ Production-ready
```

---

## 💡 Mini Project: "Optimize Slow Database"

### Phase 1: Analysis ⭐

**Requirements:**
- Analyze slow queries
- Use EXPLAIN PLAN
- Identify missing indexes
- Measure improvements

---

### Phase 2: Optimization ⭐⭐

**Requirements:**
- Add indexes
- Fix N+1 queries
- Add caching
- Batch operations

---

### Phase 3: Monitoring ⭐⭐⭐

**Requirements:**
- Query performance metrics
- Slow query logs
- Index usage tracking
- Automated optimization suggestions

---

## ⚖️ Optimization Impact

| Technique | Impact | Effort | Complexity |
|-----------|--------|--------|-----------|
| **Indexes** | 100-1000x | Low | Low |
| **N+1 fixes** | 10-100x | Medium | Low |
| **Denormalization** | 10-100x | High | High |
| **Caching** | 100-1000x | Low | Medium |
| **Partitioning** | 2-10x | High | High |

---

## ❌ Common Mistakes

### Mistake 1: Over-Indexing

```sql
-- ❌ Index on everything
CREATE INDEX idx_name ON users(name)
CREATE INDEX idx_email ON users(email)
CREATE INDEX idx_created ON users(created_at)
-- Every INSERT now updates 3 indexes! (slow writes)

-- ✅ Index strategically
CREATE INDEX idx_email ON users(email)  -- Often searched
-- Don't index name (rarely searched alone)
```

### Mistake 2: Wrong Index Order

```sql
-- ❌ Wrong order
CREATE INDEX idx_user_status ON orders(status, user_id)

Query: WHERE user_id = 123 AND status = 'pending'
└─ Index not used! (wrong column order)

-- ✅ Correct order
CREATE INDEX idx_user_status ON orders(user_id, status)

Query: WHERE user_id = 123 AND status = 'pending'
└─ Index used! (matches query conditions)
```

### Mistake 3: Ignoring Execution Plans

```sql
-- ❌ Slow query, no investigation
SELECT * FROM orders WHERE user_id = 123
-- Takes 10 seconds, nobody checks why

-- ✅ Analyze plan
EXPLAIN SELECT * FROM orders WHERE user_id = 123
-- Shows: Seq Scan (full table scan!)
-- Solution: Add index on user_id
CREATE INDEX idx_orders_user ON orders(user_id)
-- Now 10ms
```

---

## 📚 Additional Resources

**Tools:**
- [PostgreSQL EXPLAIN](https://www.postgresql.org/docs/current/sql-explain.html)
- [MySQL EXPLAIN](https://dev.mysql.com/doc/refman/8.0/en/explain.html)
- [Query Analyzer](https://www.solarwinds.com/database-performance-analyzer)

**Learning:**
- [Index Design](https://use-the-index-luke.com/)
- [Query Optimization](https://dataschool.com/sql-performance-explained/)


---

## 🎯 Before You Leave

**Can you answer these?**

1. **What's the N+1 query problem?**
   - Answer: 1 query + N queries for each result

2. **Why add indexes?**
   - Answer: Speed up queries (B-tree lookup)

3. **What's denormalization?**
   - Answer: Store redundant data for speed

4. **When to use caching?**
   - Answer: Expensive queries, read-heavy workloads

5. **How to find slow queries?**
   - Answer: EXPLAIN PLAN, query logs

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **Developer:** "Database is slow!"
>
> **DBA:** "Did you add indexes?"
>
> **Developer:** "Indexes? Like... for books?"
>
> **DBA:** *Adds index*
>
> **Developer:** "It's 100x faster now!"
>
> **DBA:** "That's literally the first thing you do." 🤦

---

[← Back to Main](../README.md) | [Previous: Edge Computing](32-edge-computing.md) | [Next: Heartbeats & Health Checks →](34-heartbeats-health-checks.md)

---

**Last Updated:** November 11, 2025  
**Difficulty:** ⭐⭐⭐⭐ Advanced (database internals)  
**Time to Read:** 27 minutes  
**Time to Implement:** 5-8 hours per phase  

---

*Database optimization: Where you discover that your slow application was slow because of the database all along.* 🚀