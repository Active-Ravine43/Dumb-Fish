import os
from pathlib import Path
from src.settings import *

_PROJECT_ROOT = Path(__file__).parent.parent.parent


def _flip_table(table):
    """Reverse row order of a positional evaluation table for the opposite colour."""
    return tuple(reversed(table))


# ── Positional evaluation tables (White perspective, row 0 = opponent back rank) ──

_PAWN_TABLE = (
    (0,   0,   0,   0,   0,   0,   0,   0),
    (50,  50,  50,  50,  50,  50,  50,  50),
    (10,  10,  20,  30,  30,  20,  10,  10),
    (5,   5,   10,  25,  25,  10,  5,   5),
    (0,   0,   0,   20,  20,  0,   0,   0),
    (5,  -5,  -10,  0,   0,  -10, -5,   5),
    (5,   10,  10, -20, -20,  10,  10,   5),
    (0,   0,   0,   0,   0,   0,   0,   0),
)

# Knight positional value is colour-independent (centre is always good)
_KNIGHT_TABLE = (
    (-50, -40, -30, -30, -30, -30, -40, -50),
    (-40, -20,   0,   0,   0,   0, -20, -40),
    (-30,   0,  10,  15,  15,  10,   0, -30),
    (-30,   5,  15,  20,  20,  15,   5, -30),
    (-30,   0,  15,  20,  20,  15,   5, -30),
    (-30,   5,  10,  15,  15,  10,   5, -30),
    (-40, -20,   0,   5,   5,   0, -20, -40),
    (-50, -40, -30, -30, -30, -30, -40, -50),
)

_BISHOP_TABLE = (
    (-20, -10, -10, -10, -10, -10, -10, -20),
    (-10,   0,   0,   0,   0,   0,   0, -10),
    (-10,   0,   5,  10,  10,   5,   0, -10),
    (-10,   5,   5,  10,  10,   5,   5, -10),
    (-10,   0,  10,  10,  10,  10,   0, -10),
    (-10,  10,  10,  10,  10,  10,  10, -10),
    (-10,   5,   0,   0,   0,   0,   5, -10),
    (-20, -10, -10, -10, -10, -10, -10, -20),
)

_ROOK_TABLE = (
    (0,   0,   0,   0,   0,   0,   0,   0),
    (5,  10,  10,  10,  10,  10,  10,   5),
    (-5,  0,   0,   0,   0,   0,   0,  -5),
    (-5,  0,   0,   0,   0,   0,   0,  -5),
    (-5,  0,   0,   0,   0,   0,   0,  -5),
    (-5,  0,   0,   0,   0,   0,   0,  -5),
    (-5,  0,   0,   0,   0,   0,   0,  -5),
    (0,   0,   0,   5,   5,   0,   0,   0),
)

_QUEEN_TABLE = (
    (-20, -10, -10, -5, -5, -10, -10, -20),
    (-10,   0,   0,  0,  0,   0,   0, -10),
    (-10,   0,   5,  5,  5,   5,   0, -10),
    (-10,   0,   5,  5,  5,   5,   0, -10),
    (-10,   0,   5,  5,  5,   5,   0, -10),
    (-10,   5,   5,  5,  5,   5,   0, -10),
    (-10,   0,   5,  0,  0,   0,   0, -10),
    (-20, -10, -10, -5, -5, -10, -10, -20),
)

_KING_TABLE = (
    (-30, -40, -40, -50, -50, -40, -40, -30),
    (-30, -40, -40, -50, -50, -40, -40, -30),
    (-30, -40, -40, -50, -50, -40, -40, -30),
    (-30, -40, -40, -50, -50, -40, -40, -30),
    (-20, -30, -30, -40, -40, -30, -30, -20),
    (-10, -20, -20, -20, -20, -20, -20, -10),
    ( 20,  20,   0,   0,   0,   0,  20,  20),
    ( 20,  30,  10,   0,   0,  10,  30,  20),
)


class Piece:

    def __init__(self, name, colour, value, texture=None, texture_rect=None):
        self.name = name
        self.colour = colour
        value_sign = 1 if colour == WHITE else -1
        self.value = value * value_sign
        self.moves = []
        self.moved = False
        self.moved_twice = False
        self.texture = texture
        self.set_texture()
        self.texture_rect = texture_rect
        self.pieces_threatening = []
        self.piece_guarding = []
        self.is_guarded = False
        self.is_threatened = False

    def set_texture(self, size=80):
        colour_name = 'white' if self.colour == WHITE else 'black'
        self.texture = str(
            _PROJECT_ROOT / 'assets' / 'images' / f'{size}px' / f'{colour_name}_{self.name}.png'
        )

    def add_moves(self, move):
        self.moves.append(move)

    def clear_moves(self):
        self.moves = []


class Pawn(Piece):

    def __init__(self, colour):
        self.dir = -1 if colour == WHITE else 1
        self.piece_eval_table = _PAWN_TABLE if colour == WHITE else _flip_table(_PAWN_TABLE)
        super().__init__('Pawn', colour, 1.0)


class Knight(Piece):

    def __init__(self, colour):
        self.dir = -1 if colour == WHITE else 1
        self.piece_eval_table = _KNIGHT_TABLE
        super().__init__('Knight', colour, 3.0)


class Bishop(Piece):

    def __init__(self, colour):
        self.dir = -1 if colour == WHITE else 1
        self.piece_eval_table = _BISHOP_TABLE if colour == WHITE else _flip_table(_BISHOP_TABLE)
        super().__init__('Bishop', colour, 3.001)


class Rook(Piece):

    def __init__(self, colour):
        self.dir = -1 if colour == WHITE else 1
        self.piece_eval_table = _ROOK_TABLE if colour == WHITE else _flip_table(_ROOK_TABLE)
        super().__init__('Rook', colour, 6.0)


class Queen(Piece):

    def __init__(self, colour):
        self.dir = -1 if colour == WHITE else 1
        self.piece_eval_table = _QUEEN_TABLE if colour == WHITE else _flip_table(_QUEEN_TABLE)
        super().__init__('Queen', colour, 9.0)


class King(Piece):

    def __init__(self, colour):
        self.left_rook = None
        self.right_rook = None
        self.dir = -1 if colour == WHITE else 1
        self.piece_eval_table = _KING_TABLE if colour == WHITE else _flip_table(_KING_TABLE)
        super().__init__('King', colour, 1000.0)
