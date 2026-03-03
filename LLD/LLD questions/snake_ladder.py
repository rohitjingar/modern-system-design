from abc import ABC, abstractmethod
from collections import deque
import random
from typing import List, Dict


# =====================================================
# Strategy Pattern → Dice / Movement Strategy
# =====================================================

class DiceStrategy(ABC):
    @abstractmethod
    def roll(self) -> int:
        pass


class StandardDice(DiceStrategy):
    def roll(self) -> int:
        return random.randint(1, 6)


class CrookedDice(DiceStrategy):
    """Returns only even numbers"""
    def roll(self) -> int:
        return random.choice([2, 4, 6])


# =====================================================
# Player
# =====================================================

class Player:
    def __init__(self, name: str):
        self.name = name
        self.position = 0


# =====================================================
# Board Elements (Factory Pattern)
# =====================================================

class BoardElement(ABC):
    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end


class Snake(BoardElement):
    pass


class Ladder(BoardElement):
    pass


class BoardElementFactory:
    @staticmethod
    def create_element(element_type: str, start: int, end: int) -> BoardElement:
        if element_type == "snake":
            return Snake(start, end)
        elif element_type == "ladder":
            return Ladder(start, end)
        else:
            raise ValueError("Invalid board element type")


# =====================================================
# Board
# =====================================================

class Board:
    def __init__(self, size: int, elements: List[BoardElement]):
        self.size = size
        self.jump_map: Dict[int, int] = {
            element.start: element.end for element in elements
        }

    def resolve_position(self, position: int) -> int:
        while position in self.jump_map:
            position = self.jump_map[position]
        return position


# =====================================================
# Game (Orchestrator)
# =====================================================

class Game:
    def __init__(self, players: List[Player], board: Board, dice: DiceStrategy):
        self.players = deque(players)
        self.board = board
        self.dice = dice

    def play(self):
        while True:
            current_player = self.players.popleft()
            roll = self.dice.roll()
            next_position = current_player.position + roll

            if next_position > self.board.size:
                pass
            elif next_position == self.board.size:
                current_player.position = next_position
                print(f"{current_player.name} wins!")
                return
            else:
                current_player.position = self.board.resolve_position(next_position)
                print(f"{current_player.name} rolled {roll} , New Position {current_player.position}")

            if roll == 6:
                self.players.appendleft(current_player)
            else:
                self.players.append(current_player)


# =====================================================
# Example Usage
# =====================================================

if __name__ == "__main__":
    players = [
        Player("Alice"),
        Player("Bob"),
        Player("Charlie")
    ]

    elements = [
        BoardElementFactory.create_element("ladder", 2, 38),
        BoardElementFactory.create_element("ladder", 7, 14),
        BoardElementFactory.create_element("snake", 16, 6),
        BoardElementFactory.create_element("snake", 49, 11),
        BoardElementFactory.create_element("ladder", 28, 84),
        BoardElementFactory.create_element("snake", 95, 75),
    ]

    board = Board(size=100, elements=elements)

    dice = StandardDice()       # swap with CrookedDice() easily
    game = Game(players, board, dice)
    game.play()
