# Cohesion vs Coupling

**Cohesion** and **Coupling** are core design principles in software engineering that impact the maintainability, reliability, and scalability of backend codebases.

***

## Cohesion

**Cohesion** describes how closely related the functions and data within a single module or class are.

- **High Cohesion:** All responsibilities of a class/module are directly related. Easier to maintain, extend, and test.
- **Low Cohesion:** The class/module has mixed, unrelated responsibilities, increasing confusion and error risk.


### Example: High Cohesion (Production Python - User Service)

```python
class UserService:
    def create_user(self, email, password):
        # User creation logic

    def authenticate_user(self, email, password):
        # Authentication logic

    def update_user(self, user_id, data):
        # User update logic
```

All methods are centered around user management.

***

## Coupling

**Coupling** measures how strongly one module/class depends on others.

- **Low Coupling:** Modules/classes interact through well-defined interfaces and minimal dependencies. Enables independent changes and unit testing.
- **High Coupling:** Modules/classes are tightly interdependent, so changes in one often force changes in others.


### Example: Low Coupling (Production Python - Decoupled Notification Service)

```python
class EmailNotifier:
    def send(self, message, recipient):
        pass

class OrderService:
    def __init__(self, notifier):
        self.notifier = notifier

    def place_order(self, user, item):
        # Order placement logic
        self.notifier.send("Order placed", user.email)
```

`OrderService` interacts with `EmailNotifier` via its interface. You could easily swap in `SMSNotifier` with no internal change.

#### Example: High Coupling (Poor Practice)

```python
class OrderService:
    def place_order(self, user, item):
        # Order placement logic
        # Directly uses email-specific implementation:
        send_email("Order placed", user.email)
```

Here, `OrderService` is tightly coupled to a specific notification method—hard to change or extend later.

***

## Production Context

- **Aim for:** High cohesion within classes/modules; low coupling between them.
- **Benefits:** Easier feature addition, safer refactoring, and better testability.
- **Anti-patterns:** "God classes" (low cohesion, high coupling) that handle unrelated logic and are tightly bound to other code.

***

## Summary Table

| Principle | Description | Example | Goal |
| :-- | :-- | :-- | :-- |
| Cohesion | Relatedness of a class/module’s internals | UserService | High |
| Coupling | Dependency strength between code units | OrderService/Notifier | Low |


***

**Summary**
Backend systems are easier to build, change, and scale with **high cohesion** and **low coupling**, keeping code organized and adaptable for future needs.

