# 61. Data Consistency Patterns (Sagas, Two-Phase Commit)

You have a distributed system. User transfers $100 from Account A to Account B. Debit Account A: Success. Network breaks. Account B never credited. User has $100 missing! Welcome to distributed transactions. You have two terrible options: 1) Two-Phase Commit (blocks everything), 2) Sagas (compensate if things fail). Either way, your system gets 100x more complex. Netflix abandoned 2PC in 2009. Now they use Sagas everywhere. Amazon switched to eventual consistency. Welcome to the dark side of scale! 🌪️💔

[← Back to Main](../README.md) | [Previous: Feature Flags](60-feature-flags.md) | [Next: Time & Ordering →](62-time-ordering.md)

---

## 🎯 Quick Summary

**Data Consistency Patterns** ensure correctness across distributed systems. **Two-Phase Commit (2PC)** locks all resources, guarantees atomicity but blocks on failures. **Sagas** orchestrate operations, compensate on failure, allow intermediate states. Netflix uses Sagas (async, resilient). Financial systems use 2PC (strong consistency required). Trade-off: 2PC = consistency but slow; Sagas = fast but complex. Challenge: distributed state, partial failures, idempotency, compensating transactions.

Think of it as: **Sagas = Distributed Transactions Without Locks**

---

## 🌟 Beginner Explanation

### The Distributed Transaction Problem

```
SINGLE DATABASE (Easy):

Transaction: Transfer $100 from Alice to Bob

BEGIN TRANSACTION
├─ UPDATE accounts SET balance = balance - 100 WHERE user_id = 1
├─ UPDATE accounts SET balance = balance + 100 WHERE user_id = 2
COMMIT

Result:
├─ Both updates succeed → COMMIT
├─ Or both fail → ROLLBACK
└─ Atomic! (all or nothing)


DISTRIBUTED SYSTEM (Hard):

Three services:
├─ Account Service (manages accounts)
├─ Transfer Service (orchestrates transfer)
└─ Notification Service (sends notifications)

Operation: Transfer $100 from Alice to Bob

1. Account Service: Debit Alice $100
   ├─ API call: POST /accounts/1/debit
   ├─ Result: Success
   └─ Balance: Alice = $900

2. Transfer Service: Record transfer
   ├─ API call: POST /transfers/new
   ├─ Result: Success
   └─ Transfer recorded

3. Account Service: Credit Bob $100
   ├─ API call: POST /accounts/2/credit
   ├─ Network error!
   ├─ Result: TIMEOUT
   └─ Balance: Bob = $400 (not credited!)

Problem:
├─ Alice debited: $900
├─ Bob not credited: $400
├─ $100 missing!
└─ No rollback mechanism!

Why not use database transaction?
├─ Account Service has its own database
├─ Transfer Service has its own database
├─ Notification Service has its own database
├─ No distributed transactions (different DB instances)
└─ ACID transactions only work within one DB
```

### Two-Phase Commit (2PC)

```
PHASE 1: PREPARE (Ask everyone to lock)

Coordinator asks all participants: "Can you commit?"

1. Account Service (prepare):
   ├─ Lock Alice's account
   ├─ Debit $100 (in transaction, not committed)
   ├─ Response: "YES, ready to commit"
   └─ Locked!

2. Transfer Service (prepare):
   ├─ Lock transfer record
   ├─ Record transfer
   ├─ Response: "YES, ready to commit"
   └─ Locked!

3. Account Service (prepare):
   ├─ Lock Bob's account
   ├─ Credit $100 (in transaction, not committed)
   ├─ Response: "YES, ready to commit"
   └─ Locked!

If any says "NO":
├─ Coordinator: ABORT
├─ All rollback locked changes
└─ Transaction fails


PHASE 2: COMMIT (Make it official)

If all say "YES":
├─ Coordinator sends: COMMIT
├─ Alice's debit: Committed (locked release)
├─ Transfer recorded: Committed
├─ Bob's credit: Committed
└─ All locks released!

Result:
├─ Alice: $900
├─ Bob: $500
├─ Transfer: Recorded
└─ Atomic! No partial failures


PROBLEMS WITH 2PC:

Blocking (Resources locked):
├─ Phase 1: Accounts locked
├─ If coordinator dies during phase 2: Still locked!
├─ Participants wait: Indefinitely!
├─ Throughput: Drops 10-100x
├─ Scalability: Very bad

Network partitions:
├─ Participant A: Says YES
├─ Network breaks
├─ Coordinator: Times out
├─ Aborts transaction
├─ Participant A: Still has locked resources
├─ Deadlock!

Complexity:
├─ Recovery logic: Complex
├─ Timeout handling: Tricky
├─ Failure scenarios: Many
└─ Production bugs: Common

When to use 2PC:
├─ Banking (strong consistency required)
├─ Financial transactions (regulatory)
├─ Small scale (< 1000 TPS)
└─ Same datacenter (fast network)

When NOT to use 2PC:
├─ Distributed systems at scale
├─ High latency networks
├─ High availability required
├─ Global scale (regions)
└─ Netflix, Amazon, Google: Don't use 2PC
```

### Sagas (Distributed Transactions)

```
SAGA PATTERN:

Long-running transaction split into local transactions.

Operation: Transfer $100 from Alice to Bob

Step 1: Debit Alice
├─ Account Service: Debit $100
├─ Success: Balance = $900
└─ No locks (committed immediately)

Step 2: Record Transfer
├─ Transfer Service: Record transfer
├─ Success: Transfer recorded
└─ No locks

Step 3: Credit Bob
├─ Account Service: Credit $100
├─ Success: Balance = $500
└─ No locks


If Step 3 fails:
├─ Error detected
├─ Compensation logic triggered
├─ Step 2 compensation: Mark transfer as failed
├─ Step 1 compensation: Credit Alice $100 (reverse debit)
├─ Result: Alice = $1000, Bob = $400, Transfer = failed


SAGA ORCHESTRATION:

Choreography vs Orchestration

CHOREOGRAPHY (Decentralized):
┌────────────────────────────────────┐
│ Event Bus (Kafka/RabbitMQ)          │
│                                    │
│ Event: "TransferRequested"         │
└────┬──────────────────────────────┘
     │
     ├─ Account Service subscribes:
     │  ├─ Debits Alice
     │  ├─ Publishes: "AliceDebited"
     │  └─ Or "AliceDebitFailed"
     │
     ├─ Transfer Service subscribes:
     │  ├─ Receives "AliceDebited"
     │  ├─ Records transfer
     │  ├─ Publishes: "TransferRecorded"
     │  └─ Or "TransferRecordFailed"
     │
     └─ Account Service subscribes:
        ├─ Receives "TransferRecorded"
        ├─ Credits Bob
        ├─ Publishes: "BobCredited"
        └─ Or "BobCreditFailed" (triggers compensations)

Flow:
TransferRequested → AliceDebited → TransferRecorded → BobCredited → Success
                 → AliceDebitFailed → Compensation (abort)


ORCHESTRATION (Centralized):

┌──────────────────────────────┐
│ Saga Orchestrator             │
├──────────────────────────────┤
│ Manages saga steps:           │
│ 1. Call Account Service       │
│ 2. Call Transfer Service      │
│ 3. Call Account Service       │
└──────────┬───────────────────┘
           │
     ┌─────┴──────┬────────┐
     │            │        │
Account Service  Transfer  Account Service
(debit)         Service   (credit)

Flow:
1. Orchestrator: "Debit Alice $100"
   ├─ Account Service: Success
   └─ Orchestrator: Continue

2. Orchestrator: "Record transfer"
   ├─ Transfer Service: Success
   └─ Orchestrator: Continue

3. Orchestrator: "Credit Bob $100"
   ├─ Account Service: Network error!
   └─ Orchestrator: Trigger compensations!

Compensation order (reverse):
├─ Step 2: Undo "Record transfer"
├─ Step 1: Undo "Debit Alice"
└─ Result: Consistent state


COMPARISON:

                  Choreography  Orchestration
Coupling:         Loose         Tight
Visibility:       Hard          Easy
Debugging:        Hard          Easy
Testing:          Hard          Easy
Scalability:      Good          OK
Typical use:      Large systems Moderate scale
```

### Idempotency & Deduplication

```
PROBLEM: Duplicate requests

Request: Transfer $100 from Alice to Bob

Scenario:
1. Request arrives
2. Debit Alice: $900
3. Network timeout (response lost)
4. Client: "Did it work?"
5. Retries same request
6. Debit Alice AGAIN: $800 (double charged!)

Solution: IDEMPOTENCY KEY

Add unique ID to request:
POST /transfer
{
  "from": "alice",
  "to": "bob",
  "amount": 100,
  "idempotency_key": "req_12345"  ← Unique!
}

Server logic:
├─ Check: Is idempotency_key already processed?
├─ Yes: Return cached result (don't reprocess)
├─ No: Process request, store result with key
└─ Result: Duplicate requests safe

Storage:
┌─────────────────────────────────────┐
│ idempotency_results table           │
├──────────────┬──────────┬───────────┤
│ key          │ result   │ timestamp │
├──────────────┼──────────┼───────────┤
│ req_12345    │ success  │ 2025-12-09│
│ req_12346    │ error    │ 2025-12-09│
└──────────────┴──────────┴───────────┘

Implementation:
def transfer(request):
    key = request.idempotency_key
    
    # Check cache first
    if key in idempotency_cache:
        return idempotency_cache[key]
    
    # Process transfer
    result = debit_alice(request.amount)
    
    # Store result
    idempotency_cache[key] = result
    
    return result

Benefits:
✅ Retries safe
✅ Duplicates detected
✅ Exactly-once semantics (on client side)
✅ No double charging
```

---

## 🔬 Advanced Concepts

### Saga States & Compensation

```
SAGA STATE MACHINE:

State: STARTED
├─ Step 1: Debit Alice
└─ Transition: → DEBIT_ALICE

State: DEBIT_ALICE
├─ Result: Success
└─ Transition: → TRANSFER_RECORD

State: DEBIT_ALICE (Failed)
├─ Error: Network timeout
└─ Transition: → DEBIT_ALICE_COMPENSATED

State: TRANSFER_RECORD
├─ Step 2: Record transfer
└─ Transition: → CREDIT_BOB

State: CREDIT_BOB
├─ Step 3: Credit Bob
├─ Result: FAILED
└─ Transition: → COMPENSATE

State: COMPENSATE
├─ Undo Step 2: Unrecord transfer
├─ Undo Step 1: Credit Alice $100
└─ Transition: → FAILED


COMPENSATION:

Reversing operations:

Debit $100 → Compensate: Credit $100
├─ Not a simple rollback
├─ New transaction (different service)
├─ Must be idempotent (retryable)

Record transfer → Compensate: Mark as failed
├─ Record new state
├─ Don't delete (audit trail!)
└─ Update: status = "failed"

Real-world example: Flight booking saga

1. Reserve flight
   ├─ Compensation: Cancel flight reservation
2. Reserve hotel
   ├─ Compensation: Cancel hotel reservation
3. Reserve rental car
   ├─ Compensation: Cancel car reservation

If step 3 fails (no cars available):
├─ Compensation step 2: Cancel hotel
├─ Compensation step 1: Cancel flight
└─ Result: User tries different dates
```

### Eventual Consistency

```
SAGA: EVENTUALLY CONSISTENT

Intermediate states:

After Step 1:
├─ Alice balance: $900 (debited)
├─ Bob balance: $400 (not yet credited)
├─ Transfer status: "in progress"
└─ Inconsistent! (but temporarily)

After Step 3:
├─ Alice balance: $900
├─ Bob balance: $500
├─ Transfer status: "complete"
└─ Consistent!

Clients must handle:
├─ Pending transfers (in progress)
├─ Failed transfers (compensated)
├─ Completed transfers
└─ Don't assume immediate consistency

Query during saga:
├─ Bob checks balance: $400 (transfer pending)
├─ Email: "You're receiving $100"
├─ Real balance: Still $400
├─ A few seconds later: $500
└─ Must communicate transient state


STRONG vs EVENTUAL CONSISTENCY:

STRONG (2PC):
├─ After operation: Immediately consistent
├─ Alice = $900, Bob = $500
├─ No intermediate states
├─ Cost: Blocking, slow, complex

EVENTUAL (Sagas):
├─ After operation: Eventually consistent
├─ Seconds delay before consistency
├─ Intermediate states visible
├─ Benefit: Fast, non-blocking, distributed

Decision:
├─ Money (balance)? Eventual OK (accounts show pending)
├─ Inventory? Eventual OK (show 0 available during saga)
├─ User seeing data? Eventual OK (refresh shows eventual state)
└─ Most systems: Eventual is fine!
```

---

## 🐍 Python Code Example

### ❌ Without Saga (Risky)

```python
# ===== WITHOUT SAGA =====

from flask import Flask
import requests

app = Flask(__name__)

@app.route('/api/transfer', methods=['POST'])
def transfer():
    """Transfer money - no saga"""
    
    data = request.json
    from_user = data['from_user']
    to_user = data['to_user']
    amount = data['amount']
    
    # Step 1: Debit sender
    response1 = requests.post(
        'http://account-service/debit',
        json={'user_id': from_user, 'amount': amount}
    )
    
    if response1.status_code != 200:
        return {'error': 'Debit failed'}, 400
    
    # Step 2: Record transfer
    response2 = requests.post(
        'http://transfer-service/record',
        json={'from': from_user, 'to': to_user, 'amount': amount}
    )
    
    if response2.status_code != 200:
        # PROBLEM: Alice already debited!
        # Bob never credited!
        # No way to fix!
        return {'error': 'Transfer recording failed'}, 400
    
    # Step 3: Credit receiver
    response3 = requests.post(
        'http://account-service/credit',
        json={'user_id': to_user, 'amount': amount}
    )
    
    if response3.status_code != 200:
        # PROBLEM: Transfer recorded!
        # Alice already debited!
        # Bob not credited!
        # Inconsistent state!
        return {'error': 'Credit failed'}, 400
    
    return {'status': 'success'}

# Problems:
# ❌ Partial failures: Inconsistent state
# ❌ No compensation: Can't undo
# ❌ Manual recovery: Data cleanup required
# ❌ No transaction semantics
```

### ✅ With Saga (Orchestration Pattern)

```python
# ===== WITH SAGA (ORCHESTRATION) =====

from flask import Flask, request, jsonify
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import uuid
import requests

app = Flask(__name__)

class SagaStep(Enum):
    """Saga steps"""
    DEBIT_ALICE = "debit_alice"
    RECORD_TRANSFER = "record_transfer"
    CREDIT_BOB = "credit_bob"
    COMPENSATE = "compensate"

@dataclass
class SagaExecution:
    """Track saga execution"""
    saga_id: str
    current_step: SagaStep
    status: str  # "in_progress", "completed", "failed", "compensating"
    data: dict
    created_at: datetime

class SagaOrchestrator:
    """Orchestrate saga execution"""
    
    def __init__(self, db):
        self.db = db
        self.executions = {}  # In-memory (use database in production)
    
    def start_saga(self, from_user, to_user, amount):
        """Start transfer saga"""
        
        saga_id = str(uuid.uuid4())
        
        execution = SagaExecution(
            saga_id=saga_id,
            current_step=SagaStep.DEBIT_ALICE,
            status='in_progress',
            data={
                'from_user': from_user,
                'to_user': to_user,
                'amount': amount,
                'idempotency_key': str(uuid.uuid4())
            },
            created_at=datetime.utcnow()
        )
        
        self.executions[saga_id] = execution
        
        # Start execution
        self._execute_step(saga_id)
        
        return saga_id
    
    def _execute_step(self, saga_id):
        """Execute current step"""
        
        execution = self.executions[saga_id]
        data = execution.data
        
        try:
            if execution.current_step == SagaStep.DEBIT_ALICE:
                self._debit_alice(saga_id, data)
            
            elif execution.current_step == SagaStep.RECORD_TRANSFER:
                self._record_transfer(saga_id, data)
            
            elif execution.current_step == SagaStep.CREDIT_BOB:
                self._credit_bob(saga_id, data)
            
            elif execution.current_step == SagaStep.COMPENSATE:
                self._compensate(saga_id, data)
        
        except Exception as e:
            # Error: Trigger compensation
            execution.status = 'compensating'
            execution.current_step = SagaStep.COMPENSATE
            self._execute_step(saga_id)
    
    def _debit_alice(self, saga_id, data):
        """Step 1: Debit Alice"""
        
        execution = self.executions[saga_id]
        
        response = requests.post(
            'http://account-service/debit',
            json={
                'user_id': data['from_user'],
                'amount': data['amount'],
                'idempotency_key': data['idempotency_key'] + '_debit'
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Debit failed: {response.text}")
        
        # Success: Move to next step
        execution.current_step = SagaStep.RECORD_TRANSFER
        self._execute_step(saga_id)
    
    def _record_transfer(self, saga_id, data):
        """Step 2: Record transfer"""
        
        execution = self.executions[saga_id]
        
        response = requests.post(
            'http://transfer-service/record',
            json={
                'from': data['from_user'],
                'to': data['to_user'],
                'amount': data['amount'],
                'saga_id': saga_id,
                'idempotency_key': data['idempotency_key'] + '_record'
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Record failed: {response.text}")
        
        # Success: Move to next step
        execution.current_step = SagaStep.CREDIT_BOB
        self._execute_step(saga_id)
    
    def _credit_bob(self, saga_id, data):
        """Step 3: Credit Bob"""
        
        execution = self.executions[saga_id]
        
        response = requests.post(
            'http://account-service/credit',
            json={
                'user_id': data['to_user'],
                'amount': data['amount'],
                'idempotency_key': data['idempotency_key'] + '_credit'
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Credit failed: {response.text}")
        
        # Success: Saga complete
        execution.status = 'completed'
    
    def _compensate(self, saga_id, data):
        """Compensation: Undo all steps"""
        
        execution = self.executions[saga_id]
        
        # Reverse order: 3 → 2 → 1
        
        # Undo step 3: Credit Bob
        try:
            requests.post(
                'http://account-service/debit',  # Undo credit with debit
                json={
                    'user_id': data['to_user'],
                    'amount': data['amount'],
                    'idempotency_key': data['idempotency_key'] + '_undo_credit'
                }
            )
        except:
            pass  # Log error, retry later
        
        # Undo step 2: Record transfer
        try:
            requests.post(
                'http://transfer-service/mark-failed',
                json={
                    'saga_id': saga_id,
                    'idempotency_key': data['idempotency_key'] + '_mark_failed'
                }
            )
        except:
            pass
        
        # Undo step 1: Debit Alice
        try:
            requests.post(
                'http://account-service/credit',  # Undo debit with credit
                json={
                    'user_id': data['from_user'],
                    'amount': data['amount'],
                    'idempotency_key': data['idempotency_key'] + '_undo_debit'
                }
            )
        except:
            pass
        
        execution.status = 'failed'

# Initialize
orchestrator = SagaOrchestrator(db)

@app.route('/api/transfer', methods=['POST'])
def transfer():
    """Transfer with saga"""
    
    data = request.json
    saga_id = orchestrator.start_saga(
        data['from_user'],
        data['to_user'],
        data['amount']
    )
    
    return {
        'saga_id': saga_id,
        'status': 'in_progress'
    }

@app.route('/api/transfer/<saga_id>')
def get_transfer_status(saga_id):
    """Get saga status"""
    
    execution = orchestrator.executions.get(saga_id)
    
    if not execution:
        return {'error': 'Saga not found'}, 404
    
    return {
        'saga_id': saga_id,
        'status': execution.status,
        'current_step': execution.current_step.value
    }

# Benefits:
# ✅ Saga orchestration
# ✅ Automatic compensation
# ✅ Idempotency keys (retryable)
# ✅ State tracking
# ✅ Eventual consistency
# ✅ No distributed locks
```

---

## 💡 Design Decisions

### 2PC vs Sagas

```
USE 2PC IF:

✅ Financial transactions (banking)
✅ Strong consistency required
✅ Small scale (< 100 TPS)
✅ Same datacenter (fast, low latency)
✅ ACID guarantees critical

Limitations:
❌ Scales poorly (blocking)
❌ Network sensitive (timeouts)
❌ High operational complexity


USE SAGAS IF:

✅ Distributed systems at scale
✅ High latency networks (cross-region)
✅ High availability needed
✅ Non-financial transactions
✅ Eventual consistency acceptable

Trade-offs:
❌ More complex (compensation logic)
❌ Intermediate states visible
❌ Eventual consistency only


RECOMMENDATION:

For most systems: Sagas
├─ Netflix: Pure Sagas
├─ Uber: Sagas
├─ Airbnb: Sagas
└─ Amazon: Sagas

2PC only for:
├─ Banking
├─ Regulated industries
├─ Single datacenter
└─ Strong consistency critical
```

### Choreography vs Orchestration

```
CHOREOGRAPHY:

Services emit events, others react

Pros:
✅ Decoupled
✅ Scalable
✅ No single point of failure

Cons:
❌ Hard to debug (implicit flow)
❌ Hard to test (many interactions)
❌ Hard to understand (order unclear)

Best for: Large, evolving systems


ORCHESTRATION:

Central orchestrator coordinates

Pros:
✅ Clear flow
✅ Easy to debug
✅ Easy to test

Cons:
❌ Coupled to orchestrator
❌ Orchestrator is bottleneck
❌ Single point of failure

Best for: Moderate complexity, clear flows


RECOMMENDATION:

Start with orchestration:
├─ Easier to understand
├─ Easier to debug
├─ Easier to test

Graduate to choreography:
├─ As system grows
├─ Multiple sagas interact
├─ Decoupling becomes critical
```

---

## ❌ Common Mistakes

### Mistake 1: Forgetting Idempotency

```python
# ❌ No idempotency
def transfer(from_user, to_user, amount):
    debit(from_user, amount)
    credit(to_user, amount)

# Request retried (network error):
# Debit twice! Balance wrong!

# ✅ With idempotency
def transfer(from_user, to_user, amount, idempotency_key):
    # Check: Already processed?
    if idempotency_key in processed_keys:
        return cached_result
    
    debit(from_user, amount)
    credit(to_user, amount)
    
    processed_keys[idempotency_key] = result
    return result

# Retry: Uses cached result, no double charge
```

### Mistake 2: Compensation Not Idempotent

```python
# ❌ Compensation fails on retry
def compensate_debit(user_id, amount):
    credit(user_id, amount)  # What if already credited?

# Retry compensation:
# Credit twice! Balance wrong!

# ✅ Idempotent compensation
def compensate_debit(user_id, amount, compensation_key):
    if compensation_key in compensated:
        return  # Already done
    
    credit(user_id, amount)
    compensated.add(compensation_key)

# Retry: Safe (already done check)
```

### Mistake 3: Long-Running Sagas

```python
# ❌ Saga runs for 24 hours
# Step 1: Book flight
# Step 2: Book hotel (8 hours later)
# Step 3: Book rental (24 hours later)
# Problem: Resources locked for 24 hours!

# ✅ Break into smaller sagas
# Saga 1: Book flight (5 min)
# Event: Flight booked
# Saga 2: Book hotel (5 min)
# Event: Hotel booked
# Saga 3: Book rental (5 min)
# Result: Short sagas, resources unlocked
```

---

## 📚 Additional Resources

**Sagas:**
- [Saga Pattern - Chris Richardson](https://microservices.io/patterns/data/saga.html)
- [Saga Orchestration vs Choreography](https://www.enterpriseintegrationpatterns.com/)

**2PC:**
- [Two-Phase Commit Protocol](https://en.wikipedia.org/wiki/Two-phase_commit_protocol)
- [Why 2PC is Bad](https://www.cockroachlabs.com/blog/distributed-transactions/)

**Implementation:**
- [Temporal (Workflow Orchestration)](https://temporal.io/)
- [Axon Saga Support](https://axoniq.io/)
- [Apache Camel (integration)](https://camel.apache.org/)

---


## 🎯 Before You Leave

**Can you answer these?**

1. **Why 2PC doesn't scale?**
   - Answer: Blocks resources, network sensitive, complex recovery

2. **Saga vs 2PC?**
   - Answer: Saga = no locks, eventual consistency; 2PC = locks, strong consistency

3. **Orchestration vs choreography?**
   - Answer: Orchestration = centralized, easier debug; Choreography = decoupled, harder debug

4. **Why idempotency key?**
   - Answer: Retries safe, prevents double charging

5. **Compensation logic?**
   - Answer: Undo steps in reverse order if saga fails

**If you got these right, you're ready for distributed ordering!** ✅

---

## 🤣 Closing Thoughts

> **Developer:** "We need distributed transactions"
>
> **Architect:** "2PC or Sagas?"
>
> **Developer:** "2PC sounds simpler"
>
> **Architect:** "Try it at scale"
>
> **6 months later:** "Everything is deadlocked"
>
> **Developer:** "Let's use Sagas"
>
> **Architect:** "Now implement compensation logic"
>
> **Developer:** "How many states?" 💀

---

[← Back to Main](../README.md) | [Previous: Feature Flags](60-feature-flags.md) | [Next: Time & Ordering →](62-time-ordering.md)

---

**Last Updated:** December 09, 2025  
**Difficulty:** ⭐⭐⭐⭐ Advanced (distributed systems)  
**Time to Read:** 35 minutes  
**Time to Implement:** 40-100 hours (depends on services)  

---

*Data Consistency Patterns: Choosing between blocking everything or managing chaos.* 💔🌪️