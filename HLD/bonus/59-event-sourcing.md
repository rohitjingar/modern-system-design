# 59. Event Sourcing

You store the current state of your database. A user updates something, you overwrite it. Then a bug writes bad data. You have no way to recover. With Event Sourcing, every change is an event. You store EVERYTHING that happened. Bug writes bad data? Replay events to before the bug. Want to know what was happening at 3 AM Tuesday? Replay events! Audit trail built in. Historical analysis trivial. The only downside? You're now storing 100x more data. But at least you know WHY it got there! 📜✨

[← Back to Main](../README.md) | [Previous: Multi-Region Architecture](58-multi-region-architecture.md) | [Next: Feature Flags & Config Management →](60-feature-flags.md)

---

## 🎯 Quick Summary

**Event Sourcing** stores immutable events instead of current state. Every change = event. Current state = replay all events. Benefits: perfect audit trail, time-travel debugging, easy event-driven architecture. Challenges: eventual consistency, storage (massive), event versioning, query complexity. Netflix uses events for personalization. Amazon uses event logs internally. Financial systems use for regulations. Trade-off: query speed for audit completeness.

Think of it as: **Event Sourcing = Append-Only History, State = Derived**

---

## 🌟 Beginner Explanation

### Traditional State vs Event Sourcing

```
TRADITIONAL STATE STORAGE:

Database table: users

┌────┬──────────┬─────────────────────┬──────────────┐
│ id │ name     │ email               │ balance      │
├────┼──────────┼─────────────────────┼──────────────┤
│ 1  │ Alice    │ alice@example.com   │ 1000         │
│ 2  │ Bob      │ bob@example.com     │ 500          │
└────┴──────────┴─────────────────────┴──────────────┘

Timeline:
├─ T=0: Alice created, balance=1000
├─ T=1: Alice transfers $100 to Bob
│  └─ Update: Alice.balance = 900, Bob.balance = 600
├─ T=2: Bug: Sets all balances to 0
│  └─ Update: Alice.balance = 0, Bob.balance = 0
└─ T=3: Now: Alice.balance = 0, Bob.balance = 0
         LOST: $1600 of user money!

Problems:
❌ No history (what was balance before?)
❌ No audit trail (who changed it?)
❌ No recovery (can't undo bug)
❌ No "why" (what was the business reason?)


EVENT SOURCING:

Database table: events (immutable, append-only)

┌───────┬────────────────────────────────────────┬──────────────┐
│ id    │ event_type                             │ data         │
├───────┼────────────────────────────────────────┼──────────────┤
│ 1     │ user_created                           │ {name: Alice}│
│ 2     │ account_balance_updated                │ {user: 1,... │
│ 3     │ money_transferred                      │ {from: 1,... │
│ 4     │ account_balance_updated                │ {user: 2,... │
│ 5     │ balance_erased_by_bug                  │ {all: 0}     │
│ 6     │ data_correction_applied                │ {revert:...} │
└───────┴────────────────────────────────────────┴──────────────┘

Timeline:
├─ Event 1: UserCreated(id=1, name="Alice")
├─ Event 2: BalanceUpdated(user=1, amount=1000)
├─ Event 3: MoneyTransferred(from=1, to=2, amount=100)
├─ Event 4: BalanceUpdated(user=2, amount=600)
├─ Event 5: BalanceErasedByBug(all=0) ← Bug!
├─ Event 6: DataCorrectionApplied(revert_events=[5])
└─ Current state: Replay events 1-6, skip 5
   Result: Alice=900, Bob=600

Benefits:
✅ Complete history (every event stored)
✅ Audit trail (who, what, when)
✅ Time-travel debugging (replay to any point)
✅ Recovery (exclude bad events)
✅ "Why" captured (business context in events)
✅ Immutable record (compliance requirement)
```

### Event Model

```
EVENT STRUCTURE:

{
  "event_id": "evt_12345",        // Unique ID
  "event_type": "MoneyTransferred", // What happened
  "aggregate_id": "user_1",         // What changed (user_1)
  "aggregate_type": "User",         // Type
  "version": 5,                     // User version after this event
  "timestamp": "2025-12-09T08:00:00Z",  // When
  "user_id": "admin_42",            // Who
  "data": {                         // What changed
    "from": "user_1",
    "to": "user_2",
    "amount": 100,
    "reason": "birthday gift"
  },
  "metadata": {
    "source": "mobile-app",
    "ip_address": "192.168.1.1",
    "correlation_id": "corr_xyz"
  }
}

Event types:
├─ Domain events: Business meaning (UserSignedUp, OrderPlaced)
├─ System events: Technical (DatabackupCompleted)
├─ Integration events: External (PaymentReceived)
└─ Policy events: Audit (DataAccessRequested)
```

### State Reconstruction (Projections)

```
SNAPSHOT: Replay all events to get current state

Events:
┌─────┬───────────────────────────────┐
│ ID  │ Event                         │
├─────┼───────────────────────────────┤
│ 1   │ UserCreated(id=1, name=Alice) │
│ 2   │ BalanceSet(1000)              │
│ 3   │ TransferOut(to=2, amt=100)    │
│ 4   │ TransferIn(from=1, amt=50)    │
│ 5   │ NameChanged(Alice → Alicia)   │
└─────┴───────────────────────────────┘

Projection: Replay to get current state

Start: state = {}

Event 1: state = {id: 1, name: "Alice"}
Event 2: state = {id: 1, name: "Alice", balance: 1000}
Event 3: state = {id: 1, name: "Alice", balance: 900}
Event 4: state = {id: 1, name: "Alice", balance: 950}
Event 5: state = {id: 1, name: "Alicia", balance: 950}

Result: Current state = {id: 1, name: "Alicia", balance: 950}


PROBLEM: Replaying all events is slow!

User with 100,000 events:
├─ Replay all: 100,000 replays = slow
├─ Query: Takes seconds
└─ Unacceptable for production

SOLUTION: Snapshots

Snapshots: Periodic state snapshots

Timeline:
├─ Events 1-100: Happen
├─ Snapshot: Save state at event 100
├─ Events 101-200: Happen
├─ Snapshot: Save state at event 200
├─ Events 201-300: Happen
├─ Query at event 300:
│  ├─ Load snapshot at event 200 (state)
│  ├─ Replay events 201-300 (100 events)
│  └─ Result: Current state
└─ Time: Much faster! (1000x improvement)


EXAMPLE: Account state

Event log:
┌─────┬────────────────────────────┬───────────┐
│ ID  │ Event                      │ Balance   │
├─────┼────────────────────────────┼───────────┤
│ 1   │ AccountOpened              │ 0         │
│ 2   │ DepositReceived(1000)      │ 1000      │
│ 3   │ WithdrawalMade(100)        │ 900       │
│ ...─┼─ (1000 more events)        │ ...       │
│ 1005│ DepositReceived(500)       │ ??        │
│ 1006│ WithdrawalMade(50)         │ ??        │
└─────┴────────────────────────────┴───────────┘

Without snapshot:
├─ Replay all 1006 events: ~10 seconds
├─ User query: Times out!
└─ Production problem

With snapshot at event 1000:
├─ Load snapshot: Balance = 98,500 (state at event 1000)
├─ Replay events 1001-1006: 6 events
├─ Final balance: 98,500 + 500 - 50 = 98,950
├─ Time: < 100ms
└─ Production ready!
```

### Event Versioning

```
PROBLEM: Event structure changes over time

Original event (2020):
{
  "event_type": "TransferMoney",
  "user_id": 1,
  "amount": 100
}

New requirement (2023): Add reason field
{
  "event_type": "TransferMoney",
  "user_id": 1,
  "amount": 100,
  "reason": "salary"  ← NEW field!
}

Problem: Old events don't have "reason"!

When replaying old events:
├─ Event has no "reason" field
├─ Code expects "reason"
├─ Crash or error!
└─ Can't replay history!


SOLUTION 1: Upcasting (transformation)

Define upgrade rules:
{
  "event_type": "TransferMoney",
  "version": 1,
  "fields": ["user_id", "amount"]
}
→ Upcast to version 2
→ Add "reason" = null (default)

When loading old events:
├─ Check version: version 1
├─ Apply upcast rules
├─ Add reason: null
├─ Now matches current schema
└─ Replay works!


SOLUTION 2: Event versioning field

Event with version:
{
  "event_type": "TransferMoney",
  "event_version": 1,  ← Track version
  "user_id": 1,
  "amount": 100
}

Code checks version:
if event_version == 1:
    event['reason'] = null
elif event_version == 2:
    event['reason'] = event['reason']

Works with both old and new formats!


SOLUTION 3: Separate event types

Don't change existing events, create new types:

Old: TransferMoney (no reason)
New: TransferMoneyWithReason (has reason)

When replaying:
├─ Old events: TransferMoney (no reason)
├─ New events: TransferMoneyWithReason (has reason)
├─ Both handled
└─ No breaking changes!

Trade-off: More event types, but cleaner
```

---

## 🔬 Advanced Concepts

### CQRS (Command Query Responsibility Segregation)

```
TRADITIONAL:

One model for everything
├─ Write: Update database
├─ Read: Query database
└─ Same schema for both

Problem:
├─ Write-optimized ≠ read-optimized
├─ Complex queries slow down writers
├─ Hard to scale independently
└─ Coupling between read and write


EVENT SOURCING + CQRS:

Write side (Command):
├─ Receive: Command (UpdateUserName)
├─ Apply: Business logic
├─ Generate: Event (UserNameUpdated)
├─ Store: Event in event log
└─ Result: Event log (source of truth)

Read side (Query):
├─ Subscribe: To events
├─ Maintain: Projections (materialized views)
├─ Query: Projections (fast!)
└─ Result: Denormalized read model

Architecture:

Command → Event Log → Event Bus → Projections → Queries
                                     ↓
                              (Multiple read models)

Projection 1 (by user):
{
  "user_1": {name: "Alice", balance: 900}
}

Projection 2 (by time):
{
  "2025-12-09": [event1, event2, event3]
}

Projection 3 (by status):
{
  "active": [user_1, user_3, user_5],
  "inactive": [user_2, user_4]
}

Benefits:
✅ Independent scaling (read scale ≠ write scale)
✅ Optimized queries (denormalized)
✅ Real-time updates (event bus)
✅ Multiple views (different projections)


EVENTUAL CONSISTENCY:

Write (synchronous):
├─ Command received
├─ Event generated
├─ Event stored
└─ ✓ Confirmed immediately

Read (asynchronous):
├─ Projections updated by event bus
├─ Takes milliseconds to seconds
├─ Query returns eventually consistent data
└─ ⚠ Briefly stale after write

Trade-off:
├─ Write: Fast & strongly consistent
├─ Read: Fast & eventually consistent
└─ Acceptable for most use cases
```

### Event Store Architecture

```
EVENT STORE:

Immutable log of events:

Database: PostgreSQL (with JSONB events)
Table: events
┌────────────────┬──────────────┬────────┬────────────┐
│ event_id       │ aggregate_id │ type   │ data       │
├────────────────┼──────────────┼────────┼────────────┤
│ evt_1          │ user_1       │ Created│ {name: ...}│
│ evt_2          │ user_1       │ Updated│ {balance..}│
│ evt_3          │ user_2       │ Created│ {name: ...}│
└────────────────┴──────────────┴────────┴────────────┘

Table: snapshots
┌────────────────┬──────────────┬──────┬────────┐
│ snapshot_id    │ aggregate_id │ ver  │ state  │
├────────────────┼──────────────┼──────┼────────┤
│ snap_1         │ user_1       │ 100  │ {...}  │
│ snap_2         │ user_2       │ 50   │ {...}  │
└────────────────┴──────────────┴──────┴────────┘

Indexes:
├─ aggregate_id (find all events for user)
├─ event_type (find all transfers)
├─ timestamp (range queries)
└─ version (replaying from point)


DEDICATED EVENT STORE PRODUCTS:

EventStoreDB:
├─ Specialized for events
├─ Built-in snapshots
├─ Projections support
├─ High throughput
└─ ~100k events/sec

Apache Kafka:
├─ Event streaming
├─ Distributed log
├─ Consumer groups
├─ Replay support
└─ ~1M messages/sec


CHOICE DEPENDS ON:

Use PostgreSQL if:
├─ Volumes: < 10k events/sec
├─ Strong consistency needed
├─ Existing PostgreSQL infrastructure
└─ Cost sensitive

Use Kafka if:
├─ Volumes: > 100k events/sec
├─ Event streaming required
├─ Multiple consumers
├─ Built for scale

Use EventStoreDB if:
├─ Event sourcing critical
├─ Projections important
├─ Snapshots needed
└─ Budget allows
```

---

## 🐍 Python Code Example

### ❌ Without Event Sourcing (State Only)

```python
# ===== WITHOUT EVENT SOURCING =====

from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)
db = psycopg2.connect(...)

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create user - state only"""
    
    data = request.json
    
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO users (name, balance)
        VALUES (%s, %s)
        RETURNING id
    """, (data['name'], 0))
    
    user_id = cursor.fetchone()[0]
    db.commit()
    
    return {'user_id': user_id}

@app.route('/api/users/<int:user_id>/transfer', methods=['POST'])
def transfer_money(user_id):
    """Transfer money - state only"""
    
    data = request.json
    to_user_id = data['to_user_id']
    amount = data['amount']
    
    cursor = db.cursor()
    
    # Debit from_user
    cursor.execute(
        "UPDATE users SET balance = balance - %s WHERE id = %s",
        (amount, user_id)
    )
    
    # Credit to_user
    cursor.execute(
        "UPDATE users SET balance = balance + %s WHERE id = %s",
        (amount, to_user_id)
    )
    
    db.commit()
    
    return {'status': 'success'}

# Problems:
# ❌ No history (why did balance change?)
# ❌ No audit trail (who changed it?)
# ❌ No recovery (if bug, lost data)
# ❌ Time-travel impossible (what was state at T=0?)
# ❌ Compliance issues (no immutable record)
```

### ✅ With Event Sourcing

```python
# ===== WITH EVENT SOURCING =====

from flask import Flask, request, jsonify
import psycopg2
import json
from datetime import datetime
from typing import Dict, List

app = Flask(__name__)
db = psycopg2.connect(...)

class EventStore:
    """Append-only event log"""
    
    def __init__(self, db):
        self.db = db
    
    def append_event(self, aggregate_id, event_type, data, user_id=None):
        """Add event to log (immutable)"""
        
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO events (aggregate_id, event_type, data, user_id, timestamp)
            VALUES (%s, %s, %s, %s, NOW())
            RETURNING id, version
        """, (aggregate_id, event_type, json.dumps(data), user_id))
        
        event_id, version = cursor.fetchone()
        self.db.commit()
        
        return {'event_id': event_id, 'version': version}
    
    def get_events(self, aggregate_id):
        """Get all events for aggregate"""
        
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT id, event_type, data, timestamp
            FROM events
            WHERE aggregate_id = %s
            ORDER BY id
        """, (aggregate_id,))
        
        return [
            {
                'id': row[0],
                'type': row[1],
                'data': json.loads(row[2]),
                'timestamp': row[3]
            }
            for row in cursor.fetchall()
        ]
    
    def reconstruct_state(self, aggregate_id):
        """Replay events to get current state"""
        
        events = self.get_events(aggregate_id)
        state = {'id': aggregate_id, 'balance': 0}
        
        for event in events:
            if event['type'] == 'UserCreated':
                state['name'] = event['data']['name']
            elif event['type'] == 'BalanceUpdated':
                state['balance'] = event['data']['balance']
            elif event['type'] == 'MoneyTransferred':
                state['balance'] -= event['data']['amount']
        
        return state

# Initialize
event_store = EventStore(db)

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create user - with events"""
    
    data = request.json
    user_id = f"user_{uuid.uuid4()}"
    
    # Store event
    event_store.append_event(
        user_id,
        'UserCreated',
        {'name': data['name']},
        user_id=request.user_id
    )
    
    # Initial balance
    event_store.append_event(
        user_id,
        'BalanceUpdated',
        {'balance': 0},
        user_id=request.user_id
    )
    
    return {'user_id': user_id}

@app.route('/api/users/<user_id>/transfer', methods=['POST'])
def transfer_money(user_id):
    """Transfer money - with events"""
    
    data = request.json
    to_user_id = data['to_user_id']
    amount = data['amount']
    reason = data.get('reason', 'unspecified')
    
    # Store transfer event (immutable)
    event = event_store.append_event(
        user_id,
        'MoneyTransferred',
        {
            'to': to_user_id,
            'amount': amount,
            'reason': reason
        },
        user_id=request.user_id
    )
    
    # Update both users' states (from events)
    from_state = event_store.reconstruct_state(user_id)
    to_state = event_store.reconstruct_state(to_user_id)
    
    return {
        'status': 'success',
        'event_id': event['event_id'],
        'from_balance': from_state['balance'] - amount,
        'to_balance': to_state['balance'] + amount
    }

@app.route('/api/users/<user_id>/history')
def get_user_history(user_id):
    """Get complete history (audit trail)"""
    
    events = event_store.get_events(user_id)
    
    return {
        'user_id': user_id,
        'events': events,
        'total_events': len(events)
    }

@app.route('/api/users/<user_id>')
def get_user(user_id):
    """Get current state (reconstructed from events)"""
    
    state = event_store.reconstruct_state(user_id)
    
    return state

# Benefits:
# ✅ Complete history available
# ✅ Audit trail (every change tracked)
# ✅ Time-travel debugging (replay to any point)
# ✅ Recovery (exclude bad events)
# ✅ Compliance (immutable record)
# ✅ "Why" captured (reason for transfer)
```

### ✅ Event Sourcing + CQRS (Production)

```python
# ===== EVENT SOURCING + CQRS =====

from dataclasses import dataclass
from typing import Dict, List
import json
from datetime import datetime

@dataclass
class Event:
    """Domain event"""
    event_id: str
    aggregate_id: str
    event_type: str
    data: Dict
    timestamp: datetime
    user_id: str

class CommandHandler:
    """Handle commands (write side)"""
    
    def __init__(self, event_store):
        self.event_store = event_store
    
    def create_user(self, user_id, name):
        """Handle CreateUser command"""
        
        # Generate event
        event = Event(
            event_id=f"evt_{uuid.uuid4()}",
            aggregate_id=user_id,
            event_type='UserCreated',
            data={'name': name},
            timestamp=datetime.utcnow(),
            user_id='system'
        )
        
        # Store (write to event log)
        self.event_store.append(event)
        
        # Publish (to event bus)
        event_bus.publish(event)
        
        return {'user_id': user_id}
    
    def transfer_money(self, from_user, to_user, amount, reason):
        """Handle TransferMoney command"""
        
        # Validate (reconstruct state)
        from_state = self.event_store.reconstruct(from_user)
        
        if from_state['balance'] < amount:
            raise ValueError("Insufficient balance")
        
        # Generate events
        event = Event(
            event_id=f"evt_{uuid.uuid4()}",
            aggregate_id=from_user,
            event_type='MoneyTransferred',
            data={
                'to': to_user,
                'amount': amount,
                'reason': reason
            },
            timestamp=datetime.utcnow(),
            user_id='user_123'
        )
        
        # Store
        self.event_store.append(event)
        
        # Publish
        event_bus.publish(event)
        
        return {'status': 'success', 'event_id': event.event_id}

class Projection:
    """Materialized view (read side)"""
    
    def __init__(self, db):
        self.db = db
    
    def on_user_created(self, event):
        """React to UserCreated event"""
        
        # Update read model
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO user_read_model (user_id, name, balance)
            VALUES (%s, %s, %s)
        """, (event.aggregate_id, event.data['name'], 0))
        
        self.db.commit()
    
    def on_money_transferred(self, event):
        """React to MoneyTransferred event"""
        
        cursor = self.db.cursor()
        
        # Update sender
        cursor.execute(
            "UPDATE user_read_model SET balance = balance - %s WHERE user_id = %s",
            (event.data['amount'], event.aggregate_id)
        )
        
        # Update receiver
        cursor.execute(
            "UPDATE user_read_model SET balance = balance + %s WHERE user_id = %s",
            (event.data['amount'], event.data['to'])
        )
        
        self.db.commit()

# Event Bus
class EventBus:
    """Publishes events to subscribers"""
    
    def __init__(self):
        self.subscribers: Dict[str, List] = {}
    
    def subscribe(self, event_type, handler):
        """Subscribe to event type"""
        
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(handler)
    
    def publish(self, event):
        """Publish event to all subscribers"""
        
        if event.event_type in self.subscribers:
            for handler in self.subscribers[event.event_type]:
                handler(event)

# Setup
event_store = EventStore(db)
event_bus = EventBus()
command_handler = CommandHandler(event_store)
projection = Projection(db)

# Subscribe projection to events
event_bus.subscribe('UserCreated', projection.on_user_created)
event_bus.subscribe('MoneyTransferred', projection.on_money_transferred)

# API endpoints (using projections for reads)

@app.route('/api/users', methods=['POST'])
def create_user():
    """Write operation"""
    
    data = request.json
    result = command_handler.create_user(
        user_id=f"user_{uuid.uuid4()}",
        name=data['name']
    )
    
    return result

@app.route('/api/users/<user_id>')
def get_user(user_id):
    """Read operation (from projection)"""
    
    cursor = db.cursor()
    cursor.execute(
        "SELECT user_id, name, balance FROM user_read_model WHERE user_id = %s",
        (user_id,)
    )
    
    result = cursor.fetchone()
    
    return {
        'id': result[0],
        'name': result[1],
        'balance': result[2]
    }

# Benefits:
# ✅ Write & read sides independent
# ✅ Scale reads independently (projection DB)
# ✅ Optimize queries (denormalized)
# ✅ Real-time updates (event bus)
# ✅ Complete audit trail
```

---

## 💡 Design Decisions

### When to Use Event Sourcing?

```
USE EVENT SOURCING IF:

✅ Audit trail critical (financial, compliance)
✅ Time-travel debugging needed
✅ Complex domain (many state changes)
✅ Event-driven architecture desired
✅ Need to analyze historical data
✅ Regulatory requirements (GDPR, PCI-DSS)

DON'T USE IF:

❌ Simple CRUD application
❌ No need for history
❌ Large object trees (massive events)
❌ Real-time consistency critical
❌ Team unfamiliar with pattern
❌ High query throughput needed (without CQRS)

HYBRID APPROACH:

Event Sourcing for critical domains:
├─ Banking (compliance, audit)
├─ Orders (history important)
├─ Payments (regulatory)
└─ Users (GDPR)

Traditional storage for simple domains:
├─ Cache (ephemeral)
├─ Sessions (temporary)
├─ Config (stable)
└─ Analytics (derived)
```

### Storage & Performance

```
STORAGE CALCULATIONS:

Event size: ~500 bytes average
Events per day: 1 million

Yearly storage:
├─ 1M events/day × 365 days = 365M events/year
├─ 365M × 500 bytes = 182 GB/year
├─ 5 years: 910 GB
└─ With replication: 2-3 TB

Archival:
├─ Hot storage: 1 year (fast access)
├─ Warm storage: 5 years (slower)
├─ Cold storage: Archive (very slow)
└─ Total cost: Manageable

Query performance:

Without CQRS:
├─ Reconstruct state: Replay all events (slow)
├─ Query aggregation: Process all events
├─ Response time: Seconds
└─ Not suitable for high-volume reads

With CQRS + Projections:
├─ Simple query: From projection (fast)
├─ Response time: Milliseconds
├─ Scalability: Independent read scaling
└─ Recommended for production
```

---

## ❌ Common Mistakes

### Mistake 1: Storing Entire Objects as Events

```python
# ❌ Event is entire user object
event = {
    'type': 'UserUpdated',
    'data': {
        'id': 1,
        'name': 'Alice',
        'email': 'alice@ex.com',
        'address': '123 Main St',
        'phone': '555-1234',
        'balance': 900,
        # ... 50 more fields
    }
}

# Problem: 50x storage overhead!

# ✅ Event captures only what changed
event = {
    'type': 'UserNameChanged',
    'data': {'old_name': 'Alice', 'new_name': 'Alicia'}
}
# Much smaller, clear intent
```

### Mistake 2: No Snapshots (Slow Queries)

```python
# ❌ No snapshots
def get_user(user_id):
    events = load_all_events(user_id)  # 100,000 events!
    for event in events:
        apply(event)
    return state
# Takes 10 seconds!

# ✅ With snapshots
def get_user(user_id):
    snapshot = load_snapshot(user_id)  # Event #50,000
    events = load_events_since(user_id, 50000)  # Last 50,000
    for event in events:
        apply(event)
    return state
# Takes 100ms!
```

### Mistake 3: Tightly Coupling Event Schema

```python
# ❌ Events tightly coupled to code
class Event:
    timestamp: datetime
    user: User  # Reference to User object!
    amount: Decimal

# Problem: Serialization, versioning hard

# ✅ Events are plain data
event = {
    'timestamp': '2025-12-09T08:00:00Z',
    'user_id': 'user_1',  # Just ID
    'amount': 100  # Plain value
}
# Easy to store, serialize, version
```

---

## 📚 Additional Resources

**Event Sourcing:**
- [Event Sourcing Pattern](https://martinfowler.com/eaaDev/EventSourcing.html)
- [CQRS Pattern](https://martinfowler.com/bliki/CQRS.html)
- [EventStoreDB](https://www.eventstore.com/)

**Implementation:**
- [Axon Framework (Java)](https://axoniq.io/)
- [EventFlow (.NET)](https://github.com/eventflow/EventFlow)
- [Eventsourcing.py (Python)](https://github.com/johnbywater/eventsourcing)

**Learning:**
- [Event Sourcing Made Simple](https://kickstarter.engineering/event-sourcing-made-simple-4a2f1800694f)
- [CQRS Documents](https://cqrs.files.wordpress.com/2010/11/cqrs_documents.pdf)

---


## 🎯 Before You Leave

**Can you answer these?**

1. **Event Sourcing vs traditional storage?**
   - Answer: Sourcing stores events; traditional stores state

2. **Projection?**
   - Answer: Materialized view created by replaying events

3. **CQRS benefit?**
   - Answer: Independent scaling, optimized queries

4. **Why snapshots?**
   - Answer: Avoid replaying all events (slow)

5. **Event versioning?**
   - Answer: Handle schema changes over time (upcasting)

**If you got these right, you're ready for feature flags!** ✅

---

## 🤣 Closing Thoughts

> **Developer:** "Our database got corrupted!"
>
> **DBA:** "Did you have backups?"
>
> **Developer:** "Yeah, from last week"
>
> **CEO:** "We lost a week of data??"
>
> **Developer:** "With event sourcing, we'd just replay to yesterday"
>
> **CEO:** "Why aren't we using that??"
>
> **Developer:** "We would, but we'd need to rewrite everything"
>
> **CEO:** "Do it anyway!" 💸

---

[← Back to Main](../README.md) | [Previous: Multi-Region Architecture](58-multi-region-architecture.md) | [Next: Feature Flags & Config Management →](60-feature-flags.md)

---

**Last Updated:** December 09, 2025  
**Difficulty:** ⭐⭐⭐⭐ Advanced (architecture pattern)  
**Time to Read:** 32 minutes  
**Time to Implement:** 30-50 hours (depends on complexity)  

---

*Event Sourcing: Never delete the truth, only add to it.* 📜✨