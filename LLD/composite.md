It’s a design pattern that lets you treat a group of objects and a single object in the same way — like a tree structure (folders containing files or other folders). Single or group — handle both the same way.

let's build a **Role-Based Access Control (RBAC) System** with nested group permissions—a common real-world need in SaaS, enterprise apps, and platforms with fine-grained user controls.

***

## 1. The Bad Example: “Manual Parent-Child Checks Everywhere”

Suppose you want to check permissions for resources/users, but you end up with code like this:

```python
def check_permission(user, permission):
    # Individual user permissions
    if permission in user.permissions:
        return True
    # Now check group
    for group in user.groups:
        if permission in group.permissions:
            return True
        # What if group has subgroups? Ugh...
        for subgroup in group.subgroups:
            if permission in subgroup.permissions:
                return True
            # ...keep nest-checking manually
    # Nightmare for deep hierarchies!
    return False
```


### Why is this bad?

- **Manual, fragile, hard-to-extend logic:** Any change in hierarchy means massive code changes.
- **Recursion bugs:** “Just one more ‘for’ loop,” until stack overflows or bugs creep in.
- **Inflexible:** What if groups themselves contain mix of users and subgroups?
- **No uniform API:** Hard to treat users/groups/subgroups the same way.

**Humour Break:**
> "RBAC the night before launch: 'Just add another loop!' —famous last words."

***

## 2. The Good Example: **Composite Pattern for Hierarchical Permissions**

With Composite, we treat both individuals and groups using a uniform interface—so you can recurse deeply, but cleanly.

### Pythonic Composite Example: RBAC (Users, Groups, Subgroups)

```python
from abc import ABC, abstractmethod
from typing import List

# Component base class
class PermissionEntity(ABC):
    @abstractmethod
    def has_permission(self, permission: str) -> bool:
        pass

# Leaf: Individual User
class User(PermissionEntity):
    def __init__(self, name, permissions):
        self.name = name
        self.permissions = set(permissions)  # Set for O(1) lookup

    def has_permission(self, permission: str) -> bool:
        print(f"Checking {permission} for user {self.name}")
        return permission in self.permissions

# Composite: Group that contains users and/or subgroups
class Group(PermissionEntity):
    def __init__(self, name):
        self.name = name
        self.members: List[PermissionEntity] = []
        self.permissions = set()  # Permissions directly on group

    def add_member(self, member: PermissionEntity):
        self.members.append(member)

    def add_permission(self, permission: str):
        self.permissions.add(permission)

    def has_permission(self, permission: str) -> bool:
        print(f"Checking {permission} for group {self.name}")
        # Direct group permissions
        if permission in self.permissions:
            return True
        # Check recursively for permissions in members
        for member in self.members:
            if member.has_permission(permission):
                return True
        return False

# Example usage
# Create users
alice = User("Alice", ["read"])
bob = User("Bob", ["write"])
carol = User("Carol", [])

# Create subgroups
admins = Group("Admins")
admins.add_member(alice)
admins.add_permission("delete")  # Admins inherit 'delete'

editors = Group("Editors")
editors.add_member(bob)
editors.add_permission("edit")

# Main group containing subgroups and users
company = Group("MyCompany")
company.add_member(admins)
company.add_member(editors)
company.add_member(carol)
company.add_permission("view")  # All company members inherit 'view'

# Permission checks (composite pattern = recursion, but clean and uniform!)
print(company.has_permission("delete"))  # True via Admins group
print(company.has_permission("edit"))    # True via Editors group
print(company.has_permission("read"))    # True via Alice, inside Admins
print(company.has_permission("view"))    # True via company permission
print(company.has_permission("write"))   # True via Bob, inside Editors
print(company.has_permission("foo"))     # False (nobody has it)
```


### **Why is this better?**

- **Recursive, but elegant:** No matter how deep the hierarchy, one method does the right thing.
- **Uniform API:** Treat users, groups, subgroups identically.
- **Flexible:** Easily add more levels, types, mix and match.
- **Extensible:** Add other entity types (roles, resources, etc.) if needed.

**Humour Break:**
> “Composite: Like Russian nesting dolls, but for permissions. And with less existential dread!”

***

## 3. **Real-World Backend Scenario**

- **Enterprise SaaS:** Nested permissions for orgs, teams, departments, projects.
- **Cloud Platforms:** IAM policies layered across groups/projects/accounts.
- **University Portals:** Faculties, schools, departments, labs—each with members and subgroups.
- **GitHub Teams:** Nested team management to grant repo/project access.

Composite lets you:

- Add/remove users/groups/subgroups dynamically.
- Check any permission efficiently, no matter hierarchy depth.
- Refactor user/group management easily as requirements change and org grows.

***

## 4. **Production Trade-Offs**

- **Recursion limits:** For “monster” orgs with thousands of nested groups, manage recursion carefully.
- **Performance:** Precompute effective permissions or cache them for big hierarchies.
- **Debugging:** Add clear logs or traces so you know *where* permission came from in deep nests.

***

## 5. **Summary**

- **Bad Example:** Manual loops for each hierarchy level, brittle and hard to manage.
- **Composite Example:** Hierarchical, uniform access control—scalable and easily maintained.
- **Real-World Use:** RBAC, IAM, team/project permissions, resource trees.

