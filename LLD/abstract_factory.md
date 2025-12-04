It provides an interface to create families of related objects — without specifying their exact classes.

Factory had a baby — and that baby builds other factories.


## 1. The Bad Example: “Copy-Pasta Factories” (How Backend Engineers Lose Their Hair)

Suppose your backend supports multiple environments—**AWS and GCP**—and you need to create resources (like storage clients and message clients) for both clouds. Here’s the classic *bad* setup you might find in a messy codebase:

```python
# AWS implementations
class AWSS3Client:
    def store(self, data): print(f"AWS S3 storing: {data}")

class AWSQueueClient:
    def send(self, msg): print(f"AWS SQS sending: {msg}")

# GCP implementations
class GCPS3Client:
    def store(self, data): print(f"GCP Storage storing: {data}")

class GCPQueueClient:
    def send(self, msg): print(f"GCP Pub/Sub sending: {msg}")

def get_s3_client(env):
    if env == "aws":
        return AWSS3Client()
    elif env == "gcp":
        return GCPS3Client()
    else:
        raise ValueError("Unknown env")

def get_queue_client(env):
    if env == "aws":
        return AWSQueueClient()
    elif env == "gcp":
        return GCPQueueClient()
    else:
        raise ValueError("Unknown env")

# Using in production:
s3 = get_s3_client("aws")
queue = get_queue_client("aws")
s3.store("production_data")
queue.send("new_job")
```


### Why is this bad?

- **Duplicate Logic**: Every time you need a new resource type, you copy-paste the “get” function and add more sad “if-else”s.
- **No Cohesion**: Resource creation logic is scattered—one function for S3, another for Queue, and so on.
- **Error-Prone**: Miss an update? Congrats, welcome to another 2 AM incident call.
- **Poor Scaling**: Add one more cloud provider and your codebase starts to resemble a spaghetti festival.

**Humour Break**:
> “Backend Engineers: Always adding ‘elif’ until Friday afternoon, then rage-quitting to play Counter-Strike.”

***

## 2. The Good Example: **Abstract Factory Pattern to the Rescue**

Now let’s see how the **Abstract Factory** design pattern transforms this headache into a zen-like backend experience.

### **Pythonic Abstract Factory Solution**

First, we define abstract interfaces, then create concrete factories for each environment.

```python
# Abstract interfaces
class StorageClient:
    def store(self, data):
        raise NotImplementedError

class MessageQueueClient:
    def send(self, msg):
        raise NotImplementedError

# AWS implementations
class AWSS3Client(StorageClient):
    def store(self, data):
        print(f"AWS S3 storing: {data}")

class AWSQueueClient(MessageQueueClient):
    def send(self, msg):
        print(f"AWS SQS sending: {msg}")

# GCP implementations
class GCPS3Client(StorageClient):
    def store(self, data):
        print(f"GCP Storage storing: {data}")

class GCPQueueClient(MessageQueueClient):
    def send(self, msg):
        print(f"GCP Pub/Sub sending: {msg}")

# Abstract Factory
class CloudResourceFactory:
    def create_storage_client(self) -> StorageClient:
        raise NotImplementedError
    def create_queue_client(self) -> MessageQueueClient:
        raise NotImplementedError

# Concrete Factories
class AWSResourceFactory(CloudResourceFactory):
    def create_storage_client(self):
        return AWSS3Client()
    def create_queue_client(self):
        return AWSQueueClient()

class GCPResourceFactory(CloudResourceFactory):
    def create_storage_client(self):
        return GCPS3Client()
    def create_queue_client(self):
        return GCPQueueClient()

# Usage in your backend (dependency injection, config-driven, etc)
def get_factory(env: str) -> CloudResourceFactory:
    factories = {"aws": AWSResourceFactory, "gcp": GCPResourceFactory}
    factory_cls = factories.get(env)
    if not factory_cls:
        raise ValueError(f"Unknown env: {env}")
    return factory_cls()

# Example use-case
factory = get_factory("aws")
storage = factory.create_storage_client()
queue = factory.create_queue_client()
storage.store("Zen and the Art of Code Maintenance")
queue.send("Deploy to production, fingers crossed!")
```


### **Why is this better?**

- **Cohesive Resource Creation**: All related resource creation logic for an environment is bundled together.
- **Open/Closed Principle**: Add new resources or providers by just creating a new factory—no mass refactoring.
- **Single Configuration Point**: Backend gets its `factory` from config; rest of the code doesn’t care what the environment is.
- **Testability**: Swap factories for mocks or stubs in test environments. Impossible with “copy-pasta” functions.

**Humour Break**:
> “Adding ‘AzureResourceFactory’? All your code is still neat! You have time for coffee *and* memes before production deploy.”

***

## 3. **Real-World Backend Scenario**

Imagine you’re building a **multi-cloud backend** for a SaaS app:

- Teams demand plug-and-play support for AWS, GCP, maybe Azure tomorrow.
- Developers can write “cloud-agnostic” code by always using the abstract factory—environment comes from config or service discovery.
- Each cloud factory may manage secrets, logging, metrics in its own way, keeping the backend clean and extensible.

Example expansion—add Azure:

```python
class AzureStorageClient(StorageClient):
    def store(self, data):
        print(f"Azure Blob storing: {data}")

class AzureQueueClient(MessageQueueClient):
    def send(self, msg):
        print(f"Azure Queue sending: {msg}")

class AzureResourceFactory(CloudResourceFactory):
    def create_storage_client(self):
        return AzureStorageClient()
    def create_queue_client(self):
        return AzureQueueClient()

factories["azure"] = AzureResourceFactory
```


***

## 4. **Trade-Offs in Production**

- **More Classes**: Abstract Factory uses more classes, but gives maintainability and clarity in exchange.
- **Extensibility vs Complexity**: For >2 environments or >2 resource types, Abstract Factory shines. For tiny scripts, vanilla factories may suffice.
- **Actual Use**: Popular in frameworks, cloud SDKs, and enterprise apps with pluggable modules.

***

## 5. **Summary**

- **Bad Example:** Disjointed copy-paste factories—harder to maintain than 40TB of logs.
- **Abstract Factory Example:** Pluggable, cohesive, scalable factories for multi-cloud resource management.
- **Real-world Scenario:** Multi-cloud backend, cloud-agnostic interfaces, ready for Azure or that new provider your boss dreams up next month.

***

### Next Steps

Ready for **Builder Pattern** next, or want a funny story about a company that copied all their “get” functions and crashed on Black Friday? 😄

***
