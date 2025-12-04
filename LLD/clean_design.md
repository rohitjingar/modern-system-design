# Interfaces \& Abstractions

Modern backend systems rely on clear interfaces and effective abstractions to keep code maintainable, scalable, and collaborative—especially in large organizations like Amazon, Google, or Stripe.

***

## Designing Contracts Between Components

A **contract** is a clearly defined API/interface that specifies how components communicate—what requests they accept, what responses they return, and the rules they follow.

### Real World Example: Payments Microservice (Inspired by Stripe)

Imagine your backend team builds a **PaymentsService** consumed by both web apps and other internal services.

#### Interface (Contract) Example

```python
class PaymentProcessorInterface:
    def charge(self, amount: float, source: dict) -> dict:
        raise NotImplementedError

    def refund(self, transaction_id: str) -> dict:
        raise NotImplementedError
```

- **Consumers** know exactly how to interact, regardless of the actual implementation (could be Stripe, Razorpay, PayPal).


#### Implementation

```python
class StripePaymentProcessor(PaymentProcessorInterface):
    def charge(self, amount, source):
        # Call Stripe's API
        return {"status": "success", "transaction_id": "123ABC"}

    def refund(self, transaction_id):
        # Call Stripe refund endpoint
        return {"status": "refunded"}
```


#### Decoupled Usage

```python
def process_checkout(processor: PaymentProcessorInterface, user, cart):
    result = processor.charge(cart.amount, user.payment_info)
    if result['status'] == "success":
        print("Order processed!")
```

*Production Context*: At Stripe, teams deploy new payment providers without affecting the consumers. The interface and contract remain stable.

***

## Clean API Design

Clean APIs make integration simple, reliable, and future-proof—helping teams across a company build on shared services.

### Principles

- **Consistency:** Method naming, argument order/type, return formats are predictable.
- **Minimalism:** Expose only what is necessary; hide implementation details.
- **Versioning:** Plan for breaking changes (Amazon API Gateway, Stripe API, etc. use versioned endpoints).
- **Documentation:** Every endpoint/class/method is clearly documented.


### Real World Example: REST API for User Management (Inspired by Google Cloud)

#### Interface

```python
# FastAPI example for User API
from fastapi import FastAPI

app = FastAPI()

@app.post("/users/")
def create_user(email: str, password: str):
    """Creates a new user account."""
    # Core logic...
    return {"user_id": "xyz", "status": "created"}

@app.get("/users/{user_id}")
def get_user(user_id: str):
    """Returns user information."""
    # Fetch logic...
    return {"user_id": user_id, "email": "test@gmail.com"}
```

- Only exposes endpoints/fields needed by consumers (other microservices, mobile apps).
- Endpoints are simple, well-named, and include rich documentation.


#### Production Example

At Google or Amazon, internal services communicate via standardized REST/gRPC APIs with strict contracts, ensuring updates to one system don’t break others. Services log requests, validate schemas, and version APIs for backward compatibility.

***

## Key Takeaways

- **Interfaces:** Provide a contract for interaction—consumer doesn’t depend on implementation.
- **Abstractions:** Hide complexity and implementation details, exposing only what’s needed.
- **Clean APIs:** Are predictable, easy to maintain, robust against future change, and drive successful cross-team collaboration.

***

**Summary:**
Top backend production systems thrive on strong interfaces and abstractions—design contracts that are clear, minimal, well-documented, and consistent, enabling rapid iteration and integration without fear of breaking existing consumers.

