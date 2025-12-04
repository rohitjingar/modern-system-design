# 15. Data Modeling

**The Joke:** Bad data modeling is like building a house on sand: it works fine until it doesn't, then everything collapses. Good data modeling is boring. That's how you know it's correct. 🏗️

[← Back to Main](../README.md) | [Previous: CDN](14-cdn.md) | [Next: File Storage →](16-file-storage.md)

---

## 🎯 Quick Summary

**Data Modeling** is designing how data is structured and organized in databases. It involves identifying entities, relationships, attributes, and designing schemas. Good modeling makes queries fast and maintainable. Bad modeling makes everything slow and breaks frequently. It's the foundation of database design, requiring understanding of normalization, denormalization, and trade-offs.

Think of it as: **Data Modeling = Blueprint for Your Database**

---

## 🌟 Beginner Explanation

### The Real Estate Analogy

**BEFORE DATA MODELING (Chaotic):**

```
Real estate agent writes everything in one notebook:

"Alice owns house at 123 Main St worth $500K bought 
2020 January 15 from Bob who lives at 456 Elm Ave has 
phone 555-1234 and email bob@example.com who is married 
to Carol and they have 2 kids named David and Eve..."

Problems:
❌ What if Alice moves? Update everywhere!
❌ What if Bob sells multiple houses? Repeated info!
❌ What if Carol's info changes? Where is it?
❌ Finding all properties in a city? Impossible!
❌ Impossible to query efficiently
```

**AFTER DATA MODELING (Organized):**

```
Database structure:

PEOPLE Table:
├─ ID: 1, Name: Alice, Email: alice@example.com
├─ ID: 2, Name: Bob, Email: bob@example.com
├─ ID: 3, Name: Carol, Email: carol@example.com

PROPERTIES Table:
├─ ID: 1, Address: 123 Main, Owner: 1 (Alice), Value: $500K
├─ ID: 2, Address: 456 Elm, Owner: 2 (Bob), Value: $600K

RELATIONSHIPS Table:
├─ ID: 1, Person: 2 (Bob), Related: 3 (Carol), Type: "married"

CHILDREN Table:
├─ ID: 1, Child: David, Parent: 3 (Carol)
├─ ID: 2, Child: Eve, Parent: 3 (Carol)

Benefits:
✅ Alice moves? Update once
✅ Bob sells another house? Add one row
✅ Carol info changes? Update in one place
✅ Find all properties in city? Easy query!
✅ Clean and organized
```

### Entities vs Attributes

```
ENTITY: A thing we track (Person, Product, Order)

ATTRIBUTES: Properties of that entity

Example:

Entity: User
├─ Attributes:
│  ├─ ID (unique identifier)
│  ├─ Name (text)
│  ├─ Email (text)
│  ├─ Age (number)
│  ├─ Created Date (timestamp)
│  └─ Is Active (boolean)

Entity: Product
├─ Attributes:
│  ├─ ID
│  ├─ Name
│  ├─ Price
│  ├─ Inventory
│  └─ Category

Entity: Order
├─ Attributes:
│  ├─ ID
│  ├─ User ID (reference to User)
│  ├─ Product ID (reference to Product)
│  ├─ Quantity
│  └─ Created Date
```

### Relationships

```
ONE-TO-ONE:
User ←→ Profile
One user has ONE profile
One profile belongs to ONE user

User Table:     Profile Table:
ID: 1           User ID: 1, Bio: "..."
Name: Alice     User ID: 2, Bio: "..."

ONE-TO-MANY:
User ←→ Orders
One user has MANY orders
One order belongs to ONE user

User Table:     Order Table:
ID: 1           ID: 1, User: 1
Name: Alice     ID: 2, User: 1
                ID: 3, User: 2

MANY-TO-MANY:
Students ←→ Classes
Many students take MANY classes
Many classes have MANY students

Requires: Bridge table!

Student Table:  Enrollment Table:  Class Table:
ID: 1           Student: 1         ID: 101
Name: Alice     Class: 101         Name: Math
                
                Student: 1         ID: 102
                Class: 102         Name: Science
                
                Student: 2
                Class: 101
```

---

## 🔬 Advanced Explanation

### Normalization: Reduce Redundancy

**PROBLEM: Denormalized (First Normal Form Issues)**

```
ORDERS Table (bad):

Order ID | User Name | User Email    | Product Name | Price
---------|-----------|---------------|--------------|-------
1        | Alice     | alice@ex.com  | Laptop       | $1000
2        | Alice     | alice@ex.com  | Mouse        | $50
3        | Bob       | bob@ex.com    | Keyboard     | $100
4        | Alice     | alice@ex.com  | Monitor      | $300

Problems:
❌ Alice's email repeated 3 times (redundancy)
❌ If Alice's email changes, update 3 rows!
❌ Data inconsistency risk
❌ Wasted storage
❌ Slow queries (process redundant data)
```

**SOLUTION: Normalized (Third Normal Form)**

```
USERS Table:
User ID | Name  | Email
--------|-------|---------------
1       | Alice | alice@ex.com
2       | Bob   | bob@ex.com

PRODUCTS Table:
Product ID | Name    | Price
-----------|---------|-------
101        | Laptop  | $1000
102        | Mouse   | $50
103        | Keyboard| $100
104        | Monitor | $300

ORDERS Table:
Order ID | User ID | Product ID
---------|---------|------------
1        | 1       | 101
2        | 1       | 102
3        | 2       | 103
4        | 1       | 104

Benefits:
✅ No redundancy
✅ Alice's email once
✅ Easy to update
✅ Consistent data
✅ Less storage
```

**NORMALIZATION LEVELS:**

```
1NF (First Normal Form):
├─ No repeating groups
├─ Atomic values only
└─ Every column unique

2NF (Second Normal Form):
├─ Must be 1NF
├─ Remove partial dependencies
└─ Non-key columns depend on WHOLE key

3NF (Third Normal Form):
├─ Must be 2NF
├─ Remove transitive dependencies
├─ Non-key columns depend ONLY on key
└─ Most common in practice

BCNF (Boyce-Codd Normal Form):
├─ Stricter than 3NF
├─ Every determinant must be candidate key
└─ Rarely needed

Note: Over-normalization can hurt performance!
```

### Denormalization: Trade Consistency for Speed

```
PROBLEM: Normalized queries are slow

Query: "Get user with all their orders and products"

Requires:
├─ Query USERS table
├─ Query ORDERS table (join)
├─ Query PRODUCTS table (join)
├─ Assemble results
└─ Multiple database hits 🐢

SOLUTION: Denormalize strategically

DENORMALIZED_ORDERS Table:
Order ID | User Name | User Email    | Product Name | Price
---------|-----------|---------------|--------------|-------
1        | Alice     | alice@ex.com  | Laptop       | $1000

Benefits:
✅ Single query (fast!)
✅ No joins needed
✅ Single database hit

Cost:
❌ Redundancy
❌ Updates harder (update 3 tables)
❌ Consistency risk

When to denormalize:
✅ Read-heavy (read much more than write)
✅ Complex queries
✅ Performance critical
✅ Accept eventual consistency

When NOT to denormalize:
❌ Write-heavy
❌ Strong consistency required
❌ Financial data
```

### Schema Patterns

**PATTERN 1: EAV (Entity-Attribute-Value)**

```
Flexible schema for varying attributes

Product Table:
ID: 1, Name: "Laptop", Type: "Electronics"

Attributes Table:
Product ID | Attribute | Value
-----------|-----------|----------
1          | CPU       | Intel i7
1          | RAM       | 16GB
1          | Storage   | 512GB SSD
1          | Weight    | 2kg

Benefits:
✅ Ultra flexible
✅ Add attributes without schema change
✅ Handle sparse data

Cons:
❌ Slower queries (many joins)
❌ Harder to aggregate
❌ Less type safety
```

**PATTERN 2: JSON/JSONB Columns**

```
Flexible nested data (PostgreSQL, MySQL)

User Table:
ID: 1
Name: "Alice"
Metadata: {
  "preferences": {
    "theme": "dark",
    "notifications": true
  },
  "settings": {
    "language": "en",
    "timezone": "UTC"
  }
}

Benefits:
✅ Flexible structure
✅ Query nested data
✅ Avoids EAV complexity

Cons:
❌ Less standardized
❌ Schema validation needed
❌ Harder to aggregate
```

**PATTERN 3: Temporal Data (Slowly Changing Dimensions)**

```
Track changes over time

VERSION 1:
User ID: 1, Name: "Alice", Version: 1, Valid From: 2024-01-01

User ID: 1, Name: "Alice M", Version: 2, Valid From: 2024-06-01

Benefits:
✅ Historical data preserved
✅ Audit trail
✅ Query "as of" date

Cost:
❌ More complex queries
❌ More storage
```

### Indexing Strategy

```
CREATE INDEX on frequently queried columns

Good indexes:
✅ User ID (frequent lookups)
✅ Email (login queries)
✅ Created Date (range queries)
✅ Status (filters)

Bad indexes:
❌ Rarely queried columns
❌ Boolean columns (too few unique values)
❌ Low cardinality (Gender: M/F only)

Impact:
Good index: 100x faster queries ⚡
Bad index: Slow writes, waste storage ❌
```

---

## 🐍 Python Code Example

### ❌ Bad Data Modeling (Denormalized, Slow)

```python
# ===== BAD DATA MODELING =====

class BadUserDB:
    """Poor data model - everything in one table"""
    
    def __init__(self):
        # All data crammed into users table
        self.users = [
            {
                "id": 1,
                "name": "Alice",
                "email": "alice@example.com",
                "orders": [
                    {"order_id": 1, "product": "Laptop", "price": 1000},
                    {"order_id": 2, "product": "Mouse", "price": 50}
                ],
                "addresses": [
                    {"street": "123 Main", "city": "NYC"},
                    {"street": "456 Elm", "city": "LA"}
                ]
            },
            {
                "id": 2,
                "name": "Alice",  # Duplicate! Inconsistent!
                "email": "alice@example.com",  # Same email!
                "orders": [
                    {"order_id": 3, "product": "Laptop", "price": 1000},  # Repeated!
                ]
            }
        ]
    
    def update_user_email(self, user_id, new_email):
        """Update causes inconsistency"""
        count = 0
        for user in self.users:
            if user["id"] == user_id:
                user["email"] = new_email
                count += 1
        return f"Updated {count} records (should be 1!)"
    
    def get_user_orders(self, user_id):
        """Inefficient - search entire structure"""
        for user in self.users:
            if user["id"] == user_id:
                return user["orders"]
        return None

# Problems:
# ❌ Data redundancy (Alice appears twice)
# ❌ Inconsistency (email repeated)
# ❌ Difficult to query
# ❌ Update anomalies
# ❌ Storage wasted
```

### ✅ Good Data Modeling (Normalized, Fast)

```python
# ===== GOOD DATA MODELING =====

class GoodUserDB:
    """Properly normalized data model"""
    
    def __init__(self):
        # Separate tables
        self.users = {
            1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
            2: {"id": 2, "name": "Bob", "email": "bob@example.com"}
        }
        
        self.products = {
            101: {"id": 101, "name": "Laptop", "price": 1000},
            102: {"id": 102, "name": "Mouse", "price": 50},
            103: {"id": 103, "name": "Keyboard", "price": 100}
        }
        
        self.orders = {
            1: {"id": 1, "user_id": 1, "product_id": 101, "quantity": 1},
            2: {"id": 2, "user_id": 1, "product_id": 102, "quantity": 1},
            3: {"id": 3, "user_id": 2, "product_id": 101, "quantity": 1}
        }
        
        self.addresses = {
            1: {"id": 1, "user_id": 1, "street": "123 Main", "city": "NYC"},
            2: {"id": 2, "user_id": 1, "street": "456 Elm", "city": "LA"}
        }
    
    def update_user_email(self, user_id, new_email):
        """Update in one place only"""
        if user_id in self.users:
            self.users[user_id]["email"] = new_email
            return f"Updated user {user_id}"
        return "User not found"
    
    def get_user_with_orders(self, user_id):
        """Query with proper joins"""
        user = self.users.get(user_id)
        if not user:
            return None
        
        # Get all orders for user
        user_orders = []
        for order in self.orders.values():
            if order["user_id"] == user_id:
                product = self.products[order["product_id"]]
                user_orders.append({
                    "order_id": order["id"],
                    "product": product["name"],
                    "price": product["price"],
                    "quantity": order["quantity"]
                })
        
        return {
            "user": user,
            "orders": user_orders
        }
    
    def get_user_addresses(self, user_id):
        """Get addresses efficiently"""
        return [addr for addr in self.addresses.values() 
                if addr["user_id"] == user_id]

# Benefits:
# ✅ No redundancy
# ✅ Consistent data
# ✅ Easy to query
# ✅ Update in one place
# ✅ Storage efficient
```

### ✅ Production Data Model (With ORM)

```python
# ===== PRODUCTION DATA MODEL (SQLAlchemy) =====

from datetime import datetime

class User:
    """User entity"""
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email
        self.created_at = datetime.now()
        self.orders = []  # Relationship
        self.addresses = []  # Relationship
    
    def add_order(self, order):
        """Add order (maintains relationship)"""
        self.orders.append(order)
        order.user_id = self.id
    
    def add_address(self, address):
        """Add address"""
        self.addresses.append(address)
        address.user_id = self.id

class Product:
    """Product entity"""
    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = price
        self.created_at = datetime.now()

class Order:
    """Order entity (links User and Product)"""
    def __init__(self, id, user_id, product_id, quantity):
        self.id = id
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity
        self.created_at = datetime.now()

class Address:
    """Address entity"""
    def __init__(self, id, user_id, street, city):
        self.id = id
        self.user_id = user_id
        self.street = street
        self.city = city

class DataModel:
    """Production data model with relationships"""
    
    def __init__(self):
        self.users = {}
        self.products = {}
        self.orders = {}
        self.addresses = {}
        self.user_id = 1
        self.product_id = 1
        self.order_id = 1
        self.address_id = 1
    
    def create_user(self, name, email):
        """Create user"""
        user = User(self.user_id, name, email)
        self.users[self.user_id] = user
        self.user_id += 1
        return user
    
    def create_product(self, name, price):
        """Create product"""
        product = Product(self.product_id, name, price)
        self.products[self.product_id] = product
        self.product_id += 1
        return product
    
    def create_order(self, user_id, product_id, quantity):
        """Create order with relationships"""
        order = Order(self.order_id, user_id, product_id, quantity)
        self.orders[self.order_id] = order
        
        # Maintain relationship
        user = self.users[user_id]
        user.add_order(order)
        
        self.order_id += 1
        return order
    
    def add_address(self, user_id, street, city):
        """Add address to user"""
        address = Address(self.address_id, user_id, street, city)
        self.addresses[self.address_id] = address
        
        # Maintain relationship
        user = self.users[user_id]
        user.add_address(address)
        
        self.address_id += 1
        return address
    
    def get_user_summary(self, user_id):
        """Get complete user summary"""
        user = self.users[user_id]
        
        # Hydrate relationships
        orders = []
        for order in user.orders:
            product = self.products[order.product_id]
            orders.append({
                "order_id": order.id,
                "product": product.name,
                "price": product.price,
                "quantity": order.quantity,
                "total": product.price * order.quantity
            })
        
        addresses = [
            {"street": addr.street, "city": addr.city}
            for addr in user.addresses
        ]
        
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "orders": orders,
            "addresses": addresses,
            "total_spent": sum(o["total"] for o in orders)
        }

# Usage
print("=== PRODUCTION DATA MODEL ===\n")

db = DataModel()

# Create users
alice = db.create_user("Alice", "alice@example.com")
bob = db.create_user("Bob", "bob@example.com")

# Create products
laptop = db.create_product("Laptop", 1000)
mouse = db.create_product("Mouse", 50)
keyboard = db.create_product("Keyboard", 100)

# Create orders
db.create_order(alice.id, laptop.id, 1)
db.create_order(alice.id, mouse.id, 2)
db.create_order(bob.id, keyboard.id, 1)

# Add addresses
db.add_address(alice.id, "123 Main St", "NYC")
db.add_address(bob.id, "456 Elm Ave", "LA")

# Get summary
summary = db.get_user_summary(alice.id)
print(f"User: {summary['name']}")
print(f"Email: {summary['email']}")
print(f"Orders: {len(summary['orders'])}")
print(f"Total Spent: ${summary['total_spent']}")
print(f"Addresses: {summary['addresses']}")

# Output:
# User: Alice
# Email: alice@example.com
# Orders: 2
# Total Spent: $1100
# Addresses: [{'street': '123 Main St', 'city': 'NYC'}]
```

---

## 💡 Mini Project: "Design a Database Schema"

### Phase 1: Simple E-Commerce ⭐

**Requirements:**
- Users, Products, Orders tables
- Relationships
- Basic queries
- No optimization

---

### Phase 2: Advanced (With Optimization) ⭐⭐

**Requirements:**
- Normalization
- Strategic denormalization
- Indexes
- Query optimization

---

### Phase 3: Enterprise (Scaling) ⭐⭐⭐

**Requirements:**
- Multi-region support
- Sharding strategy
- Temporal data
- Performance monitoring

---

## ⚖️ Normalization vs Denormalization

| Aspect | Normalized | Denormalized |
|--------|-----------|--------------|
| **Redundancy** | Minimal | High |
| **Update Consistency** | Guaranteed | Risk |
| **Query Speed** | May be slow | Fast |
| **Storage** | Efficient | Wasteful |
| **Maintenance** | Complex | Simple |
| **Join Complexity** | High | Low |
| **Best For** | Write-heavy | Read-heavy |

---

## 🎯 Design Steps

```
1. IDENTIFY ENTITIES
   What are the main "things"?
   Users, Products, Orders, etc.

2. IDENTIFY ATTRIBUTES
   What properties does each have?
   User: name, email, phone
   Product: name, price, description

3. IDENTIFY RELATIONSHIPS
   How do entities connect?
   User has many Orders
   Order contains one or more Products

4. NORMALIZE
   Remove redundancy
   Organize into tables

5. ADD INDEXES
   Speed up frequent queries

6. DENORMALIZE IF NEEDED
   For performance, if reads >> writes

7. VALIDATE
   Can you query efficiently?
   Is data consistent?
```

---

## ❌ Common Mistakes

### Mistake 1: Over-Normalization

```python
# ❌ Everything split into tiny tables
# 30 joins needed for simple query
# Performance suffers

# ✅ Balance normalization with performance
# Normalize for consistency
# Denormalize strategically
```

### Mistake 2: Using Wrong Data Types

```python
# ❌ Store phone as TEXT
# Can't do numeric operations
# Sorting weird

# ✅ Use appropriate types
# Phone: VARCHAR(20)
# Age: INT
# Created: TIMESTAMP
# Is Active: BOOLEAN
```

### Mistake 3: Forgetting Relationships

```python
# ❌ No foreign keys
# Data integrity not enforced
# Orphaned records possible

# ✅ Use foreign keys
# Enforce referential integrity
# Database ensures consistency
```

---

## 📚 Additional Resources

**Database Design:**
- [Database Design - Medium](https://medium.com/quick-code/database-design-for-beginners)
- [Normalization Explained](https://en.wikipedia.org/wiki/Database_normalization)

**Tools:**
- [ERDPlus](https://erdplus.com/) - Draw ER diagrams
- [Lucidchart](https://www.lucidchart.com/) - Diagramming
- [MySQL Workbench](https://www.mysql.com/products/workbench/) - Design & admin

---

## 🎯 Before You Leave

**Can you answer these?**

1. **What's the difference between normalization and denormalization?**
   - Answer: Norm = remove redundancy; Denorm = add redundancy for speed

2. **What are the three normal forms?**
   - Answer: 1NF (atomic), 2NF (no partial deps), 3NF (no transitive deps)

3. **When should you denormalize?**
   - Answer: Read-heavy workloads, performance critical

4. **What's a foreign key?**
   - Answer: Constraint that ensures referential integrity between tables

5. **Name the three types of relationships**
   - Answer: One-to-One, One-to-Many, Many-to-Many

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **Junior Dev:** "I'll just store everything in one table!"
>
> **Senior Dev:** "How is that going?"
>
> **Junior Dev (3 months later):** "We have 500GB of redundant data and queries take 5 minutes."
>
> **Senior Dev:** "Yeah, that's why we normalize databases."

---

[← Back to Main](../README.md) | [Previous: CDN](14-cdn.md) | [Next: File Storage →](16-file-storage.md)

---

**Last Updated:** November 10, 2025  
**Difficulty:** ⭐⭐⭐ Intermediate (requires SQL knowledge)  
**Time to Read:** 26 minutes  
**Time to Design Schemas:** 4-6 hours per phase  

---

*Good data modeling: The difference between "It works!" and "Why is everything broken?"* 🚀