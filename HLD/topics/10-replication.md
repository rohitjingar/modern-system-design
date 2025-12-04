# 10. Replication

Replication is how you copy your database so that when one catches fire, you have a backup catching fire somewhere else. It's not a solution, it's a delay tactic. 🔥🔥

[← Back to Main](../README.md) | [Previous: Sharding & Partitioning](09-sharding-partitioning.md) | [Next: CAP Theorem →](11-cap-theorem.md)

---

## 🎯 Quick Summary

**Replication** is copying data across multiple servers so if one fails, others still have the data. It trades storage space for reliability. There's Master-Slave (simple), Master-Master (complex), and Multi-region (expensive). Each has different consistency and availability guarantees.

Think of it as: **Replication = Backup That's Alive and Ready**

---

## 🌟 Beginner Explanation

### The Book Analogy

**NO REPLICATION (High Risk):**

```
Library has 1 copy of "The System Design Bible"

Scenario 1: Fire in library 🔥
Result: Book destroyed, lost forever ❌

Scenario 2: Someone steals it 😱
Result: Book gone, other users disappointed ❌

Scenario 3: Librarian gets sick 🤒
Result: No one can check out books today ❌
```

**WITH REPLICATION (Safe):**

```
Main Library has 1 copy
+ Branch Library has 1 copy (replica)
+ Downtown Library has 1 copy (replica)

Scenario 1: Fire at Main Library 🔥
Result: Branch and Downtown still have copies ✅

Scenario 2: Someone steals from Main
Result: Replicas still available ✅

Scenario 3: Main librarian sick
Result: Branch can serve customers ✅

Cost: 3x storage, but way more reliable
```

### Master-Slave Replication

**MASTER-SLAVE SETUP:**

```
MASTER (Primary Database)
├─ Accepts reads ✅
├─ Accepts writes ✅
└─ Source of truth

        ↓ (replicates data)

SLAVE 1 (Read Replica 1)
├─ Accepts reads only ✅
├─ Cannot write directly ❌
└─ Copy of data

SLAVE 2 (Read Replica 2)
├─ Accepts reads only ✅
├─ Cannot write directly ❌
└─ Copy of data

OPERATIONS:

Write: Always goes to Master
Client: "Update Alice's email"
Master: Updates ✅
Master replicates to Slaves (eventually) 📦

Read: Can go to Master or Slaves
Client: "Get Alice's data"
Option 1: Master (fresh, slower) 🐢
Option 2: Slave (may be old, faster) ⚡

BENEFITS:
✅ Read scalability (multiple slaves)
✅ Backups (slave is always a backup)
✅ Analytics (run on slave without hitting master)
✅ Geographic distribution (slave in another region)

PROBLEMS:
❌ Replication lag (slave temporarily stale)
❌ Slave can't write (must write to master)
❌ Master is single point of failure (writes)
```

### Replication Lag (The Hidden Problem)

```
TIME 1:00 PM
Master: Alice's email = old@example.com
Slave: Alice's email = old@example.com

TIME 1:00:01 PM
Client: Update Alice's email to new@example.com
Master: Receives write, updates to new@example.com
Master: Starts replicating to Slave...

TIME 1:00:02 PM (while replication in progress)
Client: Read Alice's email
Query Slave: Returns old@example.com ❌ (Lag!)
Query Master: Returns new@example.com ✅

TIME 1:00:05 PM (replication done)
Slave: Alice's email = new@example.com
All consistent again ✅

THE PROBLEM:
Between write and replication completion:
Stale reads are possible! 😱
```

---

## 🔬 Advanced Explanation

### Replication Strategies

**STRATEGY 1: Binary Log Replication (MySQL)**

```
Master writes data, also writes to binary log:

Binary Log on Master:
├─ Operation 1: INSERT INTO users VALUES (1, 'Alice')
├─ Operation 2: UPDATE users SET email='alice@example.com' WHERE id=1
├─ Operation 3: DELETE FROM users WHERE id=2
└─ ...

Slave reads binary log:
├─ Read Operation 1 → Execute on local copy
├─ Read Operation 2 → Execute on local copy
├─ Read Operation 3 → Execute on local copy
└─ Now matches Master ✅

Benefit: Works with all data (DDL, triggers, etc.)
Problem: Any non-deterministic function breaks replication
         (RAND(), NOW(), UUID())
```

**STRATEGY 2: Row-Based Replication**

```
Instead of replicating SQL statements,
replicate the actual row changes:

Master: UPDATE users SET age = age + 1 WHERE age > 18
        (affects 500,000 rows)

With Statement Replication:
Slave executes: UPDATE users SET age = age + 1 WHERE age > 18
(Same statement, might have different results!)

With Row-Based Replication:
Slave receives: Row 1: age 25→26, Row 2: age 30→31, ...
(Exact changes, guaranteed same result)

Benefit: Deterministic, guaranteed consistency
Problem: More network traffic (replicate all changes)
```

**STRATEGY 3: MVCC (Multi-Version Concurrency Control)**

```
Master maintains multiple versions of data:

Version 1 (timestamp 100):
  Alice: email = old@example.com, age = 28

Version 2 (timestamp 105):
  Alice: email = new@example.com, age = 28

Transactions see consistent snapshot:
Read at timestamp 100: Gets old email ✅
Read at timestamp 105: Gets new email ✅
Both correct, no inconsistency

Benefit: No replication lag for reads!
Problem: More complex, more storage
```

### Master-Master (Active-Active) Replication

**SETUP:**

```
MASTER 1 (Active)         MASTER 2 (Active)
├─ Accepts reads ✅       ├─ Accepts reads ✅
├─ Accepts writes ✅      ├─ Accepts writes ✅
└─ Replicates to M2       └─ Replicates to M1

Write on M1: User updates email
├─ M1 processes write
├─ M1 sends to M2
├─ M2 applies write

Write on M2: User updates phone
├─ M2 processes write
├─ M2 sends to M1
├─ M1 applies write

Both consistent ✅

BENEFITS:
✅ Both servers accept writes
✅ No single point of failure
✅ Geographic distribution (lower latency)
✅ Active-Active (both handling traffic)

PROBLEMS:
⚠️ Write conflicts possible
⚠️ Cycle detection needed (prevent infinite loops)
⚠️ Harder to debug issues
⚠️ Complex topology
```

**CONFLICT RESOLUTION:**

```
Conflict Scenario:

M1: Alice sets age = 30
M2: Alice sets age = 25

Same row, same timestamp, different values!
What do we do? 🤔

Option 1: Last-Write-Wins (LWW)
├─ Whichever write came later wins
├─ M1 at 1:00:05 PM, M2 at 1:00:03 PM
├─ M1 wins: age = 30
├─ Problem: Might lose valid data

Option 2: Version Vectors
├─ Track causality (which writes depend on which)
├─ Merge strategically
├─ Problem: Complicated, slow

Option 3: Operational Transformation
├─ Transform conflicting operations
├─ Like Google Docs real-time collab
├─ Problem: Very complex

Option 4: Application Logic
├─ Resolve at application level
├─ "If age conflict, keep higher value"
├─ Problem: Puts burden on dev
```

### Replication Topologies

**TOPOLOGY 1: Star (Master-Slave)**

```
        Master
        /  |  \
       /   |   \
     S1   S2   S3
     
Pros: Simple, clear
Cons: Master bottleneck
```

**TOPOLOGY 2: Chain**

```
Master → S1 → S2 → S3

Pros: Reduces load on master
Cons: Long replication lag, harder to debug
```

**TOPOLOGY 3: Ring (Master-Master)**

```
M1 → M2
↑    ↓
M4 ← M3

Pros: No central point of failure
Cons: Circle detection needed, complex
```

**TOPOLOGY 4: Tree**

```
      Master
      /    \
    M1      M2
    / \     / \
   S1 S2   S3 S4

Pros: Scalable, organized
Cons: Very complex
```

### Replication Problems

**PROBLEM 1: Replication Lag**

```
Master writes data
Slave hasn't replicated yet
Client reads stale data

SOLUTIONS:
1. Read from Master (slower but fresh)
2. Accept stale reads (application handles it)
3. Use read-your-writes consistency
   (if you just wrote, read from master)
4. Wait for replication
   (before returning to user: "Replicating...")
```

**PROBLEM 2: Split Brain**

```
Network partition! 🔌

M1                    M2
(isolated)            (isolated)

Client 1 writes to M1: age = 25
Client 2 writes to M2: age = 30

When network heals:
What's the truth? 25 or 30? 😱

SOLUTION: Quorum-based
Only 1 master can accept writes if < N/2 servers reachable
Prevents both from thinking they're the master
```

**PROBLEM 3: Data Loss on Failover**

```
Master receives write:
Client: "Update Alice"
Master: "Got it, write complete"

Before replication to slaves:
Master: 💥 CRASH!

Slaves don't have the update:
- Update is lost ❌
- Client thinks it worked 😱

SOLUTION: Synchronous Replication
Master waits for at least 1 slave to ACK
Before telling client "write complete"
Slower but safer
```

---

## 🐍 Python Code Example

### ❌ Simple Replication (Problems)

```python
# ===== SIMPLE MASTER-SLAVE (PROBLEMS) =====

class SimpleMaster:
    def __init__(self):
        self.data = {}
        self.slaves = []
        self.transaction_log = []
    
    def write(self, key, value):
        """Write to master"""
        self.data[key] = value
        self.transaction_log.append((key, value))
        
        # Replicate to slaves (asynchronous)
        for slave in self.slaves:
            slave.receive_update(key, value)
        
        return True
    
    def read(self, key):
        """Read from master"""
        return self.data.get(key)
    
    def register_slave(self, slave):
        """Add slave replica"""
        self.slaves.append(slave)

class SimpleSlave:
    def __init__(self):
        self.data = {}
    
    def receive_update(self, key, value):
        """Receive update from master"""
        # Simulate network delay
        import time
        time.sleep(0.1)  # 100ms lag
        self.data[key] = value
    
    def read(self, key):
        """Read from slave (might be stale!)"""
        return self.data.get(key)

# Problems with this approach:
# ❌ Replication lag (stale reads possible)
# ❌ No monitoring (don't know if slave is behind)
# ❌ Data loss risk (async replication)
# ❌ No failover handling
```

### ✅ Production Replication (With Solutions)

```python
import time
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional
import threading

class ReplicationStrategy(Enum):
    ASYNC = "async"           # Fast, data loss risk
    SEMI_SYNC = "semi_sync"   # Balanced
    SYNC = "sync"             # Slow, safe

@dataclass
class ReplicationEvent:
    """Track a replicated event"""
    timestamp: float
    key: str
    value: str
    event_id: int

class ProductionMaster:
    """Production-grade master with replication"""
    
    def __init__(self, strategy: ReplicationStrategy = ReplicationStrategy.SEMI_SYNC):
        self.data: Dict[str, str] = {}
        self.slaves: List['ProductionSlave'] = []
        self.transaction_log: List[ReplicationEvent] = []
        self.event_id = 0
        self.strategy = strategy
        self.lock = threading.Lock()
        self.slave_acks = {}
    
    def write(self, key: str, value: str) -> bool:
        """Write with replication strategy"""
        with self.lock:
            # Write to master first
            self.data[key] = value
            self.event_id += 1
            
            event = ReplicationEvent(
                timestamp=time.time(),
                key=key,
                value=value,
                event_id=self.event_id
            )
            self.transaction_log.append(event)
            
            # Replicate based on strategy
            if self.strategy == ReplicationStrategy.ASYNC:
                # Fire and forget (fast but risky)
                for slave in self.slaves:
                    threading.Thread(
                        target=slave.apply_event,
                        args=(event,)
                    ).start()
                return True
            
            elif self.strategy == ReplicationStrategy.SEMI_SYNC:
                # Wait for at least 1 slave
                acks = 0
                for slave in self.slaves:
                    if slave.apply_event(event):
                        acks += 1
                
                # If at least 1 slave ACKed, we're good
                return acks >= 1
            
            elif self.strategy == ReplicationStrategy.SYNC:
                # Wait for all slaves
                for slave in self.slaves:
                    if not slave.apply_event(event):
                        return False  # If any slave fails, reject write
                return True
    
    def read(self, key: str) -> Optional[str]:
        """Read from master (always fresh)"""
        with self.lock:
            return self.data.get(key)
    
    def register_slave(self, slave: 'ProductionSlave'):
        """Register a slave replica"""
        self.slaves.append(slave)
        self.slave_acks[slave.id] = 0
    
    def get_replication_lag(self) -> Dict[str, float]:
        """Get lag for each slave"""
        lags = {}
        for slave in self.slaves:
            lag = time.time() - slave.last_update
            lags[slave.id] = lag
        return lags
    
    def get_status(self) -> Dict:
        """Get master status"""
        return {
            "data_size": len(self.data),
            "event_count": len(self.transaction_log),
            "slave_count": len(self.slaves),
            "replication_lags": self.get_replication_lag()
        }

class ProductionSlave:
    """Production-grade slave replica"""
    
    def __init__(self, slave_id: str):
        self.id = slave_id
        self.data: Dict[str, str] = {}
        self.last_event_id = 0
        self.last_update = time.time()
        self.lock = threading.Lock()
    
    def apply_event(self, event: ReplicationEvent) -> bool:
        """Apply replicated event"""
        try:
            with self.lock:
                # Simulate network latency
                time.sleep(0.01)  # 10ms lag
                
                # Apply event
                self.data[event.key] = event.value
                self.last_event_id = event.event_id
                self.last_update = time.time()
            
            return True
        except Exception:
            return False
    
    def read(self, key: str) -> Optional[str]:
        """Read from slave (might be stale)"""
        with self.lock:
            return self.data.get(key)
    
    def get_lag(self) -> float:
        """How far behind master am I?"""
        return time.time() - self.last_update

# Usage
print("=== PRODUCTION REPLICATION ===\n")

# Create master and slaves
master = ProductionMaster(strategy=ReplicationStrategy.SEMI_SYNC)
slave1 = ProductionSlave("slave-1")
slave2 = ProductionSlave("slave-2")

master.register_slave(slave1)
master.register_slave(slave2)

# Write data
print("Writing: Alice = alice@example.com")
master.write("alice", "alice@example.com")

# Read from master (always fresh)
print(f"Master read: {master.read('alice')}")

# Read from slave (might be stale)
print(f"Slave 1 read: {slave1.read('alice')}")

# Check replication status
print(f"\nReplication Status:")
status = master.get_status()
for key, value in status.items():
    print(f"  {key}: {value}")

print(f"\nSlave lags:")
for slave in [slave1, slave2]:
    print(f"  {slave.id}: {slave.get_lag():.3f}s behind")
```

### ✅ Failover (Active-Active)

```python
class FailoverManager:
    """Handles master failure and promotion"""
    
    def __init__(self, master: ProductionMaster, slaves: List[ProductionSlave]):
        self.master = master
        self.slaves = slaves
        self.is_healthy = True
    
    def check_master_health(self) -> bool:
        """Check if master is alive"""
        try:
            # Ping master (simplified)
            self.master.read("__health__")
            return True
        except:
            return False
    
    def promote_slave_to_master(self, slave: ProductionSlave) -> ProductionMaster:
        """Promote slave to master"""
        print(f"Promoting {slave.id} to master...")
        
        # Stop replication to this slave
        # Transfer all data to new master
        new_master = ProductionMaster()
        new_master.data = slave.data.copy()
        
        print(f"✓ {slave.id} is now master")
        return new_master
    
    def monitor(self):
        """Monitor master health"""
        while True:
            if not self.check_master_health():
                print("❌ Master failed!")
                # Find healthiest slave
                healthiest = max(
                    self.slaves,
                    key=lambda s: s.last_event_id
                )
                self.promote_slave_to_master(healthiest)
                break
            
            time.sleep(1)  # Check every 1 second

# Usage
# failover = FailoverManager(master, [slave1, slave2])
# failover.monitor()  # Runs in background, detects failures
```

---

## 💡 Mini Project: "Build a Replication System"

### Phase 1: Simple Master-Slave ⭐

**Requirements:**
- Master accepts reads/writes
- Slave accepts reads only
- Async replication
- Basic monitoring

**Code:**
```python
class SimpleReplicationSystem:
    def __init__(self):
        self.master = SimpleMaster()
        self.slaves = []
    
    def add_slave(self):
        slave = SimpleSlave()
        self.master.register_slave(slave)
        self.slaves.append(slave)
    
    def write(self, key, value):
        return self.master.write(key, value)
    
    def read_from_master(self, key):
        return self.master.read(key)
    
    def read_from_slave(self, key):
        # Round-robin to slaves
        for slave in self.slaves:
            return slave.read(key)
```

---

### Phase 2: Advanced (Failover) ⭐⭐

**Requirements:**
- Detect master failure
- Promote slave to master
- Data consistency
- Monitoring dashboard

---

### Phase 3: Enterprise (Multi-Master) ⭐⭐⭐

**Requirements:**
- Multiple masters
- Conflict resolution
- Automatic failover
- Health monitoring
- Rebalancing

---

## ⚖️ Replication Trade-offs

| Type | Sync | Async | Semi-Sync |
|------|------|-------|-----------|
| **Speed** | Slow ⚠️ | Fast ✅ | Medium 🟡 |
| **Consistency** | Strong ✅ | Weak ❌ | Good ✅ |
| **Data Loss Risk** | None | High | Low |
| **Complexity** | Low | Low | Medium |
| **Latency** | High | Low | Medium |
| **Use Case** | Banking | Analytics | Balance |

---


## ❌ Common Mistakes

### Mistake 1: Async Replication for Critical Data

```python
# ❌ Bank using async replication
# Transaction: -$100 from Alice
# Confirmed to customer immediately
# Master crashes before replication
# ❌ $100 lost!

# ✅ Use semi-sync or sync for critical data
# Transaction confirmed only after at least 1 slave has it
```

### Mistake 2: Ignoring Replication Lag

```python
# ❌ Bad: Write then immediately read
master.write("alice_age", 30)
time.sleep(0.001)  # Too fast!
slave_value = slave.read("alice_age")  # Gets old value
assert slave_value == 30  # ❌ Fails!

# ✅ Good: Wait for replication
master.write("alice_age", 30)
time.sleep(0.5)  # Let replication complete
slave_value = slave.read("alice_age")  # Gets new value ✅
```

### Mistake 3: Single Master Without Failover

```python
# ❌ Master dies
# All writes impossible
# No automatic recovery
# ❌ Hours of manual intervention

# ✅ Set up automated failover
# Master dies → Slave promoted automatically
# System recovers in seconds
```

## Q : Synchronous vs Asynchronous Replication .


## 💡 First, the Core Idea

Replication = **copying data** from one database (primary/master) to another (replica/slave).
This is done to ensure **high availability, backup, and disaster recovery.**

Now, the main question is —
👉 *When* should the replica be updated relative to the master?

That’s where **Sync** and **Async** come in.

---

## ⚙️ 1️⃣ Synchronous Replication

> The primary **waits** until data is **written to both the primary and the replica** before confirming success to the client.

🧠 **In simple terms:**

* “I’ll tell the user the write is successful **only after** my backup has also saved it.”

✅ **Pros:**

* **Strong consistency** — both primary and replica always have same data.
* No data loss if the primary crashes immediately after write.

❌ **Cons:**

* **Slower writes** — because you wait for both to finish.
* If replica is slow or down → it can block writes.

💬 **Use When:**

* You care more about **data accuracy** than speed.
* Example: **Banking, finance, or transaction systems.**

---

## ⚙️ 2️⃣ Asynchronous Replication

> The primary **does not wait** for the replica to confirm the write.
> It immediately acknowledges success and **replicates later in background**.

🧠 **In simple terms:**

* “I’ll save it first, and my replica will catch up soon.”

✅ **Pros:**

* **Faster writes** — because no waiting for replicas.
* **More scalable** — replicas can lag slightly and still handle reads.

❌ **Cons:**

* **Eventual consistency** — replicas may be slightly behind.
* If the primary crashes before replication, **some data can be lost.**

💬 **Use When:**

* You care more about **performance and uptime** than immediate accuracy.
* Example: **Social media posts, analytics, caching layers.**

---

## 🧠 Interview Summary Table

| Feature              | **Synchronous Replication**               | **Asynchronous Replication**              |
| -------------------- | ----------------------------------------- | ----------------------------------------- |
| Write acknowledgment | After replica confirms                    | Immediately after master write            |
| Consistency          | Strong (always up-to-date)                | Eventual (replica may lag)                |
| Latency              | High                                      | Low                                       |
| Data loss on crash   | None                                      | Possible                                  |
| Use case             | Banking, Orders, Payments                 | Feeds, Logs, Analytics                    |
| Example systems      | PostgreSQL sync replicas, MySQL semi-sync | MySQL async replicas, MongoDB secondaries |

---

## 🎯 20-Second Interview Answer (Short & Sharp)

> “In synchronous replication, the primary waits for the replica to confirm the write — giving **strong consistency** but **higher latency**.
> In asynchronous replication, the primary doesn’t wait — it’s **faster** but may cause **replica lag** or **data loss** if the master crashes.
> So, we choose sync for **critical data**, and async for **scalable or non-critical workloads**.”

---

## 🧩 Bonus Tip (for advanced interviews)

> “Some systems use **semi-synchronous replication**, where at least one replica must confirm the write before acknowledging success — giving a balance between speed and safety.”

---


---

## 📚 Additional Resources

**Replication Systems:**
- [MySQL Replication](https://dev.mysql.com/doc/refman/8.0/en/replication.html)
- [PostgreSQL Streaming Replication](https://www.postgresql.org/docs/current/warm-standby.html)
- [MongoDB Replica Sets](https://docs.mongodb.com/manual/replication/)

**Reading:**
- DDIA Chapter 5 - Replication
- "Replication" - Martin Kleppmann
- "Consistency Models in NoSQL"

**Tools:**
- [MySQL Group Replication](https://dev.mysql.com/doc/refman/8.0/en/group-replication.html)
- [etcd](https://etcd.io/) - Distributed coordination
- [Consul](https://www.consul.io/) - Service mesh with replication

---

## 🎯 Before You Leave

**Can you answer these?**

1. **What's the main goal of replication?**
   - Answer: Keep data safe (backup + reliability)

2. **What's replication lag and why does it matter?**
   - Answer: Delay between write and replication; causes stale reads

3. **What's the difference between async and sync replication?**
   - Answer: Async fast/unsafe; sync slow/safe

4. **What's a split brain and how do you prevent it?**
   - Answer: Both masters think they're primary; use quorum voting

5. **How do you promote a slave to master?**
   - Answer: Copy data, stop replication, start accepting writes

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **DBA 1:** "I set up replication. System is now safe!"
>
> **DBA 2:** "What replication strategy did you use?"
>
> **DBA 1:** "Async. Data replicates when it feels like it."
>
> **DBA 2:** "...And when the master crashes?"
>
> **DBA 1:** "I lose all pending writes."
>
> **DBA 2:** "That's not safe, that's a time bomb." 💣

---

[← Back to Main](../README.md) | [Previous: Sharding & Partitioning](09-sharding-partitioning.md) | [Next: CAP Theorem →](11-cap-theorem.md)

---

**Last Updated:** November 10, 2025  
**Difficulty:** ⭐⭐⭐ Intermediate-Advanced (distributed systems)  
**Time to Read:** 24 minutes  
**Time to Build System:** 4-6 hours per phase  

---

*Replication: Your insurance policy against that one server that's definitely going to fail at 3 AM.* 🚀