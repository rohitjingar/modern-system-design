# 11. CAP Theorem

CAP Theorem says you can only have 2 of 3 guarantees. Developers read this and think "I'll take all three!" Then their system crashes at 2 AM and they understand. 💔

[← Back to Main](../README.md) | [Previous: Replication](10-replication.md) | [ACID vs BASE](12-acid-vs-base.md)

---

## 🎯 Quick Summary

**The CAP Theorem** states that in a distributed system, you can guarantee only two of three properties: **Consistency** (all nodes see same data), **Availability** (system always responds), or **Partition tolerance** (survives network splits). Every real distributed system picks two and accepts the trade-off of the third.

Think of it as: **You Get 2 of 3: Consistency, Availability, or Partition Tolerance**

---

## 🌟 Beginner Explanation

### The Three Properties

**CONSISTENCY (C):**
```
All nodes have the same data at the same time.

Bank Account Balance:
- Account has $100
- Master says: $100
- Replica 1 says: $100
- Replica 2 says: $100

Write Update: +$50
- Master: $150
- Replica 1: $150
- Replica 2: $150

All consistent ✅

If you read balance from ANY server: Always $150
```

**AVAILABILITY (A):**
```
System always responds to requests (never returns "Error").

Request 1: Get balance → Server responds (200ms)
Request 2: Transfer $50 → Server responds (150ms)
Request 3: Get balance → Server responds (180ms)

System handles all requests ✅

Even if slow, as long as it responds: Available ✅
```

**Partition Tolerance (P):**
```
System survives network partitions (servers can't talk to each other).

Scenario: Network cable cut! 🔌

Network Partition:
┌─────────────┐              ┌─────────────┐
│  Server 1   │ DISCONNECTED │  Server 2   │
│  Master     │ CAN'T TALK   │  Replica    │
└─────────────┘              └─────────────┘

System must keep running despite this 💪

Partition Tolerant: Yes, both keep accepting requests
Partition Tolerant: No, one shuts down
```

### The Three Trade-offs

**OPTION 1: CP (Consistency + Partition Tolerance)**

```
During network partition:
├─ Master: Accepts writes, consistent ✅
├─ Replica: Disconnected, rejects reads/writes ❌
└─ Result: System available on master only

Consistency: Guaranteed ✅
Availability: Lost (replicas down) ❌
Partition Tolerance: Handled ✅

Example: Traditional SQL databases
├─ Primary: Takes writes ✅
├─ Standby: Can't write (might be inconsistent)
├─ After reconnect: Replicas catch up ✅

When to use: Banking, critical data
```

**OPTION 2: AP (Availability + Partition Tolerance)**

```
During network partition:
├─ Server 1: Accepts all writes, returns results ✅
├─ Server 2: Accepts all writes, returns results ✅
├─ After reconnect: Servers have DIFFERENT data 😱
└─ Conflict resolution needed

Consistency: Lost (eventually consistent) ❌
Availability: Guaranteed ✅
Partition Tolerance: Handled ✅

Example: NoSQL databases (MongoDB, Cassandra)
├─ Write to Server 1: Succeeds immediately ✅
├─ Write to Server 2: Succeeds immediately ✅
├─ Servers reconnect: Merge/resolve conflicts
└─ Eventually consistent after merge

When to use: Social media, analytics
```

**OPTION 3: CA (Consistency + Availability)**

```
Assumes no network partitions (unrealistic!)

If any partition happens:
├─ You must choose: Keep CA or handle partition?
├─ You MUST pick either CP or AP
└─ CA is not possible in distributed systems!

Why? When networks partition:
- Can't have consistency (nodes diverge)
- Can't have availability (someone must go down)

Example: Single server (not distributed)
├─ No partitions possible ✅
├─ One server = always consistent ✅
├─ One server = always available ✅

But if server crashes: Neither ❌
```

### Visual: The CAP Triangle

```
        Consistency
            /\
           /  \
          /    \
         /  CA  \
        /________\
       /         /\
      /    CP   /  \
     /         /    \
    /__________/      \
   /    AP    /________\
  /          /          \
 /__________/____________\

   Partition Tolerance

Every system sits somewhere on this triangle.
Must give up at least one corner.
```

---

## 🔬 Advanced Explanation

### Consistency Models

**STRONG CONSISTENCY (Linear Consistency)**

```
Write completes → All reads return new value

Timeline:
Write: Set age = 30 (completes at T=100ms)
Read at T=101ms: Gets 30 ✅
Read at T=102ms: Gets 30 ✅
Read at T=200ms: Gets 30 ✅

Guarantee: All reads after write see new value

Cost: Slow (must replicate everywhere before confirming)
```

**EVENTUAL CONSISTENCY**

```
Write completes → Reads eventually return new value (after lag)

Timeline:
Write: Set age = 30 (completes at T=100ms locally)
Read at T=101ms: Gets old value (30 not replicated yet) 😱
Read at T=200ms: Gets 30 ✅
Read at T=500ms: Gets 30 ✅

Guarantee: All reads eventually see new value (after lag)

Cost: Fast (confirm write immediately, replicate later)
Problem: Temporary inconsistency
```

**CAUSAL CONSISTENCY**

```
Respects cause-and-effect between operations

Operation 1: Write X = 10
Operation 2: Write Y = X + 5 (depends on Op 1)
Operation 3: Read Y

With causal consistency:
- Op 3 sees Y = 15 (knows about Op 1 and 2)
- Not arbitrary ordering

Middle ground between:
- Strong consistency (too slow)
- Eventual consistency (confusing)
```

### Real-World CAP Choices

**BANKING (CP: Consistency + Partition Tolerance)**

```
Network partition: Choose consistency

Scenario: User tries to withdraw $100

Path 1 (Has connection to master):
├─ Master: Check balance ($150)
├─ Master: Withdraw $100
├─ Result: Success ✅, balance = $50

Path 2 (Disconnected from master):
├─ Replica can't write (no master connection)
├─ Result: "Error, try again" ❌
├─ Reason: Better to lose availability than lose consistency
├─ (Don't want to allow two $100 withdrawals from $150!)

Better consistency than availability 💪
```

**SOCIAL MEDIA (AP: Availability + Partition Tolerance)**

```
Network partition: Choose availability

Scenario: User posts tweet

Path 1 (Server A):
├─ Server A: Accept tweet immediately ✅
├─ Server A: "Posted!" to user
├─ Later: Replicate to Server B, C, D

Path 2 (Server B disconnected):
├─ Still accepts posts immediately ✅
├─ User gets response instantly
├─ Later: Merge/sync when reconnected

Better availability than consistency 💪
```

### PACELC Theorem (Extension of CAP)

```
CAP says: During Partition, choose Consistency or Availability

But what about normal operation (no partition)?

PACELC adds:
- If Partition: Choose C or A (CAP)
- Else (no partition): Choose Latency or Consistency

PACELC says:
Every system trades Partitions (AC vs AP)
AND trades Latency (E) vs Consistency (C)

Examples:

PostgreSQL (PC/EC):
├─ Partition: Choose Consistency
├─ Normal: Consistency over Latency (slow writes)

Cassandra (PA/EL):
├─ Partition: Choose Availability
├─ Normal: Latency over Consistency (fast writes, eventual consistency)

Riak (PA/EL):
├─ Partition: Choose Availability
├─ Normal: Latency over Consistency
```

### Handling Network Partitions

**STRATEGY 1: Stop One Side (CP)**

```
Network cuts! 🔌

[Server 1]              [Server 2]
Master              Replica
Can't talk!

Strategy: Fence off one side
├─ Master keeps running: Accepts writes ✅
├─ Replica shuts down: Rejects requests ❌
├─ Result: Consistent but not available on replica
├─ After reconnect: Replica catches up from master

Example: Traditional database failover
```

**STRATEGY 2: Keep Both Running (AP)**

```
Network cuts! 🔌

[Server 1]              [Server 2]
Accepts writes          Accepts writes
Both keep running ✅    Both keep running ✅

Results:
- Write to S1: age = 30
- Write to S2: age = 25

After reconnect:
- Age = 30 or 25? ❌
- Need conflict resolution:
  - Last-write-wins: Keep later write
  - Application logic: Merge intelligently
  - User decides: Ask user which version to keep

Example: NoSQL with multi-master
```

### Practical Decisions During Partitions

```
PARTITION HAPPENS: You have seconds to decide!

Decision Tree:

Q1: Is this data critical?
├─ YES: Choose CP (lose availability)
│   └─ Banking, healthcare: Can't afford inconsistency
│
└─ NO: Choose AP (lose consistency)
    └─ Social media, analytics: Can tolerate stale data

Q2: Can you afford downtime?
├─ NO: Choose AP (keep serving)
│   └─ Always-on services
│
└─ YES: Choose CP (consistent or fail)
    └─ Internal tools, less critical systems

Q3: How bad is inconsistency?
├─ CATASTROPHIC: Choose CP
│   └─ Financial, medical
│
└─ ACCEPTABLE: Choose AP
    └─ Preferences, feed ranking
```

---

## 🐍 Python Code Example

### ❌ Naive Distributed System (Misses CAP)

```python
# ===== NAIVE SYSTEM (CRASHES ON PARTITION) =====

class NaiveDistributedDB:
    """System that doesn't handle partitions"""
    
    def __init__(self):
        self.master_data = {}
        self.replica_data = {}
        self.network_connected = True
    
    def write(self, key, value):
        """Write to master"""
        # Write to master
        self.master_data[key] = value
        
        # Replicate to replica
        if self.network_connected:
            self.replica_data[key] = value
            return True
        else:
            # Network down! What do we do?
            # Naive: Just ignore
            # Result: Inconsistency 😱
            return True  # Lie to user
    
    def read_from_replica(self, key):
        """Read from replica"""
        # Returns stale data if write failed to replicate!
        return self.replica_data.get(key)
    
    def simulate_network_partition(self):
        """Simulate network cut"""
        self.network_connected = False

# Problems:
# ❌ Doesn't handle network partitions
# ❌ Can lose data (writes confirmed but not replicated)
# ❌ No consistency guarantee
# ❌ No availability guarantee
```

### ✅ CP System (Consistent, Partition Tolerant)

```python
from enum import Enum

class ConsistencyChoice(Enum):
    STOP = "stop"        # Reject requests
    ASYNC_CACHE = "async"  # Cache locally, sync later

class CPDistributedDB:
    """Prioritizes Consistency over Availability"""
    
    def __init__(self, choice=ConsistencyChoice.STOP):
        self.master_data = {}
        self.replica_data = {}
        self.network_connected = True
        self.consistency_choice = choice
        self.pending_writes = []  # For async mode
    
    def write(self, key, value):
        """Write with consistency guarantee"""
        
        if not self.network_connected:
            # Network partition happened!
            if self.consistency_choice == ConsistencyChoice.STOP:
                # Stop: Return error (lose availability)
                return {"success": False, "error": "Network down, rejecting write"}
            elif self.consistency_choice == ConsistencyChoice.ASYNC_CACHE:
                # Cache: Store locally, sync later
                self.pending_writes.append((key, value))
                return {"success": True, "pending": True}
        
        # Normal path: Replicate to replica before confirming
        self.master_data[key] = value
        self.replica_data[key] = value  # Wait for this!
        
        return {"success": True, "pending": False}
    
    def read(self, key):
        """Read is always consistent"""
        return self.master_data.get(key)
    
    def simulate_network_partition(self):
        """Partition happens"""
        self.network_connected = False
    
    def recover_from_partition(self):
        """Network comes back"""
        self.network_connected = True
        
        # Flush pending writes
        for key, value in self.pending_writes:
            self.replica_data[key] = value
        
        self.pending_writes = []
    
    def get_status(self):
        return {
            "master_data": self.master_data,
            "replica_data": self.replica_data,
            "network_connected": self.network_connected,
            "pending_writes": len(self.pending_writes)
        }

# Usage
print("=== CP SYSTEM (Consistency + Partition Tolerance) ===\n")

db = CPDistributedDB(choice=ConsistencyChoice.STOP)

# Normal operation
print("Write: alice_age = 30")
result = db.write("alice_age", 30)
print(f"Result: {result}")

print(f"Read: {db.read('alice_age')}")

# Network partition!
print("\n🔌 Network partition!")
db.simulate_network_partition()

print("Attempt write: alice_age = 35")
result = db.write("alice_age", 35)
print(f"Result: {result}")
# Returns error! ❌ Lose availability but keep consistency ✅

print("\n✅ Network recovered!")
db.recover_from_partition()
print(f"Status: {db.get_status()}")

# Output:
# === CP SYSTEM ===
#
# Write: alice_age = 30
# Result: {'success': True, 'pending': False}
# Read: 30
#
# 🔌 Network partition!
# Attempt write: alice_age = 35
# Result: {'success': False, 'error': 'Network down, rejecting write'}
#
# ✅ Network recovered!
# Status: {'master_data': {'alice_age': 30}, 'replica_data': {'alice_age': 30}, ...}
```

### ✅ AP System (Available, Partition Tolerant)

```python
class APDistributedDB:
    """Prioritizes Availability over Consistency"""
    
    def __init__(self):
        self.master_data = {}
        self.replica_data = {}
        self.network_connected = True
        self.master_version = {}
        self.replica_version = {}
        self.version_counter = 0
    
    def write(self, key, value):
        """Write with immediate confirmation (eventually consistent)"""
        
        self.version_counter += 1
        version = self.version_counter
        
        # Always accept write (availability!)
        self.master_data[key] = value
        self.master_version[key] = version
        
        # Try to replicate
        if self.network_connected:
            self.replica_data[key] = value
            self.replica_version[key] = version
        # If network down: Still confirm write! (Accept eventual inconsistency)
        
        return {"success": True, "version": version}
    
    def read(self, key):
        """Read from either node"""
        master_val = self.master_data.get(key)
        master_ver = self.master_version.get(key, 0)
        
        replica_val = self.replica_data.get(key)
        replica_ver = self.replica_version.get(key, 0)
        
        # Return newer version
        if master_ver >= replica_ver:
            return master_val
        else:
            return replica_val
    
    def simulate_network_partition(self):
        """Partition happens"""
        self.network_connected = False
    
    def recover_from_partition(self):
        """Network comes back, resolve conflicts"""
        self.network_connected = True
        
        # Simple conflict resolution: Last-write-wins
        for key in self.master_data:
            master_ver = self.master_version[key]
            replica_ver = self.replica_version.get(key, 0)
            
            if master_ver > replica_ver:
                # Master is newer, replica catches up
                self.replica_data[key] = self.master_data[key]
                self.replica_version[key] = master_ver
        
        for key in self.replica_data:
            replica_ver = self.replica_version[key]
            master_ver = self.master_version.get(key, 0)
            
            if replica_ver > master_ver:
                # Replica is newer, master catches up
                self.master_data[key] = self.replica_data[key]
                self.master_version[key] = replica_ver

# Usage
print("=== AP SYSTEM (Availability + Partition Tolerance) ===\n")

db = APDistributedDB()

# Normal operation
print("Write: alice_age = 30")
result = db.write("alice_age", 30)
print(f"Result: {result}")

# Network partition!
print("\n🔌 Network partition!")
db.simulate_network_partition()

print("Write: alice_age = 35")
result = db.write("alice_age", 35)
print(f"Result: {result}")
print("✅ Write accepted despite partition! (Availability)")

# Different write on replica (simulated)
db.replica_data["alice_age"] = 25
db.replica_version["alice_age"] = 2

print(f"\nMaster has: {db.master_data['alice_age']}")
print(f"Replica has: {db.replica_data['alice_age']}")
print("❌ Inconsistent during partition")

print("\n✅ Network recovered!")
db.recover_from_partition()

print(f"After conflict resolution:")
print(f"Master has: {db.master_data['alice_age']}")
print(f"Replica has: {db.replica_data['alice_age']}")
print("✅ Consistent again (eventually)")

# Output:
# === AP SYSTEM ===
# Write: alice_age = 30
# Result: {'success': True, 'version': 1}
#
# 🔌 Network partition!
# Write: alice_age = 35
# Result: {'success': True, 'version': 2}
# ✅ Write accepted despite partition!
#
# Master has: 35
# Replica has: 25
# ❌ Inconsistent during partition
#
# ✅ Network recovered!
# After conflict resolution:
# Master has: 35
# Replica has: 35
# ✅ Consistent again (eventually)
```

---

## 💡 Mini Project: "CAP Trade-off Explorer"

### Phase 1: Simple Systems ⭐

**Requirements:**
- Simulate CP system
- Simulate AP system
- Show differences
- Compare trade-offs

---

### Phase 2: Advanced (With Conflicts) ⭐⭐

**Requirements:**
- Multiple concurrent writes
- Conflict detection
- Resolution strategies
- Consistency tracking

---

### Phase 3: Enterprise (Real Scenarios) ⭐⭐⭐

**Requirements:**
- Network partition simulation
- Multiple regions
- Automatic failover
- Conflict resolution
- Monitoring

---

## ⚖️ CAP Choices by System

| System | Choice | Why |
|--------|--------|-----|
| **PostgreSQL** | CP | Critical data, consistency matters |
| **MongoDB** | AP | High availability, eventual consistency |
| **Cassandra** | AP | Distributed, high availability |
| **Dynamo (AWS)** | AP | Always available, tolerates stale data |
| **Chubby (Google)** | CP | Coordination, need consistency |
| **Redis** | CP | In-memory, can afford to go down |
| **HBase** | CP | Strong consistency for writes |
| **Memcached** | AP | Lossy cache, availability > consistency |

---

## ❌ Common Misunderstandings

### Mistake 1: "I'll Just Have All Three"

```python
# ❌ NO! Impossible in distributed systems
# If network partition happens, you MUST choose

# What happens if you try to have all three:
├─ Network partition occurs
├─ Master and replica can't talk
├─ Master allows write (availability)
├─ Replica allows write (availability)
├─ Different data on each (inconsistency)
├─ Broke consistency! 💥
```

### Mistake 2: "Partitions Never Happen"

```python
# ❌ WRONG! Partitions absolutely happen
# Real-world examples:
├─ Fiber cut 🔪
├─ Misconfigured firewall 🔥
├─ Router failure 💔
├─ BGP hijack 😱
├─ Cloud provider issues ⛈️

# Partitions are guaranteed to happen
# You must plan for them

# ✅ Every distributed system MUST be partition tolerant
# So you're really choosing between CP and AP
```

### Mistake 3: Not Understanding Trade-offs

```python
# ❌ Choosing AP thinking consistency doesn't matter
# Result: Corrupted data, inconsistent state, angry users

# When building system:
# 1. Identify what data you have
# 2. Understand consistency requirements
# 3. THEN choose CAP strategy

# ❌ Financial data? Must be consistent (CP)
# ❌ Medical data? Must be consistent (CP)
# ✅ Social media feed? Can be eventually consistent (AP)
```

---

## 📚 Additional Resources

**Foundational Papers:**
- [CAP Theorem - Eric Brewer](https://www.infoq.com/presentation/cap-theorem-2015/)
- [PACELC - Daniel Abadi](http://dbmsmusings.blogspot.com/2010/04/problems-with-cap-theorem.html)

**Real-world Examples:**
- [Consistency & Trade-offs in Distributed Systems](https://www.youtube.com/watch?v=cy9THvANvv4)
- [CRDTs & Eventual Consistency](https://crdt.tech/)

**Tools & Systems:**
- [Jepsen - Partition Testing](https://jepsen.io/)
- [Hermitage - Database Testing](https://github.com/ept/hermitage)

---

## 🎯 Before You Leave

**Can you answer these?**

1. **What are the three properties in CAP?**
   - Answer: Consistency, Availability, Partition tolerance

2. **Can a system have all three?**
   - Answer: No. With partition, must choose C or A

3. **Why do network partitions happen?**
   - Answer: Cables break, routers fail, software bugs, etc.

4. **What does CP prioritize?**
   - Answer: Consistency over availability (fails closed)

5. **What does AP prioritize?**
   - Answer: Availability over consistency (fails open)

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **New Developer:** "I'll build a system with Consistency, Availability, AND Partition Tolerance!"
>
> **Senior Dev:** "Cool. You'll learn about CAP Theorem the hard way."
>
> **3 Months Later:** Network partition happens
>
> **New Developer:** *stares in horror as data becomes inconsistent*
>
> **Senior Dev:** "Welcome to distributed systems." 😎

---

[← Back to Main](../README.md) | [Previous: Replication](10-replication.md) | [ACID vs BASE](12-acid-vs-base.md)

---

**Last Updated:** November 10, 2025  
**Difficulty:** ⭐⭐⭐ Intermediate-Advanced (requires distributed thinking)  
**Time to Read:** 23 minutes  
**Time to Build Explorer:** 3-5 hours per phase  

---

*CAP Theorem: The most important thing to understand when everything goes wrong.* 🚀