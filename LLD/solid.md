# 🟦 **SOLID Principles**

## **S → Single Responsibility Principle (SRP)**

> **A class should have one and only one reason to change.**

### 🔥 Meaning:

Each class should do **one thing only**, and do it well.

### 🧠 Why?

* Clear code
* Easy to test
* Highly maintainable
* Reduces bugs

### 💡 Real-life example:

A **restaurant waiter** does not cook food, clean tables, and do billing.
Each role has one responsibility.

### 🧱 Good Design Example:

```python
class InvoiceGenerator:
    def generate(self, order): ...

class InvoicePrinter:
    def print(self, invoice): ...
```

### 🚫 Bad Design:

```python
class Invoice:
    def calculate_total(self): ...
    def print_invoice(self): ...   # printing is not invoice's job
    def save_to_db(self): ...      # db logic shouldn't be here
```

### 🧩 Interview Tip:

SRP is the most violated principle in real systems.

---

# 🟨 **O → Open / Closed Principle (OCP)**

> **Software entities should be open for extension but closed for modification.**

### 🔥 Meaning:

You should be able to **add new features** without **modifying existing code**.

### 💡 Example (Spot allocation strategy):

```python
class Strategy(ABC):
    def select_spot(...): ...

class NearestSpotStrategy(Strategy): ...
class CheapestSpotStrategy(Strategy): ...
```

To add a new strategy (e.g., EVChargingStrategy),
➡️ **you do NOT modify ParkingLot**.

### 🚫 Bad:

```python
if strategy == "nearest":
    ...
elif strategy == "cheapest":
    ...
elif strategy == "random":
    ...
```

You modify code every time you add new strategy.

### 🧠 Interview Tip:

Talk about **Strategy Pattern**, **Factory Pattern**, **Interfaces**, and **Polymorphism** when asked about OCP.

---

# 🟩 **L → Liskov Substitution Principle (LSP)**

> **Child classes should be usable wherever parent classes are expected.**

### 🔥 Meaning:

If class B inherits class A, then A should be replaceable with B **without breaking the system**.

### 💡 Example (Vehicles):

You should be able to write:

```python
def park(v: Vehicle):
    ...
```

And safely do:

```python
park(Car("..."))
park(Bike("..."))
park(Truck("..."))
```

### 🚫 LSP Violation:

If subclass changes behavior drastically:

```python
class Bird:
    def fly(self): pass

class Ostrich(Bird):
    def fly(self):
        raise Exception("Ostrich cannot fly")  # breaks LSP
```

### 🧠 Interview Tip:

If subclass breaks assumptions of the base class → LSP violation.

---

# 🟧 **I → Interface Segregation Principle (ISP)**

> **Clients should not be forced to depend on methods they do not use.**

### 🔥 Meaning:

Instead of one fat interface, create **multiple small, specific interfaces**.

### 🚫 Bad:

```python
class Worker(ABC):
    def work(self): ...
    def eat(self): ...
```

What about a robot worker?

### 👍 Good:

```python
class Workable(ABC):
    def work(self): ...

class Eatable(ABC):
    def eat(self): ...
```

Robot implements only Workable, human implements both.

### 🧠 Interview Tip:

ISP = avoid **fat interfaces**.

---

# 🟥 **D → Dependency Inversion Principle (DIP)**

> **Depend on abstractions, not on concrete classes.**

### 🔥 Meaning:

High-level modules should not depend on low-level modules.
Both should depend on **interfaces**.

### 💡 Good:

```python
class PaymentMethod(ABC):
    def pay(): ...

class Razorpay(PaymentMethod): ...
class Stripe(PaymentMethod): ...

class PaymentService:
    def __init__(self, method: PaymentMethod):
        self.method = method
```

Switching payment provider does NOT affect PaymentService.
This also makes unit testing easy.

### 🚫 Bad:

```python
class PaymentService:
    def __init__(self):
        self.razorpay = Razorpay()  # tightly coupled
```

### 🧠 Interview Tip:

Always mention **Dependency Injection** (constructor injection).

---

# 📘 **SOLID Summary Table (For Your Notes)**

| Principle | Meaning                         | Benefit                | Example                        |
| --------- | ------------------------------- | ---------------------- | ------------------------------ |
| SRP       | One responsibility              | Easy maintainability   | Ticket class only tracks time  |
| OCP       | Extendable without modification | Add features safely    | Strategy Pattern               |
| LSP       | Subclass must work as base      | Reliable polymorphism  | Car/Bike/Truck replace Vehicle |
| ISP       | Small, focused interfaces       | Reduces unused methods | Workable / Eatable             |
| DIP       | Depend on abstractions          | Testable + decoupled   | PaymentMethod interface        |

---


# 🎯 Bonus: Interview Questions on SOLID

You MUST prepare these:

1. **Which SOLID principle is most important?**
   ➡ SRP — reduces bugs & complexity.

2. **How does Strategy Pattern help with OCP?**
   ➡ New strategies don't modify existing code.

3. **Give real-life violations of LSP.**
   ➡ Rectangle–Square problem.

4. **Difference between DIP & Factory Pattern?**
   ➡ DIP focuses on abstraction; Factory helps create objects.

5. **Where do we use ISP in enterprise-level systems?**
   ➡ Microservices splitting endpoints; segregated interfaces.
