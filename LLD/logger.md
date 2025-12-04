Let’s master the **Logger System: Singleton + Observer**—a classic interview and real-world backend combo.

### Scenario

Your backend system needs a robust, globally accessible Logger to record messages, errors, metrics, and more.
You want it to:

- Stay **singleton** (one instance, not dozens of conflicting log files).
- Support **dynamic listeners** (send logs to file, console, external server, metrics system—as “observers”).
- Make adding/removing log destinations trivial, not code-breaking.

***

## 1. **Bad Example: Logger With Global State \& Hardcoded Handlers**

```python
class Logger:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def log(self, msg):
        # Hardcoded: always logs to console
        print(msg)
        # Later, someone hacks in an email alert: if "ERROR" in msg: send_email(msg)
# Usage
logger1 = Logger()
logger2 = Logger()
assert logger1 is logger2  # Singleton, yes

logger1.log("Starting system.")
logger2.log("Critical ERROR in payment service.")
```

**Problems:**

- **Hardcoded outputs:** Routing logs requires code changes everywhere.
- **No observers:** Want to send logs to both console, file, and metrics? Messy.
- **Singleton only—no extensibility!**
- **Poor testability:** Difficult to intercept logs for test cases.

**Humour Break:**
> “The ERROR goes to console, the panic goes to email, and the debug goes to… your lost weekend fixing the logger.”

***

## 2. **Good Example: Singleton Logger + Observer Listeners**

### **Singleton Logger manages a list of Observer listeners—log output is decoupled and extensible.**

#### Pythonic Implementation

```python
from abc import ABC, abstractmethod
import threading

# --- Observer pattern for log listeners
class LogListener(ABC):
    @abstractmethod
    def notify(self, msg: str):
        pass

class ConsoleListener(LogListener):
    def notify(self, msg):
        print(f"[Console] {msg}")

class FileListener(LogListener):
    def __init__(self, filename):
        self.file = open(filename, "a")
    def notify(self, msg):
        self.file.write(msg + "\n")
    def __del__(self):
        self.file.close()

class MetricsListener(LogListener):
    def notify(self, msg):
        if "ERROR" in msg:
            print(f"[Metrics] Error counter incremented.")

# --- Singleton Logger
class Logger:
    _instance = None
    _lock = threading.Lock()  # Thread safety

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(Logger, cls).__new__(cls)
                cls._instance._listeners = []
        return cls._instance

    def add_listener(self, listener: LogListener):
        self._listeners.append(listener)
        print(f"[Logger] Listener added: {listener.__class__.__name__}")

    def remove_listener(self, listener: LogListener):
        self._listeners.remove(listener)
        print(f"[Logger] Listener removed: {listener.__class__.__name__}")

    def log(self, msg: str):
        for l in self._listeners:
            l.notify(msg)
        # Also return for unittest interception!
        return msg

# --- Usage: one logger, dynamic observers
logger = Logger()
logger.add_listener(ConsoleListener())
logger.add_listener(FileListener("app.log"))
logger.add_listener(MetricsListener())

logger.log("Backend started.")
logger.log("ERROR: Payment gateway failed.")
logger.log("Metrics and logging just got easier.")
```


***

### **Why is this better?**

- **True Singleton:** One logger instance—never conflicts.
- **Dynamic output:** Add/remove listeners for file, console, metrics, email live.
- **Testable:** Swap in test listeners, mock outputs.
- **Extensible (Open/Closed principle):** Add Slack/Telegram/HTTP/anything listeners with zero changes to Logger or clients.

**Humour Break:**
> “With Observer, Logger stays calm—even when you swap from file logging to Twitter panic alerts mid-production.”

***

## 3. **Real-World Scenario**

- **Distributed background jobs:** Send logs to file, stdout, error monitoring, and metrics.
- **Feature toggles:** Log extra debug info for certain endpoints or tests.
- **Centralized logging:** Notify external log servers (Splunk, ELK, Datadog) as listeners.

**Popular frameworks using this pattern:**

- Python logging module (`logging.Handler`)
- Java logging frameworks (`Appender` pattern)
- Microservices sending logs/events to Kafka via observer hooks

***

## 4. **Production Trade-Offs**

- **Resource safety:** File/disk listeners need proper teardown.
- **Thread safety:** Use threading/multiprocessing-safe loggers in high-concurrency systems.
- **Listener management:** Make it easy to mute/add/remove outputs via configuration.

***

## 5. **Summary**

- **Bad Example:** Singleton but hardcoded, brittle log outputs.
- **Good Example:** Singleton Logger + Observer—flexible, reliable, easily extensible, production-ready.
- **Real-World Use:** Logging, alert pipelines, real-time monitoring, dynamic diagnostics.

