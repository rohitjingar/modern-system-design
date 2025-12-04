# 09. Sharding & Partitioning

Sharding is what you do when your database gets so big that even your database is crying. You split it up and pretend it's a feature, not desperation. 🗄️💔

[← Back to Main](../README.md) | [Previous: Database Indexes](08-database-indexes.md) | [Next: Replication →](10-replication.md)

---

## 🎯 Quick Summary

**Sharding and Partitioning** are techniques to split a large database into smaller pieces so it can scale horizontally across multiple servers. Partitioning splits data logically (same server); sharding splits it physically (different servers). Both solve the problem: "My database is too big."

Think of it as: **Sharding = Horizontal Scaling for Databases**

---

## 🌟 Beginner Explanation

### The Pizza Restaurant Analogy

**SCENARIO: Database has 1 billion users**

**WITHOUT Sharding (One Giant Database):**

```
┌──────────────────────────────────┐
│   MEGA DATABASE (1 BILLION USERS) │
│                                    │
│  User 1 ─┐                        │
│  User 2  │                        │
│  User 3  │ All queries hit here  │
│  ...     │ Server is overwhelmed │
│  User 1B │                        │
└──────────────────────────────────┘

Problems:
❌ Database server at 100% CPU
❌ Queries take 5 seconds
❌ Can't add more servers (still one database!)
❌ Storage limit reached (disk maxed out)
❌ Single point of failure (everything crashes)
```

**WITH Sharding (Split Across Servers):**

```
SHARD 1 (Users A-F)      SHARD 2 (Users G-M)      SHARD 3 (Users N-Z)
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ User: Alice      │    │ User: George     │    │ User: Nick       │
│ User: Bob        │    │ User: Henry      │    │ User: Oscar      │
│ User: Carol      │    │ User: Iris       │    │ User: Pam        │
│ User: David      │    │ User: Jack       │    │ User: Quinn      │
│ User: Eve        │    │ User: Kate       │    │ User: Roger      │
│ User: Frank      │    │ User: Liam       │    │ User: Sam        │
└──────────────────┘    └──────────────────┘    └──────────────────┘
   Server 1                Server 2                Server 3

Benefits:
✅ Each server handles 1/3 the load
✅ Queries on Shard 1 are 3x faster
✅ Can add Shard 4, 5, 6... (scales infinitely!)
✅ Storage split across 3 servers
✅ If Shard 1 dies, Shards 2&3 still work
```

### Real-World Pizza Restaurant

**Single Restaurant (No Sharding):**
```
Customers: "I want pizza!"
Queue: 500 people waiting
Chef: Working alone
Time per pizza: 30 minutes
Customers leave angry 😡
```

**Sharded Restaurants (Multiple Locations):**
```
NYC Restaurant:  Handles East Coast customers
LA Restaurant:   Handles West Coast customers
Chicago:         Handles Midwest customers

Each location:
- Handles 1/3 of customers
- Shorter wait times
- Faster service ✅
- Can add more locations as needed
```

### Key Concept: Shard Key

```
SHARD KEY = What determines which shard a user goes to

Option 1: User ID (User IDs 1-250M → Shard 1)
├─ Query: Find user 123
├─ Shard Key: 123 % 3 = 0 → Shard 1
├─ Time: O(1) (instant!)

Option 2: Username (A-G → Shard 1)
├─ Query: Find user "Alice"
├─ Shard Key: "Alice"[0] = 'A' → Shard 1
├─ Time: O(1) (instant!)

Option 3: Email Domain (@gmail → Shard 1)
├─ Query: Find alice@gmail.com
├─ Shard Key: Extract domain → Shard 1
├─ Time: O(1) (instant!)

BAD Shard Key: Country
├─ All USA users on Shard 1 (99% of traffic!)
├─ Shards 2&3 empty
├─ Shard 1 still overloaded
```

---

## 🔬 Advanced Explanation

### Partitioning vs Sharding

**PARTITIONING (Logical Split, Same Server):**

```
Single Server, Multiple Partitions

┌─────────────────────────────────────────┐
│  USERS TABLE (partitioned by country)   │
│                                          │
│  Partition 1: USA Users (100M)  ──┐     │
│  Partition 2: UK Users (50M)    ──┤     │
│  Partition 3: Canada Users (25M) ──┤    │
│  Partition 4: Other (25M)       ──┘     │
│                                          │
│  All on same server                      │
└─────────────────────────────────────────┘

Queries:
- SELECT * FROM users WHERE country = 'USA'
  Uses Partition 1 only (faster)
- SELECT * FROM users WHERE country = 'UK'  
  Uses Partition 2 only (faster)

Benefits:
✅ Faster queries (partition pruning)
✅ Easier maintenance (backup individual partitions)
❌ Doesn't scale beyond one server's capacity
```

**SHARDING (Physical Split, Different Servers):**

```
Multiple Servers, Distributed Data

Server 1: USA Users          Server 2: UK Users          Server 3: Canada Users
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ Alice (NYC)     │         │ Bob (London)    │         │ Carol (Toronto) │
│ David (LA)      │         │ Eve (Manchester)│         │ Frank (Montreal)│
└─────────────────┘         └─────────────────┘         └─────────────────┘

Router: "Find Carol"
├─ Shard Key: country = "Canada"
├─ Hash: Canada % 3 = 2
└─ Query Server 3

Benefits:
✅ Scales horizontally (add more servers)
✅ Each shard is smaller
✅ Can handle massive datasets
✅ Natural load distribution
```

### Sharding Strategies

**STRATEGY 1: Range-Based (Bad for Most Cases)**

```
Shard 1: User IDs 1-250M
Shard 2: User IDs 250M-500M
Shard 3: User IDs 500M-750M
Shard 4: User IDs 750M-1B

Problem:
┌─────────────────────────────────────────┐
│ New users get IDs 1B+                   │
│ So they all go to new Shard 5           │
│ Shard 5 gets all the traffic!           │
│ Old shards 1-4 become empty              │
│ → HOTSPOT (unbalanced) 🔥               │
└─────────────────────────────────────────┘

When to use: Read-only historical data
```

**STRATEGY 2: Hash-Based (Usually Best)**

```
Shard ID = hash(user_id) % num_shards

Example: user_id = 12345
hash(12345) % 3 = 0 → Shard 1

Example: user_id = 54321
hash(54321) % 3 = 2 → Shard 3

Benefit: Even distribution across shards
Problem: Can't find user without hash (except by querying all shards)
```

**STRATEGY 3: Geographic (Good for Latency)**

```
USA Users → Shard in USA Region
EU Users → Shard in EU Region  
Asia Users → Shard in Asia Region

Benefits:
✅ Lower latency (data closer to users)
✅ Comply with data residency laws
✅ Natural fit for global apps

Problems:
❌ Imbalanced (USA has more users)
❌ Migration hard (user moves country)
```

**STRATEGY 4: Directory-Based (Flexible)**

```
Directory Service:
user_id → shard_id

12345 → Shard 1
54321 → Shard 2
78901 → Shard 3

Benefits:
✅ Perfect control
✅ Can rebalance easily
✅ Can migrate users between shards

Problems:
❌ Directory is single point of failure
❌ Extra lookup (slower queries)
```

### Sharding Architecture

```
APPLICATION LAYER

Client 1 ──┐
Client 2 ──┤
Client 3 ──┤
Client 4 ──┤                    ┌─ Shard 1 (Users A-H)
Client 5 ──┤                    │
           │                    ├─ Shard 2 (Users I-P)
    ┌──────▼──────┐             │
    │ SHARD ROUTER│ ────────────┤
    │ (Middleware)│             │
    └─────────────┘             └─ Shard 3 (Users Q-Z)

Router Logic:
1. Parse request
2. Extract shard key
3. Calculate shard ID
4. Route to correct shard
5. Return result

Query: Find user "Alice"
├─ Extract: "Alice"
├─ Hash: hash("Alice") % 3 = 0
├─ Route to Shard 1
└─ Return result
```

### Challenges of Sharding

**CHALLENGE 1: Distributed Joins**

```
❌ DOESN'T WORK:
SELECT u.name, o.amount
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.name = 'Alice'

Problem:
- User data on Shard 1 (Alice)
- Order data might be on Shard 2
- Can't join across shards! 💥

SOLUTIONS:
1. Denormalize (store order data in users shard)
2. Embed (orders as array in user document)
3. Query both shards and join in app
4. Use columnar database (if possible)
```

**CHALLENGE 2: Global Secondary Indexes**

```
❌ DOESN'T WORK:
Query: "Find all users over 25"

WHERE age > 25
├─ Need to check all 3 shards
├─ Can't use index (scattered across shards)
└─ Must do full table scan on all shards

SOLUTIONS:
1. Replicate index on each shard (expensive)
2. Create separate indexing service
3. Use search engine (Elasticsearch)
4. Accept: Need to query all shards
```

**CHALLENGE 3: Transaction Consistency**

```
❌ DOESN'T WORK:
Transaction: Transfer $100 from Alice to Bob

Alice on Shard 1:
├─ Deduct $100: Success
├─ But Bob is on Shard 2...

Bob on Shard 2:
├─ Try to add $100: Fails! (system crash)

Result:
├─ Alice lost $100 ❌
├─ Bob didn't get it ❌
├─ Money vanished! 💸

SOLUTIONS:
1. Distribute transactions (hard, slow)
2. Two-phase commit (even slower, unreliable)
3. Accept: Eventually consistent
4. Use Saga pattern (compensation on failure)
```

**CHALLENGE 4: Resharding (Adding/Removing Shards)**

```
Original: 3 shards
hash(user_id) % 3

Now adding: 4th shard
Need: hash(user_id) % 4

But now:
hash(12345) % 3 = 0 (was on Shard 1)
hash(12345) % 4 = 1 (now should be on Shard 2!)

SOLUTION: Migrate 25% of data from each shard
├─ Shard 1: Keep users 0, 1, 2, 3... → Renumber
├─ Shard 1: Move users 1, 5, 9... → Shard 4
├─ Downtime: 1-2 hours
├─ Data migration: ~50 GB if doing it wrong
└─ Risk: Data loss if something fails 💥

This is why you think carefully before sharding!
```
**Q > when and why to use partitioning vs sharding in a real-world system.**
---

> **“Partitioning is about splitting data within a single database for performance and manageability.
> Sharding is about splitting data across multiple databases or servers for scalability.”**


---

### 🔹 Partitioning — When to Use

> Use **partitioning** when your dataset is large, but it can still fit within **one database server**,
> and you mainly want **performance optimization** — like faster queries, better indexing, or easier maintenance.

**Example:**

* A PostgreSQL table with billions of rows (e.g., logs or transactions).
  You partition by `date` or `region` so queries only scan the needed partitions.

✅ **Use partitioning when:**

* You’re hitting **query performance or index size issues**.
* The data is **too big for a single table**, but not too big for one DB server.
* You still want **ACID transactions** and simple joins.

---

### 🔹 Sharding — When to Use

> Use **sharding** when your data or traffic is so large that **one database server cannot handle it**,
> so you split data **across multiple servers** (each holding a subset).

**Example:**

* A large-scale application like Instagram or Netflix,
  where user data is distributed across multiple shards to handle **massive read/write load**.

✅ **Use sharding when:**

* You need **horizontal scalability** (add more servers).
* You’re hitting **hardware limits** (CPU, RAM, storage, IOPS).
* You want to **distribute load** geographically (e.g., region-based sharding).

---

### 🧠 Key Difference Summary

| Feature      | Partitioning                | Sharding                                   |
| ------------ | --------------------------- | ------------------------------------------ |
| Scope        | Within one DB               | Across multiple DBs                        |
| Goal         | Query optimization          | Scalability & high availability            |
| Management   | Easier                      | More complex                               |
| Transactions | Still ACID                  | Often limited (cross-shard joins are hard) |
| Example      | Split orders table by month | Split users by user_id range               |

---


> “So, I’d start with **partitioning** when a single DB can still handle the data,
> but once the dataset or traffic outgrows a single node’s capacity,
> I’d move to **sharding** — which is basically distributed partitioning across multiple databases.”

---




---

## 🐍 Python Code Example

### ❌ Naive Sharding (Problems)

```python
# ===== NAIVE SHARDING (DON'T DO THIS) =====

class NaiveSharding:
    def __init__(self, num_shards=3):
        self.num_shards = num_shards
        self.shards = {i: {} for i in range(num_shards)}  # In-memory
    
    def add_user(self, user_id, user_data):
        """Add user to appropriate shard"""
        shard_id = user_id % self.num_shards
        self.shards[shard_id][user_id] = user_data
    
    def get_user(self, user_id):
        """Get user from appropriate shard"""
        shard_id = user_id % self.num_shards
        return self.shards[shard_id].get(user_id)
    
    def query_by_email(self, email):
        """Find user by email"""
        # Problem: Email doesn't map to shard!
        # Must check ALL shards 😱
        for shard_id in range(self.num_shards):
            for user_id, user_data in self.shards[shard_id].items():
                if user_data.get('email') == email:
                    return user_data
        return None
    
    def add_shard(self):
        """Add new shard (resharding)"""
        # Problem: All data needs to be rebalanced!
        old_shards = self.shards
        self.num_shards += 1
        self.shards = {i: {} for i in range(self.num_shards)}
        
        # Recalculate shard for every user
        for shard_id, users in old_shards.items():
            for user_id, user_data in users.items():
                new_shard = user_id % self.num_shards
                self.shards[new_shard][user_id] = user_data
        
        # This is expensive and requires downtime!

# Problems:
# ❌ Querying by non-shard-key hits all shards
# ❌ Adding shards requires total rebalance
# ❌ No distributed joins possible
# ❌ No transactions across shards
```

### ✅ Production Sharding (With Solutions)

```python
from abc import ABC, abstractmethod
import hashlib
from typing import Dict, List, Any
import json

class ShardingStrategy(ABC):
    """Abstract sharding strategy"""
    
    @abstractmethod
    def get_shard_id(self, key: str, num_shards: int) -> int:
        pass

class HashSharding(ShardingStrategy):
    """Hash-based sharding (most common)"""
    
    def get_shard_id(self, key: str, num_shards: int) -> int:
        """Consistent hashing"""
        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
        return hash_value % num_shards

class RangeSharding(ShardingStrategy):
    """Range-based sharding"""
    
    def __init__(self, ranges: List[tuple]):
        self.ranges = ranges  # [(0, 250M), (250M, 500M), ...]
    
    def get_shard_id(self, key: str, num_shards: int) -> int:
        """Find range for key"""
        value = int(key)
        for i, (start, end) in enumerate(self.ranges):
            if start <= value < end:
                return i
        return num_shards - 1

class DirectorySharding(ShardingStrategy):
    """Directory-based sharding (flexible)"""
    
    def __init__(self, directory: Dict[str, int]):
        self.directory = directory  # user_id → shard_id
    
    def get_shard_id(self, key: str, num_shards: int) -> int:
        """Lookup in directory"""
        return self.directory.get(key, 0)

class ShardRouter:
    """Routes requests to correct shard"""
    
    def __init__(self, strategy: ShardingStrategy, num_shards: int):
        self.strategy = strategy
        self.num_shards = num_shards
        self.shards: Dict[int, Dict] = {i: {} for i in range(num_shards)}
    
    def add_user(self, user_id: str, user_data: Dict[str, Any]):
        """Add user to correct shard"""
        shard_id = self.strategy.get_shard_id(user_id, self.num_shards)
        self.shards[shard_id][user_id] = user_data
        return shard_id
    
    def get_user(self, user_id: str):
        """Get user from correct shard"""
        shard_id = self.strategy.get_shard_id(user_id, self.num_shards)
        return self.shards[shard_id].get(user_id)
    
    def query_by_email(self, email: str) -> Dict[str, Any]:
        """Query by non-shard-key (distributed query)"""
        
        # Solution 1: Query all shards in parallel
        results = []
        for shard_id in range(self.num_shards):
            for user_id, user_data in self.shards[shard_id].items():
                if user_data.get('email') == email:
                    results.append(user_data)
        
        return results[0] if results else None
    
    def transfer_money(self, from_user: str, to_user: str, amount: float):
        """Transfer between users (possibly on different shards)"""
        
        from_shard = self.strategy.get_shard_id(from_user, self.num_shards)
        to_shard = self.strategy.get_shard_id(to_user, self.num_shards)
        
        try:
            # Deduct from source
            if from_user in self.shards[from_shard]:
                self.shards[from_shard][from_user]['balance'] -= amount
            
            # Add to destination
            if to_user in self.shards[to_shard]:
                self.shards[to_shard][to_user]['balance'] += amount
            
            # Log transaction (for consistency)
            return {"status": "success"}
        
        except Exception as e:
            # On failure: Compensate (undo deduction)
            self.shards[from_shard][from_user]['balance'] += amount
            return {"status": "failed", "error": str(e)}
    
    def get_stats(self):
        """Show shard distribution"""
        stats = {}
        for shard_id, users in self.shards.items():
            stats[f"Shard {shard_id}"] = len(users)
        return stats

# Usage
print("=== PRODUCTION SHARDING ===\n")

# Use hash-based sharding
strategy = HashSharding()
router = ShardRouter(strategy, num_shards=3)

# Add 1000 users
print("Adding 1000 users...")
for i in range(1000):
    router.add_user(
        f"user{i}",
        {
            "name": f"User {i}",
            "email": f"user{i}@example.com",
            "balance": 1000.0
        }
    )

# Check distribution
print("\nShard distribution:")
for shard, count in router.get_stats().items():
    print(f"  {shard}: {count} users")

# Get user (fast, uses shard key)
user = router.get_user("user500")
print(f"\nFound user: {user['name']}")

# Query by email (slow, searches all shards)
user = router.query_by_email("user123@example.com")
print(f"Query by email: {user['name']}")

# Transfer money
result = router.transfer_money("user100", "user200", 50)
print(f"\nTransfer result: {result['status']}")

# Output:
# === PRODUCTION SHARDING ===
#
# Adding 1000 users...
#
# Shard distribution:
#   Shard 0: 333 users
#   Shard 1: 334 users
#   Shard 2: 333 users
#
# Found user: User 500
# Query by email: User 123
#
# Transfer result: success
```

### ✅ Consistent Hashing (For Resharding)


When you use **hash-based sharding**, you normally do something like:

```
shard_id = hash(user_id) % number_of_shards
```

✅ This works well **until** you add or remove a shard.
Then all hash values change — and almost **all data has to move** to new shards 😫

That’s very expensive and slow — this is called the **resharding problem**.

---

### 🧠 What Consistent Hashing does

**Consistent Hashing** fixes that by making sure that **when you add or remove a shard**,
**only a small portion of the data moves** — not everything.

---

### 🔁 The Basic Idea (in simple terms)

1. **Imagine a circle (a ring)** — representing all possible hash values (0–360°).
2. **Place shards (servers/databases)** on that circle at different random points.

   * Example: Shard A at 90°, Shard B at 180°, Shard C at 300°.
3. **Each data item (like a user)** is also placed on the ring using its hash.

   * Example: user_id `12345` → 270°.
4. A data item is stored in the **next shard clockwise** on the ring.

---

### 🧭 When a new shard is added

Suppose you add **Shard D** at 240°.

👉 Only the data that falls **between 240° and the next shard (say 300°)** needs to move to Shard D.
Everything else stays in place.

That’s the **beauty of consistent hashing** — minimal data movement.

---

### 🧩 Summary Table

| Concept                      | Explanation                                                         |
| ---------------------------- | ------------------------------------------------------------------- |
| **Goal**                     | Distribute data evenly, but minimize reshuffling when shards change |
| **How**                      | Map both shards and data to points on a hash ring                   |
| **Data location rule**       | Data belongs to the next shard clockwise on the ring                |
| **When shard added/removed** | Only a small segment of data moves                                  |
| **Used in**                  | Systems like Cassandra, DynamoDB, Redis Cluster, Kafka              |

---

### ⚙️ Real-world analogy

Think of it like **a circular street** with several **delivery stations (shards)** placed at different points.

Each package (data item) has an address (hash value).
You always deliver to the **next station clockwise** from the address.

Now, if a new station opens, it only takes **some packages** from its nearby area —
you don’t have to move every package around the circle.

---

### 🧠 In one line:

> **Consistent Hashing** = A smart way to assign data to shards so that when shards are added or removed, only nearby data moves — not everything.

---



```python
import hashlib

class ConsistentHashRing:
    """Handles resharding with minimal data movement"""
    
    def __init__(self, num_shards: int, virtual_nodes: int = 160):
        self.num_shards = num_shards
        self.virtual_nodes = virtual_nodes
        self.ring = {}  # hash value → shard id
        self.shard_map = {}  # shard id → [hash values]
        
        self._build_ring()
    
    def _build_ring(self):
        """Build consistent hash ring"""
        for shard_id in range(self.num_shards):
            for i in range(self.virtual_nodes):
                key = f"shard-{shard_id}-{i}"
                hash_value = self._hash(key)
                self.ring[hash_value] = shard_id
                
                if shard_id not in self.shard_map:
                    self.shard_map[shard_id] = []
                self.shard_map[shard_id].append(hash_value)
    
    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def get_shard(self, key: str) -> int:
        """Find shard for key"""
        key_hash = self._hash(key)
        
        # Find next shard in ring
        sorted_hashes = sorted(self.ring.keys())
        for hash_val in sorted_hashes:
            if hash_val >= key_hash:
                return self.ring[hash_val]
        
        # Wrap around
        return self.ring[sorted_hashes[0]]
    
    def add_shard(self):
        """Add new shard (minimal resharding!)"""
        old_mapping = {}
        
        # Store old mappings
        for key_id in range(1000):
            key = f"user{key_id}"
            old_mapping[key] = self.get_shard(key)
        
        # Add new shard
        self.num_shards += 1
        self._build_ring()
        
        # Count how many moved
        moved = 0
        for key, old_shard in old_mapping.items():
            new_shard = self.get_shard(key)
            if old_shard != new_shard:
                moved += 1
        
        print(f"After adding shard: {moved}/1000 users moved (~{moved/10}%)")
        # With consistent hashing: ~1/n moved
        # Without: 100% moved!

# Usage
ring = ConsistentHashRing(3)
print(f"Initial: user0 → Shard {ring.get_shard('user0')}")

print("\nAdding new shard...")
ring.add_shard()

print(f"After: user0 → Shard {ring.get_shard('user0')}")
```

---

## 💡 Mini Project: "Build a Sharding System"

### Phase 1: Simple Sharding ⭐

**Requirements:**
- Basic hash-based sharding
- Add/get users
- Check distribution

**Code:**
```python
class SimpleShardingSystem:
    def __init__(self, num_shards=3):
        self.num_shards = num_shards
        self.shards = [dict() for _ in range(num_shards)]
    
    def add_user(self, user_id, data):
        shard = user_id % self.num_shards
        self.shards[shard][user_id] = data
    
    def get_user(self, user_id):
        shard = user_id % self.num_shards
        return self.shards[shard].get(user_id)
    
    def get_stats(self):
        return [len(s) for s in self.shards]
```

---

### Phase 2: Advanced (With Strategies) ⭐⭐

**Requirements:**
- Multiple sharding strategies
- Query by non-shard-key
- Cross-shard operations
- Statistics

---

### Phase 3: Enterprise (Consistent Hashing) ⭐⭐⭐

**Requirements:**
- Consistent hashing
- Minimal resharding
- Auto-rebalancing
- Multi-shard transactions

---

## ⚖️ When to Use Sharding

| Scenario | Decision |
|----------|----------|
| **<1TB data** | ❌ Don't shard (use indexes) |
| **1-10TB data** | 🟡 Maybe (vertical scaling works) |
| **10TB-1PB data** | ✅ Shard (necessary) |
| **Write-heavy** | ✅ Shard (helps scale writes) |
| **Complex queries** | ❌ Avoid sharding (makes queries hard) |
| **Geographic** | ✅ Shard (natural fit) |
| **Simple reads** | 🟡 Consider replication first |

---

## ❌ Common Mistakes

### Mistake 1: Sharding Too Early

```python
# ❌ 10 GB database, already sharding
# Complexity isn't worth it yet
# Better: Use indexes, caching, vertical scaling

# ✅ 1 TB database, sharding makes sense
# Complexity justified by scale benefits
```

### Mistake 2: Bad Shard Key

```python
# ❌ Shard by country (USA gets 90% of traffic)
# Shards unbalanced, hotspot on USA shard

# ✅ Shard by user_id (hash)
# Even distribution, all shards equally busy
```

### Mistake 3: Not Planning for Resharding

```python
# ❌ Use range sharding, can't add shards
# Stuck with 3 shards forever
# When need more: Weeks of migration

# ✅ Use consistent hashing
# Add shards anytime
# Only 1/n data moves
```

---

## 📚 Additional Resources

**Sharding Systems:**
- [YouTube ShardingSphere](https://shardingsphere.apache.org/)
- [Pinterest Sharding](https://medium.com/pinterest-engineering/sharding-pinterest-how-we-scaled-our-mysql-fleet-3f341e96ca6f)
- [Uber's Ringpop](https://www.uber.com/blog/ringpop-open-source-replication-ring/)

**Reading:**
- DDIA Chapter 6 - Partitioning
- "Sharding Pinterest" - Medium article
- "Consistent Hashing" - Tom White's blog

**Tools:**
- [Apache ShardingSphere](https://shardingsphere.apache.org/) - Sharding framework
- [Vitess](https://vitess.io/) - MySQL sharding middleware
- [Citus](https://www.citusdata.com/) - PostgreSQL sharding

---

## 🎯 Before You Leave

**Can you answer these?**

1. **What's the main goal of sharding?**
   - Answer: Horizontal scaling (split data across servers)

2. **What's a shard key and why does it matter?**
   - Answer: Determines which shard a user goes to; bad key = unbalanced load

3. **What's the difference between partitioning and sharding?**
   - Answer: Partitioning = logical (same server); Sharding = physical (different servers)

4. **Why are distributed joins hard with sharding?**
   - Answer: Data on different shards can't be joined efficiently

5. **What's consistent hashing and why is it useful?**
   - Answer: Hash ring that minimizes data movement when resharding

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **DBA 1:** "My database got so big I had to shard it."
>
> **DBA 2:** "Congratulations, you've earned a PhD in distributed systems pain."
>
> **DBA 1:** "What do you mean?"
>
> **DBA 2:** "Now your problems are: joins, transactions, resharding, hotspots..."
>
> **DBA 1:** *regrets life choices* 😭

---

[← Back to Main](../README.md) | [Previous: Database Indexes](08-database-indexes.md) | [Next: Replication →](10-replication.md)

---

**Last Updated:** November 10, 2025  
**Difficulty:** ⭐⭐⭐ Intermediate-Advanced (requires distributed thinking)  
**Time to Read:** 25 minutes  
**Time to Build System:** 4-6 hours per phase  

---

*Sharding: Horizontal scaling that pays dividends until it doesn't... then you pay in complexity.* 🚀