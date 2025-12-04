# Polymorphism

**Polymorphism** (“many forms”) is an OOP concept where objects of different classes can be treated as objects of a common superclass, typically by calling shared methods—each object behaves appropriately based on its actual class.
This is essential in backend systems for extensibility, plug-ability, and clean APIs.

***

## Real-World Production Example: Backend Payment Processing

Imagine you have multiple payment methods—**CreditCard**, **PayPal**, **BankTransfer**—in an e-commerce backend. All expose a common interface, but their logic differs.

### Base Class (Interface)

```python
class PaymentMethod:
    def pay(self, amount):
        raise NotImplementedError("Subclasses must implement 'pay'")
```


### Subclasses Implement Specific Logic

```python
class CreditCard(PaymentMethod):
    def pay(self, amount):
        print(f"Paid ₹{amount} by Credit Card")

class PayPal(PaymentMethod):
    def pay(self, amount):
        print(f"Paid ₹{amount} by PayPal")

class BankTransfer(PaymentMethod):
    def pay(self, amount):
        print(f"Paid ₹{amount} by Bank Transfer")
```


### Polymorphic Usage in API Code

```python
def process_payment(payment_method: PaymentMethod, amount):
    payment_method.pay(amount)

methods = [CreditCard(), PayPal(), BankTransfer()]
for method in methods:
    process_payment(method, 100)
# Output:
# Paid ₹100 by Credit Card
# Paid ₹100 by PayPal
# Paid ₹100 by Bank Transfer
```

- The function `process_payment` works with *any* payment method, using the **same code**, because all subclasses override the method `pay`.

***

## Further Backend Context

- **Plug-ability:** Add new payment providers or logic without changing existing API code; just define a new subclass.
- **Framework Use:** Popular Python frameworks (like Django REST, Flask) use polymorphism for request handling, serialization, and validation (e.g., custom serializers, authentication strategies).
- **Testing:** Mocks/fakes substitute real classes in tests because interfaces are consistent.

***

## Other Common Patterns

### Example: Serializers in API Frameworks

```python
class BaseSerializer:
    def serialize(self, obj):
        raise NotImplementedError

class UserSerializer(BaseSerializer):
    def serialize(self, user):
        return {"email": user.email}

class OrderSerializer(BaseSerializer):
    def serialize(self, order):
        return {"order_number": order.order_number}
```

In RESTful views,

```python
def render_response(serializer: BaseSerializer, obj):
    return serializer.serialize(obj)
```

Any new serializer works with `render_response` with *no changes needed.*

***

## Summary

Polymorphism lets backend Python code handle different classes using unified code. It gives production systems flexibility, pluggability, and future-proofing—critical for scalable, maintainable API and business logic design.

