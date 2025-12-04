### Entities: Have a Unique Identity and a Life Story

An **Entity** is an object whose identity matters more than its individual attributes. Think of it as a person. A person has a unique identity that persists over time, even if their attributes—like their address, last name, or job—change. Two entities are considered the same only if they share the same unique ID.[^2][^3][^4][^1]

**Key Characteristics of an Entity:**

* **Unique Identity**: It has a specific ID (like a `userID`, `orderID`, or `productID`) that distinguishes it from all other objects, even if their other properties are identical.[^1]
* **Mutable State**: Its attributes can, and often do, change over its lifetime. An order's status changes from "Pending" to "Shipped," or a user updates their profile information.[^5]
* **Continuity**: It represents something that has a history or a lifecycle within the system.[^4]


### Value Objects: Are Defined by Their Value

A **Value Object** is an object defined by its attributes, not by a unique identity. Its value *is* its identity. Think of a specific amount of money, like a \$20 bill. If you and a friend both have a \$20 bill, they are interchangeable. You don't care about *which specific* \$20 bill you have, just that its value is twenty dollars.[^6][^7]

**Key Characteristics of a Value Object:**

* **No Unique Identity**: It doesn't have an ID field. Its identity is derived from the combination of its attributes. Two Value Objects are equal if all their attributes are the same.[^8][^1]
* **Immutable**: Once created, a Value Object cannot be changed. If you need to "change" it, you create a new one with the updated values and replace the old one entirely.[^8][^1]
* **Descriptive**: It describes a characteristic of an Entity, like a date range, a color, or a location.[^9][^10]

***

### A Production Example: A Ride-Sharing App

Let's model a trip in a ride-sharing application like Uber or Lyft.

#### The `Trip` as an Entity

A `Trip` is a perfect example of an **Entity**.

* **Identity**: Each trip has a unique `tripId`. Even if two different users request a ride from the exact same start to the exact same destination at the same time, they are two distinct trips. Their `tripId` makes them unique.
* **Mutability**: The `Trip` object's state changes throughout its lifecycle.
    * It starts with a status of `REQUESTED`.
    * It changes to `DRIVER_ASSIGNED` when a driver accepts.
    * It becomes `IN_PROGRESS` when the passenger is picked up.
    * Finally, it is `COMPLETED` or `CANCELLED`.
* **Continuity**: The `Trip` entity tells a story from start to finish. We track its history, associate it with a specific user and driver, and store details about its journey.

```python
# The Trip is an ENTITY
class Trip:
    def __init__(self, trip_id, user_id, start_location, end_location):
        self.trip_id = trip_id  # The unique identifier
        self.user_id = user_id
        self.start_location = start_location
        self.end_location = end_location
        self.status = "REQUESTED"  # The state is mutable
        self.driver_id = None

    def assign_driver(self, driver_id):
        self.driver_id = driver_id
        self.status = "DRIVER_ASSIGNED"

    # Other methods to change state...

    def __eq__(self, other):
        # Equality is based ONLY on the ID
        return isinstance(other, Trip) and self.trip_id == other.trip_id
```


#### `RouteSuggestion` as a Value Object

Before a trip starts, the app might calculate several potential routes to suggest to the driver, each with an estimated duration and distance. This `RouteSuggestion` is a **Value Object**.

* **No Identity**: A route suggestion doesn't need a unique ID. It is defined entirely by its `duration`, `distance`, and the `path` (the sequence of roads to take). If the app calculates two identical routes (same duration, distance, and path), they are completely interchangeable.
* **Immutability**: A specific route suggestion is a snapshot in time. If traffic conditions change, the system doesn't modify the existing `RouteSuggestion` object. It discards it and generates a brand new `RouteSuggestion` with the updated estimates.
* **Descriptive**: It describes a characteristic of the potential journey. It doesn't have a life story; it's just a piece of data.

```python
# A RouteSuggestion is a VALUE OBJECT
class RouteSuggestion:
    def __init__(self, duration_minutes, distance_km, path_directions):
        self.duration_minutes = duration_minutes
        self.distance_km = distance_km
        self.path_directions = tuple(path_directions) # Use a tuple for immutability

    # No methods to change state are provided. It is immutable.

    def __eq__(self, other):
        # Equality is based on STRUCTURAL equality (all attributes must match)
        return (isinstance(other, RouteSuggestion) and
                self.duration_minutes == other.duration_minutes and
                self.distance_km == other.distance_km and
                self.path_directions == other.path_directions)

# --- Usage ---
route1 = RouteSuggestion(25, 10, ["Main St", "Oak Ave", "Pine Ln"])
route2 = RouteSuggestion(25, 10, ["Main St", "Oak Ave", "Pine Ln"])
route3 = RouteSuggestion(22, 9.5, ["Elm St", "Cedar Blvd"])

print(f"Is route1 the same as route2? {route1 == route2}") # True, they have the same values
print(f"Is route1 the same as route3? {route1 == route3}") # False, their values are different
```

By distinguishing between Entities and Value Objects, you create a clearer and more robust data model that better reflects the real world, leading to more maintainable and scalable software.[^6]
<span style="display:none">[^11][^12][^13][^14][^15][^16][^17][^18][^19][^20]</span>

<div align="center">⁂</div>

[^1]: https://stackoverflow.com/questions/75446/value-vs-entity-objects-domain-driven-design

[^2]: https://www.linkedin.com/pulse/entity-vs-value-object-quan-ding

[^3]: https://www.reddit.com/r/DomainDrivenDesign/comments/rxk8yd/entity_vs_value_objects/

[^4]: https://dev.to/ielgohary/domain-driven-design-entities-value-objects-and-services-chapter-51-22cm

[^5]: https://www.youtube.com/watch?v=7nnGlbkjwx8

[^6]: https://www.kranio.io/en/blog/de-bueno-a-excelente-en-ddd-entendiendo-los-entities-y-value-objects-en-domain-driven-design---2-10

[^7]: https://www.linkedin.com/pulse/value-objects-ddd-dmitry-neversky-jkijf

[^8]: https://enterprisecraftsmanship.com/posts/entity-vs-value-object-the-ultimate-list-of-differences/

[^9]: http://seedstack.org/guides/ddd-for-beginners/entities-and-value-objects/

[^10]: https://www.dremio.com/wiki/value-object/

[^11]: https://wempe.dev/blog/domain-driven-design-entities-value-objects

[^12]: https://www.tutorialspoint.com/software_engineering/software_design_strategies.htm

[^13]: https://www.telerik.com/blogs/domain-driven-design-principles-value-objects-aspnet-core

[^14]: https://www.institutedata.com/blog/erd-in-software-engineering/

[^15]: https://martinfowler.com/bliki/ValueObject.html

[^16]: https://drbtaneja.com/characteristics-of-a-good-software-design/

[^17]: https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/implement-value-objects

[^18]: https://academy.pega.com/topic/entity-design-pattern/v1

[^19]: https://www.milanjovanovic.tech/blog/value-objects-in-dotnet-ddd-fundamentals

[^20]: https://www.geeksforgeeks.org/software-engineering/software-engineering-software-characteristics/

