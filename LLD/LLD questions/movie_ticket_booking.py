from enum import Enum
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import uuid
import threading
from abc import ABC, abstractmethod


# ============================================================================
# DOMAIN MODELS
# ============================================================================

class BookingStatus(Enum):
    """Represents the lifecycle states of a booking"""
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class SeatType(Enum):
    """Different categories of seats with varying pricing"""
    REGULAR = "REGULAR"
    PREMIUM = "PREMIUM"
    VIP = "VIP"


@dataclass
class Movie:
    """Represents a movie entity"""
    movie_id: str
    title: str
    duration_minutes: int
    language: str
    genre: str
    
    def __post_init__(self):
        if self.duration_minutes <= 0:
            raise ValueError("Movie duration must be positive")


@dataclass
class Seat:
    """Represents a physical seat in a screen"""
    seat_id: str
    row: str
    number: int
    seat_type: SeatType
    
    def get_display_name(self) -> str:
        return f"{self.row}{self.number}"


@dataclass
class Screen:
    """Represents a movie screen/hall"""
    screen_id: str
    name: str
    seats: Dict[str, Seat]  # seat_id -> Seat
    total_capacity: int
    
    def validate_seats(self, seat_ids: List[str]) -> bool:
        """Check if all seat IDs exist in this screen"""
        return all(seat_id in self.seats for seat_id in seat_ids)
    
    def get_seats_by_ids(self, seat_ids: List[str]) -> List[Seat]:
        """Retrieve seat objects by their IDs"""
        return [self.seats[seat_id] for seat_id in seat_ids if seat_id in self.seats]


@dataclass
class Show:
    """Represents a movie show/screening"""
    show_id: str
    movie: Movie
    screen: Screen
    start_time: datetime
    end_time: datetime
    base_price: float
    
    def __post_init__(self):
        if self.end_time <= self.start_time:
            raise ValueError("Show end time must be after start time")
        if self.base_price <= 0:
            raise ValueError("Base price must be positive")


@dataclass
class Booking:
    """Represents a ticket booking"""
    booking_id: str
    user_id: str
    show: Show
    seats: List[Seat]
    total_amount: float
    status: BookingStatus = BookingStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    confirmed_at: Optional[datetime] = None
    
    def confirm(self):
        """Mark booking as confirmed"""
        self.status = BookingStatus.CONFIRMED
        self.confirmed_at = datetime.now()
    
    def fail(self):
        """Mark booking as failed"""
        self.status = BookingStatus.FAILED
    
    def cancel(self):
        """Mark booking as cancelled"""
        self.status = BookingStatus.CANCELLED
    
    def get_seat_ids(self) -> List[str]:
        """Extract seat IDs from booked seats"""
        return [seat.seat_id for seat in self.seats]


# ============================================================================
# SEAT LOCKING MECHANISM
# ============================================================================

@dataclass
class SeatLock:
    """Represents a temporary lock on a seat"""
    seat_id: str
    user_id: str
    locked_at: datetime
    expires_at: datetime
    
    def is_expired(self) -> bool:
        """Check if the lock has expired"""
        return datetime.now() > self.expires_at
    
    def is_owned_by(self, user_id: str) -> bool:
        """Check if lock belongs to specific user"""
        return self.user_id == user_id and not self.is_expired()


class SeatLockManager:
    """
    Thread-safe manager for seat locks with automatic expiration.
    Prevents double booking during the payment process.
    """
    
    DEFAULT_LOCK_TTL_SECONDS = 300  # 5 minutes
    
    def __init__(self, lock_ttl_seconds: int = DEFAULT_LOCK_TTL_SECONDS):
        self._locks: Dict[str, Dict[str, SeatLock]] = {}  # show_id -> seat_id -> SeatLock
        self._master_lock = threading.RLock()
        self._show_locks: Dict[str, threading.RLock] = {}
        self.lock_ttl_seconds = lock_ttl_seconds
    
    def _get_show_lock(self, show_id: str) -> threading.RLock:
        """Get or create a lock for a specific show"""
        with self._master_lock:
            if show_id not in self._show_locks:
                self._show_locks[show_id] = threading.RLock()
            return self._show_locks[show_id]
    
    def _cleanup_expired_locks(self, show_id: str):
        """Remove expired locks for a show (must be called with show lock held)"""
        if show_id in self._locks:
            self._locks[show_id] = {
                seat_id: lock 
                for seat_id, lock in self._locks[show_id].items() 
                if not lock.is_expired()
            }
    
    def acquire_locks(self, show_id: str, seat_ids: List[str], user_id: str) -> bool:
        """
        Atomically acquire locks on multiple seats.
        Returns True if successful, raises Exception if any seat is unavailable.
        """
        show_lock = self._get_show_lock(show_id)
        
        with show_lock:
            self._cleanup_expired_locks(show_id)
            
            if show_id not in self._locks:
                self._locks[show_id] = {}
            
            show_locks = self._locks[show_id]
            
            # Check availability of ALL seats before locking ANY
            for seat_id in seat_ids:
                if seat_id in show_locks:
                    existing_lock = show_locks[seat_id]
                    if not existing_lock.is_expired():
                        raise Exception(
                            f"Seat {seat_id} is currently locked by another user. "
                            f"Please try again in a few minutes."
                        )
            
            # All seats available - acquire locks atomically
            now = datetime.now()
            expires_at = now + timedelta(seconds=self.lock_ttl_seconds)
            
            for seat_id in seat_ids:
                show_locks[seat_id] = SeatLock(
                    seat_id=seat_id,
                    user_id=user_id,
                    locked_at=now,
                    expires_at=expires_at
                )
            
            return True
    
    def validate_locks(self, show_id: str, seat_ids: List[str], user_id: str) -> bool:
        """Verify that user still holds valid locks on all specified seats"""
        show_lock = self._get_show_lock(show_id)
        
        with show_lock:
            if show_id not in self._locks:
                return False
            
            show_locks = self._locks[show_id]
            
            for seat_id in seat_ids:
                if seat_id not in show_locks:
                    return False
                
                lock = show_locks[seat_id]
                if not lock.is_owned_by(user_id):
                    return False
            
            return True
    
    def release_locks(self, show_id: str, seat_ids: List[str], user_id: str):
        """Release locks held by a specific user"""
        show_lock = self._get_show_lock(show_id)
        
        with show_lock:
            if show_id not in self._locks:
                return
            
            show_locks = self._locks[show_id]
            
            for seat_id in seat_ids:
                if seat_id in show_locks:
                    lock = show_locks[seat_id]
                    if lock.user_id == user_id:
                        del show_locks[seat_id]
    
    def get_locked_seats(self, show_id: str) -> Set[str]:
        """Get all currently locked seat IDs for a show"""
        show_lock = self._get_show_lock(show_id)
        
        with show_lock:
            self._cleanup_expired_locks(show_id)
            
            if show_id not in self._locks:
                return set()
            
            return set(self._locks[show_id].keys())


# ============================================================================
# REPOSITORIES (Data Access Layer)
# ============================================================================

class BookingRepository:
    """Manages persistence of bookings"""
    
    def __init__(self):
        self._bookings: Dict[str, Booking] = {}
        self._lock = threading.RLock()
    
    def save(self, booking: Booking) -> Booking:
        """Save or update a booking"""
        with self._lock:
            self._bookings[booking.booking_id] = booking
            return booking
    
    def find_by_id(self, booking_id: str) -> Optional[Booking]:
        """Retrieve a booking by ID"""
        with self._lock:
            return self._bookings.get(booking_id)
    
    def find_by_user(self, user_id: str) -> List[Booking]:
        """Get all bookings for a user"""
        with self._lock:
            return [
                booking for booking in self._bookings.values() 
                if booking.user_id == user_id
            ]
    
    def get_confirmed_bookings_for_show(self, show_id: str) -> List[Booking]:
        """Get all confirmed bookings for a specific show"""
        with self._lock:
            return [
                booking for booking in self._bookings.values()
                if booking.show.show_id == show_id 
                and booking.status == BookingStatus.CONFIRMED
            ]
    
    def get_booked_seat_ids(self, show_id: str) -> Set[str]:
        """Get all confirmed booked seat IDs for a show"""
        confirmed_bookings = self.get_confirmed_bookings_for_show(show_id)
        booked_seats = set()
        
        for booking in confirmed_bookings:
            booked_seats.update(booking.get_seat_ids())
        
        return booked_seats


# ============================================================================
# EXTERNAL SERVICES (Interfaces & Implementations)
# ============================================================================

class PaymentService(ABC):
    """Abstract payment service interface"""
    
    @abstractmethod
    def process_payment(self, user_id: str, amount: float, booking_id: str) -> bool:
        """Process payment and return success status"""
        pass


class MockPaymentService(PaymentService):
    """Mock payment service for testing"""
    
    def process_payment(self, user_id: str, amount: float, booking_id: str) -> bool:
        """Simulate payment processing"""
        # In real implementation: integrate with payment gateway
        print(f"Processing payment of ${amount:.2f} for booking {booking_id}")
        return True  # Simulate successful payment


class NotificationService:
    """Service for sending notifications to users"""
    
    def send_booking_confirmation(self, user_id: str, booking: Booking):
        """Send booking confirmation notification"""
        print(f"Sending confirmation to user {user_id} for booking {booking.booking_id}")
    
    def send_booking_failure(self, user_id: str, reason: str):
        """Send booking failure notification"""
        print(f"Notifying user {user_id} of booking failure: {reason}")


# ============================================================================
# BUSINESS LOGIC SERVICES
# ============================================================================

class PricingService:
    """Handles dynamic pricing calculations"""
    
    SEAT_TYPE_MULTIPLIERS = {
        SeatType.REGULAR: 1.0,
        SeatType.PREMIUM: 1.5,
        SeatType.VIP: 2.0
    }
    
    def calculate_total_price(self, seats: List[Seat], base_price: float) -> float:
        """Calculate total price based on seat types"""
        total = 0.0
        for seat in seats:
            multiplier = self.SEAT_TYPE_MULTIPLIERS.get(seat.seat_type, 1.0)
            total += base_price * multiplier
        return round(total, 2)


class SeatAvailabilityService:
    """Manages seat availability queries"""
    
    def __init__(self, lock_manager: SeatLockManager, booking_repo: BookingRepository):
        self.lock_manager = lock_manager
        self.booking_repo = booking_repo
    
    def get_available_seats(self, show: Show) -> List[Seat]:
        """Get all currently available seats for a show"""
        booked_seat_ids = self.booking_repo.get_booked_seat_ids(show.show_id)
        locked_seat_ids = self.lock_manager.get_locked_seats(show.show_id)
        
        unavailable_seats = booked_seat_ids | locked_seat_ids
        
        return [
            seat for seat in show.screen.seats.values()
            if seat.seat_id not in unavailable_seats
        ]
    
    def are_seats_available(self, show: Show, seat_ids: List[str]) -> bool:
        """Check if specific seats are available"""
        available_seats = self.get_available_seats(show)
        available_seat_ids = {seat.seat_id for seat in available_seats}
        
        return all(seat_id in available_seat_ids for seat_id in seat_ids)


class BookingService:
    """
    Core service for handling ticket bookings.
    Orchestrates the booking workflow with proper error handling.
    """
    
    def __init__(
        self,
        lock_manager: SeatLockManager,
        booking_repo: BookingRepository,
        payment_service: PaymentService,
        pricing_service: PricingService,
        notification_service: NotificationService
    ):
        self.lock_manager = lock_manager
        self.booking_repo = booking_repo
        self.payment_service = payment_service
        self.pricing_service = pricing_service
        self.notification_service = notification_service
    
    def create_booking(
        self, 
        user_id: str, 
        show: Show, 
        seat_ids: List[str]
    ) -> Booking:
        """
        Create a new booking with the following workflow:
        1. Validate seats exist in screen
        2. Acquire temporary locks on seats
        3. Create pending booking
        4. Process payment
        5. Confirm or fail booking
        6. Release locks
        """
        
        # Step 1: Validate seats exist in the screen
        if not show.screen.validate_seats(seat_ids):
            raise ValueError("One or more selected seats do not exist in this screen")
        
        if not seat_ids:
            raise ValueError("At least one seat must be selected")
        
        seats = show.screen.get_seats_by_ids(seat_ids)
        
        # Step 2: Acquire locks (will raise exception if seats unavailable)
        try:
            self.lock_manager.acquire_locks(show.show_id, seat_ids, user_id)
        except Exception as e:
            self.notification_service.send_booking_failure(user_id, str(e))
            raise
        
        booking = None
        
        try:
            # Step 3: Calculate price and create pending booking
            total_amount = self.pricing_service.calculate_total_price(seats, show.base_price)
            
            booking = Booking(
                booking_id=str(uuid.uuid4()),
                user_id=user_id,
                show=show,
                seats=seats,
                total_amount=total_amount,
                status=BookingStatus.PENDING
            )
            
            self.booking_repo.save(booking)
            
            # Step 4: Validate locks still held before payment
            if not self.lock_manager.validate_locks(show.show_id, seat_ids, user_id):
                raise Exception("Seat locks expired. Please try booking again.")
            
            # Step 5: Process payment
            payment_success = self.payment_service.process_payment(
                user_id, 
                total_amount, 
                booking.booking_id
            )
            
            if payment_success:
                booking.confirm()
                self.booking_repo.save(booking)
                self.notification_service.send_booking_confirmation(user_id, booking)
            else:
                raise Exception("Payment failed. Please check your payment method.")
            
            return booking
            
        except Exception as e:
            if booking:
                booking.fail()
                self.booking_repo.save(booking)
            self.notification_service.send_booking_failure(user_id, str(e))
            raise
            
        finally:
            # Step 6: Always release locks
            self.lock_manager.release_locks(show.show_id, seat_ids, user_id)
    
    def cancel_booking(self, booking_id: str, user_id: str) -> Booking:
        """Cancel an existing booking"""
        booking = self.booking_repo.find_by_id(booking_id)
        
        if not booking:
            raise ValueError(f"Booking {booking_id} not found")
        
        if booking.user_id != user_id:
            raise ValueError("Cannot cancel another user's booking")
        
        if booking.status != BookingStatus.CONFIRMED:
            raise ValueError(f"Cannot cancel booking with status {booking.status.value}")
        
        booking.cancel()
        self.booking_repo.save(booking)
        
        return booking
    
    def get_booking(self, booking_id: str) -> Optional[Booking]:
        """Retrieve a booking by ID"""
        return self.booking_repo.find_by_id(booking_id)
    
    def get_user_bookings(self, user_id: str) -> List[Booking]:
        """Get all bookings for a user"""
        return self.booking_repo.find_by_user(user_id)


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

def demo():
    """Demonstrate the booking system"""
    
    # Initialize services
    lock_manager = SeatLockManager(lock_ttl_seconds=300)
    booking_repo = BookingRepository()
    payment_service = MockPaymentService()
    pricing_service = PricingService()
    notification_service = NotificationService()
    
    booking_service = BookingService(
        lock_manager,
        booking_repo,
        payment_service,
        pricing_service,
        notification_service
    )
    
    availability_service = SeatAvailabilityService(lock_manager, booking_repo)
    
    # Create sample data
    movie = Movie("m1", "Inception", 148, "English", "Sci-Fi")
    
    seats = {
        f"A{i}": Seat(f"A{i}", "A", i, SeatType.REGULAR)
        for i in range(1, 11)
    }
    screen = Screen("s1", "Screen 1", seats, len(seats))
    
    show = Show(
        "sh1",
        movie,
        screen,
        datetime.now() + timedelta(hours=2),
        datetime.now() + timedelta(hours=4, minutes=30),
        10.0
    )
    
    # Test booking flow
    try:
        print("Available seats:", [s.get_display_name() for s in availability_service.get_available_seats(show)])
        
        booking = booking_service.create_booking("user1", show, ["A1", "A2", "A3"])
        print(f"\nBooking successful!")
        print(f"Booking ID: {booking.booking_id}")
        print(f"Seats: {[s.get_display_name() for s in booking.seats]}")
        print(f"Total: ${booking.total_amount}")
        
        print("\nRemaining available seats:", [s.get_display_name() for s in availability_service.get_available_seats(show)])
        
    except Exception as e:
        print(f"Booking failed: {e}")


if __name__ == "__main__":
    demo()