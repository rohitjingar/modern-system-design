from abc import ABC, abstractmethod
import time
import threading
from collections import defaultdict


class RateLimiter(ABC):
    @abstractmethod
    def allow_request(self, user_id: str) -> bool:
        pass


class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill_time = time.time()
        self.lock = threading.Lock()

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill_time
        refill = elapsed * self.refill_rate

        if refill > 0:
            self.tokens = min(self.capacity, self.tokens + refill)
            self.last_refill_time = now

    def consume(self, amount: int = 1) -> bool:
        with self.lock:
            self._refill()
            if self.tokens >= amount:
                self.tokens -= amount
                return True
            return False


class LeakyBucket:
    def __init__(self, capacity: int, leak_rate: float):
        self.capacity = capacity
        self.leak_rate = leak_rate
        self.level = 0
        self.last_leak_time = time.time()
        self.lock = threading.Lock()

    def _leak(self):
        now = time.time()
        elapsed = now - self.last_leak_time
        leaked = elapsed * self.leak_rate

        if leaked > 0:
            self.level = max(0, self.level - leaked)
            self.last_leak_time = now

    def try_add(self) -> bool:
        with self.lock:
            self._leak()
            if self.level < self.capacity:
                self.level += 1
                return True
            return False



class FixedWindowLogLimiter(RateLimiter):
    def __init__(self, max_requests: int, window_size: int):
        self.max_requests = max_requests
        self.window_size = window_size
        self.data = {}
        self.map_lock = threading.Lock()

    def allow_request(self, user_id: str) -> bool:
        now = time.time()
        window_start = int(now // self.window_size) * self.window_size

        user = self.data.get(user_id)
        if user is None:
            with self.map_lock:
                if user_id not in self.data:
                    self.data[user_id] = {"timestamps": [], "lock": threading.Lock()}
                user = self.data[user_id]

        with user["lock"]:
            timestamps = user["timestamps"]
            timestamps[:] = [t for t in timestamps if t >= window_start]

            if len(timestamps) < self.max_requests:
                timestamps.append(now)
                return True
            return False


class SlidingWindowLogLimiter(RateLimiter):
    def __init__(self, max_requests: int, window_size: int):
        self.max_requests = max_requests
        self.window_size = window_size
        self.data = {}
        self.map_lock = threading.Lock()

    def allow_request(self, user_id: str) -> bool:
        now = time.time()

        user = self.data.get(user_id)
        if user is None:
            with self.map_lock:
                if user_id not in self.data:
                    self.data[user_id] = {"timestamps": [], "lock": threading.Lock()}
                user = self.data[user_id]

        with user["lock"]:
            timestamps = user["timestamps"]
            timestamps[:] = [t for t in timestamps if t >= now - self.window_size]

            if len(timestamps) < self.max_requests:
                timestamps.append(now)
                return True
            return False


class FixedWindowCounterLimiter(RateLimiter):
    def __init__(self, max_requests: int, window_size: int):
        self.max_requests = max_requests
        self.window_size = window_size
        self.data = {}
        self.map_lock = threading.Lock()

    def allow_request(self, user_id: str) -> bool:
        now = time.time()
        window_id = int(now // self.window_size)

        user = self.data.get(user_id)
        if user is None:
            with self.map_lock:
                if user_id not in self.data:
                    self.data[user_id] = {
                        "window": window_id,
                        "count": 0,
                        "lock": threading.Lock()
                    }
                user = self.data[user_id]

        with user["lock"]:
            if user["window"] != window_id:
                user["window"] = window_id
                user["count"] = 0

            if user["count"] < self.max_requests:
                user["count"] += 1
                return True
            return False



class SlidingWindowCounterLimiter(RateLimiter):
    def __init__(self, max_requests: int, window_size: int):
        self.max_requests = max_requests
        self.window_size = window_size
        self.data = {}
        self.map_lock = threading.Lock()

    def allow_request(self, user_id: str) -> bool:
        now = time.time()
        window_start = int(now // self.window_size) * self.window_size

        user = self.data.get(user_id)
        if user is None:
            with self.map_lock:
                if user_id not in self.data:
                    self.data[user_id] = {
                        "current": 0,
                        "previous": 0,
                        "window_start": window_start,
                        "lock": threading.Lock()
                    }
                user = self.data[user_id]

        with user["lock"]:
            if user["window_start"] != window_start:
                user["previous"] = user["current"]
                user["current"] = 0
                user["window_start"] = window_start

            elapsed = now - user["window_start"]
            weight = max(0.0, (self.window_size - elapsed) / self.window_size)

            estimated = user["current"] + user["previous"] * weight

            if estimated < self.max_requests:
                user["current"] += 1
                return True
            return False
