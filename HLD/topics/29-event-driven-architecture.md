# 29. Event-Driven Architecture

Event-driven architecture is like running a restaurant where instead of taking orders directly, the waiter yells "ORDER!" and anyone interested shows up to handle it. Sounds chaotic. Turns out it scales better than making the waiter wait for everyone individually. Also, sometimes the order gets lost in the noise. 📣🚀

[← Back to Main](../README.md) | [Previous: Distributed Caching](28-distributed-caching.md) | [Next: CQRS →](30-cqrs.md)

---

## 🎯 Quick Summary

**Event-Driven Architecture** decouples systems by using events: when something happens (user signs up, order placed, payment processed), an event is published. Other systems react to events asynchronously. Instead of Service A calling Service B directly, Service A publishes "user.created" event, Service B subscribes and reacts. Enables scalability, resilience, and independent scaling. Trade-off: eventual consistency, complexity. Used by Netflix, Uber, Amazon for real-time systems.

Think of it as: **Event-Driven = Observer Pattern at Scale**

---

## 🌟 Beginner Explanation

### Synchronous vs Asynchronous

**SYNCHRONOUS (Request-Response):**

```
User Service calls Order Service directly:

User Service:
  ├─ Request: "Create order for user 123"
  └─ Wait for response...
        ↓
    Order Service:
      ├─ Create order
      ├─ Update database
      ├─ Send response
      └─ Response received
        ↓
  User Service continues

Problem:
❌ User Service blocked until Order Service responds
❌ If Order Service slow: User Service slow
❌ If Order Service down: User Service fails
❌ Both services tightly coupled
```

**ASYNCHRONOUS (Event-Driven):**

```
User Service publishes event:

User Service:
  ├─ User signed up
  ├─ Publish: "user.created" event
  ├─ Return immediately (don't wait!)
  └─ Continue processing

Event Queue/Bus:
  ├─ Message: {"type": "user.created", "user_id": 123}
  └─ Available to subscribers

Order Service (if subscribed):
  ├─ Receives event
  ├─ Processes in background
  └─ Acknowledges when done

Notification Service (if subscribed):
  ├─ Receives event
  ├─ Sends welcome email
  └─ Acknowledges

Result:
✅ User Service returns immediately (fast!)
✅ Order Service processes independently (slow OK)
✅ Services loosely coupled
✅ Can scale independently
```

### Event Flow

```
TRADITIONAL (Imperative):

1. User signup request
2. Create user in database
3. Send welcome email (wait)
4. Create loyalty account (wait)
5. Add to newsletter (wait)
6. Return response

If step 3 slow: User sees delay!


EVENT-DRIVEN (Declarative):

1. User signup request
2. Create user in database
3. Publish "user.signup" event
4. Return response immediately!

Event Queue broadcasts to:
├─ Email Service (sends welcome)
├─ Loyalty Service (creates account)
├─ Newsletter Service (adds subscription)
└─ Analytics Service (tracks signup)

All happen in parallel, user sees no delay!
```

### Components

```
PUBLISHER (Produces events):

User Service:
  ├─ User action: "signup"
  └─ Publish: event = {
      "type": "user.created",
      "user_id": 123,
      "email": "alice@example.com",
      "timestamp": "2025-11-11T16:54:00Z"
    }

EVENT (Message):

{
  "event_id": "evt-xyz789",
  "type": "user.created",
  "data": {
    "user_id": 123,
    "email": "alice@example.com",
    "name": "Alice"
  },
  "timestamp": "2025-11-11T16:54:00Z",
  "source": "user-service"
}

BROKER (Carries messages):

Kafka, RabbitMQ, AWS SNS/SQS, Redis Streams
├─ Stores events
├─ Routes to subscribers
└─ Manages delivery

SUBSCRIBER (Consumes events):

Email Service:
  ├─ Listen for "user.created" event
  └─ Send welcome email

Loyalty Service:
  ├─ Listen for "user.created" event
  └─ Create loyalty account

Analytics Service:
  ├─ Listen for all events
  └─ Track metrics
```

---

## 🔬 Advanced Explanation

### Event Sources and Sinks

```
EVENT SOURCES (What triggers events):

1. User Actions:
   ├─ user.signup
   ├─ user.login
   ├─ user.update_profile
   └─ user.delete

2. System Events:
   ├─ payment.processed
   ├─ order.created
   ├─ order.shipped
   └─ inventory.low

3. External Events:
   ├─ payment_provider.webhook (stripe)
   ├─ sms_delivery.confirmed
   ├─ email.bounced
   └─ notification.failed

EVENT SINKS (What reacts to events):

1. Services:
   ├─ Email Service (sends emails)
   ├─ SMS Service (sends SMS)
   ├─ Notification Service (push notifications)
   └─ Analytics Service (tracks metrics)

2. Data Storage:
   ├─ Data Lake (store all events)
   ├─ Analytics DB (aggregated data)
   ├─ Cache invalidation (refresh cache)
   └─ Search index update (Elasticsearch)

3. External Systems:
   ├─ CRM (Salesforce)
   ├─ BI Tools (analytics)
   ├─ Webhooks (third-party)
   └─ Other services
```

### Event Patterns

**PUBLISH-SUBSCRIBE (Fan-Out):**

```
One publisher → Many subscribers

Publisher: "order.created" event
  ├─ Email Service subscribes → Gets event
  ├─ SMS Service subscribes → Gets event
  ├─ Analytics subscribes → Gets event
  ├─ Inventory subscribes → Gets event
  └─ Fraud Detection subscribes → Gets event

All subscribers get same event
All process independently
Event not consumed (reusable)

Used for: Broadcasting events to many consumers
Example: Kafka topic with multiple consumer groups
```

**POINT-TO-POINT (Queue):**

```
One publisher → One consumer (per message)

Publisher: "payment.process" message
  ├─ Put in queue
  ├─ Consumer 1 takes message
  ├─ Consumer 1 processes
  ├─ Message consumed (removed)
  └─ Next message for Consumer 2

Only one consumer per message
Message consumed after processing
Load balancing across consumers

Used for: Work distribution
Example: Payment processing queue
```

**CHOREOGRAPHY vs ORCHESTRATION:**

```
CHOREOGRAPHY (Decentralized):

User Service: Publish "order.created"
  ├─ Payment Service: Receives, processes payment
  │  └─ Publish "payment.processed"
  │     ├─ Inventory Service: Receives, updates stock
  │     │  └─ Publish "inventory.updated"
  │     │     └─ Shipping Service: Receives, ships order
  │     └─ Notification Service: Receives, sends receipt
  └─ All services independent

Benefits:
✅ Decoupled (no central orchestrator)
✅ Easy to add new services (just subscribe)
❌ Hard to debug (scattered logic)
❌ Complex flow visualization


ORCHESTRATION (Centralized):

Order Orchestrator (Controller):
  ├─ 1. Call Payment Service (wait)
  ├─ 2. Call Inventory Service (wait)
  ├─ 3. Call Shipping Service (wait)
  ├─ 4. Call Notification Service (wait)
  └─ 5. Return to user

Central orchestrator knows entire flow

Benefits:
✅ Easy to understand (one place)
✅ Easy to debug (central logic)
❌ Tightly coupled (orchestrator is bottleneck)
❌ Hard to scale (orchestrator becomes complex)
```

### Event Ordering and Consistency

```
ORDERING PROBLEM:

Event 1: order.created (user_id=123, amount=$100)
Event 2: payment.processed (order_id=1)
Event 3: payment.failed (order_id=1)

If received out of order:
├─ 3, 1, 2 (payment failed before created!)
├─ Consistency broken
└─ State invalid

SOLUTION: Event Versioning

Each event has version:
├─ Event 1: order.created v1
├─ Event 2: payment.processed v1
├─ Event 3: order.updated v2 (if structure changes)

Consumers check version:
├─ If older: May need migration
├─ If newer: Backward compatible
└─ Guarantees consistency


CAUSAL ORDERING:

Use causality tracking:
Event 1: user.created
  ├─ ID: evt-1
  └─ Cause: signup

Event 2: order.created
  ├─ ID: evt-2
  ├─ Cause: evt-1 (depends on user.created)
  └─ Parent: evt-1

Event 3: payment.processed
  ├─ ID: evt-3
  ├─ Cause: evt-2 (depends on order.created)
  └─ Parent: evt-2

Enforced order:
├─ evt-1 must process before evt-2
├─ evt-2 must process before evt-3
└─ Guarantees consistency
```

### Event Storage (Event Sourcing)

```
TRADITIONAL (State-Based):

Database stores current state:
Users table:
├─ id: 123
├─ name: "Alice"
├─ email: "alice@new@example.com"
└─ status: "verified"

Problem:
❌ History lost (how did Alice's email change?)
❌ Can't replay (no event record)
❌ Debugging hard (no audit trail)


EVENT SOURCING (Event-Based):

Database stores all events:
├─ evt-1: user.created {user_id: 123, name: "Alice", email: "alice@old.com"}
├─ evt-2: user.email_updated {user_id: 123, email: "alice@new@example.com"}
├─ evt-3: user.verified {user_id: 123}

Current state = replay all events
├─ Start: empty
├─ Apply evt-1: user = {id: 123, name: "Alice", email: "alice@old.com"}
├─ Apply evt-2: user.email = "alice@new@example.com"
├─ Apply evt-3: user.status = "verified"
└─ Result: Current state

Benefits:
✅ Full history preserved
✅ Can replay to any point in time
✅ Audit trail (who did what when)
✅ Debugging easier (replay events)
```

---

## 🐍 Python Code Example

### ❌ Synchronous (Tightly Coupled)

```python
# ===== SYNCHRONOUS (TIGHTLY COUPLED) =====

from flask import Flask, jsonify
import requests

app = Flask(__name__)

class OrderService:
    """Synchronous: Calls other services directly"""
    
    def create_order(self, user_id, items):
        """Create order by calling other services directly"""
        
        # 1. Call Payment Service
        try:
            payment_response = requests.post(
                'http://payment-service:8003/charge',
                json={'user_id': user_id, 'amount': 100},
                timeout=5
            )
            if payment_response.status_code != 200:
                return {'error': 'Payment failed'}
        except Exception as e:
            return {'error': f'Payment service down: {e}'}
        
        # 2. Call Inventory Service
        try:
            inventory_response = requests.post(
                'http://inventory-service:8004/reserve',
                json={'items': items},
                timeout=5
            )
            if inventory_response.status_code != 200:
                return {'error': 'Inventory unavailable'}
        except Exception as e:
            return {'error': f'Inventory service down: {e}'}
        
        # 3. Call Notification Service
        try:
            requests.post(
                'http://notification-service:8005/send-email',
                json={'user_id': user_id, 'type': 'order_confirmation'},
                timeout=5
            )
        except Exception as e:
            # If notification fails: Order still created (inconsistent)
            pass
        
        return {'status': 'order created'}

# Problems:
# ❌ Services tightly coupled
# ❌ If any service slow: Order creation slow
# ❌ If any service down: Order creation fails
# ❌ Hard to add new service (must modify code)
```

### ✅ Asynchronous (Event-Driven)

```python
# ===== ASYNCHRONOUS (EVENT-DRIVEN) =====

from flask import Flask, jsonify
import json
from datetime import datetime
from queue import Queue
import threading

app = Flask(__name__)

# Simple event bus
class EventBus:
    """Publish-subscribe event system"""
    
    def __init__(self):
        self.subscribers = {}  # topic -> [handlers]
        self.event_history = []
    
    def subscribe(self, event_type, handler):
        """Subscribe to event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
    
    def publish(self, event_type, data):
        """Publish event to all subscribers"""
        event = {
            'type': event_type,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Store in history
        self.event_history.append(event)
        
        # Deliver to subscribers
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                # Run in background (don't wait)
                threading.Thread(target=handler, args=(event,), daemon=True).start()

event_bus = EventBus()

# Order Service (Publisher)
class OrderService:
    """Create order and publish events"""
    
    def create_order(self, user_id, items):
        """Create order and publish event"""
        
        # 1. Create order (in database)
        order = {
            'id': 'order-123',
            'user_id': user_id,
            'items': items,
            'status': 'pending'
        }
        
        # 2. Publish event (don't wait for responses!)
        event_bus.publish('order.created', {
            'order_id': order['id'],
            'user_id': user_id,
            'items': items,
            'amount': 100
        })
        
        # 3. Return immediately
        return {'order_id': order['id'], 'status': 'created'}

# Services (Subscribers - react to events)
def payment_handler(event):
    """Payment service processes order.created event"""
    print(f"[Payment] Processing payment for {event['data']['order_id']}")
    # Process payment asynchronously
    # Publish: payment.processed

def inventory_handler(event):
    """Inventory service processes order.created event"""
    print(f"[Inventory] Reserving items for {event['data']['order_id']}")
    # Reserve inventory asynchronously

def notification_handler(event):
    """Notification service processes order.created event"""
    print(f"[Notification] Sending confirmation to user {event['data']['user_id']}")
    # Send email asynchronously

def analytics_handler(event):
    """Analytics service processes all events"""
    print(f"[Analytics] Tracking event: {event['type']}")
    # Update metrics

# Register subscribers
event_bus.subscribe('order.created', payment_handler)
event_bus.subscribe('order.created', inventory_handler)
event_bus.subscribe('order.created', notification_handler)
event_bus.subscribe('order.created', analytics_handler)

# API
order_service = OrderService()

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create order endpoint"""
    order_id = order_service.create_order(
        user_id='user-123',
        items=['item-1', 'item-2']
    )
    return jsonify(order_id)

# Benefits:
# ✅ Order creation returns immediately
# ✅ Services process independently (asynchronously)
# ✅ If one service slow: Doesn't affect others
# ✅ If one service down: Others still process
# ✅ Easy to add new service (just subscribe)
```

### ✅ Production Event-Driven (Kafka)

```python
# ===== PRODUCTION EVENT-DRIVEN (KAFKA) =====

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import json
import threading
from datetime import datetime

# Kafka producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Kafka consumers
class KafkaEventConsumer:
    """Consumer for Kafka topics"""
    
    def __init__(self, topic, group_id, handler):
        self.topic = topic
        self.group_id = group_id
        self.handler = handler
        self.consumer = KafkaConsumer(
            topic,
            group_id=group_id,
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
    
    def start(self):
        """Start consuming messages"""
        threading.Thread(target=self._consume, daemon=True).start()
    
    def _consume(self):
        """Consume messages in background"""
        for message in self.consumer:
            try:
                self.handler(message.value)
            except Exception as e:
                print(f"Error processing message: {e}")

# Order Service (Producer)
class OrderService:
    """Produces order events"""
    
    def create_order(self, user_id, items):
        """Create order and publish to Kafka"""
        
        # Create order
        order_id = f"order-{user_id}-{int(datetime.now().timestamp())}"
        
        # Publish to Kafka
        event = {
            'order_id': order_id,
            'user_id': user_id,
            'items': items,
            'amount': 100,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        future = producer.send('order.created', value=event)
        
        # Wait for delivery (optional)
        try:
            future.get(timeout=10)
            print(f"Event published: {order_id}")
        except KafkaError as e:
            print(f"Failed to publish: {e}")
        
        return {'order_id': order_id, 'status': 'created'}

# Subscribers (Consumers)
def payment_handler(event):
    """Payment service subscribes to order.created"""
    print(f"[Payment] Processing payment for {event['order_id']}: ${event['amount']}")
    # Call payment API
    # Publish payment.processed event

def inventory_handler(event):
    """Inventory service subscribes to order.created"""
    print(f"[Inventory] Reserving {len(event['items'])} items")
    # Update inventory
    # Publish inventory.reserved event

def notification_handler(event):
    """Notification service subscribes to order.created"""
    print(f"[Notification] Sending confirmation email to user {event['user_id']}")
    # Send email

def analytics_handler(event):
    """Analytics subscribes to all order events"""
    print(f"[Analytics] Logging event: {event}")
    # Track metrics

# Start consumers
payment_consumer = KafkaEventConsumer('order.created', 'payment-group', payment_handler)
inventory_consumer = KafkaEventConsumer('order.created', 'inventory-group', inventory_handler)
notification_consumer = KafkaEventConsumer('order.created', 'notification-group', notification_handler)
analytics_consumer = KafkaEventConsumer('order.created', 'analytics-group', analytics_handler)

payment_consumer.start()
inventory_consumer.start()
notification_consumer.start()
analytics_consumer.start()

# API
order_service = OrderService()

from flask import Flask, request

app = Flask(__name__)

@app.route('/api/orders', methods=['POST'])
def create_order():
    result = order_service.create_order(
        user_id='user-123',
        items=['item-1', 'item-2']
    )
    return result

# Benefits:
# ✅ Kafka provides reliable message delivery
# ✅ Multiple consumer groups (independent processing)
# ✅ Scalable (add more consumers for parallel processing)
# ✅ Durable (messages persist)
# ✅ Replay capability (consume from beginning)
```

---

## 💡 Mini Project: "Build Event-Driven System"

### Phase 1: Simple Event Bus ⭐

**Requirements:**
- Publish-subscribe pattern
- In-memory event storage
- Multiple subscribers
- Event history

---

### Phase 2: Kafka Integration ⭐⭐

**Requirements:**
- Kafka topics
- Multiple consumer groups
- Event serialization
- Error handling

---

### Phase 3: Enterprise (Event Sourcing) ⭐⭐⭐

**Requirements:**
- Event store (database)
- Event replay
- Snapshots
- Event versioning

---

## ⚖️ Sync vs Async Comparison

| Aspect | Synchronous | Asynchronous |
|--------|------------|--------------|
| **Latency** | Higher (wait) | Lower (no wait) |
| **Coupling** | Tight | Loose |
| **Reliability** | One failure = all fail | Failures isolated |
| **Complexity** | Simple | Complex |
| **Scaling** | Hard | Easy |
| **Debugging** | Easy | Hard |
| **Consistency** | Strong | Eventual |

---

## ❌ Common Mistakes

### Mistake 1: Lost Events

```python
# ❌ In-memory queue
events = []
events.append(event)
# If service crashes: Events lost!

# ✅ Use durable queue (Kafka, RabbitMQ)
kafka_producer.send('events', event)
# Persisted to disk, survives crashes
```

### Mistake 2: No Event Schema

```python
# ❌ Publish inconsistent events
event1 = {'order_id': 123, 'amount': 100}
event2 = {'orderId': 456, 'total': 200}  # Different fields!

# ✅ Define schema
event = {
    'order_id': 123,
    'amount': 100,
    'currency': 'USD',
    'timestamp': '2025-11-11T16:54:00Z',
    'version': 1
}
```

### Mistake 3: Blocking Event Handlers

```python
# ❌ Handler blocks on external call
def handler(event):
    result = requests.post('http://slow-service', timeout=60)
    # If slow-service slow: Handler blocks 60 seconds
    # Other events delayed

# ✅ Handler runs in thread
def handler(event):
    threading.Thread(target=slow_operation, args=(event,)).start()
    return  # Return immediately
```

---

## 📚 Additional Resources

**Event-Driven:**
- [Event Sourcing Pattern](https://martinfowler.com/eaaDev/EventSourcing.html)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [RabbitMQ Tutorials](https://www.rabbitmq.com/getstarted.html)

**Choreography:**
- [Saga Pattern](https://microservices.io/patterns/data/saga.html)
- [Event Choreography](https://www.nginx.com/blog/event-driven-data-management-for-microservices/)


---

## 🎯 Before You Leave

**Can you answer these?**

1. **What's the advantage of event-driven over synchronous?**
   - Answer: Decoupling, scalability, resilience

2. **What's eventual consistency?**
   - Answer: Data not immediately consistent but consistent eventually

3. **What's choreography vs orchestration?**
   - Answer: Choreography = services react independently; Orchestration = central controller

4. **Why use event sourcing?**
   - Answer: Full history, auditability, replay capability

5. **What's thundering herd in event systems?**
   - Answer: Multiple services all publishing/consuming simultaneously

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **Engineer:** "Let's build an event-driven system!"
>
> **After 1 month:** "Events are being processed!"
>
> **After 2 months:** "Why is this event processed 3 times?"
>
> **After 3 months:** "What happened to this event? It disappeared!"
>
> **After 4 months:** "We now have eventual consistency bugs"
>
> **Senior Engineer:** "Welcome to event-driven systems, where bugs arrive eventually." 🎭

---

[← Back to Main](../README.md) | [Previous: Distributed Caching](28-distributed-caching.md) | [Next: CQRS →](30-cqrs.md)

---

**Last Updated:** November 11, 2025  
**Difficulty:** ⭐⭐⭐ Intermediate-Advanced (consistency challenges)  
**Time to Read:** 26 minutes  
**Time to Implement:** 5-8 hours per phase  

---

*Event-driven architecture: Making your system more resilient and your debugging 10x harder.* 🚀