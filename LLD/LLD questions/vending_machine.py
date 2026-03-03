from enum import Enum
from typing import Dict, Optional


# -------------------- STATES --------------------

class State(str, Enum):
    IDLE = "IDLE"
    ACCEPTING_MONEY = "ACCEPTING_MONEY"
    PRODUCT_SELECTED = "PRODUCT_SELECTED"
    DISPENSING = "DISPENSING"
    RETURNING_CHANGE = "RETURNING_CHANGE"
    CANCELLED = "CANCELLED"


# -------------------- DOMAIN MODELS --------------------

class Product:
    def __init__(self, product_id: str, name: str):
        self.product_id = product_id
        self.name = name


class ProductSlot:
    def __init__(self, slot_id: str, product: Product, price: float, quantity: int):
        self.slot_id = slot_id
        self.product = product
        self.price = price
        self.quantity = quantity

    def has_stock(self) -> bool:
        return self.quantity > 0

    def dispense(self):
        if self.quantity <= 0:
            raise Exception("Product out of stock")
        self.quantity -= 1


class Inventory:
    def __init__(self):
        self._slots: Dict[str, ProductSlot] = {}

    def add_slot(self, slot: ProductSlot):
        self._slots[slot.slot_id] = slot

    def get_slot(self, slot_id: str) -> Optional[ProductSlot]:
        return self._slots.get(slot_id)


# -------------------- TRANSACTION --------------------

class Transaction:
    def __init__(self):
        self.reset()

    def reset(self):
        self.state: State = State.IDLE
        self.amount: float = 0.0
        self.selected_slot: Optional[ProductSlot] = None

    # ---------- ACTIONS ----------

    def add_money(self, amount: float):
        if self.state not in {State.IDLE, State.ACCEPTING_MONEY}:
            raise Exception(f"Cannot add money in state {self.state}")

        if amount <= 0:
            raise Exception("Amount must be positive")

        self.amount += amount
        self.state = State.ACCEPTING_MONEY

    def select_product(self, slot: ProductSlot):
        if self.state != State.ACCEPTING_MONEY:
            raise Exception(f"Cannot select product in state {self.state}")

        if not slot:
            raise Exception("Invalid product slot")

        if not slot.has_stock():
            raise Exception("Product out of stock")

        if self.amount < slot.price:
            raise Exception("Insufficient funds")

        self.selected_slot = slot
        self.state = State.PRODUCT_SELECTED

    def dispense_product(self):
        if self.state != State.PRODUCT_SELECTED:
            raise Exception(f"Cannot dispense in state {self.state}")

        # Validate first
        if not self.selected_slot.has_stock():
            raise Exception("Product out of stock")

        self.state = State.DISPENSING

        # Atomic operation
        self.selected_slot.dispense()
        self.amount -= self.selected_slot.price

        if self.amount > 0:
            self.return_change()

        self.reset()

    def return_change(self):
        self.state = State.RETURNING_CHANGE
        print(f"Returning change: ₹{self.amount:.2f}")
        self.amount = 0.0

    def cancel(self):
        if self.state not in {State.ACCEPTING_MONEY, State.PRODUCT_SELECTED}:
            raise Exception(f"Cannot cancel in state {self.state}")

        if self.amount > 0:
            self.return_change()

        self.state = State.CANCELLED
        self.reset()


# -------------------- VENDING MACHINE --------------------

class VendingMachine:
    def __init__(self, inventory: Inventory):
        self.inventory = inventory
        self.transaction = Transaction()

    def insert_money(self, amount: float):
        self.transaction.add_money(amount)

    def select_product(self, slot_id: str):
        slot = self.inventory.get_slot(slot_id)
        self.transaction.select_product(slot)

    def dispense(self):
        self.transaction.dispense_product()

    def cancel(self):
        self.transaction.cancel()
    