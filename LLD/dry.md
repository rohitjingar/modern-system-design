### What is DRY?

**DRY** means any piece of knowledge, logic, or code should only exist in *one* place in your codebase—not repeated or duplicated across files, functions, or modules.[^1][^2]

- If you copy-paste code, change one piece but forget to update the others, bugs and inconsistency sneak in.
- If every business rule, calculation, or utility has a single source of truth, you only fix/update it once.


### Why DRY Matters

**Benefits:**

- **Maintainability:** When logic is centralized, updating it is easy and safe. No need to hunt through endless files for every duplicate snippet.[^1]
- **Readability:** The code is cleaner. Everyone knows where to find things.
- **Consistency:** Every module or component behaves the same way when logic isn’t repeated.[^1]
- **Bug Prevention:** Reduces accidental errors from leaving old, duplicated snippets around.
- **Testability:** You test one piece, not many, so you know it works everywhere.[^1]

***

### How Do You Apply DRY?

#### 1. Extract to a Function

Instead of re-writing logic, encapsulate it in a function and call it everywhere.

**DRY Example:**

```python
def is_valid_email(email):
    return "@" in email and "." in email

# Used in multiple functions 
def register_user(email, password):
    if not is_valid_email(email): raise ValueError("Invalid email")
    # ...register logic

def invite_user(email):
    if not is_valid_email(email): raise ValueError("Invalid email")
    # ...invite logic
```


#### 2. Centralize Constants/Settings

Keep your constants in one place.

**DRY Example:**

```python
# settings.py file
MAX_UPLOAD_SIZE_MB = 50

# everywhere else
if file_size > MAX_UPLOAD_SIZE_MB:
    raise ValueError("File too big!")
```


#### 3. Share Utility Functions/Classes

If you find yourself copy-pasting utility logic (date formatting, string manipulation, etc.) across files, create a dedicated module for them.[^3]

#### 4. Reusable UI Components

In frontend development, create shared UI components instead of copy-paste markup or styles.[^3]

#### 5. Modularize Common Logic

Group shared logic into libraries or modules accessed by multiple projects.

***

### DRY in Data Engineering and DevOps

- **Central Models:** Define table schemas/ETL logic in one place, so change propagates everywhere.[^2]
- **Template Engines:** Use templates for repetitive SQL or configuration generation.[^2]
- **Single Source of Truth:** Reference one config or settings file for all environments, not multiple replicas.

***

### Real Production Example

**Non-DRY:**

```python
# File A
def calculate_gst_for_product1(amt):
    return (amt/100) * 18

# File B
def calculate_gst_for_product2(amt):
    return (amt/100) * 18
```

**DRY:**

```python
def calculate_gst(amt):
    return (amt/100) * 18

# Used everywhere:
gst1 = calculate_gst(price1)
gst2 = calculate_gst(price2)
```

Now, if GST rate changes, only one line needs fixing!

***

**Summary:**
DRY saves you time, reduces bugs, and keeps code clean, simple, and maintainable. Look for patterns, group repeated logic, and extract to single sources—functions, modules, configs, or components.[^2][^3][^1]
<span style="display:none">[^4][^5][^6][^7][^8][^9]</span>

<div align="center">⁂</div>

[^1]: https://www.geeksforgeeks.org/software-engineering/dont-repeat-yourselfdry-in-software-development/

[^2]: https://www.secoda.co/glossary/dry-dont-repeat-yourself

[^3]: https://codefinity.com/blog/The-DRY-Principle

[^4]: https://thevaluable.dev/dry-principle-cost-benefit-example/

[^5]: https://www.baeldung.com/cs/dry-software-design-principle

[^6]: https://www.bytehide.com/blog/dry-principle-csharp

[^7]: https://workat.tech/machine-coding/tutorial/software-design-principles-dry-yagni-eytrxfhz1fla

[^8]: https://algomaster.io/learn/lld/dry

[^9]: https://www.getdbt.com/blog/dry-principles

