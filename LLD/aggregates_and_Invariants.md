### What is an Aggregate?

An **Aggregate** is a cluster of related domain objects (Entities and Value Objects) that are treated as a single, self-contained unit. Think of it as a protective boundary drawn around a group of objects that logically belong together. This boundary isn't just for organization; it's a consistency boundary.[^1][^2][^3]

The key rules for an Aggregate are:

1. **The Aggregate Root**: Every aggregate has a single, specific entity known as the **Aggregate Root**. It's the "front door" to the aggregate.[^4][^5]
2. **External Access**: Objects outside the aggregate boundary are only allowed to hold a reference to the Aggregate Root. They are forbidden from directly accessing or modifying any other object inside the aggregate.[^3]
3. **Transactional Consistency**: When a change is made, the entire aggregate is loaded, the change is applied, and the entire aggregate is saved within a single transaction. This ensures that the aggregate as a whole is always in a consistent state.[^6]

### What is an Invariant?

An **Invariant** is a business rule or condition that must *always* be true for an aggregate to be considered valid. It's a promise of consistency that the aggregate must never break.[^7][^8][^3]

For example:

* The total price of an order must equal the sum of its line items plus tax.
* A bank account balance must never drop below zero.[^7]
* A shipment cannot be marked as "delivered" before it has been marked as "shipped".

The primary responsibility of the **Aggregate Root** is to enforce these invariants. It acts as a gatekeeper, validating all incoming commands and rejecting any operation that would violate a business rule and put the aggregate in an invalid state.[^8]

***

### A Production Example: A Collaborative Whiteboard

Imagine a collaborative online whiteboard application where users can create boards, add notes, and invite others to collaborate. A `Whiteboard` is a perfect candidate for an Aggregate.

* **Aggregate Root**: `Whiteboard`
* **Internal Objects**: `Note` (could be a Value Object), `Collaborator` (Entity)

Here are some business rules **(Invariants)** for our whiteboard:

1. A board must always have an owner.
2. The number of notes on a "Free Tier" board cannot exceed 50.
3. A `Collaborator` with "Read-Only" permissions cannot add or delete notes.
4. A note's position (x, y coordinates) cannot be outside the boundaries of the whiteboard.
5. A board cannot be deleted if it has active collaborators other than the owner.

The `Whiteboard` class, as the Aggregate Root, is responsible for enforcing all these rules.

```python
class Collaborator:
    def __init__(self, user_id, role="ReadOnly"): # Roles: "Editor", "ReadOnly"
        self.user_id = user_id
        self.role = role

class Note:
    def __init__(self, note_id, content, position):
        self.note_id = note_id
        self.content = content
        self.position = position # A Value Object, e.g., Point(x, y)

# The Whiteboard is the AGGREGATE ROOT
class Whiteboard:
    def __init__(self, board_id, owner_id, plan_tier="Free"):
        self._id = board_id
        self._owner_id = owner_id
        self._plan_tier = plan_tier
        self._notes = {} # Internal collection of notes
        self._collaborators = {owner_id: Collaborator(owner_id, "Owner")}
        self._width = 1920
        self._height = 1080

    @property
    def id(self):
        return self._id

    # This method is the "gatekeeper" for adding notes
    def add_note(self, user_id, note_id, content, position):
        # INVARIANT CHECK 1: Permission
        if user_id not in self._collaborators or self._collaborators[user_id].role == "ReadOnly":
            raise PermissionError("User does not have permission to add notes.")

        # INVARIANT CHECK 2: Plan limits
        if self._plan_tier == "Free" and len(self._notes) >= 50:
            raise ValueError("Free tier boards cannot have more than 50 notes.")
        
        # INVARIANT CHECK 3: Position boundaries
        if not (0 <= position.x <= self._width and 0 <= position.y <= self._height):
            raise ValueError("Note position is outside the board boundaries.")

        # If all invariants pass, perform the operation
        new_note = Note(note_id, content, position)
        self._notes[note_id] = new_note
        print(f"Note {note_id} added successfully.")

    def add_collaborator(self, user_id, role):
        if user_id in self._collaborators:
            # Logic to update role if needed
            return
        self._collaborators[user_id] = Collaborator(user_id, role)

    # The gatekeeper for deletion
    def can_be_deleted(self):
        # INVARIANT CHECK 4: Cannot delete with active collaborators
        if len(self._collaborators) > 1:
            return False # Business rule: Don't allow deletion if others are collaborating
        return True

```

In this example, you can't just create a `Note` and assign it to a board from the outside. You **must** go through the `Whiteboard.add_note()` method. This allows the `Whiteboard` aggregate to protect its internal consistency by verifying every business rule (invariant) before making a change.
<span style="display:none">[^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^20][^9]</span>

<div align="center">⁂</div>

[^1]: https://martinfowler.com/bliki/DDD_Aggregate.html

[^2]: https://stackoverflow.com/questions/76373430/what-is-an-aggregate

[^3]: https://codeopinion.com/aggregate-design-using-invariants-as-a-guide/

[^4]: https://dzone.com/articles/domain-driven-design-aggregate

[^5]: https://www.baeldung.com/cs/aggregate-root-ddd

[^6]: https://www.jamesmichaelhickey.com/domain-driven-design-aggregates/

[^7]: https://ddd-practitioners.com/home/glossary/business-invariant/

[^8]: https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/domain-model-layer-validations

[^9]: https://www.linkedin.com/pulse/understanding-aggregates-domain-driven-design-ddd-dmitry-neversky-qxbff

[^10]: https://stackoverflow.com/questions/1958621/whats-an-aggregate-root

[^11]: https://www.reddit.com/r/DomainDrivenDesign/comments/1kdxhzz/how_do_i_enforce_invariants_between_aggregates/

[^12]: https://www.youtube.com/watch?v=djq0293b2bA

[^13]: https://mbarkt3sto.hashnode.dev/ddd-entity-vs-value-object-vs-aggregate-root

[^14]: https://redis.io/glossary/domain-driven-design-ddd/

[^15]: https://khorikov.org/posts/2022-06-06-validation-vs-invariants/

[^16]: https://www.youtube.com/watch?v=Pkvt87yL6Gs

[^17]: https://stackoverflow.com/questions/17967888/ddd-enforce-invariants-with-small-aggregate-roots

[^18]: https://www.alibabacloud.com/blog/an-in-depth-understanding-of-aggregation-in-domain-driven-design_598034

[^19]: https://no-kill-switch.ghost.io/why-domain-invariants-are-critical-to-build-good-software/

[^20]: https://www.youtube.com/watch?v=64ngP-aUYPc

