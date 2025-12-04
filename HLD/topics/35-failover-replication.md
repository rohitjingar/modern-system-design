# 35. Failover & Replication Strategies

Replication is keeping copies of your data so when one fails, you have backups. Failover is automatically switching to the backup. Together they make your system survive catastrophes. Except when replication is 5 seconds behind and your failover is too slow. Then everyone loses data and you update your resume. Welcome to distributed systems! 📋➡️💥

[← Back to Main](../README.md) | [Previous: Heartbeats & Health Checks](34-heartbeats-health-checks.md) | [Next: Circuit Breakers →](36-circuit-breakers.md)

---

## 🎯 Quick Summary

**Replication** copies data across multiple servers (master-slave, peer-to-peer). **Failover** automatically switches to replica when primary fails. Without: one server dies, data lost. With: primary dies, replica takes over, zero downtime. Trade-offs: consistency (eventual vs strong), complexity (coordination), latency (sync vs async replication). Netflix uses active-active replication across regions. Amazon has auto-failover minutes. Critical for high availability systems.

Think of it as: **Replication = Safety Net, Failover = Automatic Rescue**

---

## 🌟 Beginner Explanation

### Replication Types

**MASTER-SLAVE (Primary-Replica):**

```
Write (Master):
├─ Client writes to master
├─ Master processes transaction
├─ Data stored locally
├─ Transaction committed
└─ Return "success" to client

Replication (Asynchronous):
├─ Master broadcasts: "New row added"
├─ Slave 1: Receives, applies locally
├─ Slave 2: Receives, applies locally
├─ Slave 3: Receives, applies locally
└─ Takes 1-5 seconds (lag!)

Read (Slave):
├─ Client reads from slave
├─ Faster (no writes)
├─ Might be stale (if replication lagging)
└─ "Eventually consistent"

Pros:
✅ Write scaling (one master)
✅ Read scaling (many slaves)
✅ Simple coordination (master decides)
✅ Fast writes (master doesn't wait)

Cons:
❌ If master dies: Data loss (unreplicated writes)
❌ Slaves can be stale
❌ Master bottleneck for writes
❌ Write throughput limited by master
```

**PEER-TO-PEER (Multi-Master):**

```
Write (Any Node):
├─ Client writes to Node A
├─ Node A processes transaction
├─ Node A broadcasts: "New row"
└─ Return success (immediately!)

Replication (Asynchronous):
├─ Node B: Receives, applies
├─ Node C: Receives, applies
├─ Node D: Receives, applies
└─ All have same data (eventually)

Meanwhile:
├─ Client writes to Node B
├─ Node B processes transaction
├─ Node B broadcasts
└─ Nodes A, C, D apply

Result:
├─ All nodes have all writes
├─ Can write to any node
├─ Highly available

Pros:
✅ No single point of failure
✅ Write to any node
✅ Any node can fail
✅ Highly available

Cons:
❌ Conflict resolution (two writes conflict?)
❌ Complex coordination
❌ Slower (need quorum)
❌ Consistency harder
```

### Failover Process

```
MANUAL FAILOVER (Old way):

T=0: Master dies
├─ System down
└─ Users see errors

T=5: Monitoring detects failure
├─ Sends alert
└─ PagerDuty rings phone

T=10: On-call engineer wakes up
├─ Reads alert
├─ Checks database
└─ "Master is dead"

T=15: Engineer SSH to slave
├─ Runs: "PROMOTE REPLICA"
├─ Slave becomes new master
└─ Sends update to application

T=20: Application reconnects to new master
├─ Resumes accepting writes
└─ System back up!

Downtime: 20 minutes!
Data loss: Writes in last 5 minutes lost!


AUTOMATIC FAILOVER (Modern way):

T=0: Master dies
├─ Stops responding to health checks
└─ Heartbeat stops

T=5: Health check detects failure
├─ Master marked "down"
├─ Triggers automatic failover
└─ Monitoring alerts

T=5.5: Failover logic runs
├─ Check: Is slave up to date?
├─ Check: Can slave be promoted?
├─ Promote slave to master
├─ Update DNS/service discovery
└─ Application auto-reconnects (no code change!)

T=6: System back up!
├─ Failover completed
├─ Application resumed
└─ New master accepting writes

Downtime: ~1 second!
Data loss: None (if using synchronous replication)!
```

### Replication Lag Problem

```
SYNCHRONOUS REPLICATION (Safe but slow):

Master write:
├─ Write data
├─ Wait for slave confirmation
├─ Slave received and stored
├─ Return "success" to client

Latency: 50-100ms (waiting for network)

Safety:
✅ Slave always in sync
✅ Zero data loss
❌ Write throughput limited (must wait)


ASYNCHRONOUS REPLICATION (Fast but risky):

Master write:
├─ Write data
├─ Return "success" immediately
├─ Queue write for replication
├─ Slave catches up (later)

Latency: < 1ms (no wait!)

Risk:
❌ Master dies before replication
├─ Writes lost!
├─ Slave doesn't have them
└─ Data inconsistency

Example:
T=0: Write "order created"
T=0.1: Return success
T=1: Master crashes (before replicating)
T=2: Failover to slave
T=3: Slave doesn't have order! (lost)


SEMI-SYNCHRONOUS REPLICATION (Balance):

Master write:
├─ Write data
├─ Wait for at least 1 slave confirmation
├─ Return "success"
├─ Other slaves catch up asynchronously

Latency: 20-50ms (wait for 1 slave)

Safety:
✅ At least 2 copies (master + 1 slave)
✅ Tolerate 1 node failure
✅ Lower latency than full sync
❌ 2nd slave might be behind
```

---

## 🔬 Advanced Explanation

### Failover Strategies

```
ACTIVE-PASSIVE (One way):

Active (master): Accepts all traffic
├─ Processes writes
├─ Serves reads
└─ Single point of failure

Passive (slave): Idle, waiting
├─ Replicates data
├─ Can't process traffic
├─ Resources wasted

Failover:
├─ Master dies
├─ Promote slave to master
├─ Slave becomes active
└─ Old master was passive, so no conflict

Tradeoff:
✅ Simple (one active master)
✅ Clear consistency model
✅ Easy conflict resolution (no conflicts!)
❌ Idle slave resources wasted
❌ Failover slightly slower (promotion takes time)


ACTIVE-ACTIVE (Both ways):

Active 1: Accepts traffic
├─ Processes writes
├─ Serves reads
└─ Replicates to Active 2

Active 2: Accepts traffic
├─ Processes writes
├─ Serves reads
└─ Replicates to Active 1

Failover:
├─ Node 1 dies
├─ Node 2 continues serving
├─ No failover needed!
└─ Other nodes route to Node 2

Benefits:
✅ No idle resources (both working)
✅ Both serve reads
✅ Natural load distribution
❌ Complexity (both writing)
❌ Conflict resolution needed (if both write same data)

Example conflict:
T=0: Node A writes row:  name="Alice"
T=0: Node B writes same row: name="Bob"
T=1: Replication arrives at opposite node
T=1: Both nodes see conflict!
T=2: Conflict resolution: Last write wins (or merge)
```

### Consistency Models

```
STRONG CONSISTENCY (ACID):

All reads see latest writes:

Write: user.name = "Alice"
├─ Stored on master
├─ Synchronously replicated to all slaves
└─ Return "success"

Read (any node):
├─ Always returns: name = "Alice"
├─ All nodes have latest
└─ Consistent view

Pros:
✅ Simple (no surprises)
✅ Predictable
✅ ACID transactions

Cons:
❌ Slow (wait for replication)
❌ Fails if replication down
❌ Lower throughput


EVENTUAL CONSISTENCY:

Reads might see old writes (temporarily):

Write: user.name = "Alice"
├─ Stored on master
├─ Return "success"
├─ Asynchronously replicate
└─ Might take 5 seconds

Read from slave (1 second later):
├─ Slave still has: name = "Bob" (old)
├─ Returns stale data
└─ Inconsistent!

But eventually:
├─ Replication completes
├─ Slave updates: name = "Alice"
├─ Consistency achieved!

Pros:
✅ Fast (don't wait)
✅ High throughput
✅ Survives replication delays

Cons:
❌ Temporary inconsistency
❌ Complex reasoning
❌ Bugs if not handled


CAUSAL CONSISTENCY (Middle ground):

Related operations stay consistent:

Write 1: Create user (Alice)
Write 2: Create order for Alice

On read:
├─ Might see order before user (inconsistent!)
├─ But can't happen with causal consistency
├─ If you see order, you've seen user

Pros:
✅ Consistency for related operations
✅ Better throughput than strong
✅ More predictable than eventual

Cons:
❌ Complex to implement
❌ Still potential for unrelated inconsistency
```

### Handling Replication Lag

```
PROBLEM: Slave is 5 seconds behind

T=0: Write order: $100
T=1: Read from slave: $0 (old value!)
T=2: Display: "Order not found!"
T=5: Slave catches up
T=6: Read from slave: $100

User sees inconsistency!

SOLUTION 1: Read from master

Write order:
└─ Write to master

Read order:
└─ Read from master (always latest)

Downside:
❌ Master becomes bottleneck
❌ No read scaling


SOLUTION 2: Read-your-write consistency

Write order:
├─ Write to master
├─ Store write-token (version: 1000)
└─ Return to client

Read order:
├─ Send write-token to slave
├─ Slave checks: "My version >= 1000?"
├─ If yes: Serve from slave (caught up!)
├─ If no: Wait or read from master
└─ Client always sees writes

Pro:
✅ Scales reads (if slave caught up)
✅ Strong for user's own writes


SOLUTION 3: Sticky reads

Write order:
├─ Write to master: 101
└─ Return to client

Read order:
├─ Route to same master (sticky)
├─ Always see latest
└─ Consistent!

Downside:
❌ Can't load balance reads
❌ If master slow: All reads slow
```

---

## 🐍 Python Code Example

### ❌ Without Replication (Single Point of Failure)

```python
# ===== WITHOUT REPLICATION =====

import psycopg2

# Single database server
db = psycopg2.connect("dbname=shop host=db1.example.com")

def create_order(user_id, items):
    """Create order on single server"""
    
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO orders (user_id, items, created_at)
        VALUES (%s, %s, NOW())
        RETURNING id
    """, (user_id, str(items)))
    
    order_id = cursor.fetchone()[0]
    db.commit()
    
    return order_id

# Problem:
# ❌ Single database server
# ❌ If db1 dies: Orders can't be created
# ❌ Data lost (no backup)
# ❌ No failover
# ❌ Single point of failure
```

### ✅ Master-Slave Replication

```python
# ===== MASTER-SLAVE REPLICATION =====

import psycopg2
import psycopg2.pool

# Connection pools for master and slave
master_pool = psycopg2.pool.SimpleConnectionPool(
    1, 10,
    "dbname=shop host=master.example.com user=admin"
)

slave_pool = psycopg2.pool.SimpleConnectionPool(
    1, 20,  # More slaves for read scaling
    "dbname=shop host=slave.example.com user=readonly"
)

def create_order(user_id, items):
    """Create order on master"""
    
    master_conn = master_pool.getconn()
    try:
        cursor = master_conn.cursor()
        cursor.execute("""
            INSERT INTO orders (user_id, items, created_at)
            VALUES (%s, %s, NOW())
            RETURNING id
        """, (user_id, str(items)))
        
        order_id = cursor.fetchone()[0]
        master_conn.commit()
        
        # Replication happens asynchronously
        # (slave catches up in background)
        
        return order_id
    
    finally:
        master_pool.putconn(master_conn)

def get_orders(user_id):
    """Read orders from slave (read scaling)"""
    
    slave_conn = slave_pool.getconn()
    try:
        cursor = slave_conn.cursor()
        cursor.execute("""
            SELECT * FROM orders
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))
        
        return cursor.fetchall()
    
    finally:
        slave_pool.putconn(slave_conn)

# Benefits:
# ✅ Writes to master (consistent)
# ✅ Reads from slave (scalable)
# ✅ Replication asynchronous (fast)
# ✅ Handles 10x more reads
```

### ✅ Production Failover (Automatic)

```python
# ===== PRODUCTION FAILOVER (AUTOMATIC) =====

import psycopg2
from dataclasses import dataclass
from typing import Optional
import threading
import time

@dataclass
class DatabaseNode:
    name: str
    host: str
    port: int = 5432
    role: str = "replica"  # master or replica
    is_healthy: bool = True

class FailoverManager:
    """Manage failover between master and replicas"""
    
    def __init__(self):
        self.master: Optional[DatabaseNode] = None
        self.replicas: list[DatabaseNode] = []
        self.master_pool = None
        self.replica_pools = {}
    
    def add_master(self, name: str, host: str):
        """Register master database"""
        self.master = DatabaseNode(name, host, role="master")
        self.master_pool = self._create_pool(host)
    
    def add_replica(self, name: str, host: str):
        """Register replica database"""
        replica = DatabaseNode(name, host, role="replica")
        self.replicas.append(replica)
        self.replica_pools[name] = self._create_pool(host)
    
    def _create_pool(self, host: str):
        """Create connection pool"""
        return psycopg2.pool.SimpleConnectionPool(
            1, 10,
            f"dbname=shop host={host} user=app"
        )
    
    def health_check_master(self) -> bool:
        """Check if master is healthy"""
        
        try:
            conn = self.master_pool.getconn()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            self.master_pool.putconn(conn)
            
            self.master.is_healthy = True
            return True
        
        except Exception as e:
            self.master.is_healthy = False
            print(f"Master health check failed: {e}")
            return False
    
    def write_to_master(self, query: str, params: tuple):
        """Write always goes to master"""
        
        if not self.master.is_healthy:
            raise Exception("Master is down, cannot write!")
        
        conn = self.master_pool.getconn()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            result = cursor.fetchone()
            return result
        
        finally:
            self.master_pool.putconn(conn)
    
    def read_from_replica(self, query: str, params: tuple):
        """Read from any healthy replica"""
        
        for replica in self.replicas:
            if not replica.is_healthy:
                continue
            
            try:
                pool = self.replica_pools[replica.name]
                conn = pool.getconn()
                cursor = conn.cursor()
                cursor.execute(query, params)
                result = cursor.fetchall()
                pool.putconn(conn)
                
                return result
            
            except Exception as e:
                print(f"Read from {replica.name} failed: {e}")
                replica.is_healthy = False
                continue
        
        raise Exception("All replicas down!")
    
    def promote_replica_to_master(self, replica_name: str):
        """Promote replica to master (failover)"""
        
        print(f"Promoting {replica_name} to master...")
        
        replica = next((r for r in self.replicas if r.name == replica_name), None)
        if not replica:
            raise Exception(f"Replica {replica_name} not found")
        
        # Get connection to replica
        pool = self.replica_pools[replica_name]
        conn = pool.getconn()
        
        try:
            cursor = conn.cursor()
            
            # Run promotion commands
            cursor.execute("SELECT pg_wal_replay_pause()")  # Pause replication
            cursor.execute("ALTER SYSTEM SET primary_conninfo = ''")  # Remove primary
            cursor.execute("SELECT pg_ctl_promote()")  # Promote to master
            
            conn.commit()
            print(f"✓ {replica_name} promoted to master")
            
            # Update in-memory state
            old_master = self.master
            self.master = replica
            self.master.role = "master"
            self.master.is_healthy = True
            
            # Remove from replicas list
            self.replicas.remove(replica)
            
            return True
        
        finally:
            pool.putconn(conn)
    
    def start_health_monitoring(self, interval_seconds=10):
        """Background thread to monitor health"""
        
        def monitor():
            while True:
                # Check master
                if not self.health_check_master():
                    print("⚠ Master down! Initiating failover...")
                    
                    # Find best replica
                    best_replica = self.replicas[0]
                    
                    # Promote it
                    try:
                        self.promote_replica_to_master(best_replica.name)
                        print("✓ Failover completed!")
                    except Exception as e:
                        print(f"✗ Failover failed: {e}")
                
                # Check replicas
                for replica in self.replicas:
                    try:
                        pool = self.replica_pools[replica.name]
                        conn = pool.getconn()
                        cursor = conn.cursor()
                        cursor.execute("SELECT 1")
                        pool.putconn(conn)
                        replica.is_healthy = True
                    except:
                        replica.is_healthy = False
                
                time.sleep(interval_seconds)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

# Usage
failover = FailoverManager()
failover.add_master("master1", "master.example.com")
failover.add_replica("replica1", "replica1.example.com")
failover.add_replica("replica2", "replica2.example.com")

# Start automatic health monitoring
failover.start_health_monitoring(interval_seconds=10)

# Write always goes to master
def create_order(user_id, items):
    result = failover.write_to_master(
        """INSERT INTO orders (user_id, items)
           VALUES (%s, %s) RETURNING id""",
        (user_id, str(items))
    )
    return result[0]

# Read can use replicas
def get_orders(user_id):
    results = failover.read_from_replica(
        "SELECT * FROM orders WHERE user_id = %s",
        (user_id,)
    )
    return results

# If master dies:
# 1. Health check detects failure (10 seconds)
# 2. Automatically promotes replica to master
# 3. Writes resume (with new master)
# 4. No manual intervention needed!

# Benefits:
# ✅ Automatic failover (no manual steps)
# ✅ High availability (survives master failure)
# ✅ Read scaling (multiple replicas)
# ✅ Production-ready
```

---

## 💡 Mini Project: "Build Failover System"

### Phase 1: Master-Slave Replication ⭐

**Requirements:**
- Setup master database
- Setup replica database
- Replication configuration
- Monitor replication lag

---

### Phase 2: Automatic Failover ⭐⭐

**Requirements:**
- Health check master
- Detect failure
- Promote replica
- Update routing

---

### Phase 3: Multi-Region Failover ⭐⭐⭐

**Requirements:**
- Multiple replicas
- Quorum-based promotion
- DNS failover
- Zero-downtime updates

---

## ⚖️ Replication Strategies Comparison

| Strategy | Latency | Data Loss | Complexity | Failover Time |
|----------|---------|-----------|-----------|---------------|
| **Async** | Low | Possible | Low | Fast |
| **Sync** | High | None | Medium | Slow |
| **Semi-Sync** | Medium | Minimal | Medium | Medium |
| **Multi-Master** | Low | None | High | Very Fast |

---

## ❌ Common Mistakes

### Mistake 1: Async Replication Without Monitoring

```python
# ❌ Assume replication is instant
write_to_master(order)
read_from_slave(order_id)  # Might not exist yet!

# ✅ Handle replication lag
write_to_master(order)
if need_immediate_read:
    read_from_master(order_id)  # Guaranteed fresh
else:
    read_from_slave_with_timeout(order_id)
```

### Mistake 2: Slave Promotion Without Checks

```python
# ❌ Promote without checking if caught up
promote_replica_to_master(replica)
# Might have lost writes!

# ✅ Check before promoting
if replica.replication_lag < 1000:  # Less than 1000 bytes behind
    promote_replica_to_master(replica)
else:
    alert("Replica too far behind, manual intervention needed")
```

### Mistake 3: No Automatic Failover

```python
# ❌ Manual failover
# Master dies
# On-call engineer gets paged
# 30 minutes downtime

# ✅ Automatic failover
# Master dies
# Health check detects (10 seconds)
# Automatic promotion
# 10 seconds downtime
```

---

## 📚 Additional Resources

**Replication:**
- [PostgreSQL Replication](https://www.postgresql.org/docs/current/warm-standby.html)
- [MySQL Replication](https://dev.mysql.com/doc/refman/8.0/en/replication.html)

**Failover:**
- [Patroni (PostgreSQL failover)](https://github.com/zalando/patroni)
- [MHA (MySQL failover)](https://code.google.com/archive/p/mysql-master-ha/)


---

## 🎯 Before You Leave

**Can you answer these?**

1. **What's master-slave replication?**
   - Answer: Master handles writes, slave copies data

2. **What's failover?**
   - Answer: Automatically switch to backup when primary fails

3. **Async vs sync replication?**
   - Answer: Async = fast + risk; Sync = slow + safe

4. **When to use multi-master?**
   - Answer: When need write to any node, handle conflicts

5. **How long should failover take?**
   - Answer: < 10 seconds for production systems

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **Architect:** "We need replication for safety!"
>
> **After setup:** "Replication is 5 seconds behind"
>
> **Then:** "Replication broke, data diverged"
>
> **Then:** "Which replica do we promote?"
>
> **Engineer:** "Just choose one and hope"
>
> **Everyone:** "This is fine." 🔥

---

[← Back to Main](../README.md) | [Previous: Heartbeats & Health Checks](34-heartbeats-health-checks.md) | [Next: Circuit Breakers →](36-circuit-breakers.md)

---

**Last Updated:** November 11, 2025  
**Difficulty:** ⭐⭐⭐⭐ Advanced (distributed systems)  
**Time to Read:** 27 minutes  
**Time to Implement:** 6-10 hours per phase  

---

*Failover & Replication: The art of having Plan B, Plan C, and a prayer that Plan A doesn't go down.* 🚀