
# Abstraction

**Abstraction** is an OOP principle where only essential features of an object are exposed to the outside world, hiding internal details and implementation.
It enables developers to work with higher-level concepts, designing flexible and maintainable interfaces while masking complexity.

***

## Real-World Example: Email Notification System in Backend

Suppose you need to send notifications via different channels: **Email**, **SMS**, **Push**. Each has different implementations, but exposes a simple, common interface.

### Abstract Base Class

```python
from abc import ABC, abstractmethod

class Notifier(ABC):
    @abstractmethod
    def send(self, message, recipient):
        pass
```

- Using the `abc` module, `Notifier` enforces a standard interface, yet leaves implementation up to subclasses.


### Concrete Implementations

```python
class EmailNotifier(Notifier):
    def send(self, message, recipient):
        # Internal implementation (SMTP integration)
        print(f"Sending email to {recipient}: {message}")

class SMSNotifier(Notifier):
    def send(self, message, recipient):
        # Internal implementation (SMS API)
        print(f"Sending SMS to {recipient}: {message}")
```


### Abstraction in Usage

```python
def notify_user(notifier: Notifier, message, recipient):
    notifier.send(message, recipient)

# The caller doesn't need to know *how* the message is sent!
notifiers = [EmailNotifier(), SMSNotifier()]
for n in notifiers:
    notify_user(n, "Your order shipped!", "alice@domain.com")
# Output:
# Sending email to alice@domain.com: Your order shipped!
# Sending SMS to alice@domain.com: Your order shipped!
```


***

## Production Backend Context

- **Frameworks/SDKs:** Use abstract base classes for plugins (e.g., authentication, logging, external integrations)
- **APIs:** Define abstract request handlers/services to make code extensible for future needs
- **Maintainability:** Changing internals of a notifier doesn’t affect callers, as long as the interface is stable

***

## Other Abstraction Patterns

### Example: Storage Backends

```python
class StorageBackend(ABC):
    @abstractmethod
    def save(self, data):
        pass

class S3Storage(StorageBackend):
    def save(self, data):
        # Actual S3 upload logic

class FileStorage(StorageBackend):
    def save(self, data):
        # Write to local filesystem
```

Use `StorageBackend` in API code and swap storage backends easily—implementation remains hidden.

***

## Summary

Abstraction lets backend developers design clean, focused interfaces, hiding complexity and allowing interchangeability.
It’s critical for robust production systems—maintainable, flexible, and future-proof by design.

