It’s a design pattern that lets you choose different algorithms or behaviors at runtime without changing the main code that uses them.
“Define many ways to do something — pick one when needed.”

Imagine your team wants to support multiple ranking strategies (popularity, user relevance, price-sensitivity, recent arrivals)—switching between them on the fly during A/B tests or for different customer types.

***

## 1. The Bad Example: “If-Else Ranking Mayhem”

Suppose your product listing endpoint looks like this mess:

```python
def rank_products(products, strategy, user_id=None):
    if strategy == "popularity":
        # Sort by most sold
        return sorted(products, key=lambda p: p.sales, reverse=True)
    elif strategy == "recent":
        # Sort by newest
        return sorted(products, key=lambda p: p.added_at, reverse=True)
    elif strategy == "personalized":
        if user_id is None:
            raise Exception("User needed!")
        # Sort by user relevance score
        return sorted(products, key=lambda p: get_user_relevance(p, user_id), reverse=True)
    elif strategy == "price_low":
        return sorted(products, key=lambda p: p.price)
    else:
        raise Exception("Unknown ranking strategy.")
# Usage: spaghetti everywhere—add a new strategy, update every endpoint!
```


### Why is this bad?

- **Endless `if-else` blocks**: Unreadable, hard to maintain.
- **Impossible to extend**: Add a new strategy, edit every endpoint and test.
- **No encapsulation**: Ranking logic mixed with controller logic.
- **No testability or configuration**: Can't change strategy easily for A/B testing or business rules.

**Humour Break:**
> “How many `elif` blocks does it take to support user-based ranking? More than you can safely deploy on Friday evening!”

***

## 2. The Good Example: **Strategy Pattern for Search Ranking**

With Strategy, you encapsulate each ranking algorithm in its own class, expose a uniform interface, and let your backend select/swaps strategies at runtime (config, request, feature flags—anything goes).

### Pythonic Strategy Pattern Example: Search Ranking Service

```python
from abc import ABC, abstractmethod
from typing import List

class Product:
    def __init__(self, id, sales, price, added_at):
        self.id = id
        self.sales = sales
        self.price = price
        self.added_at = added_at
    # __repr__ for readable prints
    def __repr__(self):
        return f"Product(id={self.id})"

# 1. Strategy base class
class RankingStrategy(ABC):
    @abstractmethod
    def rank(self, products: List[Product], **kwargs) -> List[Product]:
        pass

# 2. Concrete strategies
class PopularityRanking(RankingStrategy):
    def rank(self, products, **kwargs):
        print("[Strategy] Popularity")
        return sorted(products, key=lambda p: p.sales, reverse=True)

class RecentArrivalRanking(RankingStrategy):
    def rank(self, products, **kwargs):
        print("[Strategy] Recent")
        return sorted(products, key=lambda p: p.added_at, reverse=True)

class PriceLowToHighRanking(RankingStrategy):
    def rank(self, products, **kwargs):
        print("[Strategy] Price Low-High")
        return sorted(products, key=lambda p: p.price)

class PersonalizedRanking(RankingStrategy):
    def rank(self, products, **kwargs):
        user_id = kwargs.get("user_id")
        if not user_id:
            raise Exception("User needed for personalized ranking!")
        print("[Strategy] Personalized")
        # Simulate relevance computation
        import random
        return sorted(products, key=lambda p: random.random(), reverse=True)

# 3. Context for selecting strategy (runtime config, A/B tests, endpoint arg etc)
class ProductRanker:
    def __init__(self, strategy: RankingStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: RankingStrategy):
        self.strategy = strategy

    def rank_products(self, products: List[Product], **kwargs):
        return self.strategy.rank(products, **kwargs)

# Usage in your backend—super clean, swap strategy at any time!
products = [
    Product("A", sales=100, price=10, added_at=170000),
    Product("B", sales=150, price=8, added_at=172000),
    Product("C", sales=70, price=12, added_at=177500)
]

ranker = ProductRanker(PopularityRanking())
print(ranker.rank_products(products))

ranker.set_strategy(RecentArrivalRanking())
print(ranker.rank_products(products))

ranker.set_strategy(PriceLowToHighRanking())
print(ranker.rank_products(products))

ranker.set_strategy(PersonalizedRanking())
print(ranker.rank_products(products, user_id="jon_snow"))
```


### **Why Is This Better?**

- **Encapsulation**: Each algorithm self-contained.
- **Flexible**: Change, add, remove strategies—code stays clean.
- **A/B Testing/Feature Flags**: Swap strategies live!
- **Extensible**: Add “hybrid,” “geo-relevance,” “seasonal discount” strategies easily.
- **Testing**: Test strategies in isolation, with mock products.

**Humour Break:**
> “With Strategy, changing ranking algorithm is a one-liner—not an `elif` marathon.”

***

## 3. **Real-World Backend Scenario**

- **E-commerce**: Feature flags or config-driven selection for different ranking algorithms.
- **Search Engines**: Dynamic user or region-specific search ranking logic.
- **Content Platforms**: News feed ordering, A/B experiments, personalized curation.
- **Banking/FinTech**: Show top offers or personalized highlights based on account activity.

**Popular frameworks using strategies:**

- Django’s authentication backend selection (strategies for password, OAuth, SSO, etc.)
- ML model serving (swap ranking models by business rule)
- Recommendation engines (plug-in ranking algorithms)

***

## 4. **Production Trade-Offs**

- **Too many strategies?** Modularize, document, and use configs for selection logic.
- **Performance**: Some ranking algorithms may be expensive—monitor and profile!
- **Dynamic swapping**: Build in config/hooks for easy swap (admin dashboard, feature flag, etc).

***

## 5. **Summary**

- **Bad Example:** Scattered, unreadable, `if-else` heavy ranking logic.
- **Strategy Example:** Modular, swappable, extensible—add features without pain.
- **Real-World Use:** Ranking, sorting, selection, filtering in any complex backend.
