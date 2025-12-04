# 20. Pub/Sub Systems

Pub/Sub is like a magazine subscription: you publish an issue, everyone subscribed gets it automatically. Except if someone's away, they miss it. And if you cancel your subscription, you don't get back issues. It's not email (everyone gets it), it's "opt-in broadcasting." 📰

[← Back to Main](../README.md) | [Previous: Message Queues](19-message-queues.md) | [Distributed Logging & Monitoring](21-distributed-logging.md)

---

## 🎯 Quick Summary

**Pub/Sub (Publish-Subscribe)** is a messaging pattern where publishers send messages to topics, and subscribers receive them. Unlike queues (one consumer per message), pub/sub broadcasts to all subscribers. Perfect for: real-time notifications, event streaming, decoupled systems. Google Pub/Sub, AWS SNS, Redis Pub/Sub, Apache Kafka. Essential for event-driven architectures and real-time features like notifications, live feeds, and monitoring.

Think of it as: **Pub/Sub = Broadcast to Everyone Interested**

---

## 🌟 Beginner Explanation

### Queue vs Pub/Sub

**MESSAGE QUEUE (One Message → One Consumer):**

```
Queue: [Order-1, Order-2, Order-3]

Consumer 1: Takes Order-1
Consumer 2: Takes Order-2
Consumer 3: Takes Order-3

Key: Each message consumed by ONE consumer only
Used: Order processing, email delivery, tasks
```

**PUB/SUB (One Message → All Subscribers):**

```
Publisher: "New order received!"
         ↓
Topic: orders

Subscriber 1 (Email Service): Gets "New order!" → Send email
Subscriber 2 (Analytics):    Gets "New order!" → Update stats
Subscriber 3 (Inventory):    Gets "New order!" → Update stock
Subscriber 4 (Notification): Gets "New order!" → Send push

Key: ALL subscribers get the SAME message
Used: Notifications, live updates, event streaming
```

### Real-World Analogy

```
YOUTUBE SUBSCRIBER MODEL (Pub/Sub):

Creator publishes video → ALL subscribers get notification
├─ Subscriber 1: Gets notification
├─ Subscriber 2: Gets notification
├─ Subscriber 3: Gets notification
└─ Subscriber 10,000: Gets notification

Everyone sees the video simultaneously
(Not: Only one person can watch)

If you're not subscribed: You don't get notified
(No history, no backlog, you miss it)
```

### When Each Is Used

```
USE QUEUE WHEN:
├─ One consumer processes each message
├─ Task distribution (work sharing)
├─ Email, SMS sending
├─ Order processing
├─ Job scheduling
└─ Need guaranteed delivery to one

USE PUB/SUB WHEN:
├─ Multiple consumers need same message
├─ Real-time notifications
├─ Event broadcasting
├─ Live feeds (Twitter, sports scores)
├─ Monitoring alerts
├─ Activity streams
└─ Multiple independent systems react to event
```

---

## 🔬 Advanced Explanation

### Pub/Sub Architecture

```
PUBLISHER:
├─ Creates event/message
├─ Sends to topic
└─ Doesn't wait for subscribers

TOPIC (Channel):
├─ Named destination (e.g., "orders", "user_login")
├─ Holds message briefly
├─ Broadcasts to all subscribers
└─ Message might be transient (lost if no subscribers)

SUBSCRIBER:
├─ Registers interest in topic
├─ Receives all messages published
├─ Processes independently
└─ Can subscribe/unsubscribe dynamically

KEY DIFFERENCE: No guarantee subscribers exist
Subscriber joins AFTER publish? Misses the message!
```

### Delivery Semantics

**FANOUT (All Subscribers):**

```
Publisher: "New user signed up!"
    ↓
All subscribers receive it:
├─ Email service
├─ Analytics
├─ Notification service
├─ Recommendation engine
├─ Feed service

Benefit: Event reaches everyone interested
Cost: Each subscriber must process
```

**RETAINED MESSAGES (History):**

```
Pub/Sub usually: Transient messages only
├─ Subscriber 1: Processes message
├─ Subscriber 2 (joins later): DOESN'T get it
└─ Message lost

Kafka-style: Retains messages in log
├─ Subscriber 1: Processes message
├─ Subscriber 2 (joins later): Can replay from beginning
└─ Full history available

Benefit: New subscribers can catch up
Cost: More storage
```

**FILTERING (Topic Subscriptions):**

```
Topics:
├─ orders.created
├─ orders.shipped
├─ orders.delivered
├─ user.signup
├─ user.deleted

Subscriber can filter:
├─ "I only care about orders.created and orders.shipped"
├─ Another subscriber: "I only want user.* events"
└─ Filtering at publish time (efficiency!)

Alternative: Wildcard subscriptions
├─ "orders.*" matches all order events
├─ "user.*" matches all user events
```

### Pub/Sub vs Pub/Queue Hybrid

```
PURE PUB/SUB (Google Pub/Sub):
├─ Publish to topic
├─ Each message seen by all subscribers
├─ Transient (no history)

HYBRID (Kafka):
├─ Publish to topic
├─ Multiple consumer groups
├─ Each group has one consumer per partition
├─ Retains messages
└─ Can function like queue OR pub/sub

AWS SNS + SQS (Hybrid):
├─ SNS publishes to topic
├─ SQS queues can subscribe to topic
├─ Multiple SQS queues = multiple independent consumers
└─ Best of both worlds!
```

### At-Least-Once vs Fire-and-Forget

**FIRE-AND-FORGET (Fast, Lossy):**

```
Publisher sends message
Doesn't wait for subscriber acknowledgment
If subscriber down: Message lost

Used: Analytics, logs, metrics
Acceptable: Losing occasional event OK
```

**AT-LEAST-ONCE (Reliable):**

```
Publisher sends message
Waits for subscriber acknowledgment
If subscriber doesn't ACK: Resend

Used: Critical events, financial
Cost: Slower, duplicates possible
```

### Pub/Sub Services

**GOOGLE CLOUD PUB/SUB:**

```
Pros:
✅ Fully managed (serverless)
✅ Simple API
✅ Good for events
✅ Auto-scaling

Cons:
❌ Transient (no history)
❌ GCP only
❌ Can be expensive

Good for: Real-time notifications, live updates
```

**APACHE KAFKA:**

```
Pros:
✅ High throughput (1M+ msgs/sec)
✅ Persistent (weeks of history)
✅ Replay messages
✅ Open source
✅ Excellent for streaming

Cons:
❌ Complex setup
❌ Needs cluster management
❌ Overkill for simple use

Good for: Event streaming, data pipelines
```

**REDIS PUB/SUB:**

```
Pros:
✅ Simple, fast
✅ In-memory
✅ Good for real-time

Cons:
❌ No persistence (messages lost on crash)
❌ No history
❌ Single-machine (not distributed)
❌ Not great for high volume

Good for: Chat, real-time notifications
```

**AWS SNS (Simple Notification Service):**

```
Pros:
✅ Fully managed
✅ Integrates with AWS services
✅ Fanout to multiple endpoints
✅ Mobile push notifications

Cons:
❌ Limited filtering
❌ No message history
❌ AWS only

Good for: Broadcasting events, notifications
```

---

## 🐍 Python Code Example

### ❌ Without Pub/Sub (Tightly Coupled)

```python
# ===== WITHOUT PUB/SUB (TIGHTLY COUPLED) =====

class OrderService:
    """Order service that calls other services directly"""
    
    def __init__(self, email_service, inventory_service, analytics_service):
        self.email = email_service
        self.inventory = inventory_service
        self.analytics = analytics_service
    
    def create_order(self, user_id, product_id, quantity):
        """Create order and notify all services"""
        
        # 1. Create order (DB)
        order = {
            'id': 123,
            'user_id': user_id,
            'product_id': product_id,
            'quantity': quantity
        }
        print(f"Order created: {order['id']}")
        
        # 2. Send email (call directly)
        try:
            self.email.send_confirmation(user_id)
        except Exception as e:
            print(f"Email failed: {e}")
        
        # 3. Update inventory (call directly)
        try:
            self.inventory.reduce_stock(product_id, quantity)
        except Exception as e:
            print(f"Inventory failed: {e}")
        
        # 4. Log analytics (call directly)
        try:
            self.analytics.log_order(user_id, product_id)
        except Exception as e:
            print(f"Analytics failed: {e}")
        
        return order

# Problems:
# ❌ Tight coupling (OrderService knows about all services)
# ❌ If any service slow: create_order waits
# ❌ If any service fails: create_order fails
# ❌ Hard to add new service (modify OrderService)
# ❌ Hard to test (mock all dependencies)
```

### ✅ Simple Pub/Sub (In-Memory)

```python
# ===== SIMPLE PUB/SUB (IN-MEMORY) =====

from typing import Callable, Dict, List
from dataclasses import dataclass

@dataclass
class Event:
    """Event in pub/sub system"""
    topic: str
    data: Dict

class SimplePubSub:
    """Simple in-memory pub/sub"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, topic: str, handler: Callable):
        """Subscribe to topic"""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(handler)
    
    def publish(self, topic: str, data: Dict):
        """Publish event to topic"""
        event = Event(topic=topic, data=data)
        
        if topic in self.subscribers:
            for handler in self.subscribers[topic]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Handler error: {e}")

class OrderService:
    """Order service using pub/sub"""
    
    def __init__(self, pubsub: SimplePubSub):
        self.pubsub = pubsub
    
    def create_order(self, user_id, product_id, quantity):
        """Create order and publish event"""
        
        # 1. Create order
        order = {
            'id': 123,
            'user_id': user_id,
            'product_id': product_id,
            'quantity': quantity
        }
        print(f"Order created: {order['id']}")
        
        # 2. Publish event (don't wait!)
        self.pubsub.publish('order.created', order)
        
        return order

# Subscribers react to events
def email_handler(event: Event):
    """Email service subscribes to order.created"""
    order = event.data
    print(f"  [Email] Sending confirmation for order {order['id']}")

def inventory_handler(event: Event):
    """Inventory service subscribes to order.created"""
    order = event.data
    print(f"  [Inventory] Reducing stock by {order['quantity']}")

def analytics_handler(event: Event):
    """Analytics service subscribes to order.created"""
    order = event.data
    print(f"  [Analytics] Logging order {order['id']}")

# Usage
print("=== SIMPLE PUB/SUB ===\n")

pubsub = SimplePubSub()
order_service = OrderService(pubsub)

# Subscribers register
pubsub.subscribe('order.created', email_handler)
pubsub.subscribe('order.created', inventory_handler)
pubsub.subscribe('order.created', analytics_handler)

# Create order (publishes event)
order_service.create_order(user_id=1, product_id=101, quantity=5)

# Benefits:
# ✅ Loose coupling (OrderService doesn't know subscribers)
# ✅ Fast (doesn't wait for handlers)
# ✅ Easy to add services (just subscribe)
# ✅ Easy to test (mock subscribers)
```

### ✅ Production Pub/Sub (Advanced)

```python
# ===== PRODUCTION PUB/SUB =====

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional
from datetime import datetime
import json

@dataclass
class Event:
    """Event with metadata"""
    id: str
    topic: str
    data: Dict
    timestamp: float
    source: str
    version: int = 1

class Subscription:
    """Subscription with filtering"""
    
    def __init__(self, topic: str, handler: Callable, filter_fn: Optional[Callable] = None):
        self.topic = topic
        self.handler = handler
        self.filter_fn = filter_fn
    
    def should_handle(self, event: Event) -> bool:
        """Check if subscription should handle event"""
        if self.filter_fn:
            return self.filter_fn(event)
        return True

class ProductionPubSub:
    """Production pub/sub with advanced features"""
    
    def __init__(self):
        self.subscriptions: Dict[str, List[Subscription]] = {}
        self.history: List[Event] = []
        self.event_id_counter = 0
    
    def subscribe(self, topic: str, handler: Callable, 
                 filter_fn: Optional[Callable] = None) -> str:
        """Subscribe to topic with optional filter"""
        
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        
        subscription = Subscription(topic, handler, filter_fn)
        self.subscriptions[topic].append(subscription)
        
        return f"sub-{len(self.subscriptions[topic])}"
    
    def publish(self, topic: str, data: Dict, source: str):
        """Publish event to topic"""
        
        self.event_id_counter += 1
        event = Event(
            id=f"evt-{self.event_id_counter}",
            topic=topic,
            data=data,
            timestamp=datetime.now().timestamp(),
            source=source
        )
        
        # Store in history (for replay)
        self.history.append(event)
        
        # Deliver to subscribers
        if topic in self.subscriptions:
            for subscription in self.subscriptions[topic]:
                if subscription.should_handle(event):
                    try:
                        subscription.handler(event)
                    except Exception as e:
                        print(f"Handler error: {e}")
        
        return event.id
    
    def get_event_history(self, topic: str, limit: int = 10):
        """Get event history (for replay)"""
        return [e for e in self.history if e.topic == topic][-limit:]
    
    def get_stats(self) -> Dict:
        """Get pub/sub statistics"""
        total_subscriptions = sum(len(subs) for subs in self.subscriptions.values())
        return {
            'topics': len(self.subscriptions),
            'total_subscriptions': total_subscriptions,
            'events_published': len(self.history)
        }

# Usage
print("=== PRODUCTION PUB/SUB ===\n")

pubsub = ProductionPubSub()

# Email service (all events)
def email_subscriber(event: Event):
    print(f"  [Email] Processing {event.topic}: {event.data}")

# Analytics (only high-value orders)
def analytics_subscriber(event: Event):
    if event.data.get('amount', 0) > 100:
        print(f"  [Analytics] High-value order: {event.data}")

# Subscribe with filtering
pubsub.subscribe('order.created', email_subscriber)
pubsub.subscribe(
    'order.created',
    analytics_subscriber,
    filter_fn=lambda e: e.data.get('amount', 0) > 100  # Only high-value orders
)

# Publish events
print("Publishing events:")
pubsub.publish('order.created', 
              {'order_id': 1, 'amount': 50}, 
              source='web')
pubsub.publish('order.created',
              {'order_id': 2, 'amount': 150},
              source='mobile')

# Replay history
print(f"\nEvent history: {pubsub.get_event_history('order.created')}")
print(f"\nStats: {pubsub.get_stats()}")

# Output shows:
# ✅ Event filtering
# ✅ Event history
# ✅ Async delivery
# ✅ Metadata tracking
```

---

## 💡 Mini Project: "Build a Pub/Sub System"

### Phase 1: Simple In-Memory ⭐

**Requirements:**
- Publish/Subscribe
- Multiple subscribers
- Basic event dispatch
- No persistence

---

### Phase 2: Advanced (Filtering & History) ⭐⭐

**Requirements:**
- Topic filtering
- Event history/replay
- Wildcard subscriptions
- Error handling
- Metrics

---

### Phase 3: Enterprise (Distributed) ⭐⭐⭐

**Requirements:**
- Network communication
- Persistence (disk/DB)
- Consumer groups
- Dead letter queue
- Monitoring/alerting

---

## ⚖️ Pub/Sub Services Comparison

| Feature | Google Pub/Sub | Kafka | Redis | AWS SNS |
|---------|---|---|---|---|
| **Throughput** | 1M+/sec | 1M+/sec | 1M+/sec | 1M+/sec |
| **Persistence** | ❌ | ✅ | ❌ | ❌ |
| **History** | ❌ | ✅ | ❌ | ❌ |
| **Managed** | ✅ | ❌ | ❌ | ✅ |
| **Filtering** | Limited | Good | No | Limited |
| **Complexity** | Low | High | Low | Medium |
| **Cost** | Pay-per-use | Self-hosted | Self-hosted | Pay-per-use |

---

## 🎯 When to Use Pub/Sub

```
✅ USE PUB/SUB WHEN:
- Multiple systems react to events
- Real-time notifications needed
- Broadcasting events
- Event-driven architecture
- Decoupling systems
- Live features (chat, feeds, scores)

❌ DON'T USE WHEN:
- One consumer per message (use queue)
- Guaranteed individual delivery
- History critical (use Kafka instead)
- Complex ordering (use queue)
```

---

## ❌ Common Mistakes

### Mistake 1: Assuming Subscribers Always Exist

```python
# ❌ Publish event before subscribers ready
pubsub.publish('order.created', order_data)
# Subscribers haven't registered yet! Event lost!

# ✅ Ensure subscribers registered first
# OR use persistent pub/sub (Kafka)
```

### Mistake 2: Mixing Queue and Pub/Sub Logic

```python
# ❌ Treating pub/sub like queue
# Two subscribers: each should get message
# But treating as: only one processes

# ✅ Understand the difference
# Queue: one consumer per message (work distribution)
# Pub/Sub: all subscribers get message (broadcast)
```

### Mistake 3: No Error Handling in Subscribers

```python
# ❌ One subscriber fails, blocks others
for subscriber in subscribers:
    subscriber.handle(event)  # If one fails, rest don't run!

# ✅ Handle errors per subscriber
for subscriber in subscribers:
    try:
        subscriber.handle(event)
    except:
        log_error()  # One failure doesn't block others
```

---

## 📚 Additional Resources

**Google Cloud Pub/Sub:**
- [Google Cloud Pub/Sub](https://cloud.google.com/pubsub)
- [Pub/Sub Concepts](https://cloud.google.com/pubsub/docs/concepts)

**Kafka:**
- [Apache Kafka](https://kafka.apache.org/)
- [Kafka as Pub/Sub](https://kafka.apache.org/documentation/#consumerconfigs)

**AWS SNS:**
- [AWS SNS](https://aws.amazon.com/sns/)
- [SNS + SQS Pattern](https://docs.aws.amazon.com/sns/latest/dg/sns-sqs-as-subscriber.html)


---

## 🎯 Before You Leave

**Can you answer these?**

1. **How is Pub/Sub different from Queue?**
   - Answer: Queue = one consumer; Pub/Sub = all subscribers

2. **What's fanout?**
   - Answer: One message to multiple subscribers

3. **Why use Pub/Sub over direct calls?**
   - Answer: Decoupling, scalability, resilience

4. **What's the problem with transient messages?**
   - Answer: Late subscribers miss events (no history)

5. **Why filter at publish time?**
   - Answer: Efficiency (less network traffic)

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **Startup:** "We need real-time notifications!"
>
> **DevOps:** "Use Pub/Sub."
>
> **Developer:** "But what if the user isn't subscribed when the event happens?"
>
> **DevOps:** "They miss the notification."
>
> **Developer:** "That's terrible UX!"
>
> **DevOps:** "Use Kafka if you want history."
>
> **Developer:** "That's way too complex."
>
> **DevOps:** "Welcome to distributed systems." 🎭

---

[← Back to Main](../README.md) | [Previous: Message Queues](19-message-queues.md) | [Distributed Logging & Monitoring](21-distributed-logging.md)

---

**Last Updated:** November 10, 2025  
**Difficulty:** ⭐⭐⭐ Intermediate-Advanced (event-driven)  
**Time to Read:** 25 minutes  
**Time to Build System:** 3-6 hours per phase  

---

*Pub/Sub: Making sure everyone who cares hears about it at the same time.* 🚀