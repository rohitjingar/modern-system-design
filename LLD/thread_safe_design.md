let's explore how to design thread-safe components, focusing on three common and important examples: the Singleton, a Cache, and a Counter.

### 1. Thread-Safe Singleton

The **Singleton** pattern ensures that a class has only one instance and provides a single, global point of access to it. In a multithreaded environment, it's crucial to prevent multiple threads from creating their own instances simultaneously.[^1][^2][^3][^4]

The cleanest and most recommended way to implement a thread-safe singleton in Python is by using a lock to guard the instantiation process.

#### Production Code Example:

This implementation uses a lock and a technique called **double-checked locking**. It's efficient because it only acquires the lock when the instance has not yet been created.[^3]

```python
import threading

class SingletonLogger:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        # First check: Avoids the expensive lock acquisition in the common case.
        if cls._instance is None:
            # Acquire the lock to ensure only one thread can create the instance.
            with cls._lock:
                # Second check: A different thread might have created the instance
                # while the current thread was waiting for the lock.
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    # Initialize any resources here.
                    cls._instance.log_file = "app.log"
                    print("Logger instance created.")
        return cls._instance

    def log(self, message):
        with open(self.log_file, "a") as f:
            f.write(f"{message}\\n")

# --- Usage Example ---
def task(thread_id):
    logger = SingletonLogger()
    print(f"Thread-{thread_id}: Logger instance: {id(logger)}")
    logger.log(f"Message from thread {thread_id}")

threads = [threading.Thread(target=task, args=(i,)) for i in range(3)]
for t in threads:
    t.start()
for t in threads:
    t.join()

# Verify that only one instance was created
logger1 = SingletonLogger()
logger2 = SingletonLogger()
print(f"Are instances the same? {id(logger1) == id(logger2)}")

```


### 2. Thread-Safe Cache

A **cache** stores data to provide faster access later. In a concurrent system, multiple threads may try to read from and write to the cache at the same time, leading to data corruption or inconsistent reads.[^5]

A simple way to make a cache thread-safe is to protect its data structure (like a dictionary) with a lock.

#### Production Code Example (LRU Cache):

This example implements a thread-safe **Least Recently Used (LRU)** cache, which automatically evicts the least-used item when it reaches capacity.

```python
import threading
from collections import OrderedDict

class ThreadSafeLRUCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.lock = threading.Lock()

    def get(self, key: int):
        with self.lock:
            if key not in self.cache:
                return -1
            
            # Move the accessed item to the end to mark it as recently used.
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key: int, value: int):
        with self.lock:
            if key in self.cache:
                # Update existing key and move it to the end.
                self.cache[key] = value
                self.cache.move_to_end(key)
            else:
                if len(self.cache) >= self.capacity:
                    # Evict the first item (least recently used).
                    self.cache.popitem(last=False)
                self.cache[key] = value

# --- Usage Example ---
cache = ThreadSafeLRUCache(2)

def cache_user(thread_id):
    cache.put(thread_id, thread_id * 10)
    print(f"Thread-{thread_id}: Put key {thread_id}. Cache: {cache.cache}")
    retrieved = cache.get(1)
    print(f"Thread-{thread_id}: Got key 1 with value {retrieved}. Cache: {cache.cache}")


threads = [threading.Thread(target=cache_user, args=(i,)) for i in range(1, 4)]
for t in threads:
    t.start()
for t in threads:
    t.join()

```


### 3. Thread-Safe Counter

A **counter** is a simple variable that gets incremented. It's a classic example used to demonstrate race conditions, where multiple threads incrementing a shared counter can lead to a final value that is less than expected.[^6][^7]

The simplest way to make a counter thread-safe is to protect the increment operation with a lock.[^8]

#### Production Code Example:

```python
import threading

class ThreadSafeCounter:
    def __init__(self):
        self._count = 0
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            self._count += 1

    def get_count(self):
        with self._lock:
            return self._count

# --- Usage Example ---
counter = ThreadSafeCounter()

def increment_task():
    for _ in range(100_000):
        counter.increment()

threads = [threading.Thread(target=increment_task) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

# The final count should be 1,000,000 if the counter is thread-safe.
print(f"Final Count: {counter.get_count()}")

```

In each of these examples, a `threading.Lock` is used to create a **critical section**—a block of code that only one thread can execute at a time. This guarantees atomic operations on shared resources and is the fundamental principle behind creating thread-safe designs.[^9][^10]
<span style="display:none">[^11][^12][^13][^14][^15][^16][^17][^18][^19][^20]</span>

<div align="center">⁂</div>

[^1]: https://www.geeksforgeeks.org/java/java-singleton-design-pattern-practices-examples/

[^2]: https://www.digitalocean.com/community/tutorials/thread-safety-in-java-singleton-classes

[^3]: https://dotnettutorials.net/lesson/thread-safe-singleton-design-pattern/

[^4]: https://javatechonline.com/singleton-design-pattern-in-java-with-all-scenarios/

[^5]: https://codesignal.com/learn/courses/advanced-real-life-concurrency-challenges/lessons/implementing-a-thread-safe-lru-cache-with-high-concurrency

[^6]: https://www.linkedin.com/posts/orkhanhuseynli_concurrency-multithreading-counters-activity-7341508169422028801-nntu

[^7]: http://pminkov.github.io/blog/implementing-a-fast-multi-threaded-counter.html

[^8]: https://foojay.io/today/thread-safe-counter-in-java-a-comprehensive-guide/

[^9]: https://stackoverflow.com/questions/29883719/java-multithreading-threadsafe-counter

[^10]: https://www.baeldung.com/java-thread-safety

[^11]: https://stackoverflow.com/questions/16106260/thread-safe-singleton-class

[^12]: https://refactoring.guru/design-patterns/singleton/java/example

[^13]: https://stackoverflow.com/questions/8605747/how-to-make-cache-thread-safe

[^14]: https://www.baeldung.com/java-implement-thread-safe-singleton

[^15]: https://www.youtube.com/watch?v=wvhQ9vevmrE

[^16]: https://www.youtube.com/watch?v=wRMNQH5tgKw

[^17]: https://www.c-sharpcorner.com/article/a-threadsafe-c-sharp-lrucache-implementation/

[^18]: https://codefinity.com/courses/v2/3ab6312a-e52b-4c3d-acf6-0b7f845f3d5e/000bf9ef-8ab8-4640-a639-96d5c5443732/aea68801-0bef-42f1-a806-a3d0d0278d64

[^19]: https://leetcode.com/problems/lru-cache/discuss/1851511/thread-safe-lru-cache-implementation

[^20]: https://raghavsikaria.github.io/lru-and-mru-cache-in-python/

