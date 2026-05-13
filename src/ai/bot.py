import copy
import math

from src.core.board import Board
from src.core.move import DummyMove
from src.core.piece import Pawn, Knight, Bishop, Rook, Queen, King
from src.settings import ROWS, COLS, WHITE, BLACK, KVALUE, QVALUE, RVALUE, BVALUE, NVALUE, PVALUE

_PIECE_VALUES = {
    Pawn:   PVALUE,
    Knight: NVALUE,
    Bishop: BVALUE,
    Rook:   RVALUE,
    Queen:  QVALUE,
    King:   KVALUE,
}


class ChessBot:

    def __init__(self, colour, board):
        self.colour = colour
        self.board = board

    # ── Public interface ──────────────────────────────────────────────────────

    def make_move(self, board, difficulty=3):
        move = self.find_best_moves(copy.deepcopy(board), self.colour, depth=difficulty)
        if move is not None:
            initial_square = board.squares[move.initial.row][move.initial.col]
            piece = initial_square.piece
            move.board = copy.deepcopy(board)
            if piece is not None:
                board.move(piece, move)
        return move

    # ── Search ────────────────────────────────────────────────────────────────

    def find_best_moves(self, board, colour, depth=3, alpha=-math.inf, beta=math.inf):
        if depth <= 0:
            return DummyMove(self.eval_board(board, colour))

        all_moves = self.generate_all_moves(board, colour)
        if not all_moves:
            return None

        best_move = None
        for m in all_moves:
            piece = m.moved_piece
            board.move(piece, m, testing=True)
            self.assign_move_value(board, m)
            opponent_move = self.find_best_moves(
                board, self.opposite_colour(colour),
                depth=depth - 1, alpha=-beta, beta=-alpha,
            )
            self.undo_move(board, m, piece)

            if opponent_move is not None and hasattr(opponent_move, 'move_value'):
                current_value = -opponent_move.move_value
                m.move_value = m.move_value + current_value
                if current_value > alpha:
                    alpha = current_value
                    best_move = m
                if alpha >= beta:
                    break

        return best_move

    # ── Move generation ───────────────────────────────────────────────────────

    def generate_all_moves(self, board, colour):
        best = -math.inf
        moves = []
        for row in range(ROWS):
            for col in range(COLS):
                if board.squares[row][col].has_team_piece(colour):
                    piece = board.squares[row][col].piece
                    piece_moves = self.generate_piece_moves(board, piece, row, col, best)
                    if piece_moves:
                        moves.extend(piece_moves)
        if moves:
            moves = self.sort_moves(moves)
        return moves

    def generate_piece_moves(self, board, piece, row, col, best):
        best_moves = []
        board.calculate_moves(piece, row, col)
        count = 0
        for m in piece.moves:
            if board.valid_move(piece, m):
                self.estimate_move_value(board, m, piece)
                if m.estimate_val > best:
                    best = m.estimate_val
                    best_moves = [m]
                    count = 0
                elif m.estimate_val == best or count <= 3:
                    best_moves.append(m)
                    count += 1
        return best_moves

    # ── Evaluation ────────────────────────────────────────────────────────────

    def assign_move_value(self, board, move):
        capture_value = self.piece_value(move.captured_piece) if move.captured_piece else 0
        move.move_value = self.eval_board(board, move.colour) + capture_value

    def estimate_move_value(self, board, move, piece):
        capture_value = self.piece_value(move.captured_piece) if move.captured_piece else 0
        positional = piece.piece_eval_table[move.final.row][move.final.col]
        material_self = self.evaluate_piece_value(board, move.colour)
        material_opp = -self.evaluate_piece_value(board, self.opposite_colour(piece.colour)) - capture_value
        move.estimate_val = positional + (material_self - material_opp)

    def eval_board(self, board, colour):
        value = 0
        for row in range(ROWS):
            for col in range(COLS):
                sq = board.squares[row][col]
                if sq.has_team_piece(colour):
                    value += self.piece_value(sq.piece)
                    value += sq.piece.piece_eval_table[row][col]
                elif sq.has_enemy_piece(colour):
                    value -= self.piece_value(sq.piece)
                    value += sq.piece.piece_eval_table[row][col]
        value += self.evaluate_if_gives_check(board, colour)
        return value

    def evaluate_material(self, board, colour):
        return self.evaluate_piece_value(board, colour) - self.evaluate_piece_value(board, self.opposite_colour(colour))

    def evaluate_piece_value(self, board, colour):
        total = 0
        for row in range(ROWS):
            for col in range(COLS):
                sq = board.squares[row][col]
                if sq.has_team_piece(colour):
                    total += self.piece_value(sq.piece)
        return total

    def evaluate_if_gives_check(self, board, colour):
        return 500 if board.in_check(self.opposite_colour(colour), board) else 0

    # ── Utilities ─────────────────────────────────────────────────────────────

    def piece_value(self, piece):
        return _PIECE_VALUES.get(type(piece), 0)

    def opposite_colour(self, colour):
        return BLACK if colour == WHITE else WHITE

    def undo_move(self, board, move, piece):
        board.squares[move.initial.row][move.initial.col].piece = piece
        if move.captured_piece:
            board.squares[move.final.row][move.final.col].piece = move.captured_piece
            move.captured_piece = None
        else:
            board.squares[move.final.row][move.final.col].piece = None

    def sort_moves(self, moves):
        moves.sort(key=lambda m: m.estimate_val, reverse=True)
        return moves[:3]
