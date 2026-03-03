from abc import ABC, abstractmethod
from random import random
from copy import deepcopy


# ===================== CONSTANTS =====================

class Color:
    WHITE = 'W'
    BLACK = 'B'

    @staticmethod
    def opposite(color):
        return Color.BLACK if color == Color.WHITE else Color.WHITE


# ===================== MOVE VALIDATORS =====================

class MoveValidator(ABC):
    @abstractmethod
    def is_valid(self, board, piece, from_pos, to_pos) -> bool:
        pass


class PawnMoveValidator(MoveValidator):
    def is_valid(self, board, piece, f, t):
        fr, fc = f
        tr, tc = t
        direction = 1 if piece.color == Color.WHITE else -1
        start_row = 1 if piece.color == Color.WHITE else 6

        # Forward move
        if fc == tc and tr - fr == direction and board.get_piece(t) is None:
            return True

        # Double move
        if fc == tc and fr == start_row and tr - fr == 2 * direction:
            if board.get_piece((fr + direction, fc)) is None and board.get_piece(t) is None:
                return True

        # Capture
        if abs(tc - fc) == 1 and tr - fr == direction:
            target = board.get_piece(t)
            if target and target.color != piece.color:
                return True

        # En passant handled outside
        return False


class RookMoveValidator(MoveValidator):
    def is_valid(self, board, piece, f, t):
        fr, fc = f
        tr, tc = t
        if fr != tr and fc != tc:
            return False
        step_r = 0 if fr == tr else (1 if tr > fr else -1)
        step_c = 0 if fc == tc else (1 if tc > fc else -1)
        r, c = fr + step_r, fc + step_c
        while (r, c) != (tr, tc):
            if board.get_piece((r, c)):
                return False
            r += step_r
            c += step_c
        return True


class KnightMoveValidator(MoveValidator):
    def is_valid(self, board, piece, f, t):
        fr, fc = f
        tr, tc = t
        return (abs(fr - tr), abs(fc - tc)) in [(2, 1), (1, 2)]


class BishopMoveValidator(MoveValidator):
    def is_valid(self, board, piece, f, t):
        fr, fc = f
        tr, tc = t
        if abs(fr - tr) != abs(fc - tc):
            return False
        step_r = 1 if tr > fr else -1
        step_c = 1 if tc > fc else -1
        r, c = fr + step_r, fc + step_c
        while (r, c) != (tr, tc):
            if board.get_piece((r, c)):
                return False
            r += step_r
            c += step_c
        return True


class QueenMoveValidator(MoveValidator):
    def is_valid(self, board, piece, f, t):
        return (
            RookMoveValidator().is_valid(board, piece, f, t) or
            BishopMoveValidator().is_valid(board, piece, f, t)
        )


class KingMoveValidator(MoveValidator):
    def is_valid(self, board, piece, f, t):
        fr, fc = f
        tr, tc = t
        return abs(fr - tr) <= 1 and abs(fc - tc) <= 1


# ===================== PIECES =====================

class Piece:
    def __init__(self, color, validator):
        self.color = color
        self.validator = validator
        self.has_moved = False

    def can_move(self, board, f, t):
        return self.validator.is_valid(board, self, f, t)


class Pawn(Piece): pass
class Rook(Piece): pass
class Knight(Piece): pass
class Bishop(Piece): pass
class Queen(Piece): pass
class King(Piece): pass


# ===================== FACTORY =====================

class ChessPieceFactory:
    @staticmethod
    def create(piece, color):
        return {
            "pawn": Pawn(color, PawnMoveValidator()),
            "rook": Rook(color, RookMoveValidator()),
            "knight": Knight(color, KnightMoveValidator()),
            "bishop": Bishop(color, BishopMoveValidator()),
            "queen": Queen(color, QueenMoveValidator()),
            "king": King(color, KingMoveValidator()),
        }[piece]


# ===================== BOARD =====================

class Board:
    def __init__(self):
        self.grid = [[None] * 8 for _ in range(8)]
        self.last_move = None
        self.setup()

    def get_piece(self, pos):
        r, c = pos
        return self.grid[r][c]

    def set_piece(self, pos, piece):
        r, c = pos
        self.grid[r][c] = piece

    def setup(self):
        for c in range(8):
            self.grid[1][c] = ChessPieceFactory.create("pawn", Color.WHITE)
            self.grid[6][c] = ChessPieceFactory.create("pawn", Color.BLACK)

        order = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
        for c, p in enumerate(order):
            self.grid[0][c] = ChessPieceFactory.create(p, Color.WHITE)
            self.grid[7][c] = ChessPieceFactory.create(p, Color.BLACK)

    def clone(self):
        return deepcopy(self)


# ===================== GAME RULES =====================

class GameRules:
    @staticmethod
    def is_in_check(board, color):
        king_pos = None
        for r in range(8):
            for c in range(8):
                p = board.get_piece((r, c))
                if isinstance(p, King) and p.color == color:
                    king_pos = (r, c)

        for r in range(8):
            for c in range(8):
                p = board.get_piece((r, c))
                if p and p.color != color:
                    if p.can_move(board, (r, c), king_pos):
                        return True
        return False

    @staticmethod
    def is_checkmate(board, color):
        if not GameRules.is_in_check(board, color):
            return False

        for r in range(8):
            for c in range(8):
                piece = board.get_piece((r, c))
                if piece and piece.color == color:
                    for tr in range(8):
                        for tc in range(8):
                            if piece.can_move(board, (r, c), (tr, tc)):
                                temp = board.clone()
                                temp.set_piece((tr, tc), piece)
                                temp.set_piece((r, c), None)
                                if not GameRules.is_in_check(temp, color):
                                    return False
        return True


# ===================== GAME =====================

class ChessGame:
    def __init__(self):
        self.board = Board()
        self.current = Color.WHITE

    def play(self):
        while True:
            if GameRules.is_checkmate(self.board, self.current):
                print(f"Checkmate! {Color.opposite(self.current)} wins!")
                return

            print(f"{self.current}'s turn")
            move = input("Move (e2 e4): ")
            if move == "exit":
                return

            f, t = move.split()
            fr, fc = int(f[1]) - 1, ord(f[0]) - 97
            tr, tc = int(t[1]) - 1, ord(t[0]) - 97

            piece = self.board.get_piece((fr, fc))
            if not piece or piece.color != self.current:
                print("Invalid piece")
                continue

            if not piece.can_move(self.board, (fr, fc), (tr, tc)):
                print("Illegal move")
                continue

            temp = self.board.clone()
            temp.set_piece((tr, tc), piece)
            temp.set_piece((fr, fc), None)

            if GameRules.is_in_check(temp, self.current):
                print("Move puts king in check")
                continue

            self.board = temp
            piece.has_moved = True
            self.current = Color.opposite(self.current)


# ===================== RUN =====================

if __name__ == "__main__":
    ChessGame().play()
