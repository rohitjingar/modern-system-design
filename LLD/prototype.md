# 🧬 Prototype Design Pattern — "Don’t rebuild, just copy!"

> It’s a design pattern used to **create new objects by copying (cloning)** existing ones instead of constructing them from scratch.  
> Think: duplicating a “base product template” rather than re-entering every detail manually.

---

## 🚫 Bad Example: “Manual Product Recreation Hell”

Imagine you work for an e-commerce backend (like Amazon or Flipkart).  
Each new product variant (color, size, or region) needs the same base data — pricing rules, tax settings, shipping policies, SEO metadata, etc.  

Here’s the *painful* approach:

```python
import time
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Product:
    name: str
    price: float
    metadata: Dict[str, str]
    logistics: Dict[str, str]
    seo: Dict[str, str]

class ProductBuilder:
    '''Simulates a slow process for fetching templates and logistics info.'''
    def __init__(self):
        # Expensive initialization
        time.sleep(0.2)  # simulate DB/API calls
        self.template = self._fetch_default_template()
        self.logistics = self._fetch_logistics_rules()

    def _fetch_default_template(self):
        return {"tax": "GST-18%", "currency": "INR"}

    def _fetch_logistics_rules(self):
        return {"ship_via": "BlueDart", "delivery_days": "3-5"}

    def create_product(self, name, price, region):
        return Product(
            name=name,
            price=price,
            metadata=self.template.copy(),
            logistics=self.logistics.copy(),
            seo={"region": region, "keywords": f"{name.lower()} in {region}"}
        )

# 🐢 Naive usage
def bulk_create_variants():
    variants = []
    for region in ["IN", "US", "EU", "APAC"]:
        builder = ProductBuilder()  # ❌ Slow every time
        product = builder.create_product("iPhone 16", 999.99, region)
        variants.append(product)
        print(f"Created {product.name} for {region}")
    return variants

bulk_create_variants()
```

### ❌ What’s wrong:
- Every region = new `ProductBuilder()` → repeated API/DB calls.  
- Initialization delay: 0.2 s × 4 regions = 0.8 s wasted.  
- Imagine doing this for **10k SKUs** — your nightly job dies before morning coffee ☕.

---

## ✅ Good Example: “Prototype to the Rescue”

Let’s build once, then clone cheaply.

```python
import copy
import time
from dataclasses import dataclass
from typing import Dict

# --- Prototype Interface ---
class Prototype:
    def clone(self):
        return copy.deepcopy(self)

# --- Product Model ---
@dataclass
class Product(Prototype):
    name: str
    price: float
    metadata: Dict[str, str]
    logistics: Dict[str, str]
    seo: Dict[str, str]

    def customize(self, region: str, price: float = None):
        '''Adjust only what's needed for the clone.'''
        if price:
            self.price = price
        self.seo["region"] = region
        self.seo["keywords"] = f"{self.name.lower()} in {region}"
        return self


# --- Prototype Registry ---
class ProductRegistry:
    def __init__(self):
        self._prototypes = {}
        self._load_base_templates()

    def _load_base_templates(self):
        print("Initializing base product templates (expensive setup)...")
        time.sleep(0.2)  # Simulate API/DB
        base_product = Product(
            name="iPhone 16",
            price=999.99,
            metadata={"tax": "GST-18%", "currency": "INR"},
            logistics={"ship_via": "BlueDart", "delivery_days": "3-5"},
            seo={"region": "IN", "keywords": "iphone 16 india"}
        )
        self._prototypes["iphone16"] = base_product
        print("✅ Base templates ready")

    def get_clone(self, name: str):
        if name not in self._prototypes:
            raise ValueError("Unknown product prototype")
        return self._prototypes[name].clone()


# --- Usage ---
def bulk_create_variants_with_prototype():
    registry = ProductRegistry()  # one-time setup

    regions = ["IN", "US", "EU", "APAC"]
    region_prices = {"IN": 999.99, "US": 1099.99, "EU": 1049.99, "APAC": 979.99}

    variants = []
    for region in regions:
        product = registry.get_clone("iphone16").customize(region, price=region_prices[region])
        variants.append(product)
        print(f"✅ Cloned variant for {region}: ${product.price}")

    return variants

bulk_create_variants_with_prototype()
```

---

### 🌟 Why this is better
| Problem | Solution via Prototype |
|----------|------------------------|
| Expensive initialization per variant | Done once, cloned instantly |
| Repeated DB/API calls | Cached in prototype |
| Code duplication | Simple `clone()` + `customize()` |
| Hard to extend | Add new prototypes easily |

⏱ From 0.8 s → ~0.2 s total, even for 10,000 variants!

---

### 🏭 Real-world relevance
You’ll see this idea in:
- Shopify / BigCommerce → product template duplication  
- Game engines → cloning preconfigured enemies/items  
- Kubernetes / Helm → templated YAML configs cloned per environment  
- Machine learning pipelines → clone base model configs for each experiment  

---

### 🧠 Takeaway
- **Without Prototype:** you rebuild heavy objects from scratch each time.  
- **With Prototype:** you prepare a “template,” then clone and tweak it.  
- **Mantra:** *“Don’t rebuild. Just copy and customize.”*
