from abc import ABC, abstractmethod
from enum import Enum
from collections import defaultdict


# ===================== BASICS =====================

class Direction(Enum):
    UP = 1
    DOWN = -1
    NONE = 0


class Request:
    def __init__(self, floor: int, direction: Direction):
        self.floor = floor
        self.direction = direction


class Door:
    def __init__(self):
        self.opened = False

    def open(self):
        self.opened = True

    def close(self):
        self.opened = False


# ===================== STATE INTERFACE =====================

class ElevatorState(ABC):
    @abstractmethod
    def on_enter(self, elevator): pass

    @abstractmethod
    def on_tick(self, elevator): pass

    @abstractmethod
    def handle_request(self, elevator, request: Request): pass


# ===================== ELEVATOR CONTEXT =====================

class Elevator:
    def __init__(self, eid: int, min_floor: int, max_floor: int):
        self.id = eid
        self.current_floor = min_floor
        self.min_floor = min_floor
        self.max_floor = max_floor

        self.direction = Direction.NONE
        self.state: ElevatorState = IdleState()
        self.door = Door()

        self.internal_requests = set()
        self.external_requests = defaultdict(set)

        self.state.on_enter(self)

    # ---------- Events ----------
    def on_tick(self):
        self.state.on_tick(self)

    def on_external_request(self, request: Request):
        self.external_requests[request.floor].add(request.direction)
        self.state.handle_request(self, request)

    def on_internal_request(self, floor: int):
        self.internal_requests.add(floor)

    # ---------- Helpers ----------
    def set_state(self, new_state: ElevatorState):
        self.state = new_state
        self.state.on_enter(self)

    def has_requests_above(self):
        return any(
            f > self.current_floor
            for f in self.internal_requests
        ) or any(
            f > self.current_floor
            for f in self.external_requests
        )

    def has_requests_below(self):
        return any(
            f < self.current_floor
            for f in self.internal_requests
        ) or any(
            f < self.current_floor
            for f in self.external_requests
        )

    def should_stop_here(self):
        if self.current_floor in self.internal_requests:
            return True

        if self.current_floor in self.external_requests:
            return self.direction in self.external_requests[self.current_floor]

        return False

    def clear_current_floor_requests(self):
        self.internal_requests.discard(self.current_floor)
        self.external_requests.pop(self.current_floor, None)


# ===================== STATES =====================

class IdleState(ElevatorState):
    def on_enter(self, elevator):
        elevator.direction = Direction.NONE

    def handle_request(self, elevator, request):
        pass  # decision happens on tick

    def on_tick(self, elevator):
        
        if elevator.should_stop_here():
            elevator.set_state(DoorOpenState())
        elif elevator.has_requests_above():
            elevator.direction = Direction.UP
            elevator.set_state(MovingUpState())
        elif elevator.has_requests_below():
            elevator.direction = Direction.DOWN
            elevator.set_state(MovingDownState())


class MovingUpState(ElevatorState):
    def on_enter(self, elevator):
        pass

    def handle_request(self, elevator, request):
        pass  # requests are stored, not acted on immediately

    def on_tick(self, elevator):
        if elevator.current_floor < elevator.max_floor:
            elevator.current_floor += 1

        if elevator.should_stop_here():
            elevator.set_state(DoorOpenState())
            return

        if not elevator.has_requests_above():
            if elevator.has_requests_below():
                elevator.direction = Direction.DOWN
                elevator.set_state(MovingDownState())
            else:
                elevator.set_state(IdleState())


class MovingDownState(ElevatorState):
    def on_enter(self, elevator):
        pass

    def handle_request(self, elevator, request):
        pass

    def on_tick(self, elevator):
        if elevator.current_floor > elevator.min_floor:
            elevator.current_floor -= 1

        if elevator.should_stop_here():
            elevator.set_state(DoorOpenState())
            return

        if not elevator.has_requests_below():
            if elevator.has_requests_above():
                elevator.direction = Direction.UP
                elevator.set_state(MovingUpState())
            else:
                elevator.set_state(IdleState())


class DoorOpenState(ElevatorState):
    DOOR_OPEN_TICKS = 2

    def on_enter(self, elevator):
        elevator.door.open()
        elevator.clear_current_floor_requests()
        self.timer = self.DOOR_OPEN_TICKS

    def handle_request(self, elevator, request):
        pass  # collect only, no movement

    def on_tick(self, elevator):
        self.timer -= 1
        if self.timer == 0:
            elevator.door.close()
            if elevator.direction == Direction.UP:
                elevator.set_state(MovingUpState())
            elif elevator.direction == Direction.DOWN:
                elevator.set_state(MovingDownState())
            else:
                elevator.set_state(IdleState())


class MaintenanceState(ElevatorState):
    def on_enter(self, elevator):
        elevator.direction = Direction.NONE

    def handle_request(self, elevator, request):
        pass

    def on_tick(self, elevator):
        pass


class EmergencyState(ElevatorState):
    def on_enter(self, elevator):
        elevator.direction = Direction.NONE

    def handle_request(self, elevator, request):
        pass

    def on_tick(self, elevator):
        pass


# ===================== SCHEDULER =====================

class Scheduler:
    def select_elevator(self, elevators, request: Request) -> Elevator:
        best = None
        best_distance = float("inf")

        for e in elevators:
            if isinstance(e.state, IdleState):
                dist = abs(e.current_floor - request.floor)
                if dist < best_distance:
                    best = e
                    best_distance = dist

            elif (
                e.direction == request.direction and
                ((request.direction == Direction.UP and e.current_floor <= request.floor) or
                 (request.direction == Direction.DOWN and e.current_floor >= request.floor))
            ):
                return e  # perfect match

        return best


# ===================== SYSTEM =====================

class ElevatorSystem:
    def __init__(self, num_elevators, min_floor, max_floor):
        self.elevators = [
            Elevator(i, min_floor, max_floor)
            for i in range(num_elevators)
        ]
        self.scheduler = Scheduler()

    def hall_request(self, floor, direction):
        req = Request(floor, direction)
        elevator = self.scheduler.select_elevator(self.elevators, req)
        if elevator:
            elevator.on_external_request(req)

    def tick(self):
        for e in self.elevators:
            e.on_tick()



## ===================== USAGE EXAMPLE =====================
if __name__ == "__main__":
    system = ElevatorSystem(num_elevators=3, min_floor=0, max_floor=10)

    system.hall_request(3, Direction.UP)
    system.hall_request(7, Direction.DOWN)
    

    for _ in range(15):
        system.tick()
        for e in system.elevators:
            print(f"Elevator {e.id} - Floor: {e.current_floor}, State: {type(e.state).__name__}, Door Opened: {e.door.opened}")
        print("-----")
        
        