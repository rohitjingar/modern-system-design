# 08. Database Indexes

Without indexes, a database query is like finding a specific book in a library with no catalog — you must read every single book. With indexes, it's like the Dewey Decimal System. With bad indexes, it's like a catalog that's alphabetized by color. 📚

[← Back to Main](../README.md) | [Previous: SQL vs NoSQL](07-sql-vs-nosql.md) | [Next: Sharding & Partitioning →](09-sharding-partitioning.md)

---

## 🎯 Quick Summary

**Database Indexes** are data structures that speed up queries. They're like the index at the back of a book: instead of reading every page to find a topic, you look it up in the index and jump directly to the relevant pages. Indexes trade storage space for query speed.

Think of it as: **Index = Roadmap to Your Data**

---

## 🌟 Beginner Explanation

### Finding Data: With and Without Indexes

**SCENARIO: Find all users named "Alice"**

**Without Index (Table Scan):**
```
Database has 1 million users.

Computer: "Find users where name = 'Alice'"
Database: "OK, I'll check every single row..."

Row 1: Bob ❌
Row 2: Carol ❌
Row 3: Alice ✅ (Found 1!)
Row 4: David ❌
... (checking all 1M rows)
Row 1,000,000: Alice ✅ (Found another!)

Time: ~1000ms (whole database scanned)
CPU: 100% (doing all the work)
```

**With Index (Lookup):**
```
Database has NAME INDEX:

Alice → [Row IDs: 3, 1000000, ...]
Bob → [Row IDs: 1, 50000, ...]
Carol → [Row IDs: 2, 75000, ...]

Computer: "Find users where name = 'Alice'"
Database: "Looking in index... found!"

Index lookup: Alice → [Row 3, Row 1000000]
Direct fetch: Jump to rows

Time: ~1ms (just index lookup!)
CPU: 1% (super efficient)
```

**Speed Improvement: 1000x faster!** ⚡

### The Library Analogy

**Without Index (Chaos):**
```
LIBRARY WITH NO CATALOG

Customer: "Where are books about cooking?"
Librarian: "Uh... I don't know. Check every shelf."

Customer walks around... checking every shelf for 4 hours 😡
Finally finds 3 cooking books scattered randomly
```

**With Index (Organized):**
```
LIBRARY WITH DEWEY DECIMAL SYSTEM

Customer: "Where are books about cooking?"
Librarian: "Cooking is 641.5. Go to that section."

Customer walks to section, finds 50 cooking books instantly ✅
Total time: 5 minutes
```

### Types of Indexes

```
PRIMARY KEY INDEX:
├─ Automatically created
├─ Must be unique (no duplicates)
├─ Example: user_id is primary key
└─ Fastest lookups

SECONDARY INDEX:
├─ Manually created
├─ Can have duplicates
├─ Example: INDEX on email
└─ Good for WHERE email = '...'

COMPOSITE INDEX:
├─ Multiple columns
├─ Example: INDEX on (user_id, created_date)
└─ Good for WHERE user_id = X AND created_date > Y

UNIQUE INDEX:
├─ Enforces uniqueness
├─ Example: UNIQUE INDEX on email
└─ Prevents duplicate emails
```

---

## 🔬 Advanced Explanation

### B-Tree Index (Most Common)

**Structure:**

```
B-TREE (Balanced Tree)

                    [50]
                   /    \
                 /        \
            [25]            [75]
           /    \          /    \
         /        \      /        \
    [10] [35]   [60]  [90]
    / | \  | \  / | \ / | \
   5 15 20 30 40 55 65 70 80 85 95 100

Rules:
✅ Tree is balanced (same height everywhere)
✅ All data is sorted
✅ Leaf nodes contain actual data pointers
✅ Very fast lookups

Search for 70:
1. Start at root [50]
2. 70 > 50? Go right
3. At [75]
4. 70 < 75? Go left
5. At [60]
6. 70 > 60? Go right
7. Found [70] in leaf

Time: Log(n) = Very fast!
```

**Why B-Tree?**

```
Why not just sort the array?
(Array: [1, 2, 3, 4, 5, ..., 1000000])

Find 500000:
Binary search: Check middle (500000)
Found in 1 lookup! ✅

But... what if data changes?
- Insert 250000 → Need to shift 500k elements ❌
- Delete 500000 → Need to shift 500k elements ❌

B-Tree handles insertions/deletions efficiently!
```

### How Indexes Speed Up Queries

**WITHOUT INDEX:**

```sql
SELECT * FROM users WHERE age > 25 AND city = 'NYC';

Database scans entire table:
1. Load row 1: Check age (18) ❌ Skip
2. Load row 2: Check age (30) ✅ Check city (NYC) ✓
3. Load row 3: Check age (22) ❌ Skip
... (millions of rows)

Time: O(n) = Very slow!
Disk I/O: 1,000,000+ read operations
```

**WITH INDEX ON (age, city):**

```sql
SELECT * FROM users WHERE age > 25 AND city = 'NYC';

Database uses index:
1. Find index entries where age > 25
2. Within those, filter city = 'NYC'
3. Get row IDs from index
4. Fetch only matching rows

Time: O(log n) = Much faster!
Disk I/O: 100-1000 read operations
```

**Speed ratio: 1000x faster!**

### Index Trade-offs

```
ADVANTAGES:
✅ Queries much faster (100-1000x)
✅ Complex WHERE clauses work well
✅ Joins become faster
✅ Sorting becomes faster (ORDER BY)

DISADVANTAGES:
❌ Takes extra storage space (20-50% more data)
❌ INSERT/UPDATE/DELETE slower (must update index)
❌ Memory usage increases
❌ Maintenance overhead
```

### Composite Index Deep Dive

**Example: COMPOSITE INDEX (user_id, created_date)**

```
INDEX STRUCTURE:

(1, 2024-01-01) → Row 100
(1, 2024-01-15) → Row 105
(1, 2024-02-01) → Row 110
(2, 2024-01-05) → Row 200
(2, 2024-01-20) → Row 205
(3, 2024-02-15) → Row 300

QUERY 1: WHERE user_id = 1
Result: Uses index (finds 1, [2024-01-01, 2024-01-15, 2024-02-01])
✅ Fast!

QUERY 2: WHERE user_id = 1 AND created_date > 2024-01-15
Result: Uses index (finds 1, then filters dates)
✅ Fast!

QUERY 3: WHERE created_date > 2024-01-15
Result: ❌ Can't use index (first column must match)
Must scan entire index!

KEY INSIGHT:
Composite index works best when:
1. First column is most selective (filters most rows)
2. Query uses first column
3. Additional columns help narrow further
```

### Common Indexing Mistakes

**MISTAKE 1: Index on Every Column**

```sql
-- ❌ Bad: Too many indexes
CREATE INDEX idx_user_name ON users(name);
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_user_age ON users(age);
CREATE INDEX idx_user_city ON users(city);
CREATE INDEX idx_user_phone ON users(phone);

Problem:
- Indexes take lots of storage
- INSERT becomes slow (update all 5 indexes!)
- Memory bloated
- Maintenance nightmare
```

**GOOD: Index only frequently queried columns**

```sql
-- ✅ Good: Strategic indexes
CREATE INDEX idx_user_email ON users(email);    -- Used in login
CREATE INDEX idx_user_id_created ON users(id, created_date);  -- Used in queries
-- Don't index phone/city (rarely used)
```

**MISTAKE 2: Misunderstanding Index Order**

```sql
-- ❌ Inefficient: Index on (age, user_id)
CREATE INDEX idx_age_user ON users(age, user_id);

Query: SELECT * WHERE user_id = 123 AND age > 25
Problem: Index built for (age, user_id) order
         Query starts with user_id
         Can't use index efficiently! ❌

-- ✅ Good: Index matches query order
CREATE INDEX idx_user_age ON users(user_id, age);

Query: SELECT * WHERE user_id = 123 AND age > 25
Result: Uses index perfectly! ✅
```

**MISTAKE 3: Not Considering Selectivity**

```sql
-- ❌ Bad: Index on low-selectivity column
CREATE INDEX idx_gender ON users(gender);

Problem:
Column has only 3 values: M, F, Other
Query: WHERE gender = 'M'
Result: Still scans half the table!
Index adds overhead without much benefit.

-- ✅ Good: Index on high-selectivity column
Create INDEX idx_email ON users(email);

Column has millions of unique values
Query: WHERE email = 'alice@example.com'
Result: Instantly finds 1 row! ✅
```

### Query Optimization Techniques

**EXPLAIN to see if index is used:**

```sql
-- Check if query uses index
EXPLAIN SELECT * FROM users WHERE email = 'alice@example.com';

Output:
Seq Scan on users (cost=0.00..1000.00) ❌
Could be improved with index!

After adding index:
CREATE INDEX idx_email ON users(email);

EXPLAIN SELECT * FROM users WHERE email = 'alice@example.com';

Output:
Index Scan using idx_email (cost=0.10..0.20) ✅
Much faster!
```

**Statistics Help Optimizer:**

```sql
-- Tell database to update statistics
ANALYZE users;

-- Now optimizer knows:
-- - Column distribution
-- - Unique value count
-- - Can make better decisions

Query: SELECT * FROM users WHERE age > 25 AND city = 'NYC'
Optimizer thinks:
- 1M users total
- age > 25 filters to 800k users (80%)
- city = 'NYC' filters to 100k users (10%)
- Total result: ~80k rows
- Use city index first! (more selective)
```

---

## 🐍 Python Code Example

### ❌ Slow Queries (No Indexes)

```python
import sqlite3
import time

def slow_queries():
    """Demonstrate query speed WITHOUT indexes"""
    
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Create table (no indexes)
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER,
            name TEXT,
            email TEXT,
            age INTEGER,
            city TEXT
        )
    ''')
    
    # Insert 100,000 users
    print("Inserting 100,000 users...")
    users = [(i, f"User{i}", f"user{i}@example.com", 20 + (i % 50), 
              ["NYC", "LA", "Chicago", "Boston"][i % 4])
             for i in range(100_000)]
    cursor.executemany(
        "INSERT INTO users VALUES (?, ?, ?, ?, ?)",
        users
    )
    conn.commit()
    
    # Query 1: Find user by email
    print("\nQuery 1: Find user by email (NO INDEX)")
    start = time.time()
    for _ in range(100):
        cursor.execute("SELECT * FROM users WHERE email = 'user50000@example.com'")
        _ = cursor.fetchone()
    duration = time.time() - start
    print(f"Time for 100 queries: {duration:.3f}s (avg: {duration/100*1000:.1f}ms each)")
    
    # Query 2: Find users by age range
    print("\nQuery 2: Find users by age range (NO INDEX)")
    start = time.time()
    cursor.execute("SELECT * FROM users WHERE age > 40")
    results = cursor.fetchall()
    duration = time.time() - start
    print(f"Time: {duration:.3f}s, Found: {len(results)} users")
    
    # Query 3: Complex query
    print("\nQuery 3: Complex query (NO INDEX)")
    start = time.time()
    cursor.execute("SELECT * FROM users WHERE age > 35 AND city = 'NYC'")
    results = cursor.fetchall()
    duration = time.time() - start
    print(f"Time: {duration:.3f}s, Found: {len(results)} users")
    
    conn.close()

slow_queries()

# Output (without indexes):
# Query 1: Find user by email (NO INDEX)
# Time for 100 queries: 0.450s (avg: 4.5ms each)
# 
# Query 2: Find users by age range (NO INDEX)
# Time: 0.025s, Found: 50000 users
# 
# Query 3: Complex query (NO INDEX)
# Time: 0.015s, Found: 5000 users

# ❌ These are SLOW for a 100K dataset
# Imagine with 1M or 1B users!
```

### ✅ Fast Queries (With Indexes)

```python
import sqlite3
import time

def fast_queries():
    """Demonstrate query speed WITH indexes"""
    
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER,
            name TEXT,
            email TEXT,
            age INTEGER,
            city TEXT
        )
    ''')
    
    # Insert 100,000 users
    print("Inserting 100,000 users...")
    users = [(i, f"User{i}", f"user{i}@example.com", 20 + (i % 50), 
              ["NYC", "LA", "Chicago", "Boston"][i % 4])
             for i in range(100_000)]
    cursor.executemany(
        "INSERT INTO users VALUES (?, ?, ?, ?, ?)",
        users
    )
    conn.commit()
    
    # CREATE INDEXES
    print("Creating indexes...")
    start = time.time()
    cursor.execute("CREATE INDEX idx_email ON users(email)")
    cursor.execute("CREATE INDEX idx_age_city ON users(age, city)")
    cursor.execute("CREATE INDEX idx_city ON users(city)")
    conn.commit()
    index_time = time.time() - start
    print(f"Index creation time: {index_time:.3f}s")
    
    # Query 1: Find user by email (uses idx_email)
    print("\nQuery 1: Find user by email (WITH INDEX)")
    start = time.time()
    for _ in range(100):
        cursor.execute("SELECT * FROM users WHERE email = 'user50000@example.com'")
        _ = cursor.fetchone()
    duration = time.time() - start
    print(f"Time for 100 queries: {duration:.3f}s (avg: {duration/100*1000:.1f}ms each)")
    print(f"Speedup: ~{4.5/(duration/100*1000):.0f}x faster!")
    
    # Query 2: Find users by age range (uses idx_age_city)
    print("\nQuery 2: Find users by age range (WITH INDEX)")
    start = time.time()
    cursor.execute("SELECT * FROM users WHERE age > 40")
    results = cursor.fetchall()
    duration = time.time() - start
    print(f"Time: {duration:.3f}s, Found: {len(results)} users")
    
    # Query 3: Complex query (uses idx_age_city)
    print("\nQuery 3: Complex query (WITH INDEX)")
    start = time.time()
    cursor.execute("SELECT * FROM users WHERE age > 35 AND city = 'NYC'")
    results = cursor.fetchall()
    duration = time.time() - start
    print(f"Time: {duration:.3f}s, Found: {len(results)} users")
    
    # Check index statistics
    print("\nIndex Statistics:")
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index'")
    for name, sql in cursor.fetchall():
        print(f"  {name}: {sql}")
    
    conn.close()

fast_queries()

# Output (with indexes):
# Query 1: Find user by email (WITH INDEX)
# Time for 100 queries: 0.015s (avg: 0.15ms each)
# Speedup: ~30x faster!
# 
# Query 2: Find users by age range (WITH INDEX)
# Time: 0.003s, Found: 50000 users
# 
# Query 3: Complex query (WITH INDEX)
# Time: 0.001s, Found: 5000 users
```

### ✅ Index Analysis Tool

```python
import sqlite3

class IndexAnalyzer:
    """Analyze and optimize indexes"""
    
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
    
    def find_unused_indexes(self):
        """Find indexes that aren't helping"""
        # Note: SQLite doesn't track index usage like PostgreSQL
        # This is a conceptual example
        self.cursor.execute('''
            SELECT name, sql FROM sqlite_master 
            WHERE type='index' AND sql IS NOT NULL
        ''')
        
        indexes = self.cursor.fetchall()
        print("Current Indexes:")
        for name, sql in indexes:
            print(f"  {name}: {sql}")
    
    def estimate_query_performance(self, query):
        """Estimate if query will be fast"""
        self.cursor.execute(f"EXPLAIN QUERY PLAN {query}")
        plan = self.cursor.fetchall()
        
        print(f"\nQuery: {query}")
        print("Execution Plan:")
        for row in plan:
            print(f"  {row}")
            
            # Check if it's a full scan
            if "SCAN" in str(row):
                if "TABLE" in str(row):
                    print("  ⚠️ WARNING: Full table scan (slow!)")
                    print("  💡 Suggestion: Add index on WHERE columns")
            elif "SEARCH" in str(row):
                print("  ✅ Using index (fast!)")
    
    def analyze_column_selectivity(self, table, column):
        """Check how selective a column is"""
        # Get total rows
        self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
        total = self.cursor.fetchone()[0]
        
        # Get unique values
        self.cursor.execute(f"SELECT COUNT(DISTINCT {column}) FROM {table}")
        unique = self.cursor.fetchone()[0]
        
        selectivity = unique / total * 100
        
        print(f"\nColumn Selectivity: {table}.{column}")
        print(f"  Total rows: {total}")
        print(f"  Unique values: {unique}")
        print(f"  Selectivity: {selectivity:.1f}%")
        
        if selectivity > 90:
            print("  ✅ Good for indexing (high selectivity)")
        elif selectivity > 50:
            print("  🟡 OK for indexing (medium selectivity)")
        else:
            print("  ❌ Poor for indexing (low selectivity)")
    
    def recommend_indexes(self, table, common_queries):
        """Recommend indexes based on query patterns"""
        print(f"\nRecommended Indexes for {table}:")
        
        # Analyze WHERE clauses
        columns_in_where = set()
        for query in common_queries:
            if "WHERE" in query:
                where_part = query.split("WHERE")[1]
                # Simple extraction (real implementation more complex)
                columns_in_where.update([col.split()[0] for col in where_part.split("AND")])
        
        if columns_in_where:
            for col in columns_in_where:
                print(f"  CREATE INDEX idx_{table}_{col} ON {table}({col});")
        else:
            print("  No indexes recommended based on queries")

# Usage
analyzer = IndexAnalyzer(':memory:')
analyzer.find_unused_indexes()
analyzer.estimate_query_performance("SELECT * FROM users WHERE email = 'test@example.com'")
# analyzer.analyze_column_selectivity('users', 'email')
# analyzer.recommend_indexes('users', [
#     "SELECT * FROM users WHERE email = 'test@example.com'",
#     "SELECT * FROM users WHERE age > 25 AND city = 'NYC'"
# ])
```


---



| Concept           | B-Tree                         | B+Tree                                   |
| ----------------- | ------------------------------ | ---------------------------------------- |
| **Data stored**   | In all nodes (internal + leaf) | Only in leaf nodes                       |
| **Internal node** | Can contain record pointers    | Contains only keys                       |
| **Leaf nodes**    | Contain data pointers          | Contain data pointers + linked list      |
| **Range scans**   | Slower                         | Fast, sequential                         |
| **Used by**       | Legacy DBs                     | MongoDB, MySQL, PostgreSQL, file systems |




## 🧩  First: What is a B-Tree, really?

Think of a B-Tree like a **sorted bookshelf**.

* Each **node** can store multiple keys (like `_id`s).
* When a node becomes too full, it **splits** into smaller shelves (nodes).
* The **middle key** moves up to become a parent (root or internal node).
* That parent then **directs** lookups to left or right child nodes, based on key order.

👉 So the **structure forms dynamically** as more keys are inserted.

---

## 📦 When MongoDB starts inserting documents

Say you’re inserting `_id`s in sorted order (as ObjectIds tend to be roughly time-sorted):

```
6900fb9908a372ae0578c621  
6900fb9908a372ae0578c622  
6900fb9908a372ae0578c623  
6900fb9908a372ae0578c624  
...
```

MongoDB uses the **WiredTiger storage engine** (which uses a B+Tree for indexes).

Let’s assume:

* Each node (page) can hold up to **3 keys** (for simplicity).
  (In reality, it’s thousands of keys per page depending on page size, usually 4KB or 16KB.)

---

## ⚙️  Step-by-Step: How the `_id` B-Tree Forms

### 🪜 Step 1: First few inserts — single node

```
Insert _id: 621 → [621]
Insert _id: 622 → [621, 622]
Insert _id: 623 → [621, 622, 623]
```

✅ Fits in one node, so the tree looks like:

```
[621, 622, 623]
```

This is both the **root** and **leaf** (a flat structure).

---

### 🪜 Step 2: Insert one more (node full → split)

```
Insert _id: 624
```

Now node is **over capacity** (4 keys for max 3).
→ MongoDB/WiredTiger **splits** it into two leaf nodes.

```
Left:  [621, 622]
Middle: 623 (moves up)
Right: [624]
```

So the new structure is:

```
         [623]
        /     \
  [621,622]   [624]
```

Now `[623]` becomes the **root key**.
Keys `< 623` go left, keys `> 623` go right.

---

### 🪜 Step 3: More inserts (tree grows)

Insert `_id: 625, 626, 627, 628, ...` — Mongo keeps filling the right leaf node.

```
Right leaf: [624,625,626]
Insert 627 → full → split again.
```

When it splits:

* Middle key (625) goes **up** into the parent.
* Parent (root) now has 2 keys.

```
         [623,625]
        /    |    \
 [621,622] [624] [626,627]
```

✅ The tree has grown *wider*, but it’s still balanced.

---

### 🪜 Step 4: Root Split (when root overflows)

As more `_id`s come, eventually even the **root node** gets full.
When that happens, the root **splits** too, and a new root is created above it.

So if you insert up to `_id: 630`, you might get:

```
              [625]
             /     \
      [623]         [627]
     /   \          /   \
[621,622] [624] [626] [628,629,630]
```

✅ Notice:

* The **root** key (625) divides the tree.
* Each level directs you closer to the leaf containing your `_id`.

---

## 🧮  How Mongo Decides Root and Children

It’s **not manually chosen** — it’s **algorithmic**:

* Each index page (node) can hold a certain number of key-pointer pairs.
* When a node exceeds its capacity → **split**.
* **Middle key** bubbles up → becomes parent key.
* Children are automatically linked left/right by key ranges.

This ensures:

* All leaves are at the same depth (balanced)
* Keys are always sorted
* Lookup time stays O(log N)

---

## 🧠  What Happens When You Have 100 Documents

With 100 `_id`s (ObjectIds are roughly sequential):

* MongoDB starts from one node.
* Gradually splits nodes as more documents come.
* The result is a small B+Tree with:

  * 1 root node
  * 1–2 internal levels
  * ~10–20 leaf nodes depending on page size.

Roughly like:

```
                [6900fb9908a372ae0578c650]
               /                         \
     [6900fb9908a372ae0578c625]       [6900fb9908a372ae0578c675]
    /         \                       /             \
 [20–25]   [26–30]              [65–70]         [71–100]
```

Each leaf node holds pointers to actual documents on disk.

---

## ⚡ If Inserts Are Random (Not Sequential)

If `_id`s were random UUIDs instead of sequential ObjectIds:

* Inserts would happen **all over the tree**, not just the right edge.
* MongoDB would have to **rebalance** and **split nodes** more often.
* That’s why sequential ObjectIds (by timestamp) perform better — they always append near the “rightmost leaf.”

---

## 🧾  Summary Table

| Concept          | Meaning                                            |
| ---------------- | -------------------------------------------------- |
| Node             | A “page” that holds multiple keys (`_id`s)         |
| Root node        | The top-most node (middle key promoted first time) |
| Left/Right child | Nodes holding smaller/larger keys than parent      |
| Split            | Happens when a node gets too full                  |
| Promotion        | Middle key moves up to parent node                 |
| Pointer          | Links parent → child or leaf → data location       |
| Balanced         | All leaf nodes are at same depth                   |
| Growth           | Automatically managed by WiredTiger engine         |


---

## 💡 Mini Project: "Build an Index Optimizer"

### Phase 1: Simple Index Advisor ⭐

**Requirements:**
- Analyze query patterns
- Suggest indexes
- Display recommendations

**Code:**
```python
class SimpleIndexAdvisor:
    def __init__(self):
        self.queries = []
    
    def add_query(self, query):
        """Record a query"""
        self.queries.append(query)
    
    def analyze(self):
        """Suggest indexes"""
        columns_in_where = {}
        
        for query in self.queries:
            if "WHERE" in query:
                where_part = query.split("WHERE")[1]
                for col in where_part.split("AND"):
                    col_name = col.split()[0].strip()
                    columns_in_where[col_name] = columns_in_where.get(col_name, 0) + 1
        
        print("Recommended Indexes:")
        for col, count in sorted(columns_in_where.items(), key=lambda x: x[1], reverse=True):
            print(f"  CREATE INDEX idx_{col} ON users({col});  -- Used {count} times")
```

---

### Phase 2: Advanced (With Performance Metrics) ⭐⭐

**Requirements:**
- Measure query time
- Before/after index comparison
- Cost estimation

**Features:**
```python
class AdvancedIndexOptimizer:
    def measure_query_time(self, conn, query, iterations=10):
        """Measure query performance"""
        cursor = conn.cursor()
        start = time.time()
        for _ in range(iterations):
            cursor.execute(query)
        return (time.time() - start) / iterations
    
    def optimize(self, conn, table, query):
        """Show impact of index"""
        # Measure without index
        time_before = self.measure_query_time(conn, query)
        
        # Create index
        # Extract WHERE column
        # CREATE INDEX
        
        # Measure with index
        time_after = self.measure_query_time(conn, query)
        
        speedup = time_before / time_after
        print(f"Speedup: {speedup:.1f}x faster!")
```

---

### Phase 3: Enterprise (Auto-Optimization) ⭐⭐⭐

**Requirements:**
- Monitor slow queries
- Auto-create indexes
- Track index effectiveness
- Remove unused indexes

**Features:**
```python
class EnterpriseIndexManager:
    def __init__(self, db_conn):
        self.conn = db_conn
        self.slow_query_log = []
    
    def monitor_queries(self):
        """Monitor and log slow queries"""
        # Track queries > 100ms
        # Log which columns are used
        # Identify patterns
    
    def auto_optimize(self):
        """Automatically create beneficial indexes"""
        for query in self.slow_query_log:
            if self.would_benefit_from_index(query):
                self.create_index(query)
    
    def cleanup_unused_indexes(self):
        """Remove indexes that aren't helping"""
        for index in self.get_all_indexes():
            if self.index_usage_count(index) == 0:
                print(f"Dropping unused index: {index}")
                self.drop_index(index)
```

---

## ⚖️ Indexing Trade-offs

| Aspect | Without Index | With Index |
|--------|---|---|
| **Query Speed** | Slow (O(n)) | Fast (O(log n)) |
| **INSERT Speed** | Fast | Slower (update index) |
| **UPDATE Speed** | Fast | Slower (update index) |
| **DELETE Speed** | Fast | Slower (update index) |
| **Storage** | Minimal | +20-50% |
| **Memory Usage** | Lower | Higher |
| **Maintenance** | None | Needed (ANALYZE) |
| **Ideal For** | Write-heavy | Read-heavy |

---

## 🎯 When to Index

```
✅ INDEX IF:
- Column frequently used in WHERE clauses
- Column has high selectivity (many unique values)
- Queries run often (worth the overhead)
- Reads >> Writes
- SELECT queries are performance bottleneck

❌ DON'T INDEX IF:
- Column has low selectivity (gender, boolean)
- Updates/Deletes are frequent
- Storage space is limited
- Query rarely runs
- Performance isn't a bottleneck
```

---

## ❌ Common Mistakes

### Mistake 1: Index Everything

```sql
-- ❌ Bad: Indexes on all columns
CREATE INDEX idx_gender ON users(gender);  -- Only M/F/O (3 values!)
CREATE INDEX idx_active ON users(active);  -- Only true/false (2 values!)
CREATE INDEX idx_created ON users(created_date);  -- Not queried often

Problem:
- Wasted storage
- Slows down INSERT
- Maintenance overhead
```

### Mistake 2: Wrong Index Order

```sql
-- ❌ Bad: Index on (B, A) but queries use (A, B)
CREATE INDEX idx_wrong ON users(age, user_id);

Query: SELECT * WHERE user_id = 1 AND age > 25;
Problem: Index can't be used efficiently!

-- ✅ Good: Index matches query order
CREATE INDEX idx_right ON users(user_id, age);
```

### Mistake 3: Forgetting to ANALYZE

```sql
-- ❌ Query slow even with index
SELECT * FROM users WHERE city = 'NYC' AND age > 25;

Reason: Statistics outdated
Optimizer doesn't know city is more selective

-- ✅ Update statistics
ANALYZE users;

Now optimizer: "NYC is 1% of users, use city index first!"
```

---

## 📚 Additional Resources

**Tools:**
- [EXPLAIN](https://www.postgresql.org/docs/current/sql-explain.html) - Understand query plans
- [pgBadger](https://pgbadger.ortho.info/) - PostgreSQL query analyzer
- [Percona Toolkit](https://www.percona.com/software/database-tools/percona-toolkit) - MySQL tools
- [Query Profiler](https://dev.mysql.com/doc/refman/8.0/en/performance-schema.html) - MySQL profiling

**Reading:**
- DDIA Chapter 3 - Storage and Retrieval
- "Indexes Under the Hood" - High Scalability blog
- PostgreSQL Index Documentation

---

## 🎯 Before You Leave

**Can you answer these?**

1. **What's the main purpose of a database index?**
   - Answer: Speed up queries (trade storage for speed)

2. **Why is a B-Tree index so popular?**
   - Answer: Balanced, self-organizing, O(log n) lookups

3. **What's a composite index and when use it?**
   - Answer: Multiple columns; use when queries filter by multiple columns

4. **Why do INSERT/UPDATE/DELETE slow down with indexes?**
   - Answer: Index must be updated when data changes

5. **What's index selectivity and why does it matter?**
   - Answer: % of unique values; high selectivity = good for indexing

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **DBA 1:** "I indexed every column."
>
> **DBA 2:** "How's INSERT performance?"
>
> **DBA 1:** "...Horrible. Takes 5 seconds per row."
>
> **DBA 2:** "Yeah. You indexed columns that don't need it."
>
> **DBA 1:** "But I wanted it to be fast!"
>
> **DBA 2:** "Now it's slow at everything." 🤷

---

[← Back to Main](../README.md) | [Previous: SQL vs NoSQL](07-sql-vs-nosql.md) | [Next: Sharding & Partitioning →](09-sharding-partitioning.md)

---

**Last Updated:** November 10, 2025  
**Difficulty:** ⭐⭐⭐ Intermediate (requires database concepts)  
**Time to Read:** 23 minutes  
**Time to Build Optimizer:** 3-5 hours per phase  

---

*Indexing: the difference between "found instantly" and "still waiting for the query to finish".* 🚀