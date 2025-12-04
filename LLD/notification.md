# Notification Service

Let’s design a **Notification Service** using **Observer + Strategy** patterns—just as they’re tested in backend interviews and used in real-world microservices.

### **Scenario:**

You’re building a notification system for a platform that sends messages (order updates, alerts, marketing) by Email, SMS, and Push—sometimes with personalized rules (timing, language, channel preference, etc.).

- **Observer** lets multiple handlers receive and react to each notification event (e.g., database logger, audit, metrics, failover).
- **Strategy** lets you swap message formatting or channel selection logic on the fly (e.g., promotional vs transaction, best channel per user).

***

## 1. **Bad Example: Hardcoded Sending \& Scattershot Channel Logic**

```python
def send_notification(user_id, msg, msg_type):
    # Hardcoded logic—ugh!
    if msg_type == "order":
        send_email(user_id, msg)
        send_sms(user_id, msg)
    elif msg_type == "promo":
        send_push(user_id, msg)
        send_email(user_id, msg)  # but only if user opted in!
        # ...try to add logging, failover, etc. by copying everywhere...
    # Want to change rules or channels? Refactor all handlers, everywhere.
```

**Problems:**

- **No extensibility:** Changing channel logic means rewriting everything.
- **No observers:** Can’t easily add logging, retry, metrics, or fallback.
- **Not testable:** No way to swap behaviors or intercept for audits/tests.

**Humour Break:**
> “Hardcoding notification logic is like sending spam—nobody wants it, and it’s impossible to manage.”

***

## 2. **Good Example: Observer + Strategy For Notification Service**

**Observer:**
Define a notification event; observers (handlers) react—send, log, audit, etc.

**Strategy:**
Define multiple sending/logging/formatting algorithms dynamically selected per message/user/context.

***

### **Python Implementation**

```python
from abc import ABC, abstractmethod

# --- Strategy: Message sending algorithm ---
class NotificationStrategy(ABC):
    @abstractmethod
    def send(self, user_id, msg):
        pass

class EmailStrategy(NotificationStrategy):
    def send(self, user_id, msg):
        print(f"[Email] {user_id}: {msg}")

class SMSStrategy(NotificationStrategy):
    def send(self, user_id, msg):
        print(f"[SMS] {user_id}: {msg}")

class PushStrategy(NotificationStrategy):
    def send(self, user_id, msg):
        print(f"[Push] {user_id}: {msg}")

class PromoStrategy(NotificationStrategy):
    def send(self, user_id, msg):
        # Custom promo logic, e.g., Push for some, Email for others
        if user_id.endswith("9"):
            print(f"[Push] {user_id}: {msg} (Promo)")
        else:
            print(f"[Email] {user_id}: {msg} (Promo)")

# --- Observer: Notification event listeners ---
class NotificationListener(ABC):
    @abstractmethod
    def on_notification_sent(self, user_id, msg, channel):
        pass

class AuditListener(NotificationListener):
    def on_notification_sent(self, user_id, msg, channel):
        print(f"[Audit] {channel} notification sent to {user_id}")

class MetricsListener(NotificationListener):
    def on_notification_sent(self, user_id, msg, channel):
        print(f"[Metrics] {channel} notification counted for {msg[:10]}...")

# --- Notification Service with both patterns
class NotificationService:
    def __init__(self, strategy: NotificationStrategy):
        self.strategy = strategy
        self.listeners = []

    def add_listener(self, listener: NotificationListener):
        self.listeners.append(listener)

    def send(self, user_id, msg):
        # Send using strategy
        self.strategy.send(user_id, msg)
        # Notify observers
        channel = self.strategy.__class__.__name__.replace("Strategy", "")
        for listener in self.listeners:
            listener.on_notification_sent(user_id, msg, channel)

# --- Usage ---
notifier = NotificationService(EmailStrategy())
notifier.add_listener(AuditListener())
notifier.add_listener(MetricsListener())

notifier.send("user123", "Order shipped!")

# Swap to SMS
notifier.strategy = SMSStrategy()
notifier.send("user999", "Order delivered!")

# Swap to PromoStrategy for marketing campaign
notifier.strategy = PromoStrategy()
notifier.send("user999", "Big Sale - 50% Off!")

# Output:
# [Email] user123: Order shipped!
# [Audit] Email notification sent to user123
# [Metrics] Email notification counted for Order shi...
# [SMS] user999: Order delivered!
# [Audit] SMS notification sent to user999
# [Metrics] SMS notification counted for Order deli...
# [Push] user999: Big Sale - 50% Off! (Promo)
# [Audit] Push notification sent to user999
# [Metrics] Push notification counted for Big Sale ...
```


***

### **Why Is This Better?**

- **Flexible:** Swap sending/channel logic at runtime per message/user/context.
- **Extensible:** Add infinite observers (audit, retry, alert, logging, webhook) by plugging listeners.
- **Decoupled:** Notification logic and delivery/channels are cleanly separated.
- **Testable:** Mock strategies and listeners for tests/audit.

**Humour Break:**
> “Real pattern masters swap notification channels so fast, marketing thinks they’re magic.”

***

## 3. **Real-World Use Cases**

- **E-commerce:** Transactional notifications (order/shipment), promotional campaigns, failover channels.
- **Banking/FinTech:** Alerts, fraud warnings, multi-channel high-delivery requirement.
- **Social Apps:** Push for engagement, email for summary/verification, SMS for critical action.
- **Internal tools:** Incident alerts, multi-person audit logs, dynamic triggers.

***

## 4. **Production Extensions**

- Feature flags to pick strategies by user segment, country, or campaign type.
- Observers for regulatory logging, analytics, escalation triggers.
- Retries, queueing, prioritization pluggable as observers/strategies.

***

## **Summary**

- **Observer:** Multi-channel listeners and dynamic event hooks.
- **Strategy:** Flexible, swappable delivery algorithms for every scenario.
- **Real-world robustness:** No matter how crazy notification requirements get, your design survives!
