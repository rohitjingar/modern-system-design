It’s a design pattern that lets you access elements of a collection (like a list or database cursor) one by one without exposing how the collection is built internally.
Don’t touch how data is stored — just use the iterator to go item by item.

***

## 1. The Bad Example: “Hand-Rolled Paging Logic”

Here's how things often look in real product code:

```python
def fetch_all_events(api_client):
    all_events = []
    next_token = None
    while True:
        response = api_client.get_events(page_token=next_token)
        all_events.extend(response["events"])
        next_token = response.get("next_token")
        if not next_token:
            break
    return all_events

# Usage: developer must wire paging logic into EVERY endpoint/request loop!
```


### Why is this bad?

- **Duplication:** Every API consumer must repeat the page-fetch logic.
- **No abstraction:** Can't reuse or mock iteration easily.
- **Error-prone:** Easy to miss edge cases, leaks, or infinite loops.
- **No standard API:** Can't swap in-memory data or API results with a single interface.

**Humour Break:**
> “Writing page-token loops feels like debugging a printer error—every time, something different goes wrong!”

***

## 2. The Good Example: **Pythonic Iterator for Paginated API Results**

With the Iterator pattern, you encapsulate the page-fetching details inside a custom iterable object. Client code just loops, with zero concern for tokens, batching, or API-glitches. Swap in-memory, file, or API sources with identical logic.

### Pythonic Iterator Example: Stripe-Like Event Streaming

```python
class PaginatedEventIterator:
    def __init__(self, api_client):
        self.api_client = api_client
        self.next_token = None
        self._buffer = []  # Local cache for current page only

    def __iter__(self):
        return self

    def __next__(self):
        if not self._buffer:
            # Fetch next page if buffer empty
            response = self.api_client.get_events(page_token=self.next_token)
            self._buffer = response["events"]
            self.next_token = response.get("next_token")

        if not self._buffer:
            # No more data
            raise StopIteration

        # Pop and return the next event
        return self._buffer.pop(0)

# --- Simulated API client ---
class FakeAPIClient:
    def __init__(self):
        self._data = [
            [ {"id": 1}, {"id": 2}, {"id": 3} ],   # page 1
            [ {"id": 4}, {"id": 5}, {"id": 6} ],   # page 2
            [ {"id": 7}, {"id": 8} ]               # page 3
        ]

    def get_events(self, page_token=None):
        page_num = 0 if page_token is None else int(page_token)
        if page_num >= len(self._data):
            return { "events": [], "next_token": None }
        next_tok = str(page_num + 1) if page_num + 1 < len(self._data) else None
        return { "events": self._data[page_num], "next_token": next_tok }

# --- Usage in backend service (no paging logic needed!) ---
api_client = FakeAPIClient()
event_iter = PaginatedEventIterator(api_client)

for event in event_iter:
    print(f"Processing event: {event['id']}")

# Output: Processing event: 1 ... up to 8, one per line.
```


### **Why is this better?**

- **Abstracts complexity:** Client code never worries about paging, tokens, batch sizes.
- **Swappable:** Iterator API works for files, DB rows, APIs—just write a new iterator!
- **Memory-wise:** Can implement on-demand/lazy fetching for huge data sets.
- **Testable:** Plug in fake iterator for unit/integration tests.

**Humour Break:**
> “With proper iterators, batch-fetching is as easy as iterating a list. No more page-token-induced nightmares.”

***

## 3. **Real-World Backend Scenario**

- **Stripe/Shopify/AWS APIs:** Always paginated; iterator spares business logic from complexity.
- **Large DBs:** Streaming billions of rows without loading all in memory.
- **Log aggregation:** Stream events/files (S3, BigQuery, Elasticsearch).
- **Hybrid sources:** Seamlessly switch between cache, API, archived files via unified iteration.

**Popular frameworks:**

- Python’s built-in iterators/generators
- Django QuerySet iterator
- Pandas DataFrames (`.iterrows()`)
- AWS Boto3 paginators

***

## 4. **Production Trade-Offs**

- **Network limits:** Iterator fetches batches, so handle throttling/timeouts gracefully.
- **Error handling:** Raise exceptions or yield error objects? Design for reliability!
- **Streaming:** For huge datasets, add buffering and/or save resume-tokens.

***

## 5. **Summary**

- **Bad Example:** Manual batch/page-token logic everywhere; brittle and hard to test.
- **Iterator Example:** Encapsulate batch API paging—loop as easily as a list, and swap sources fluidly.
- **Real-World Use:** Paginated API access, file/data streaming, seamless lazy access to very large datasets.

