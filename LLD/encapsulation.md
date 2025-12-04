
# Encapsulation

**Encapsulation** is one of the four fundamental concepts of Object-Oriented Programming (OOP), alongside inheritance, polymorphism, and abstraction. It refers to the *bundling* of data (attributes) and methods (functions) that operate on that data into a single unit (class), and the *restriction* of direct access to some of the object's components.

***

## Key Points

- **Private Data:** Encapsulation hides the internal state of an object. Private variables cannot be accessed directly from outside the class.
- **Public Interface:** Any interaction with the underlying data should occur via public methods (getters, setters, etc.), creating a controlled interface.
- **Protection \& Maintenance:** By enforcing encapsulation, the internal implementation can change without affecting outside code, which reduces bugs and improves maintainability.
- **Security:** Sensitive information or operations of a class are shielded from unwanted interference.

***

## Example (Python)

```python
class BankAccount:
    def __init__(self, balance):
        self.__balance = balance  # Private variable

    def deposit(self, amount):
        self.__balance += amount

    def withdraw(self, amount):
        if amount <= self.__balance:
            self.__balance -= amount

    def get_balance(self):
        return self.__balance  # Public method (getter)
```

- `__balance` is not accessible outside `BankAccount` directly.
- Use methods to interact with `balance`.

***

## Benefits

- **Improved security:** Prevents accidental or unauthorized modification of internal data.
- **Code flexibility:** Internal implementation changes don’t break consuming code.
- **Simplifies debugging:** The internal state is only modified in predictable ways.
- **Promotes modularity:** Classes and objects can be reused safely.

***

## Best Practices

- Always mark sensitive properties private or protected.
- Expose necessary operations through public/protected methods.
- Use property decorators or getter/setter methods for controlled access.
- Document your class interface clearly.

***

## Summary

Encapsulation is vital for designing robust, reusable, and maintainable code by keeping implementation details hidden and exposing only what is necessary for object interaction.

---
