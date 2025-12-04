# 30. CQRS (Command Query Responsibility Segregation)

CQRS is the idea that reading data and writing data are fundamentally different operations with different requirements. So let's make them completely separate. Problem solved! New problem: Now your data is out of sync and you spend all night debugging eventual consistency issues. Trade-offs: You've got to love 'em. 📝➡️🔍

[← Back to Main](../README.md) | [Previous: Event-Driven Architecture](29-event-driven-architecture.md) | [Next: Data Pipelines & Stream Processing →](31-data-pipelines.md)

---

## 🎯 Quick Summary

**CQRS** separates read and write operations into different models. Command (write): creates orders, updates profiles, deletes users. Query (read): lists orders, fetches profile, searches users. Reads optimized for speed (denormalized, indexed). Writes optimized for correctness (normalized, transactional). Enables independent scaling: write-heavy system scales writes, read-heavy scales reads. Trade-off: eventual consistency, complexity. Used by Netflix, Microsoft, CQRS-specialized companies for complex domains.

Think of it as: **CQRS = Separate Database Models for Reads and Writes**

---

## 🌟 Beginner Explanation

### Traditional CRUD vs CQRS

**TRADITIONAL CRUD (Single Model):**

```
One model handles reads AND writes:

Database:
├─ orders table
│  ├─ id (PK)
│  ├─ user_id (FK)
│  ├─ amount
│  ├─ status
│  ├─ created_at
│  └─ updated_at

Read (list orders):
├─ SELECT * FROM orders WHERE user_id = 123
├─ Executes query against normalized table
└─ Result: 10 orders

Write (create order):
├─ INSERT INTO orders (user_id, amount, status) VALUES (...)
├─ Updates normalized table
└─ All fields consistent

Simple but:
❌ Reads join multiple tables (slow)
❌ Writes must maintain consistency (locks)
❌ Can't scale reads separately
❌ One database for everything
```

**CQRS (Separated Models):**

```
Command Model (Write):
├─ Normalized database
├─ orders table (just data)
├─ user_orders table (joins)
├─ inventory table
└─ optimized for correctness

Query Model (Read):
├─ Denormalized view
├─ user_orders_view (pre-aggregated)
│  ├─ user_id
│  ├─ order_count
│  ├─ total_spent
│  ├─ last_order
│  └─ all fields needed by read
└─ optimized for speed

Flow:
1. User creates order → Writes to Command Model
2. Command Model processes → Publishes event
3. Event → Updates Query Model
4. User reads orders → Reads from Query Model

Benefits:
✅ Reads: Denormalized, fast, no joins
✅ Writes: Normalized, consistent, atomic
✅ Scale independently (many read replicas)
✅ Different databases possible (SQL write, NoSQL read)
```

### Read vs Write Requirements

```
WRITE OPERATIONS (Commands):

Requirements:
├─ Atomicity (all or nothing)
├─ Consistency (no invalid state)
├─ Isolation (no race conditions)
├─ Durability (survives crashes)
├─ Strong consistency needed
└─ Serializable transactions

Examples:
├─ Create order
├─ Update payment
├─ Deduct from wallet
└─ Transfer funds

Patterns:
├─ ACID transactions
├─ Normalized schema
├─ Foreign keys
├─ Constraints

READ OPERATIONS (Queries):

Requirements:
├─ Speed (< 100ms latency)
├─ Availability (always online)
├─ Eventually consistent OK
├─ Denormalized preferred
└─ Optimized access patterns

Examples:
├─ List user orders
├─ Get user profile
├─ Search products
├─ Get recommendations

Patterns:
├─ Denormalized views
├─ Pre-aggregated data
├─ No joins needed
├─ Indexed heavily
```

### Architecture Flow

```
COMMAND SIDE (Write):

User Action: Create Order
  ├─ Command: CreateOrderCommand
  │  ├─ user_id: 123
  │  ├─ items: [item1, item2]
  │  └─ amount: $100
  ├─ Validate command
  ├─ Execute against database
  ├─ Persist (ACID transaction)
  ├─ Generate event: OrderCreated
  └─ Publish event

QUERY SIDE (Read):

Event: OrderCreated
  ├─ Received by event handler
  ├─ Update query model
  ├─ Add to user_orders_view
  ├─ Increment order_count
  ├─ Update total_spent
  └─ Commit

User Query: Get My Orders
  ├─ Query: GetUserOrdersQuery
  │  └─ user_id: 123
  ├─ Hit query model (fast!)
  ├─ Return pre-built view
  └─ User sees orders (eventually consistent)
```

---

## 🔬 Advanced Explanation

### Command Side Deep Dive

```
COMMAND MODEL (Write):

Responsibilities:
├─ Accept commands
├─ Validate business rules
├─ Maintain strong consistency
├─ Persist to database
├─ Generate events
└─ Publish to message bus

Example: Create Order Command

Command Handler:
  1. Receive CreateOrderCommand
  2. Load user (check exists)
  3. Check wallet balance
  4. Lock user for transaction
  5. Check inventory
  6. Reserve inventory
  7. Deduct wallet
  8. Create order
  9. Commit transaction
  10. Generate OrderCreated event
  11. Publish event
  12. Return order_id

Result: Atomic, consistent, isolated
Trades off: Slower (all checks done)
```

### Query Side Deep Dive

```
QUERY MODEL (Read):

Responsibilities:
├─ Receive queries
├─ Return data quickly
├─ Accept eventual consistency
├─ No business logic
├─ No transactions
└─ Denormalized data

Example: Get User Orders Query

Query Handler:
  1. Receive GetUserOrdersQuery (user_id=123)
  2. Execute SELECT against denormalized view
  3. Return results (pre-joined, pre-aggregated)

Result: Fast (< 10ms)
Costs: Stale data (eventual)

Denormalized View:
┌─────────────────────────────────┐
│ user_orders_view (materialized) │
├─────────────────────────────────┤
│ user_id: 123                    │
│ order_count: 42                 │
│ total_spent: $5,420             │
│ last_order_date: 2025-11-11     │
│ avg_order_value: $129           │
│ preferred_category: Electronics │
│ VIP_status: true                │
└─────────────────────────────────┘

All fields pre-calculated
No joins needed
One SELECT query
Result in < 1ms
```

### Event Synchronization

```
PROBLEM: Command and Query out of sync

T=0: User creates order
  ├─ Command model: Order created ✓
  ├─ Event published
  └─ Query model: Not updated yet (lag!)

T=0.1s: User queries orders
  ├─ Query model doesn't have new order yet
  ├─ Returns stale results
  └─ User doesn't see their order!

T=1s: Event processed
  ├─ Query model: Order added ✓
  └─ Now visible

Solution: Versioning

Command publishes event with version:
├─ OrderCreated v1 (sequence_id=1000)
└─ Published to event bus

Query subscribes:
├─ Receive event v1
├─ Update query model
├─ Store processed_version=1000
└─ Idempotent (if reprocessed: ignore)

If query receives out-of-order:
├─ Event v1001 before v1000
├─ Queue it (wait for v1000)
├─ Process in order
└─ No inconsistency
```

### Scaling Implications

```
TRADITIONAL MONOLITH:
┌──────────────────────┐
│ Database (reads+writes)
└──────────────────────┘
        ↑        ↑
        │        │
    Writes    Reads
   (10% traffic) (90% traffic)

Problem:
❌ Read traffic overloads database
❌ Write throughput limited
❌ Can't scale independently


CQRS ARCHITECTURE:

Write Model:                Read Models:
┌──────────────────┐   ┌─────────────┐
│ Primary Database │   │ Read Replica 1│
│  (normalized)    │─→ ├─────────────┤
│ (strong consistency) │ Read Replica 2│
└──────────────────┘   ├─────────────┤
                       │ Read Replica N│
                       └─────────────┘

Scaling:
├─ Writes: Single master (ACID)
├─ Reads: Multiple replicas (parallel)
├─ 1000 read replicas if needed!
└─ Independent scaling

Result:
✅ Reads: Ultra-fast (distributed)
✅ Writes: Consistent (centralized)
✅ Scales 100x better
```

### CQRS + Event Sourcing

```
CQRS ALONE:
├─ Read model denormalized
├─ Write model normalized
└─ Out of sync possible

CQRS + EVENT SOURCING:
├─ Commands processed
├─ Events immutable
├─ Query model rebuilt from events
├─ Always consistent with event log
└─ Perfect reconstruction

Benefits:
✅ Complete audit trail (all events)
✅ Replay capability (rebuild models)
✅ Time travel (show state at any point)
✅ No data loss (events immutable)

Example:
Event 1: OrderCreated(123, alice, $100)
Event 2: PaymentProcessed(123, approved)
Event 3: OrderShipped(123)
Event 4: OrderDelivered(123)

Query model rebuilds:
├─ Apply event 1: Order = {user: alice, amount: $100, status: created}
├─ Apply event 2: Order.status = paid
├─ Apply event 3: Order.status = shipped
├─ Apply event 4: Order.status = delivered
└─ Final state: Delivered order

If needed: Replay to any point
├─ After event 2: Order = {user: alice, paid}
├─ After event 3: Order = {user: alice, shipped}
```

---

## 🐍 Python Code Example

### ❌ Traditional CRUD (Mixed Model)

```python
# ===== TRADITIONAL CRUD (MIXED MODEL) =====

from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)
db = psycopg2.connect("dbname=shop")

# One model handles reads AND writes
class OrderService:
    """Single model CRUD"""
    
    def create_order(self, user_id, items, amount):
        """Create order"""
        cursor = db.cursor()
        
        # Write
        cursor.execute("""
            INSERT INTO orders (user_id, items, amount, status)
            VALUES (%s, %s, %s, 'pending')
            RETURNING id
        """, (user_id, str(items), amount))
        
        order_id = cursor.fetchone()[0]
        db.commit()
        
        return {'order_id': order_id}
    
    def get_user_orders(self, user_id):
        """Get user orders"""
        cursor = db.cursor()
        
        # Read (same normalized table)
        cursor.execute("""
            SELECT o.id, o.amount, o.status, COUNT(i.id) as item_count
            FROM orders o
            LEFT JOIN order_items i ON o.id = i.order_id
            WHERE o.user_id = %s
            GROUP BY o.id
            ORDER BY o.created_at DESC
        """, (user_id,))
        
        orders = cursor.fetchall()
        return {'orders': orders}

# Problem:
# ❌ Same database for reads and writes
# ❌ Reads do complex joins
# ❌ Writes locked while joins happen
# ❌ Can't scale independently
```

### ✅ Simple CQRS (Separated Models)

```python
# ===== SIMPLE CQRS (SEPARATED MODELS) =====

from flask import Flask, jsonify, request
import psycopg2
import json

app = Flask(__name__)

# Command database (writes)
write_db = psycopg2.connect("dbname=shop_write")

# Query database (reads)
read_db = psycopg2.connect("dbname=shop_read")

class CommandModel:
    """Write model (normalized)"""
    
    def create_order(self, user_id, items, amount):
        """Create order (write)"""
        cursor = write_db.cursor()
        
        # Normalized write
        cursor.execute("""
            INSERT INTO orders (user_id, amount, status)
            VALUES (%s, %s, 'pending')
            RETURNING id
        """, (user_id, amount))
        
        order_id = cursor.fetchone()[0]
        
        # Insert items separately
        for item in items:
            cursor.execute("""
                INSERT INTO order_items (order_id, item_id, quantity)
                VALUES (%s, %s, %s)
            """, (order_id, item['id'], item['quantity']))
        
        write_db.commit()
        
        # Publish event (for read model to consume)
        event = {
            'type': 'order_created',
            'order_id': order_id,
            'user_id': user_id,
            'amount': amount,
            'items': items
        }
        publish_event(event)
        
        return order_id

class QueryModel:
    """Read model (denormalized)"""
    
    def get_user_orders(self, user_id):
        """Get user orders (read, denormalized)"""
        cursor = read_db.cursor()
        
        # Denormalized read (no joins!)
        cursor.execute("""
            SELECT order_id, user_id, amount, item_count, status, created_at
            FROM user_orders_view
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))
        
        orders = cursor.fetchall()
        return orders

class EventHandler:
    """Synchronize models via events"""
    
    def on_order_created(self, event):
        """Update read model when order created"""
        cursor = read_db.cursor()
        
        # Update denormalized view
        cursor.execute("""
            INSERT INTO user_orders_view (order_id, user_id, amount, item_count, status)
            VALUES (%s, %s, %s, %s, 'pending')
        """, (event['order_id'], event['user_id'], event['amount'], len(event['items'])))
        
        read_db.commit()

# Usage
cmd_model = CommandModel()
query_model = QueryModel()

@app.route('/api/orders', methods=['POST'])
def create_order():
    order_id = cmd_model.create_order(
        user_id='user-123',
        items=[{'id': 'item-1', 'quantity': 2}],
        amount=100
    )
    return jsonify({'order_id': order_id})

@app.route('/api/users/<user_id>/orders', methods=['GET'])
def get_orders(user_id):
    orders = query_model.get_user_orders(user_id)
    return jsonify({'orders': orders})

# Benefits:
# ✅ Write model: Normalized, ACID
# ✅ Read model: Denormalized, fast
# ✅ Synchronized via events
# ✅ Can scale independently
```

### ✅ Production CQRS (Event Sourcing + Projections)

```python
# ===== PRODUCTION CQRS (EVENT SOURCING) =====

from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime
import json

# Command side
@dataclass
class CreateOrderCommand:
    user_id: str
    items: List[Dict]
    amount: float

class CommandHandler:
    """Process commands and generate events"""
    
    def handle_create_order(self, cmd: CreateOrderCommand):
        """Handle order creation"""
        
        # Validate
        if cmd.amount <= 0:
            raise ValueError("Amount must be positive")
        
        if not cmd.items:
            raise ValueError("Order must have items")
        
        # Generate event (immutable fact)
        event = {
            'event_id': 'evt-' + str(int(datetime.now().timestamp() * 1000)),
            'event_type': 'OrderCreated',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'order_id': 'order-' + str(int(datetime.now().timestamp())),
                'user_id': cmd.user_id,
                'items': cmd.items,
                'amount': cmd.amount,
                'status': 'pending'
            },
            'version': 1
        }
        
        # Store event (append-only)
        self.store_event(event)
        
        # Publish for read model
        self.publish_event(event)
        
        return event['data']['order_id']
    
    def store_event(self, event):
        """Store in event store (immutable)"""
        # In production: Append to database
        print(f"Event stored: {event['event_type']}")
    
    def publish_event(self, event):
        """Publish to message bus"""
        # In production: Send to Kafka
        print(f"Event published: {event['event_type']}")

# Query side
class ProjectionManager:
    """Build and maintain query models"""
    
    def __init__(self):
        self.projections = {}  # In-memory, would use database
    
    def handle_event(self, event):
        """Update projections when event received"""
        
        if event['event_type'] == 'OrderCreated':
            self.project_order_created(event['data'])
    
    def project_order_created(self, data):
        """Update user_orders view"""
        user_id = data['user_id']
        
        # Initialize user entry
        if user_id not in self.projections:
            self.projections[user_id] = {
                'orders': [],
                'order_count': 0,
                'total_spent': 0,
                'last_order_date': None
            }
        
        # Add to projection
        self.projections[user_id]['orders'].append({
            'order_id': data['order_id'],
            'amount': data['amount'],
            'items_count': len(data['items']),
            'status': data['status']
        })
        
        self.projections[user_id]['order_count'] += 1
        self.projections[user_id]['total_spent'] += data['amount']
        self.projections[user_id]['last_order_date'] = datetime.utcnow().isoformat()
    
    def get_user_orders(self, user_id):
        """Query the projection"""
        return self.projections.get(user_id, {
            'orders': [],
            'order_count': 0,
            'total_spent': 0
        })

# Usage
cmd_handler = CommandHandler()
projection = ProjectionManager()

# Create order (command)
order_id = cmd_handler.handle_create_order(CreateOrderCommand(
    user_id='user-123',
    items=[{'id': 'item-1', 'quantity': 2}],
    amount=100
))

# Simulate event reaching projection
event = {
    'event_type': 'OrderCreated',
    'data': {
        'order_id': order_id,
        'user_id': 'user-123',
        'items': [{'id': 'item-1', 'quantity': 2}],
        'amount': 100,
        'status': 'pending'
    }
}

projection.handle_event(event)

# Query (read)
result = projection.get_user_orders('user-123')
print(f"User orders: {result}")

# Benefits:
# ✅ Command: Pure, no side effects
# ✅ Events: Immutable history
# ✅ Projections: Built from events
# ✅ Replay: Rebuild models anytime
# ✅ Eventually consistent
```

---

## 💡 Mini Project: "Implement CQRS"

### Phase 1: Basic Separation ⭐

**Requirements:**
- Separate command and query handlers
- Different database connections
- Event publishing
- Basic synchronization

---

### Phase 2: Event Sourcing ⭐⭐

**Requirements:**
- Event store (append-only)
- Event replay
- Projections
- Versioning

---

### Phase 3: Enterprise (Multi-Projection) ⭐⭐⭐

**Requirements:**
- Multiple read models
- Complex projections
- Dead letter queue
- Projection rebuilding

---

## ⚖️ CQRS Pros and Cons

| Aspect | Pros | Cons |
|--------|------|------|
| **Scalability** | Independent read/write scaling | Operational complexity |
| **Consistency** | Strong writes | Eventually consistent reads |
| **Performance** | Fast reads (denormalized) | Eventual consistency lag |
| **Debugging** | Clear separation | Harder to debug |
| **Complexity** | Clear responsibilities | Many moving parts |
| **Data** | Optimized storage | Multiple copies |

---

## ❌ Common Mistakes

### Mistake 1: Complex Projections

```python
# ❌ Projection does too much
def handle_event(event):
    # Complex logic
    # Multiple joins
    # Aggregations
    # This blocks event processing!

# ✅ Simple projections
def handle_event(event):
    # Just update what changed
    # Add to lists
    # Increment counters
    # Fast operation
```

### Mistake 2: No Versioning

```python
# ❌ Events with no version
event = {
    'type': 'OrderCreated',
    'data': {...}
}

# Later: Change event structure
# Old projections break!

# ✅ Version your events
event = {
    'type': 'OrderCreated',
    'version': 1,
    'data': {...}
}
```

### Mistake 3: Stale Reads

```python
# ❌ Ignore eventual consistency
# User creates order
# Immediately reads orders
# Order not there yet! (projection lag)
# User confused

# ✅ Handle eventual consistency
# Return write-response immediately
# Include version number
# Client waits if needed
```

---

## 📚 Additional Resources

**CQRS:**
- [CQRS Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/cqrs)
- [Martin Fowler CQRS](https://martinfowler.com/bliki/CQRS.html)

**Event Sourcing:**
- [Event Sourcing Pattern](https://martinfowler.com/eaaDev/EventSourcing.html)
- [Greg Young on Event Sourcing](https://www.youtube.com/watch?v=JHGkaLCar6c)


---

## 🎯 Before You Leave

**Can you answer these?**

1. **Why separate commands from queries?**
   - Answer: Different requirements (consistency vs speed)

2. **What's eventual consistency?**
   - Answer: Read model eventually matches write model

3. **How do projections stay in sync?**
   - Answer: Via events published by commands

4. **When should you use CQRS?**
   - Answer: Complex domains, independent read/write scaling

5. **What's CQRS + Event Sourcing?**
   - Answer: Events are source of truth, rebuild projections from events

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **Architect:** "Let's use CQRS to scale reads independently!"
>
> **After 1 month:** "Our read model is 2 seconds out of sync"
>
> **User:** "Why is my order not showing?"
>
> **Engineer:** "It'll be there eventually!"
>
> **User:** "I need it now!"
>
> **Architect:** "Welcome to eventual consistency." 🕐

---

[← Back to Main](../README.md) | [Previous: Event-Driven Architecture](29-event-driven-architecture.md) | [Next: Data Pipelines & Stream Processing →](31-data-pipelines.md)

---

**Last Updated:** November 11, 2025  
**Difficulty:** ⭐⭐⭐⭐ Advanced (architectural pattern)  
**Time to Read:** 27 minutes  
**Time to Implement:** 6-10 hours per phase  

---

*CQRS: Making your system faster and your consistency eventually correct.* 🚀