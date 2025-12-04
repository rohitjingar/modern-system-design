It’s a design pattern that lets an object change its behavior when its internal state changes, as if it became a different object

***

## 1. The Bad Example: “If-Else State Machine Soup”

Suppose the order workflow is tangled like this:

```python
def update_order(order, action):
    if order.state == "created":
        if action == "pay":
            order.state = "paid"
            # do billing
        elif action == "cancel":
            order.state = "cancelled"
        else:
            raise Exception("Invalid transition.")
    elif order.state == "paid":
        if action == "pack":
            order.state = "packed"
        elif action == "refund":
            order.state = "refunded"
        else:
            raise Exception("Invalid transition.")
    elif order.state == "packed":
        if action == "ship":
            order.state = "shipped"
        else:
            raise Exception("Invalid transition.")
    # ...and so on—gets worse as order logic grows!
```


### Why is this bad?

- **Grows out of control:** New state or action = edit EVERYWHERE
- **Error-prone:** Easy to miss a transition or allow an invalid one.
- **No encapsulation:** All logic smeared into one method, hard to test each state.
- **Hard to add features:** Want tracking, hooks, logs, or side-effects for just one state? Good luck.

**Humour Break:**
> “Your state machine has so many nested ‘if’ blocks that even Python’s indentation gets confused!”

***

## 2. The Good Example: **State Pattern for Order Workflows**

With State Pattern, each order state is a separate object/class and *encapsulates its own behavior and valid transitions*. The order object delegates all state-dependent logic to its current state.

### Pythonic State Pattern: E-commerce Order Example

```python
from abc import ABC, abstractmethod

# 1. Define the State abstract base
class OrderState(ABC):
    @abstractmethod
    def next_state(self, order, action):
        pass
    @abstractmethod
    def __str__(self):
        pass

# 2. Concrete State classes
class CreatedState(OrderState):
    def next_state(self, order, action):
        if action == "pay":
            print("[Order] Payment received, moving to Paid state.")
            order.state = PaidState()
        elif action == "cancel":
            print("[Order] Order cancelled.")
            order.state = CancelledState()
        else:
            raise Exception("Invalid action in Created state.")
    def __str__(self):
        return "Created"

class PaidState(OrderState):
    def next_state(self, order, action):
        if action == "pack":
            print("[Order] Order packed and ready for shipment.")
            order.state = PackedState()
        elif action == "refund":
            print("[Order] Order refunded.")
            order.state = RefundedState()
        else:
            raise Exception("Invalid action in Paid state.")
    def __str__(self):
        return "Paid"

class PackedState(OrderState):
    def next_state(self, order, action):
        if action == "ship":
            print("[Order] Order shipped!")
            order.state = ShippedState()
        else:
            raise Exception("Invalid action in Packed state.")
    def __str__(self):
        return "Packed"

class ShippedState(OrderState):
    def next_state(self, order, action):
        if action == "deliver":
            print("[Order] Order delivered!")
            order.state = DeliveredState()
        else:
            raise Exception("Invalid action in Shipped state.")
    def __str__(self):
        return "Shipped"

class DeliveredState(OrderState):
    def next_state(self, order, action):
        raise Exception("Order already delivered. No further actions allowed.")
    def __str__(self):
        return "Delivered"

class CancelledState(OrderState):
    def next_state(self, order, action):
        raise Exception("Order has been cancelled. No further actions allowed.")
    def __str__(self):
        return "Cancelled"

class RefundedState(OrderState):
    def next_state(self, order, action):
        raise Exception("Order has been refunded. No further actions allowed.")
    def __str__(self):
        return "Refunded"

# 3. Order context class
class Order:
    def __init__(self):
        self.state = CreatedState()  # initial state

    def handle_action(self, action):
        print(f"[Order] Action: {action}, Current State: {self.state}")
        self.state.next_state(self, action)
        print(f"[Order] New State: {self.state}")

# --- Usage: every state transition is clear and encapsulated
order = Order()
order.handle_action("pay")
order.handle_action("pack")
order.handle_action("ship")
order.handle_action("deliver")
# order.handle_action("refund")  # will throw error: already delivered

# You can create and test individual state classes in isolation now!
```


### **Why Is This Better?**

- **Encapsulation:** Each state knows its valid actions and transitions.
- **Extensible:** Add new states or transitions by creating/updating just one class.
- **Testable:** Test and debug transitions per state, not a single complex method.
- **Features per state:** Logging, side-effects, triggers—easy to do by overriding relevant state methods.

**Humour Break:**
> “With State pattern, orders move like chess pieces—no more illegal moves, and no more code headaches!”

***

## 3. **Real-World Backend Scenario**

- **Payments:** Transactions with multiple states (initiated, authorized, settled, failed, refunded…)
- **Support Ticketing:** New, assigned, in-progress, resolved, escalated, closed.
- **Resource Lifecycle:** VMs, containers, or resources move from pending, running, stopping, stopped, terminated.
- **User Onboarding:** Registered, verified, activated, suspended, banned.

**Frameworks:**

- Workflow engines (like AWS Step Functions, Camunda) use state/transition objects at their core.

***

## 4. **Production Trade-Offs**

- **Too many states?** Design hierarchies or collapse into state groups.
- **Persistence:** Store current state as a string or enum in DB, then map to state class in code.
- **Auditability:** You can log/track each transition cleanly in one place.

***

## 5. **Summary**

- **Bad Example:** Bloated if-else soup, hard to add/extend/maintain.
- **State Example:** Transitions and behaviors encapsulated in per-state classes—easy to reason about and scale up.
- **Real-World Use:** Order/stateful workflows, lifecycle management, anywhere states matter.


