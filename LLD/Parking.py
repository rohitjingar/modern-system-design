from abc import ABC, abstractmethod
from datetime import datetime
from threading import Lock
import uuid
import random


# -----------------------------------------
# ENUMS / CONSTANTS
# -----------------------------------------

class SpotSize:
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"


class SpotStatus:
    AVAILABLE = "Available"
    OCCUPIED = "Occupied"
    OUT_OF_SERVICE = "OutOfService"


class FloorStatus:
    ACTIVE = "Active"
    CLOSED = "Closed"


# -----------------------------------------
# VEHICLES
# -----------------------------------------

class Vehicle(ABC):
    def __init__(self, plate_number: str, vehicle_type: str, size: str):
        self.plate_number = plate_number
        self.vehicle_type = vehicle_type
        self.size = size


class Car(Vehicle):
    def __init__(self, plate_number: str):
        super().__init__(plate_number, "Car", SpotSize.MEDIUM)


class Bike(Vehicle):
    def __init__(self, plate_number: str):
        super().__init__(plate_number, "Bike", SpotSize.SMALL)


class Truck(Vehicle):
    def __init__(self, plate_number: str):
        super().__init__(plate_number, "Truck", SpotSize.LARGE)


# -----------------------------------------
# PARKING SPOT (THREAD-SAFE)
# -----------------------------------------

class ParkingSpot:
    def __init__(self, spot_id: str, spot_size: str):
        self.spot_id = spot_id
        self.spot_size = spot_size
        self.spot_status = SpotStatus.AVAILABLE
        self.current_vehicle: Vehicle | None = None
        self._lock = Lock()

    @property
    def is_available(self) -> bool:
        # small race conditions here are acceptable because
        # assign/remove use the lock and are atomic
        return self.spot_status == SpotStatus.AVAILABLE and self.current_vehicle is None

    def assign_vehicle(self, vehicle: Vehicle):
        with self._lock:
            if not self.is_available:
                # someone else might have taken it already
                raise ValueError("Spot is not available")
            self.current_vehicle = vehicle
            self.spot_status = SpotStatus.OCCUPIED

    def remove_vehicle(self):
        with self._lock:
            if self.current_vehicle is None:
                raise ValueError("Spot is not occupied")
            self.current_vehicle = None
            self.spot_status = SpotStatus.AVAILABLE


# -----------------------------------------
# FLOOR
# -----------------------------------------

class Floor:
    def __init__(self, floor_number: int):
        self.floor_number = floor_number
        self.status = FloorStatus.ACTIVE
        self.spots_by_size: dict[str, list[ParkingSpot]] = {
            SpotSize.SMALL: [],
            SpotSize.MEDIUM: [],
            SpotSize.LARGE: []
        }

    def add_spots(self, spot_size: str, count: int):
        for _ in range(count):
            spot_id = str(uuid.uuid4())
            self.spots_by_size[spot_size].append(ParkingSpot(spot_id, spot_size))

    def get_available_spots(self, spot_size: str) -> list[ParkingSpot]:
        if self.status != FloorStatus.ACTIVE:
            return []
        # reading is fine since spot-level operations are locked
        return [spot for spot in self.spots_by_size[spot_size] if spot.is_available]


# -----------------------------------------
# TICKET
# -----------------------------------------

class ParkingTicket:
    def __init__(self, vehicle_number: str, floor_number: int, spot_id: str):
        self.ticket_id = str(uuid.uuid4())
        self.vehicle_number = vehicle_number
        self.floor_number = floor_number
        self.spot_id = spot_id
        self.entry_time = datetime.now()
        self.exit_time = None


# -----------------------------------------
# SPOT ASSIGNMENT STRATEGIES (THREAD-SAFE BY DESIGN - STATELESS)
# -----------------------------------------

class SpotAssignmentStrategy(ABC):
    @abstractmethod
    def select_spot(self, floors: list[Floor], vehicle: Vehicle) -> tuple[Floor, ParkingSpot] | None:
        pass


class NearestSpotStrategy(SpotAssignmentStrategy):
    """Choose the first available spot floor-by-floor, smallest index first."""
    def select_spot(self, floors: list[Floor], vehicle: Vehicle):
        priority = {
            SpotSize.SMALL: [SpotSize.SMALL, SpotSize.MEDIUM, SpotSize.LARGE],
            SpotSize.MEDIUM: [SpotSize.MEDIUM, SpotSize.LARGE],
            SpotSize.LARGE: [SpotSize.LARGE]
        }

        for floor in floors:
            for size in priority[vehicle.size]:
                available = floor.get_available_spots(size)
                if available:
                    return floor, available[0]
        return None


class RandomSpotStrategy(SpotAssignmentStrategy):
    def select_spot(self, floors: list[Floor], vehicle: Vehicle):
        matches: list[tuple[Floor, ParkingSpot]] = []
        priority = {
            SpotSize.SMALL: [SpotSize.SMALL, SpotSize.MEDIUM, SpotSize.LARGE],
            SpotSize.MEDIUM: [SpotSize.MEDIUM, SpotSize.LARGE],
            SpotSize.LARGE: [SpotSize.LARGE]
        }

        for floor in floors:
            for size in priority[vehicle.size]:
                for spot in floor.get_available_spots(size):
                    matches.append((floor, spot))

        return random.choice(matches) if matches else None


class CheapestSpotStrategy(SpotAssignmentStrategy):
    """For demo: assume Small < Medium < Large is cheaper."""
    price_order = [SpotSize.SMALL, SpotSize.MEDIUM, SpotSize.LARGE]

    def select_spot(self, floors: list[Floor], vehicle: Vehicle):
        priority = {
            SpotSize.SMALL: self.price_order,
            SpotSize.MEDIUM: self.price_order[1:],
            SpotSize.LARGE: self.price_order[2:]
        }

        for size in priority[vehicle.size]:
            for floor in floors:
                available = floor.get_available_spots(size)
                if available:
                    return floor, available[0]
        return None


# -----------------------------------------
# PARKING LOT (THREAD-SAFE)
# -----------------------------------------

class ParkingLot:
    def __init__(self, name: str, location: str, strategy: SpotAssignmentStrategy):
        self.name = name
        self.location = location
        self.floors: list[Floor] = []
        self.strategy = strategy

        # shared mutable state
        self.active_parking_map: dict[str, ParkingSpot] = {}   # vehicle_number → spot
        self.active_tickets: dict[str, ParkingTicket] = {}     # ticket_id → ticket

        # main lock to protect shared structures & overall park/unpark operations
        self._lock = Lock()

    def add_floor(self, floor: Floor):
        # floors list is usually set up during initialization;
        # if modified at runtime, wrap in lock as well
        self.floors.append(floor)

    def park_vehicle(self, vehicle: Vehicle) -> ParkingTicket:
        with self._lock:
            if vehicle.plate_number in self.active_parking_map:
                raise ValueError("Vehicle already parked.")

            # choose spot using strategy
            result = self.strategy.select_spot(self.floors, vehicle)
            if not result:
                raise ValueError("No available spot found.")

            floor, spot = result

            # this can still fail if another thread grabbed the spot in the tiny gap
            # but assign_vehicle is atomic & will raise, and in real world we'd retry
            spot.assign_vehicle(vehicle)

            ticket = ParkingTicket(vehicle.plate_number, floor.floor_number, spot.spot_id)
            self.active_parking_map[vehicle.plate_number] = spot
            self.active_tickets[ticket.ticket_id] = ticket

            return ticket

    def unpark_vehicle(self, vehicle_number: str) -> ParkingTicket:
        with self._lock:
            if vehicle_number not in self.active_parking_map:
                raise ValueError("Vehicle not parked here.")

            spot = self.active_parking_map[vehicle_number]
            spot.remove_vehicle()

            # Find matching ticket
            ticket: ParkingTicket | None = None
            for t in self.active_tickets.values():
                if t.vehicle_number == vehicle_number:
                    ticket = t
                    break

            if not ticket:
                raise RuntimeError("Ticket not found for vehicle.")

            ticket.exit_time = datetime.now()

            # Cleanup
            del self.active_parking_map[vehicle_number]
            del self.active_tickets[ticket.ticket_id]

            return ticket

    def get_available_spots(self) -> dict[int, dict[str, int]]:
        # read-only snapshot; we take the lock to avoid reading mid-update
        with self._lock:
            summary: dict[int, dict[str, int]] = {}
            for floor in self.floors:
                summary[floor.floor_number] = {
                    size: len(floor.get_available_spots(size))
                    for size in floor.spots_by_size
                }
            return summary

# -----------------------------------------
# VEHICLE FACTORY
# -----------------------------------------

class VehicleFactory:
    @staticmethod
    def create_vehicle(vehicle_type: str, plate_number: str) -> Vehicle:
        v = vehicle_type.lower()

        if v == "car":
            return Car(plate_number)
        elif v == "bike":
            return Bike(plate_number)
        elif v == "truck":
            return Truck(plate_number)

        raise ValueError(f"Unknown vehicle type: {vehicle_type}")



# -----------------------------------------
# SAMPLE USAGE / TESTING
# -----------------------------------------

if __name__ == "__main__":
    # Create Parking Lot with desired strategy
    strategy = NearestSpotStrategy()
    parking_lot = ParkingLot("City Center Parking", "Downtown", strategy)

    # Create Floors
    floor1 = Floor(1)
    floor1.add_spots(SpotSize.SMALL, 2)
    floor1.add_spots(SpotSize.MEDIUM, 2)
    floor1.add_spots(SpotSize.LARGE, 1)

    floor2 = Floor(2)
    floor2.add_spots(SpotSize.SMALL, 1)
    floor2.add_spots(SpotSize.MEDIUM, 2)
    floor2.add_spots(SpotSize.LARGE, 1)

    parking_lot.add_floor(floor1)
    parking_lot.add_floor(floor2)

    # Print available spots
    print("\nAvailable spots initially:")
    print(parking_lot.get_available_spots())



    car = VehicleFactory.create_vehicle("car", "CAR-1234")
    bike = VehicleFactory.create_vehicle("bike", "BIKE-1111")
    truck = VehicleFactory.create_vehicle("truck", "TRUCK-4444")

    # Park vehicles
    print("\n--- Parking Vehicles ---")
    ticket1 = parking_lot.park_vehicle(car)
    print(f"Car parked → Ticket: {ticket1.ticket_id}, Floor: {ticket1.floor_number}, Spot: {ticket1.spot_id}")

    ticket2 = parking_lot.park_vehicle(bike)
    print(f"Bike parked → Ticket: {ticket2.ticket_id}, Floor: {ticket2.floor_number}, Spot: {ticket2.spot_id}")

    ticket3 = parking_lot.park_vehicle(truck)
    print(f"Truck parked → Ticket: {ticket3.ticket_id}, Floor: {ticket3.floor_number}, Spot: {ticket3.spot_id}")

    # Print available spots again
    print("\nAvailable spots after parking:")
    print(parking_lot.get_available_spots())

    # Unpark a vehicle
    print("\n--- Unparking Car ---")
    final_ticket = parking_lot.unpark_vehicle("CAR-1234")
    print(f"Vehicle: {final_ticket.vehicle_number} exited at {final_ticket.exit_time}")
    print(f"Ticket ID: {final_ticket.ticket_id}")
    
    # Available spots after unparking
    print("\nAvailable spots after car exit:")
    print(parking_lot.get_available_spots())
