# 07. SQL vs NoSQL

SQL is like going to a structured grocery store where everything is in its place. NoSQL is like a farmer's market where you find good deals but nobody can tell you exactly where the tomatoes are. 🍅

[← Back to Main](../README.md) | [Previous: Load Testing & Capacity Estimation](06-load-testing-capacity.md) | [Next: Database Indexes →](08-database-indexes.md)

---

## 🎯 Quick Summary

**SQL and NoSQL** are two fundamentally different ways to store and organize data. SQL is structured, uses tables, and enforces schemas. NoSQL is flexible, uses various formats (documents, key-value, graphs), and adapts easily. Neither is universally better; choice depends on your use case.

Think of it as: **SQL = Structured Tables, NoSQL = Flexible Collections**

---

## 🌟 Beginner Explanation

### The Filing Cabinet Analogy

**SQL (Traditional Filing Cabinet):**

```
FILING CABINET (SQL Database)

Drawer 1: USERS
├─ Folder 1: User #1
│  ├─ Name: Alice
│  ├─ Email: alice@example.com
│  ├─ Age: 28
│  └─ City: NYC
├─ Folder 2: User #2
│  ├─ Name: Bob
│  ├─ Email: bob@example.com
│  ├─ Age: 32
│  └─ City: LA

Drawer 2: ORDERS
├─ Folder 1: Order #1
│  ├─ OrderID: 101
│  ├─ UserID: 1 (links to User #1)
│  ├─ Amount: $100
│  └─ Date: 2024-01-01

RULES:
✅ Every drawer has same structure
✅ Every folder has same fields
✅ City field required (not optional)
✅ Age must be a number
✅ Very organized, rigid
❌ Hard to change structure
❌ Takes time to add new fields
```

**NoSQL (Messy Desk):**

```
MESSY DESK (NoSQL Database)

Collection: USERS
{
  "user1": {
    "name": "Alice",
    "email": "alice@example.com",
    "age": 28,
    "city": "NYC",
    "phone": "555-1234"  ← Alice has phone
  },
  "user2": {
    "name": "Bob",
    "email": "bob@example.com",
    "age": 32
    # Bob doesn't have phone, city, that's OK!
  },
  "user3": {
    "name": "Charlie",
    "email": "charlie@example.com",
    "age": 25,
    "city": "Chicago",
    "tags": ["admin", "developer"]  ← Charlie has extra field!
  }
}

RULES:
✅ Each document can be different
✅ Optional fields (totally fine)
✅ Easy to add new fields
✅ Flexible structure
✅ Fast to get started
❌ No rigid structure
❌ Harder to validate data
❌ Can become messy
```

### Real-World Analogy: Restaurant Menu

**SQL Restaurant:**
```
RESTAURANT WITH FIXED MENU (SQL)

Every dish has:
- Name (required)
- Price (required)
- Ingredients (required)
- Calories (required)
- Allergens (required)

Structure is same for every dish ✅
Menu is very organized ✅
New dish? Need to update entire menu structure ❌
Takes time to decide on new categories ❌
```

**NoSQL Restaurant:**
```
FOOD TRUCK WITH CHANGING MENU (NoSQL)

Today's special:
- Tacos: $5 (no price listed yesterday)
- Quesadillas: $6 (not on menu yesterday)
- Mystery salad: ingredients unknown (weird but allowed)

Very flexible ✅
Update menu instantly ✅
Customers confused (what's in salad?) ❌
No consistency ❌
```

### Quick Comparison

```
SITUATION 1: E-commerce Website
├─ Users (predictable: name, email, phone)
├─ Products (predictable: name, price, description)
├─ Orders (predictable: user_id, product_id, quantity)
→ Use SQL ✅ (structured data)

SITUATION 2: Social Media Feed
├─ Posts (varied: text only, text+image, text+video, polls, etc.)
├─ Comments (varied: just text, or text+emoji, or text+image)
├─ Stories (temporary, different schema than posts)
→ Use NoSQL ✅ (flexible, varied data)

SITUATION 3: Real-time Analytics
├─ Millions of events per second
├─ Events have 50+ attributes
├─ Attributes vary by event type
→ Use NoSQL ✅ (fast writes, flexible)

SITUATION 4: Financial System
├─ Transactions (exact precision required)
├─ Balances (must be consistent)
├─ Audits (must follow rules exactly)
→ Use SQL ✅ (structured, ACID)
```

---

## 🔬 Advanced Explanation

### SQL: Structured Query Language

**Architecture:**

```
RELATIONAL DATABASE (SQL)

Tables (like Excel sheets):
┌─────── USERS ───────┐
│ id | name  | email  │
├────┼───────┼────────┤
│ 1  │Alice  │alice@… │
│ 2  │Bob    │bob@…   │
│ 3  │Carol  │carol@…│
└────────────────────┘

┌────────── ORDERS ────────┐
│ id | user_id | amount | date │
├────┼─────────┼────────┼──────┤
│101 │ 1       │ 100    │ 1/1  │
│102 │ 2       │ 250    │ 1/2  │
│103 │ 1       │ 75     │ 1/3  │
└──────────────────────────┘

RELATIONSHIPS:
Orders.user_id → USERS.id (Foreign Key)
Alice (id=1) has multiple orders (101, 103)
```

**ACID Properties (Guaranteed):**

```
A = ATOMICITY: All or nothing
  Transaction: Send $100 from Alice to Bob
  ├─ Deduct $100 from Alice: SUCCESS
  ├─ Add $100 to Bob: FAILS (system crash)
  └─ Result: ROLLBACK - Alice gets $100 back
     (Not: Alice loses $100 and Bob gets nothing)

C = CONSISTENCY: Valid to valid state
  Before: Alice=$1000, Bob=$500 (total=$1500)
  After: Alice=$900, Bob=$600 (total=$1500)
  ✅ Always consistent (total unchanged)

I = ISOLATION: Transactions don't interfere
  Transaction 1: Read Alice's balance ($1000)
  Transaction 2: Deduct $100 from Alice
  Transaction 1: Read Alice's balance again
  ✅ Still sees $1000 (Transaction 2 isolated)

D = DURABILITY: Saved permanently
  Write to disk: ✅ Confirmed
  Server crashes: ✅ Data still there
  You can trust it
```

**SQL Schema:**

```sql
-- Define structure upfront
CREATE TABLE users (
  id INT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,      -- Required field
  email VARCHAR(100) UNIQUE,        -- Must be unique
  age INT,                          -- Optional
  created_at TIMESTAMP DEFAULT NOW()
);

-- RIGID: Can't insert without name!
INSERT INTO users (id, email, age)  -- ❌ Fails! name is required
VALUES (1, 'alice@example.com', 28);

-- ✅ Works: Provides required fields
INSERT INTO users (id, name, email, age)
VALUES (1, 'Alice', 'alice@example.com', 28);
```

**SQL Queries:**

```sql
-- Find all users named Alice
SELECT * FROM users WHERE name = 'Alice';

-- Find orders for user Alice
SELECT o.* FROM orders o
JOIN users u ON o.user_id = u.id
WHERE u.name = 'Alice';

-- Complex: Orders > $100 by city
SELECT u.city, COUNT(*) as order_count, SUM(o.amount) as total
FROM orders o
JOIN users u ON o.user_id = u.id
WHERE o.amount > 100
GROUP BY u.city;

-- Power: Complex logic possible!
```

### NoSQL: Not Only SQL

**Types of NoSQL:**

```
1. DOCUMENT STORES (MongoDB, Firestore)
   ├─ Store data as documents (JSON-like)
   ├─ Flexible schema
   ├─ Good for: Content, user profiles, varied data
   
2. KEY-VALUE STORES (Redis, Memcached)
   ├─ Simple: key → value
   ├─ Super fast access
   ├─ Good for: Cache, sessions, counters
   
3. COLUMN-FAMILY (HBase, Cassandra)
   ├─ Store by column (not row)
   ├─ Fast analytics
   ├─ Good for: Time series, analytics
   
4. GRAPH STORES (Neo4j)
   ├─ Store relationships as edges
   ├─ Fast relationship queries
   ├─ Good for: Social networks, recommendations
   
5. SEARCH ENGINES (Elasticsearch)
   ├─ Full-text search
   ├─ Autocomplete, fuzzy matching
   ├─ Good for: Search, logging
```

**Document Store Example (MongoDB):**

```javascript
// No schema needed!
// Each document can be different

db.users.insertOne({
  name: "Alice",
  email: "alice@example.com",
  age: 28,
  phone: "555-1234"
});

db.users.insertOne({
  name: "Bob",
  email: "bob@example.com"
  // No age, no phone - that's fine!
});

db.users.insertOne({
  name: "Carol",
  email: "carol@example.com",
  age: 25,
  tags: ["admin", "developer"],  // Extra field!
  metadata: {                      // Nested object!
    joinDate: "2024-01-01",
    lastLogin: "2024-01-15"
  }
});

// Query: Find users over 25
db.users.find({ age: { $gt: 25 } });

// Query: Find admins (in tags array)
db.users.find({ tags: "admin" });
```

**Key-Value Store (Redis):**

```
SET user:1:name "Alice"          // Store string
SET user:1:email "alice@…"
SET user:1:age 28                // Number

GET user:1:name                  // Retrieve: "Alice"
GET user:1:age                   // Retrieve: 28

INCR user:1:age                  // Increment: 28 → 29
EXPIRE user:1:name 3600          // Delete in 1 hour
```

**Key Differences:**

```
SQL GUARANTEES:
✅ ACID transactions
✅ Data consistency
✅ Complex queries
✅ Relationships (joins)
✅ Schema validation
❌ Slower at massive scale
❌ Rigid structure

NoSQL ADVANTAGES:
✅ Horizontal scaling (very easy)
✅ Flexible schema
✅ Fast writes (no validation)
✅ Handle varied data
✅ Great for big data
❌ No transactions (some have them now)
❌ Weaker consistency
❌ Harder complex queries
```

---

## 🐍 Python Code Example

### ❌ SQL Database (Simple)

```python
# ===== SQL WITH SQLite =====
import sqlite3

def sql_example():
    """Simple SQL operations"""
    
    # Connect to database
    conn = sqlite3.connect(':memory:')  # In-memory for demo
    cursor = conn.cursor()
    
    # CREATE TABLE (define schema)
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            age INTEGER
        )
    ''')
    
    # INSERT data
    cursor.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                   ("Alice", "alice@example.com", 28))
    cursor.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                   ("Bob", "bob@example.com", 32))
    cursor.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                   ("Carol", "carol@example.com", 25))
    conn.commit()
    
    # QUERY data
    cursor.execute("SELECT * FROM users WHERE age > 26")
    results = cursor.fetchall()
    for user_id, name, email, age in results:
        print(f"{name} ({age}): {email}")
    
    # JOIN example
    cursor.execute('''
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            amount REAL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute("INSERT INTO orders (user_id, amount) VALUES (1, 100)")
    cursor.execute("INSERT INTO orders (user_id, amount) VALUES (1, 75)")
    cursor.execute("INSERT INTO orders (user_id, amount) VALUES (2, 250)")
    conn.commit()
    
    # Complex query with JOIN
    cursor.execute('''
        SELECT u.name, COUNT(*) as order_count, SUM(o.amount) as total
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        GROUP BY u.id
    ''')
    
    for name, order_count, total in cursor.fetchall():
        print(f"{name}: {order_count} orders, ${total}")
    
    conn.close()

# Output:
# Alice (28): alice@example.com
# Bob (32): bob@example.com
# Carol (25): carol@example.com
# Alice: 2 orders, $175.0
# Bob: 1 orders, $250.0
# Carol: 0 orders, None

sql_example()

# Benefits:
# ✅ Strong schema
# ✅ JOINs work perfectly
# ✅ Complex queries
# ✅ Data integrity
```

### ✅ NoSQL Database (Flexible)

```python
# ===== NoSQL WITH MongoDB =====
from pymongo import MongoClient
import json

def nosql_example():
    """NoSQL operations with MongoDB"""
    
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['myapp']
    users_collection = db['users']
    
    # No schema definition needed!
    
    # INSERT flexible documents
    users = [
        {
            "name": "Alice",
            "email": "alice@example.com",
            "age": 28,
            "phone": "555-1234"  # Alice has phone
        },
        {
            "name": "Bob",
            "email": "bob@example.com",
            "age": 32
            # Bob doesn't have phone (that's OK!)
        },
        {
            "name": "Carol",
            "email": "carol@example.com",
            "age": 25,
            "tags": ["admin", "developer"],  # Carol has extra field!
            "metadata": {
                "joinDate": "2024-01-01"
            }
        }
    ]
    
    result = users_collection.insert_many(users)
    print(f"Inserted {len(result.inserted_ids)} users")
    
    # QUERY data (flexible)
    print("\nUsers over 26:")
    for user in users_collection.find({"age": {"$gt": 26}}):
        print(f"  {user['name']}: {user['age']}")
    
    # Query with optional fields
    print("\nUsers with phone:")
    for user in users_collection.find({"phone": {"$exists": True}}):
        print(f"  {user['name']}: {user['phone']}")
    
    # Query with tags
    print("\nAdmins:")
    for user in users_collection.find({"tags": "admin"}):
        print(f"  {user['name']}")
    
    # UPDATE flexible document
    users_collection.update_one(
        {"name": "Bob"},
        {"$set": {"phone": "555-5678", "nickname": "Bobby"}}
    )
    print(f"\nUpdated Bob: {users_collection.find_one({'name': 'Bob'})}")
    
    # INSERT orders (same collection or different?)
    orders_collection = db['orders']
    orders = [
        {"user_id": user['_id'], "amount": 100} for user in users
    ]
    orders_collection.insert_many(orders)
    
    # Query across collections
    print("\nOrders:")
    for order in orders_collection.find():
        user = users_collection.find_one({"_id": order['user_id']})
        print(f"  {user['name']}: ${order['amount']}")

# Benefits:
# ✅ Flexible schema
# ✅ Easy to get started
# ✅ Handle varied data
# ✅ No migrations
# ❌ No native JOINs
# ❌ Harder to ensure consistency
```

### ✅ Comparison: When to Use Each

```python
class DatastoreChooser:
    """Decide which database to use"""
    
    @staticmethod
    def evaluate_sql():
        """SQL is good when:"""
        return {
            "use_sql": [
                "Data is structured and predictable",
                "Relationships matter (JOINs needed)",
                "ACID transactions required",
                "Complex queries needed",
                "Data integrity critical",
                "Queries are complex"
            ],
            "examples": [
                "E-commerce (products, orders, inventory)",
                "Banking (accounts, transactions)",
                "SaaS app (users, subscriptions, billing)",
                "Reporting system (need complex aggregations)"
            ]
        }
    
    @staticmethod
    def evaluate_nosql():
        """NoSQL is good when:"""
        return {
            "use_nosql": [
                "Data is unstructured or varied",
                "Need horizontal scaling",
                "Flexibility matters",
                "Write-heavy workload",
                "Real-time data (events, logs)",
                "Simple queries, lots of them"
            ],
            "examples": [
                "Social media (varied posts, comments)",
                "IoT sensors (millions of events)",
                "Real-time analytics (events)",
                "Content management (varied schemas)"
            ]
        }
    
    @staticmethod
    def evaluate_both():
        """Polyglot persistence: Use both!"""
        return {
            "strategy": "Use the right tool for each job",
            "example": {
                "SQL": "User accounts, billing, orders (structured)",
                "NoSQL (Document)": "Product catalogs, user profiles (varied)",
                "NoSQL (Key-Value)": "Cache, sessions, real-time counters",
                "NoSQL (Search)": "Product search, logging"
            },
            "companies": [
                "Netflix: SQL + NoSQL",
                "Twitter: SQL + NoSQL",
                "Amazon: Mix of everything",
                "Uber: Polyglot (SQL, NoSQL, Graph, TimeSeriesDB)"
            ]
        }

# Usage
chooser = DatastoreChooser()
print("SQL Use Cases:", json.dumps(chooser.evaluate_sql(), indent=2))
print("NoSQL Use Cases:", json.dumps(chooser.evaluate_nosql(), indent=2))
print("Polyglot:", json.dumps(chooser.evaluate_both(), indent=2))
```

---

## 💡 Mini Project: "Build a Flexible Data Store"

### Phase 1: Simple SQL Database ⭐

**Requirements:**
- Create users table
- Create products table
- Link them with foreign keys
- Simple queries

**Code:**
```python
class SimpleStore:
    def __init__(self):
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.setup_tables()
    
    def setup_tables(self):
        # Users
        self.cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE
            )
        ''')
        
        # Products
        self.cursor.execute('''
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL
            )
        ''')
        
        # Orders
        self.cursor.execute('''
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
        ''')
        self.conn.commit()
    
    def add_user(self, name, email):
        self.cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)",
                          (name, email))
        self.conn.commit()
    
    def get_user_orders(self, user_id):
        self.cursor.execute('''
            SELECT u.name, p.name, o.quantity, p.price * o.quantity as total
            FROM orders o
            JOIN users u ON o.user_id = u.id
            JOIN products p ON o.product_id = p.id
            WHERE u.id = ?
        ''', (user_id,))
        return self.cursor.fetchall()

# Usage
store = SimpleStore()
store.add_user("Alice", "alice@example.com")
orders = store.get_user_orders(1)
```

---

### Phase 2: Hybrid Store (SQL + NoSQL) ⭐⭐

**Requirements:**
- SQL for structured data (users, orders)
- NoSQL for varied data (profiles, preferences)
- Query both

**Code:**
```python
class HybridStore:
    def __init__(self):
        # SQL for structured
        self.sql_conn = sqlite3.connect('structured.db')
        self.sql_cursor = self.sql_conn.cursor()
        
        # NoSQL for flexible
        mongo_client = MongoClient('mongodb://localhost:27017/')
        self.mongo_db = mongo_client['flexible']
    
    def get_user_profile(self, user_id):
        # From SQL: Structured data
        self.sql_cursor.execute('''
            SELECT id, name, email FROM users WHERE id = ?
        ''', (user_id,))
        user = self.sql_cursor.fetchone()
        
        # From MongoDB: Flexible data
        profile = self.mongo_db.profiles.find_one({"user_id": user_id})
        
        # Combine results
        return {
            "basic": user,
            "profile": profile
        }
```

---

### Phase 3: Enterprise Data Store ⭐⭐⭐

**Requirements:**
- Multiple data stores (SQL, MongoDB, Redis, Elasticsearch)
- Query router (pick right DB)
- Caching layer
- Optimization

**Features:**
```python
class EnterpriseDataStore:
    def __init__(self):
        self.sql = PostgreSQL()
        self.mongo = MongoDB()
        self.redis = Redis()
        self.elasticsearch = Elasticsearch()
    
    def query(self, query_type, params):
        """Route query to appropriate database"""
        
        if query_type == "user_by_id":
            # Try cache first
            cached = self.redis.get(f"user:{params['id']}")
            if cached:
                return cached
            
            # Query SQL
            user = self.sql.query(f"SELECT * FROM users WHERE id = ?", [params['id']])
            
            # Cache for next time
            self.redis.setex(f"user:{params['id']}", 3600, user)
            
            return user
        
        elif query_type == "search_posts":
            # Full-text search in Elasticsearch
            return self.elasticsearch.search(params['query'])
        
        elif query_type == "user_preferences":
            # Flexible data in MongoDB
            return self.mongo.find_one({"user_id": params['id']})
        
        elif query_type == "recent_logins":
            # Time-series, get from Redis sorted set
            return self.redis.zrange(f"logins:global", 0, 100)
    
    def optimize_queries(self):
        """Add indexes, caching, partitioning"""
        self.sql.add_index("users", "id")
        self.elasticsearch.add_analyzer("posts", "full_text")
        self.redis.set_ttl("session:*", 3600)
```



---

## ⚖️ SQL vs NoSQL: Complete Comparison

| Feature | SQL | NoSQL |
|---------|-----|-------|
| **Schema** | Rigid, defined upfront | Flexible, evolves |
| **Scaling** | Vertical (bigger machine) | Horizontal (more machines) |
| **Transactions** | ✅ ACID guaranteed | ⚠️ Often eventual consistency |
| **Joins** | ✅ Native, powerful | ❌ Application-level |
| **Data Integrity** | ✅ Enforced | ⚠️ Application responsibility |
| **Learning Curve** | 🟡 Medium | 🟡 Medium (different concepts) |
| **Query Language** | SQL (standard) | Varies (JSON, JavaScript, etc.) |
| **Speed** | 50-100ms | 1-10ms (often faster) |
| **Suitable For** | Structured, relational | Varied, massive scale |
| **Examples** | PostgreSQL, MySQL | MongoDB, Cassandra, Redis |
| **Cost at 1TB** | Moderate | Lower (horizontal scaling) |
| **Cost at 1PB** | Very High | Manageable |

---

## 🎯 Real-World Decisions

**Netflix:**
```
✅ SQL: User accounts, subscriptions, billing
✅ NoSQL: User watch history, preferences, recommendations
✅ NoSQL Search: Content search (Elasticsearch)
✅ NoSQL Cache: Session data, trending content (Redis)
```

**Uber:**
```
✅ SQL: User accounts, payment history, order metadata
✅ NoSQL: Real-time location data, driver status
✅ Graph DB: Relationship queries (friend recommendations)
✅ TimeSeriesDB: Metrics, analytics
```

**Twitter:**
```
✅ SQL: User accounts, follower relationships
✅ NoSQL: Tweet data, feed (massive scale)
✅ Search: Tweet search (Elasticsearch)
✅ Cache: Trending topics, home feed (Redis)
```

---

## ❌ Common Mistakes

### Mistake 1: Using NoSQL Everywhere

```python
# ❌ Bad: NoSQL for everything
class BadDesign:
    # Financial transactions in MongoDB
    # ❌ No ACID, money can be lost!
    
    # Complex reports in MongoDB
    # ❌ No JOINs, slow and painful
    
    # User accounts in MongoDB
    # ❌ No schema validation, data corrupts

# ✅ Good: Right tool for job
SQL: Financial transactions
SQL: User accounts
NoSQL: User preferences, real-time data
```

### Mistake 2: Using SQL for Massive Scale

```python
# ❌ Bad: Single SQL database
# 1M QPS hitting one PostgreSQL
# ❌ Can't scale horizontally easily
# ❌ Vertical scaling has limits
# ❌ Cost explodes

# ✅ Good: Design for scale
# Use SQL for structured (accounts, billing)
# Use NoSQL for massive scale (events, logs)
# Cache aggressively
```

### Mistake 3: Ignoring Schema in NoSQL

```python
# ❌ Bad: Completely unstructured
{
  "user_data": {
    "name": "Alice",
    "email": "alice@example.com",
    "age": 28,
    // Wait, was age a string before?
    "created": "2024-01-01",
    // Or timestamp? Nobody knows!
  }
}

# ✅ Good: Document validation
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "email"],
      properties: {
        name: { bsonType: "string" },
        email: { bsonType: "string" },
        age: { bsonType: "int" }
      }
    }
  }
})
```

### Mistake 4: Not Understanding Consistency

```python
# ❌ Bad: Assuming NoSQL has ACID
# Transfer money: deduct from Alice, add to Bob
# System crashes after deduction
# Alice loses money, Bob gets nothing! 😱

# ✅ Good: Handle eventual consistency
# SQL: Transaction (atomic)
BEGIN;
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
  UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

# NoSQL: Application logic
try:
    deduct_from_alice();  // Success
    add_to_bob();         // Fails!
    // Compensating transaction: reverse deduct
catch:
    reverse_deduct_from_alice();
```

---

## 📚 Additional Resources

**SQL Databases:**
- [PostgreSQL](https://www.postgresql.org/) - Best SQL (free)
- [MySQL](https://www.mysql.com/) - Popular but limited
- [SQLite](https://www.sqlite.org/) - Lightweight (great for mobile)

**NoSQL Databases:**
- [MongoDB](https://www.mongodb.com/) - Document store (most popular)
- [Redis](https://redis.io/) - In-memory cache/datastore
- [Cassandra](https://cassandra.apache.org/) - Distributed, massive scale
- [Neo4j](https://neo4j.com/) - Graph database

**Learning:**
- [DDIA Chapter 2-3](https://dataintensive.net/) - Data models
- "SQL vs NoSQL: Choose the Right Database"
- [MongoDB vs SQL Comparison](https://www.mongodb.com/compare/mongodb-vs-mysql)

---

## 🎯 Before You Leave

**Can you answer these?**

1. **What's the main difference between SQL and NoSQL?**
   - Answer: SQL is structured/rigid; NoSQL is flexible

2. **When should you use SQL?**
   - Answer: Structured data, ACID needed, JOINs needed

3. **When should you use NoSQL?**
   - Answer: Flexible/varied data, massive scale, fast writes

4. **What does ACID mean?**
   - Answer: Atomicity, Consistency, Isolation, Durability

5. **Can you use both SQL and NoSQL together?**
   - Answer: Yes! Polyglot persistence (right tool for right job)

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **DBA 1:** "We need to scale. Let's add NoSQL!"
>
> **DBA 2:** "For what? Your schema is perfectly rigid."
>
> **DBA 1:** "True, but it's trendy."
>
> **3 months later:** "Why is everything broken? The data's inconsistent!"
>
> **DBA 2:** "Because NoSQL isn't just 'SQL but easier.'" 🤦

---

[← Back to Main](../README.md) | [Previous: Load Testing & Capacity Estimation](06-load-testing-capacity.md) | [Next: Database Indexes →](08-database-indexes.md)

---

**Last Updated:** November 10, 2025  
**Difficulty:** ⭐⭐ Beginner-Intermediate (database concepts)  
**Time to Read:** 24 minutes  
**Time to Build Store:** 3-5 hours per phase  

---

*Choosing the right database: SQL for structure, NoSQL for scale, both for wisdom.* 🚀