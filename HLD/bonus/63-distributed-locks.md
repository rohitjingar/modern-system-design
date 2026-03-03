# 63. Distributed Locks

You have a resource (database, file, critical section). Two servers want to use it simultaneously. Without locks: Corruption! With locks: Both wait forever (deadlock!). With distributed locks: One server gets lock, does work, releases. But what if that server crashes while holding lock? It's stuck forever. Welcome to distributed locks, where deadlock is expected and recovery is an art. Netflix uses Redis locks (best effort). Google uses Chubby (paper published but nobody copies it). Amazon uses DynamoDB conditional writes. LinkedIn uses Kafka for everything. Everyone has nightmares about deadlocked production systems. 🔒💀

[← Back to Main](../README.md) | [Previous: Time & Ordering](62-time-ordering.md) | [Next: Leader Election →](64-leader-election.md)

---

## 🎯 Quick Summary

**Distributed Locks** protect shared resources in multi-server systems. **Mutual exclusion:** Only one process holds lock at a time. **Deadlock prevention** requires timeout mechanisms. **Lock contention** causes performance issues. Redis (fast, unsafe), etcd (consensus, slower), DynamoDB (conditional writes). Trade-off: performance (Redis) vs correctness (consensus). Netflix uses Redis locks with timeouts. Google uses Chubby (internal, not public). Challenge: lock expiration, recovery on crash, lock contention, fairness. Essential for: state machines, critical sections, migrations.

Think of it as: **Distributed Locks = Mutual Exclusion at Scale**

---

## 🌟 Beginner Explanation

### The Distributed Lock Problem

```
SINGLE SERVER (Easy):


with lock:  # Acquire lock
    critical_section()  # Only one thread runs
    # Lock automatically released


Why it works:
├─ One process per machine
├─ Kernel enforces mutual exclusion
├─ Timeout: OS kills process
└─ Simple!


DISTRIBUTED SYSTEM (Hard):

┌─────────────┐  Shared Resource  ┌─────────────┐
│  Server A   │←──(Database File)──→│  Server B   │
└─────────────┘                     └─────────────┘

Problem:
├─ Server A tries to lock resource
├─ Server B tries to lock resource
├─ Both acquire lock? (No enforcement!)
├─ Both modify resource simultaneously
├─ Corruption!

Solution: Distributed lock service

┌─────────────┐                    ┌─────────────┐
│  Server A   │                    │  Server B   │
└──────┬──────┘                    └──────┬──────┘
       │ "Can I have lock?"               │ "Can I have lock?"
       └─────────────┬─────────────────────┘
                     ↓
            ┌─────────────────┐
            │  Lock Service   │
            │  (Redis/etcd)   │
            └─────────────────┘
            
Lock service logic:
├─ Server A: Grants lock
├─ Server B: "Lock held by A, wait"
├─ Server A: Releases lock
├─ Server B: Gets lock, proceeds
└─ Mutual exclusion! ✓
```

### Lock Acquisition Strategies

```
STRATEGY 1: Blocking Lock (Wait)

Server A: "Lock resource X" (blocks)
├─ Lock available: Granted immediately
├─ Lock held by other: WAIT
└─ When released: Granted

Problem:
├─ Server waits indefinitely
├─ If holder crashes: Stuck forever!
└─ Deadlock!

Solution: Add timeout

Server A: "Lock resource X" (timeout 10 seconds)
├─ Lock available: Granted
├─ Lock held: Wait up to 10 seconds
├─ 10 seconds passed: Timeout, fail
└─ Prevent infinite waits


STRATEGY 2: Non-blocking Lock (Try)

Server A: "Try to lock resource X"
├─ Lock available: Granted, return true
├─ Lock held: Return false immediately
└─ No wait

Server code:

if lock.try_lock(timeout=1):
    # Got lock, do work
    critical_section()
    lock.release()
else:
    # Couldn't get lock, retry later
    retry_later()


Pros:
✓ Never blocks indefinitely
✓ Can retry

Cons:
✗ Busy-waiting (retry loop)
✗ High latency (wait for next retry)


STRATEGY 3: Wait-and-Signal (Best)

Server A: "Lock resource X" (blocking with timeout)
├─ Lock available: Granted immediately
├─ Lock held: Wait (don't busy loop)
├─ Lock released: Signal waiting servers
├─ Timeout: Give up after N seconds
└─ Efficient!

Problem:
├─ Network signal might be lost
├─ Server might crash before signal
└─ Still need timeout as fallback

Implementation:
├─ Lock service maintains queue
├─ Waiting servers: Subscribe to unlock event
├─ Lock released: Publish event
├─ Next in queue: Awakened
└─ Timeout: Fallback mechanism
```

### Lock Expiration & Deadlock Prevention

```
PROBLEM: Holder crashes while holding lock

Scenario:
├─ Server A: Acquires lock
├─ Server A: Crashes (while holding lock)
├─ Server B: Waiting for lock (forever!)
└─ Deadlock!

Solution: Lock expiration (lease)

Lock with TTL:
├─ Server A: Lock resource X for 10 seconds
├─ Server A: Acquires lock
├─ Server A: Crashes
├─ After 10 seconds: Lock expires automatically
├─ Server B: Gets lock (deadline passed)
└─ Deadlock prevented! ✓


IMPLEMENTATION:

Lock structure:
{
  "resource": "database_file",
  "owner": "server_a",
  "acquired_at": 10.0,
  "expires_at": 20.0,  // Current time + 10 seconds
  "renew_token": "abc123"
}

Server A's responsibility:
├─ While holding lock: Renew periodically
├─ Example: Renew every 3 seconds (before 10 second expiry)
├─ If crash: Stop renewing
├─ After 10 seconds: Lock expires
└─ Server B: Can acquire

Code:

# Acquire lock with 10 second expiry
lock_token = lock_service.acquire("resource", timeout=10)

while doing_work:
    # Renew every 3 seconds
    lock_service.renew(lock_token, timeout=10)
    sleep(3)

# Done: Release
lock_service.release(lock_token)


GARBAGE COLLECTION:

Lock service periodically checks:

Current time: 30.0
Lock expires_at: 20.0
Expired? YES → Delete lock

Server B can now acquire!


Trade-off:
├─ Short TTL (1 sec): Fast recovery, but risky if work takes 1.1 seconds
├─ Long TTL (1 min): Safe, but slow recovery if crash
└─ Typical: 10-30 seconds


### Lock Contention & Performance


SCENARIO: Many servers want same lock

N servers all trying to lock "database_migration"

┌──────────────┐
│  Server 1    │ Waiting
├──────────────┤
│  Server 2    │ Waiting
├──────────────┤
│  Server 3    │ Waiting
├──────────────┤
│  Server 4    │ **LOCK HELD**
├──────────────┤
│  Server 5    │ Waiting
└──────────────┘

Problem:
├─ Only 1 server works
├─ Others wait (wasted resources)
├─ Throughput: 1 out of N
└─ Very slow!

Solutions:

Option 1: Queue-based lock
├─ Fair: FIFO order
├─ Problem: Still only 1 at a time
└─ Slower than free-for-all

Option 2: Lock sharding
├─ Multiple locks (database_shard_1, database_shard_2, ...)
├─ Each shard: One lock
├─ Multiple shards: Can be locked simultaneously
├─ Throughput: Multiplied by # shards
└─ Complexity: Must handle shard conflicts

Example:
Lock("user_1") ≠ Lock("user_2")
├─ Thread A: Locks user_1
├─ Thread B: Locks user_2
├─ Both: Can run simultaneously!
├─ No contention between different users
└─ Better throughput!

Option 3: Read-write locks
├─ Multiple readers (no locks)
├─ Single writer (exclusive lock)
├─ Example: Update cache (writer) vs read cache (readers)
└─ Good for read-heavy workloads

Option 4: Optimistic locking
├─ No lock acquired
├─ Check version before update
├─ "Update if version == 5"
├─ Conflict: Retry with new version
└─ Good for low-contention scenarios
```

---

## 🔬 Advanced Concepts

### Redis Locks (Optimistic)

```
REDIS LOCKS (Fast but unsafe):

How it works:

SET lock:resource:X value:token NX EX 10

├─ NX: Only set if not exists (atomic!)
├─ EX: Expire in 10 seconds
└─ Returns: OK if locked, nil if taken

Lock acquisition:

token = uuid.uuid4()  # Unique token

# Try to acquire
result = redis.set(
    f"lock:{resource}",
    token,
    nx=True,  # Only if not exists
    ex=10     # Expire in 10 seconds
)

if result:
    # Acquired lock!
else:
    # Locked by someone else


Release:

# Use Lua script (atomic)
SCRIPT = """
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end
"""

# Compare token before deleting
result = redis.eval(SCRIPT, 1, f"lock:{resource}", token)
if result:
    # Successfully released
else:
    # Token mismatch (lock expired, someone else has it)


Benefits:
✓ Very fast (< 1ms)
✓ Simple implementation
✓ Good for low-contention scenarios

Problems:
✗ Not "safe" by distributed systems standards
✗ Redis can lose data (crash)
✗ Clock skew: Expire time unreliable
✗ "best effort" locking

Use case:
├─ Cache invalidation
├─ Rate limiting
├─ Low-stakes operations
└─ Acceptable data loss


CONSENSUS LOCKS (Safe but slow):

Etcd/Zookeeper style:

How it works:
├─ Write lock to replicated log
├─ Wait for replication (consensus)
├─ Once replicated: Lock granted
├─ Crash resilient: Other servers have copy

Benefits:
✓ Safe (crash resilient)
✓ Consensus guarantees
✓ No data loss

Problems:
✗ Slower (50-500ms)
✗ More complex
✗ Network partition sensitive

Use case:
├─ Database migrations
├─ State machine transitions
├─ Leader election
└─ Safety critical
```

### Deadlock & Prevention

```
DEADLOCK SCENARIO:

Transaction 1: Lock A, then Lock B
Transaction 2: Lock B, then Lock A

Timeline:
├─ T=0: Transaction 1 locks A
├─ T=1: Transaction 2 locks B
├─ T=2: Transaction 1 waits for B (held by Tx2)
├─ T=3: Transaction 2 waits for A (held by Tx1)
├─ T=4: Both waiting forever! DEADLOCK!

Prevention:

Strategy 1: Lock ordering
├─ Always lock in same order
├─ Example: Always lock A before B
│  ├─ Transaction 1: Lock A, then Lock B ✓
│  ├─ Transaction 2: Lock A (held), wait
│  ├─ When A released: Lock B ✓
│  └─ No deadlock!

Strategy 2: Timeout
├─ Every lock has timeout
├─ Tx1 waits for B (timeout 5s)
├─ If not acquired in 5s: Release A, fail
├─ Retry later (likely in different order)
└─ Prevents infinite waits

Strategy 3: Deadlock detection
├─ Graph cycle detection
├─ If cycle: Abort transaction
├─ Expensive (only for critical locks)
└─ Reactive (detect after deadlock)
```

### Lock Starvation

```
PROBLEM: Fair lock distribution

Many servers want one lock:
├─ Server 1, 2, 3, 4, 5...
├─ Lock busy
├─ New servers keep trying
├─ Early servers starve (never get lock)
└─ Unfair!

Solution: FIFO queue

Lock service maintains queue:

Queue:
├─ Server 1 (waiting)
├─ Server 2 (waiting)
├─ Server 3 (waiting)
├─ Server 4 (**HAS LOCK**)
└─ Server 5 (not in queue yet)

When lock released:
├─ Server 4: Releases
├─ Server 1: Gets lock (first in queue)
├─ Server 2, 3, 5: Continue waiting
└─ Fair! FIFO order
```

IMPLEMENTATION:

```python
class FairLock:
    def __init__(self):
        self.queue = []  # Waiting servers
        self.holder = None
    
    def acquire(self, server_id, timeout=10):
        # Add to queue
        queue_entry = {
            'server_id': server_id,
            'acquired_at': time.time()
        }
        self.queue.append(queue_entry)
        
        # Wait for our turn
        deadline = time.time() + timeout
        
        while True:
            # Are we first in queue?
            if self.queue and self.queue[0]['server_id'] == server_id:
                # Is lock free?
                if not self.holder:
                    self.holder = server_id
                    self.queue.pop(0)  # Remove from queue
                    return True
            
            # Timeout check
            if time.time() > deadline:
                self.queue.remove(queue_entry)  # Remove from queue
                return False
            
            # Wait a bit
            sleep(0.01)
    
    def release(self, server_id):
        if self.holder == server_id:
            self.holder = None
            # Next in queue will get lock
```
```
Benefits:
✓ Fair (FIFO)
✓ No starvation
✓ Predictable

Trade-off:
✗ Slower (must wait for turn)
✗ More complex
```

---

## 🐍 Python Code Example

### ❌ Without Distributed Locks (Unsafe)

```python
# ===== WITHOUT DISTRIBUTED LOCKS =====

from flask import Flask
import sqlite3

app = Flask(__name__)
db = sqlite3.connect('shared.db')

@app.route('/api/migrate', methods=['POST'])
def migrate():
    """Database migration - no lock"""
    
    cursor = db.cursor()
    
    # Check if migration needed
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    # Two servers might reach here simultaneously!
    if user_count > 0:
        # Add new column
        cursor.execute("ALTER TABLE users ADD COLUMN new_field TEXT")
        db.commit()
    
    return {'status': 'migrated'}

# Problems:
# ❌ Two servers run migration simultaneously
# ❌ Both try to add column
# ❌ Database corruption!
# ❌ "ERROR: column already exists"
# ❌ No way to prevent
```

### ✅ With Redis Locks

```python
# ===== WITH REDIS LOCKS =====

from flask import Flask
import redis
import uuid
import time

app = Flask(__name__)
redis_client = redis.Redis(host='localhost', port=6379)

class RedisLock:
    """Redis-based distributed lock"""
    
    def __init__(self, redis_client, key, timeout=10):
        self.redis = redis_client
        self.key = f"lock:{key}"
        self.timeout = timeout
        self.token = str(uuid.uuid4())
    
    def acquire(self, timeout_seconds=5):
        """Try to acquire lock"""
        
        deadline = time.time() + timeout_seconds
        
        while time.time() < deadline:
            # Try to set key (atomic)
            result = self.redis.set(
                self.key,
                self.token,
                nx=True,  # Only if not exists
                ex=self.timeout  # Expire in timeout
            )
            
            if result:
                return True  # Lock acquired!
            
            # Wait a bit, retry
            time.sleep(0.01)
        
        return False  # Timeout
    
    def release(self):
        """Release lock (atomic with Lua script)"""
        
        # Lua script: Only delete if token matches
        SCRIPT = """
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("DEL", KEYS[1])
        else
            return 0
        end
        """
        
        result = self.redis.eval(SCRIPT, 1, self.key, self.token)
        return bool(result)
    
    def __enter__(self):
        """Context manager entry"""
        if not self.acquire():
            raise TimeoutError(f"Could not acquire lock: {self.key}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()

@app.route('/api/migrate', methods=['POST'])
def migrate():
    """Database migration - with Redis lock"""
    
    lock = RedisLock(redis_client, 'db_migration')
    
    try:
        if not lock.acquire(timeout_seconds=30):
            return {'error': 'Could not acquire migration lock'}, 409
        
        # Safe to migrate
        cursor = db.cursor()
        cursor.execute("ALTER TABLE users ADD COLUMN new_field TEXT")
        db.commit()
        
        lock.release()
        
        return {'status': 'migrated'}
    
    except Exception as e:
        lock.release()
        return {'error': str(e)}, 500

# Benefits:
# ✅ Only one server migrates at a time
# ✅ Simple and fast
# ✅ Automatic expiration (crash recovery)
# ✅ Safe!
```

### ✅ Production: Consensus-Based Locks (etcd)

```python
# ===== PRODUCTION: ETCD CONSENSUS LOCKS =====

from flask import Flask
import etcd3
import uuid
import contextlib

app = Flask(__name__)
etcd = etcd3.client(host='localhost', port=2379)

class ConsensusLock:
    """Etcd-based consensus lock (safe)"""
    
    def __init__(self, etcd_client, key, timeout=10):
        self.etcd = etcd_client
        self.key = f"lock/{key}"
        self.timeout = timeout
        self.token = str(uuid.uuid4())
        self.lease = None
    
    def acquire(self, timeout_seconds=30):
        """Acquire lock with consensus"""
        
        # Create lease (auto-expire after timeout)
        self.lease = self.etcd.lease(self.timeout)
        
        try:
            # Try to create key (only if not exists)
            result = self.etcd.put(
                self.key,
                self.token,
                lease=self.lease,
                prev_kv=False
            )
            
            return True  # Lock acquired!
        
        except Exception:
            # Key already exists (locked by someone else)
            return False
    
    def release(self):
        """Release lock"""
        
        try:
            # Only delete if token matches
            tx = self.etcd.txn()
            tx.compare(self.key, '==', self.token)
            tx.success(self.etcd.delete(self.key))
            result = tx.commit()
            
            return result[0]  # True if deleted
        
        except:
            return False
    
    @contextlib.contextmanager
    def context(self):
        """Context manager"""
        
        if not self.acquire():
            raise TimeoutError(f"Could not acquire lock: {self.key}")
        
        try:
            yield self
        
        finally:
            self.release()

@app.route('/api/critical-section', methods=['POST'])
def critical_section():
    """Critical section with consensus lock"""
    
    lock = ConsensusLock(etcd, 'critical_operation')
    
    try:
        with lock.context():
            # Safe to run critical section
            # Lock is replicated across etcd cluster
            
            # Example: State machine transition
            state = get_state()
            
            if state == 'READY':
                set_state('PROCESSING')
                
                # Do work
                do_work()
                
                set_state('COMPLETE')
            
            return {'status': 'success'}
    
    except TimeoutError:
        return {'error': 'Lock timeout'}, 409

# Benefits:
# ✅ Crash-safe (replicated)
# ✅ Consensus guarantee
# ✅ No data loss
# ✅ Production-ready
# ✅ Works across regions
```

---

## 💡 Design Decisions

### Redis vs Etcd Locks

```
REDIS LOCKS:

Pros:
✓ Very fast (< 1ms)
✓ Simple to implement
✓ Good for most cases

Cons:
✗ Not crash-safe (single point)
✗ Clock skew issues
✗ Best-effort semantics

Use when:
├─ Performance critical
├─ Loss is acceptable
├─ Non-critical sections
└─ Cache invalidation


ETCD/ZOOKEEPER LOCKS:

Pros:
✓ Crash-safe (replicated)
✓ Consensus guarantees
✓ No clock dependencies

Cons:
✗ Slower (50-500ms)
✗ More complex
✗ Network sensitive

Use when:
├─ Safety critical
├─ State transitions
├─ Database migrations
└─ Leader election


CONDITIONAL WRITES (DynamoDB):

Pros:
✓ Part of database
✓ Atomic
✓ No separate lock service

Cons:
✗ Only works for DynamoDB
✗ Limited to application

Use when:
├─ Using DynamoDB already
├─ Application-level locking
```

---

## ❌ Common Mistakes

### Mistake 1: Forgetting Lock Release

```python
# ❌ No release on exception
def critical_section():
    lock.acquire()
    do_work()  # If exception, lock never released!
    lock.release()

# ✅ Use context manager
with lock.context():
    do_work()  # Exception: Lock still released!
```

### Mistake 2: Wrong Token Comparison

```python
# ❌ Just delete without checking
def release(self):
    redis.delete(self.key)  # What if someone else has lock?

# ✅ Check token before deleting
SCRIPT = """
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
end
"""
redis.eval(SCRIPT, 1, key, token)
```

### Mistake 3: Too Short Timeout

```python
# ❌ 1 second timeout
lock = RedisLock(redis, key, timeout=1)

# Work takes 2 seconds
do_work()  # Takes 2 seconds
# Lock expired after 1 second!
# Another server acquired lock!
# CORRUPTION!

# ✅ Long timeout + renew
lock = RedisLock(redis, key, timeout=30)

while doing_work:
    lock.renew(timeout=30)
    sleep(5)
```

---

## 📚 Additional Resources

**Distributed Locks:**
- [Redlock (Redis Locks)](https://redis.io/topics/distlock)
- [Is Redlock Safe? (Criticism)](http://martin.kleppmann.com/papers/redlock.pdf)

**Consensus Locks:**
- [etcd Concurrency](https://etcd.io/docs/v3.5/dev-guide/concurrency/introduction/)
- [Zookeeper Recipes](https://zookeeper.apache.org/doc/current/recipes.html)

**Implementation:**
- [Redis Locks](https://redis.io/commands/set)
- [etcd Locks](https://etcd.io/docs/v3.4/learning/why/#lock-service)


---

## 🎯 Before You Leave

**Can you answer these?**

1. **Why distributed locks needed?**
   - Answer: Prevent simultaneous access to shared resources

2. **Redis vs Etcd locks?**
   - Answer: Redis = fast, unsafe; Etcd = slow, safe

3. **Lock expiration (TTL)?**
   - Answer: Prevent deadlock if holder crashes

4. **Why token in lock?**
   - Answer: Ensure only holder can release their lock

5. **Lock contention problem?**
   - Answer: Only one server works, others wait (throughput = 1/N)

**If you got these right, you're ready for leader election!** ✅

---

## 🤣 Closing Thoughts

> **Developer:** "We need a distributed lock"
>
> **Senior Dev:** "Use Redis locks"
>
> **Developer:** "Is it safe?"
>
> **Senior Dev:** "Safe enough"
>
> **6 months later:** "Database corrupted"
>
> **Senior Dev:** "Should have used Etcd"
>
> **Developer:** "Why not start with that?"
>
> **Senior Dev:** "Because performance" 🔒💀

---

[← Back to Main](../README.md) | [Previous: Time & Ordering](62-time-ordering-distributed-systems.md) | [Next: Leader Election →](64-leader-election.md)

---

**Last Updated:** December 09, 2025  
**Difficulty:** ⭐⭐⭐⭐ Advanced (distributed systems)  
**Time to Read:** 32 minutes  
**Time to Implement:** 10-20 hours (depends on consistency requirements)  

---

*Distributed Locks: Preventing chaos when multiple servers want the same thing.* 🔒💫