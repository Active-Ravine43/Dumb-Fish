import copy

from src.core.move import Move
from src.core.piece import (
    Piece, Pawn, Knight, Bishop, Rook, Queen, King,
)
from src.core.square import Square
from src.settings import ROWS, COLS, WHITE, BLACK


class Board:

    def __init__(self):
        self.squares = [[0] * COLS for _ in range(ROWS)]
        self._create()
        self._add_pieces(WHITE)
        self._add_pieces(BLACK)

    # ── Move execution ────────────────────────────────────────────────────────

    def move(self, piece, move, testing=False):
        initial = move.initial
        final = move.final

        self.squares[initial.row][initial.col].piece = None

        if self.squares[final.row][final.col].has_enemy_piece(piece.colour):
            move.captured_piece = self.squares[final.row][final.col].piece
            self.squares[final.row][final.col].piece = None

        self.squares[final.row][final.col].piece = piece

        if isinstance(piece, Pawn):
            self.check_pawn_promotion(piece, final)
            self._handle_en_passant(piece, initial, final)

        if isinstance(piece, King):
            self._handle_castling(piece, initial, final, testing)

        if piece.moved:
            piece.moved_twice = True
        piece.moved = True
        piece.clear_moves()

    def _handle_en_passant(self, piece, initial, final):
        sq = self.squares[initial.row][final.col]
        if sq.has_enemy_piece(piece.colour) and not sq.has_pawn_moved_twice():
            if isinstance(sq.piece, Pawn):
                sq.piece = None

    def _handle_castling(self, piece, initial, final, testing):
        if self.castling(initial, final) and not testing:
            diff = final.col - initial.col
            rook = piece.left_rook if diff < 0 else piece.right_rook
            self.move(rook, rook.moves[-1])

    # ── Move validation ───────────────────────────────────────────────────────

    def valid_move(self, piece, move):
        return move in piece.moves

    def check_pawn_promotion(self, piece, final):
        if final.row == 0 or final.row == 7:
            self.squares[final.row][final.col].piece = Queen(piece.colour)

    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2

    def potential_check(self, piece, move):
        temp_piece = copy.deepcopy(piece)
        temp_board = copy.deepcopy(self)
        temp_board.move(temp_piece, move, testing=True)
        return self.in_check(temp_piece.colour, temp_board)

    def in_check(self, colour, board):
        for row in range(ROWS):
            for col in range(COLS):
                if board.squares[row][col].has_enemy_piece(colour):
                    p = board.squares[row][col].piece
                    board.calculate_moves(p, row, col, check_for_check=False)
                    for m in p.moves:
                        if isinstance(board.squares[m.final.row][m.final.col].piece, King):
                            return True
        return False

    def has_legal_moves(self, colour):
        temp_board = copy.deepcopy(self)
        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_team_piece(colour):
                    p = temp_board.squares[row][col].piece
                    temp_board.calculate_moves(p, row, col)
                    if p.moves:
                        return True
        return False

    # ── Move generation ───────────────────────────────────────────────────────

    def calculate_moves(self, piece, row, col, check_for_check=True):
        if isinstance(piece, Pawn):
            self._pawn_moves(piece, row, col, check_for_check)
        elif isinstance(piece, Knight):
            self._knight_moves(piece, row, col, check_for_check)
        elif isinstance(piece, Bishop):
            self._straightline_moves(piece, row, col, [(-1, 1), (-1, -1), (1, 1), (1, -1)], check_for_check)
        elif isinstance(piece, Rook):
            self._straightline_moves(piece, row, col, [(-1, 0), (0, 1), (1, 0), (0, -1)], check_for_check)
        elif isinstance(piece, Queen):
            self._straightline_moves(
                piece, row, col,
                [(-1, 1), (-1, -1), (1, 1), (1, -1), (-1, 0), (0, 1), (1, 0), (0, -1)],
                check_for_check,
            )
        elif isinstance(piece, King):
            self._king_moves(piece, row, col, check_for_check)

    def _pawn_moves(self, piece, row, col, check_for_check):
        steps = 1 if piece.moved else 2
        start = row + piece.dir
        end = row + piece.dir * (1 + steps)

        for move_row in range(start, end, piece.dir):
            if not Square.in_range(move_row):
                break
            if not self.squares[move_row][col].isempty():
                break
            move = Move(Square(row, col), Square(move_row, col), piece)
            if check_for_check:
                if not self.potential_check(piece, move):
                    piece.add_moves(move)
            else:
                piece.add_moves(move)

        possible_move_row = row + piece.dir
        for possible_move_col in [col - 1, col + 1]:
            if not Square.in_range(possible_move_row, possible_move_col):
                continue
            if self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.colour):
                final_piece = self.squares[possible_move_row][possible_move_col].piece
                move = Move(Square(row, col), Square(possible_move_row, possible_move_col, final_piece), piece)
                if check_for_check:
                    if not self.potential_check(piece, move):
                        piece.add_moves(move)
                    else:
                        continue
                else:
                    piece.add_moves(move)

            # En passant
            if possible_move_row in (2, 5):
                sq = self.squares[row][possible_move_col]
                if sq.has_enemy_piece(piece.colour) and not sq.has_pawn_moved_twice():
                    final_piece = self.squares[possible_move_row][possible_move_col].piece
                    move = Move(Square(row, col), Square(possible_move_row, possible_move_col, final_piece), piece)
                    if check_for_check:
                        if not self.potential_check(piece, move):
                            piece.add_moves(move)
                    else:
                        piece.add_moves(move)

    def _knight_moves(self, piece, row, col, check_for_check):
        offsets = [
            (-2, 1), (-1, 2), (1, 2), (2, 1),
            (2, -1), (1, -2), (-1, -2), (-2, -1),
        ]
        for dr, dc in offsets:
            r, c = row + dr, col + dc
            if not Square.in_range(r, c):
                continue
            if not self.squares[r][c].isempty_or_enemy(piece.colour):
                continue
            final_piece = self.squares[r][c].piece
            move = Move(Square(row, col), Square(r, c, final_piece), piece)
            if check_for_check:
                if not self.potential_check(piece, move):
                    piece.add_moves(move)
            else:
                piece.add_moves(move)

    def _straightline_moves(self, piece, row, col, increments, check_for_check):
        for row_incr, col_incr in increments:
            r = row + row_incr
            c = col + col_incr
            while Square.in_range(r, c):
                final_piece = self.squares[r][c].piece
                move = Move(Square(row, col), Square(r, c, final_piece), piece)

                if self.squares[r][c].isempty():
                    if check_for_check:
                        if not self.potential_check(piece, move):
                            piece.add_moves(move)
                        else:
                            break
                    else:
                        piece.add_moves(move)
                elif self.squares[r][c].has_enemy_piece(piece.colour):
                    if check_for_check:
                        if not self.potential_check(piece, move):
                            piece.add_moves(move)
                        else:
                            break
                    else:
                        piece.add_moves(move)
                    break
                else:
                    break

                r += row_incr
                c += col_incr

    def _king_moves(self, piece, row, col, check_for_check):
        for dr, dc in [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]:
            r, c = row + dr, col + dc
            if not Square.in_range(r, c):
                continue
            if not self.squares[r][c].isempty_or_enemy(piece.colour):
                continue
            move = Move(Square(row, col), Square(r, c), piece)
            if check_for_check:
                if not self.potential_check(piece, move):
                    piece.add_moves(move)
            else:
                piece.add_moves(move)

        if piece.moved:
            return

        # Queenside castling
        left_rook = self.squares[row][0].piece
        if isinstance(left_rook, Rook) and not left_rook.moved:
            for i in range(1, 4):
                if self.squares[row][i].has_piece():
                    break
                if i == 3:
                    piece.left_rook = left_rook
                    move_r = Move(Square(row, 0), Square(row, 3), left_rook)
                    move_k = Move(Square(row, col), Square(row, 2), piece)
                    if check_for_check:
                        if not self.potential_check(piece, move_k) and not self.potential_check(left_rook, move_r):
                            left_rook.add_moves(move_r)
                            piece.add_moves(move_k)
                        else:
                            break
                    elif left_rook is not None:
                        left_rook.add_moves(move_r)
                        piece.add_moves(move_k)

        # Kingside castling
        right_rook = self.squares[row][7].piece
        if isinstance(right_rook, Rook) and not right_rook.moved:
            for i in range(5, 7):
                if self.squares[row][i].has_piece():
                    break
                if i == 6:
                    piece.right_rook = right_rook
                    move_r = Move(Square(row, 7), Square(row, 5), right_rook)
                    move_k = Move(Square(row, col), Square(row, 6), piece)
                    if check_for_check:
                        if not self.potential_check(piece, move_k) and not self.potential_check(right_rook, move_r):
                            right_rook.add_moves(move_r)
                            piece.add_moves(move_k)
                        else:
                            break
                    elif right_rook is not None:
                        right_rook.add_moves(move_r)
                        piece.add_moves(move_k)

    # ── Board initialisation ──────────────────────────────────────────────────

    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def _add_pieces(self, colour):
        row_pawn, row_other = (6, 7) if colour == WHITE else (1, 0)

        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(colour))

        self.squares[row_other][1] = Square(row_other, 1, Knight(colour))
        self.squares[row_other][6] = Square(row_other, 6, Knight(colour))
        self.squares[row_other][2] = Square(row_other, 2, Bishop(colour))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(colour))
        self.squares[row_other][0] = Square(row_other, 0, Rook(colour))
        self.squares[row_other][7] = Square(row_other, 7, Rook(colour))
        self.squares[row_other][3] = Square(row_other, 3, Queen(colour))
        self.squares[row_other][4] = Square(row_other, 4, King(colour))
