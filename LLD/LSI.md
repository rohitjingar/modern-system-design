### Locks

In concurrent programming, a **lock** is a mechanism that allows only one thread to access a shared resource at a time. Think of it as a key to a room; only the person with the key can enter. If another person wants to enter, they must wait for the first person to come out and release the key.[^1]

In programming, a thread "acquires" a lock before accessing a shared resource, and "releases" it when it's done. This prevents other threads from interfering and causing data corruption.[^2]

Here is a simple Python example of a lock:

```python
import threading

counter = 0
lock = threading.Lock()

def increment():
    global counter
    for _ in range(1000000):
        lock.acquire()
        counter += 1
        lock.release()

threads = [threading.Thread(target=increment) for _ in range(2)]
for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

print(f"Final counter value: {counter}")
```

In this example, the `lock.acquire()` and `lock.release()` calls ensure that only one thread can modify the `counter` at a time, preventing a race condition where the final value might be incorrect.

### Synchronization

**Synchronization** is the broader concept of coordinating the execution of multiple threads to ensure data consistency and prevent conflicts. Locks are one of the tools used to achieve synchronization.[^3][^4]

When threads share resources, their operations can overlap in unexpected ways, leading to incorrect results. Synchronization ensures that these operations happen in a controlled and predictable manner.[^5]

Consider this example of a bank account where multiple threads are trying to withdraw money:

```python
import threading

class BankAccount:
    def __init__(self, balance):
        self.balance = balance
        self.lock = threading.Lock()

    def withdraw(self, amount):
        with self.lock:
            if self.balance >= amount:
                print(f"{threading.current_thread().name} withdrawing {amount}")
                self.balance -= amount
                print(f"New balance: {self.balance}")
            else:
                print(f"Insufficient funds for {threading.current_thread().name}")


account = BankAccount(1000)

def withdraw_task():
    for _ in range(5):
        account.withdraw(100)

threads = [threading.Thread(target=withdraw_task) for _ in range(2)]
for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

```

In this example, the `with self.lock:` statement automatically acquires the lock before entering the block of code and releases it upon exit. This synchronizes access to the `balance`, ensuring that the check for sufficient funds and the withdrawal happen as a single, atomic operation.[^2]

### Immutability

An **immutable object** is an object whose state cannot be changed after it is created. If you want to modify an immutable object, you create a new object with the desired changes instead.[^6]

Immutability is a powerful way to achieve thread safety because if data is never modified, there is no risk of multiple threads corrupting it. Shared, unchangeable data is inherently thread-safe.[^7][^6]

Here is an example of an immutable `UserProfile` class:

```python
class UserProfile:
    def __init__(self, username, email):
        self._username = username
        self._email = email

    @property
    def username(self):
        return self._username

    @property
    def email(self):
        return self._email

    def with_email(self, new_email):
        return UserProfile(self.username, new_email)

# Original profile
user1 = UserProfile("john_doe", "john.doe@example.com")

# To "change" the email, we create a new UserProfile instance
user2 = user1.with_email("new.john.doe@example.com")

print(f"User 1 email: {user1.email}")
print(f"User 2 email: {user2.email}")

```

In this example, the `UserProfile` object is immutable. Its `username` and `email` cannot be changed directly. The `with_email` method doesn't modify the existing object; it returns a *new* `UserProfile` instance with the updated email. This makes it safe to share `UserProfile` objects across multiple threads without worrying about data races.[^8]
<span style="display:none">[^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^20][^9]</span>

<div align="center">⁂</div>

[^1]: https://web.mit.edu/6.005/www/fa15/classes/23-locks/

[^2]: https://docs.python.org/3/library/threading.html

[^3]: https://www.lenovo.com/my/en/glossary/syn/

[^4]: https://www.geeksforgeeks.org/java/synchronization-in-java/

[^5]: https://www.c-sharpcorner.com/article/understanding-thread-synchronization-in-concurrent-programming/

[^6]: https://workingwithruby.com/wwrt/immutability/

[^7]: https://ocw.mit.edu/ans7870/6/6.005/s16/classes/20-thread-safety/

[^8]: https://www.scribd.com/document/526903049/g-thread-safety-immutability
