
# Inheritance

**Inheritance** is an OOP principle allowing a class (child/subclass) to derive properties and behaviors (methods, attributes) from another class (parent/superclass). It enables code reuse, promotes consistency, and models real-world relationships in software.

***

## Real-World Example: Production Backend (Python)

### Scenario: User Types in a Web Application

Suppose you manage different user roles in a backend: **User**, **Admin**, and **Guest**. All users share basic attributes (like email), but admins have extra permissions.

#### Base Class

```python
class User:
    def __init__(self, email):
        self.email = email

    def get_permissions(self):
        return ['read']

    def __repr__(self):
        return f'User(email={self.email})'
```


#### Subclass for Admins

```python
class Admin(User):  # Inherits from User
    def get_permissions(self):
        return ['read', 'write', 'delete']

    def __repr__(self):
        return f'Admin(email={self.email})'
```


#### Subclass for Guests

```python
class Guest(User):
    def get_permissions(self):
        return ['read']

    def __repr__(self):
        return f'Guest(email={self.email})'
```


#### Usage in Backend API

```python
def show_user_permissions(user: User):
    print(f"{user}: {user.get_permissions()}")

u1 = User("alice@company.com")
a1 = Admin("bob@company.com")
g1 = Guest("guest@domain.com")

show_user_permissions(u1)  # User(email=alice@company.com): ['read']
show_user_permissions(a1)  # Admin(email=bob@company.com): ['read', 'write', 'delete']
show_user_permissions(g1)  # Guest(email=guest@domain.com): ['read']
```


***

## Production Context

- **DRY Principle:** Inheritance avoids duplicating shared fields (like email) or methods (like `get_permissions`).
- **Extensibility:** New user roles (e.g., `Moderator`) can be added easily by subclassing and overriding methods.
- **Backend Usage:** In REST APIs (e.g., Flask/Django), views or serializers often use inheritance to build on base request/response logic or validation patterns.
- **Security:** Permission logic is centralized and can be changed for all user types by updating the base class.

***

## Other Common Backend Patterns

### Example: ORM Models (Django/SQLAlchemy)

Often, base models are subclassed for shared database fields or behaviors.

```python
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class Customer(BaseModel):
    name = models.CharField(max_length=100)

class Order(BaseModel):
    order_number = models.CharField(max_length=50)
```

All models inherit the creation timestamp—no repetition needed.

***

## Summary

Inheritance in backend Python codebases models real-world relationships (users/roles/entities), centralizes shared logic and attributes, and streamlines extension and maintenance. Always use inheritance for DRY, scalable, and maintainable backend architecture.

