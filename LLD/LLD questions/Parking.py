from abc import ABC, abstractmethod
from datetime import datetime
import time
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
        try:
            with self._lock:
                if not self.is_available:
                    # someone else might have taken it already
                    raise ValueError("Spot is not available")
                self.current_vehicle = vehicle
                self.spot_status = SpotStatus.OCCUPIED
        except Exception as e:
            print(f"Error while assign the vehicle: {vehicle.plate_number} to spot", e)
            raise

    def remove_vehicle(self):
        try:
            with self._lock:
                if self.current_vehicle is None:
                    raise ValueError("Spot is not occupied")
                self.current_vehicle = None
                self.spot_status = SpotStatus.AVAILABLE
        except Exception as e:
            print(f"Error while removing the vehicle: {self.current_vehicle.plate_number} to spot", e)
            raise


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

    def __init__(self, vehicle_number: str, floor_number: int, spot: ParkingSpot):
        self.ticket_id = str(uuid.uuid4())
        self.vehicle_number = vehicle_number
        self.floor_number = floor_number
        self.spot = spot
        self.entry_time = time.time() * 1000 # in ms
        self.exit_time = None
        self.status = 'Active'
        
    def close(self):
        self.exit_time = time.time() * 1000 # in ms
        self.status = 'Close'
        
        
class PricingStrategy:
    parking_rate_per_hour = 100
    

    def calculate_parking_fee(self, ticket:ParkingTicket) -> float:
        if not ticket.entry_time or not ticket.exit_time:
            raise Exception(f"Entry and Exit time required for the ticket : {ticket.ticket_id} to calculate the parking") 
        total_time_hours  = ((ticket.exit_time - ticket.entry_time)/ (1000*60*60))
        total_price = round(self.parking_rate_per_hour * total_time_hours, 2)
        return total_price
        


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
        try:
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
        except Exception as e:
            print("Error while finding the spot in NearestSpotStrategy", e)
            raise


class RandomSpotStrategy(SpotAssignmentStrategy):
    def select_spot(self, floors: list[Floor], vehicle: Vehicle):
        try:
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
        except Exception as e:
            print("Error while finding the spot in RandomSpotStrategy", e)
            raise
            


class CheapestSpotStrategy(SpotAssignmentStrategy):
    """For demo: assume Small < Medium < Large is cheaper."""
    price_order = [SpotSize.SMALL, SpotSize.MEDIUM, SpotSize.LARGE]

    def select_spot(self, floors: list[Floor], vehicle: Vehicle):
        try:
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
        except Exception as e:
            print("Error while finding the spot in CheapestSpotStrategy", e)
            raise


# -----------------------------------------
# PARKING LOT (THREAD-SAFE)
# -----------------------------------------

class ParkingLot:
    def __init__(self, name: str, location: str, strategy: SpotAssignmentStrategy, pricing_strategy:PricingStrategy):
        self.name = name
        self.location = location
        self.floors: list[Floor] = []
        self.strategy = strategy
        self.pricing_strategy = pricing_strategy
        self._lock = Lock()

    def add_floor(self, floor: Floor):
        # floors list is usually set up during initialization;
        # if modified at runtime, wrap in lock as well
        self.floors.append(floor)

    def park_vehicle(self, vehicle: Vehicle) -> ParkingTicket:
        try:

            # choose spot using strategy
            result = self.strategy.select_spot(self.floors, vehicle)
            if not result:
                raise ValueError("No available spot found.")
            floor, spot = result
            spot.assign_vehicle(vehicle)
            ticket = ParkingTicket(vehicle.plate_number, floor.floor_number, spot)
            return ticket
        except Exception as e:
            print(f"Error while parking the vehicle: {vehicle.plate_number}", e)
            raise
                

    def unpark_vehicle(self, ticket: ParkingTicket) -> ParkingTicket:
        try:
            if not ticket:
                raise("Ticket will be required to unpark the vehicle")
            ticket.close()
            ticket.spot.remove_vehicle()
            return ticket
        except Exception as e:
            print(f"Error while unparking the vehicle: {ticket.vehicle_number}", e)
            raise
        
    def get_parking_fee(self, ticket: ParkingTicket) -> float:
        try:
            if not ticket:
                raise("Ticket will be required to get the parking fees")
            return self.pricing_strategy.calculate_parking_fee(ticket)

        except Exception as e:
            print(f"Error while getting the parking fees for ticket: {ticket.ticket_id}", e)
            raise
        
        
            

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

