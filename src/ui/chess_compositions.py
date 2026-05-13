import random
from pathlib import Path

import pygame as pg

from src.core.move import Move
from src.core.piece import Pawn, Knight, Bishop, Rook, Queen, King
from src.core.square import Square
from src.settings import (
    BLACK, WHITE, RED, BLUE, DARK_BLUE, GREY, LIGHT_GREY, TILESIZE, ROWS, COLS,
)
from src.ui.game import Game

_PROJECT_ROOT = Path(__file__).parent.parent.parent

_PIECE_CLASS_MAP = {
    'P': Pawn,
    'N': Knight,
    'B': Bishop,
    'R': Rook,
    'Q': Queen,
    'K': King,
}


class ChessCompositions(Game):
    """Chess puzzle mode with lives and hints."""

    def __init__(self, screen, running, clock, playing):
        super().__init__(screen, running, clock, playing)
        self.expected_moves = []
        self.player_colour = None
        self.lives = 3
        self.hints = 3
        self.move_hint = None

    # ── Game loop ─────────────────────────────────────────────────────────────

    def run(self):
        self.get_chess_comp()
        while self.playing:
            if self.player_colour == self.player:
                self.events()
            else:
                self.make_move_response()
            self.draw()

    # ── Event handling ────────────────────────────────────────────────────────

    def events(self):
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                self.piece_grabber.update_mouse(event.pos)
                clicked_row = self.piece_grabber.mouse_y // TILESIZE
                clicked_col = self.piece_grabber.mouse_x // TILESIZE

                if clicked_col == 8 and clicked_row != 8:
                    self.undo_move(clicked_row)
                elif clicked_row == 8 and (clicked_col == 7 or clicked_col == 8) and self.hints > 0:
                    self.move_hint = self.convert_chess_notation_into_move(
                        self.expected_moves[0], self.player_colour
                    )
                    self.hints -= 1
                elif clicked_row == 8 and 2.4 < clicked_col < 6.4:
                    self.t_box_active = not self.t_box_active
                elif Square.in_range(clicked_row, clicked_col) and self.board.squares[clicked_row][clicked_col].has_piece():
                    piece = self.board.squares[clicked_row][clicked_col].piece
                    if piece.colour == self.player:
                        self.board.calculate_moves(piece, clicked_row, clicked_col, check_for_check=True)
                        self.piece_grabber.save_initial_pos(event.pos)
                        self.piece_grabber.grab_piece(piece)

            elif event.type == pg.MOUSEMOTION:
                if self.piece_grabber.holding:
                    self.piece_grabber.update_mouse(event.pos)
                    self.piece_grabber.update_grabber(self.screen)

            elif event.type == pg.MOUSEBUTTONUP:
                if self.piece_grabber.holding:
                    self.piece_grabber.update_mouse(event.pos)
                    released_row = self.piece_grabber.mouse_y // TILESIZE
                    released_col = self.piece_grabber.mouse_x // TILESIZE
                    initial = Square(self.piece_grabber.initial_row, self.piece_grabber.initial_col)
                    final = Square(released_row, released_col)
                    move = Move(initial, final, self.piece_grabber.piece)

                    if self.board.valid_move(self.piece_grabber.piece, move):
                        if self.expected_moves:
                            expected = self.convert_move_into_chess_notation(
                                self.piece_grabber.piece, move.initial, move.final
                            )
                            if self.expected_moves[0] == expected:
                                self.add_move_to_stack(self.piece_grabber.piece, move)
                                self.board.move(self.piece_grabber.piece, move)
                                self.move_hint = None
                                self.expected_moves.pop(0)
                                self.player_turn()
                            else:
                                self.lives -= 1

                        if self.lives == 0:
                            self.black_board_val = self._calculate_board_value(BLACK)
                            self.white_board_val = self._calculate_board_value(WHITE)
                            self.result = 'FAIL...'
                            self.game_over = True
                            self.playing = False
                        elif not self.expected_moves:
                            self.black_board_val = self._calculate_board_value(BLACK)
                            self.white_board_val = self._calculate_board_value(WHITE)
                            self.result = 'Complete'
                            self.game_over = True
                            self.playing = False

                    self.piece_grabber.ungrab_piece()

                elif self.temp_board:
                    self.redo_move()

            elif event.type == pg.KEYDOWN:
                if self.t_box_active:
                    self.text_box_event(event, self.player)

            if event.type == pg.QUIT:
                pg.quit()

    # ── Rendering ─────────────────────────────────────────────────────────────

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_grid()
        self.draw_coordinates()
        if self.move_hint is not None:
            self.show_move_hint()
        self.show_last_move()
        self.show_possible_moves()
        self.show_pieces(self.screen)
        if self.previous_moves:
            self.show_previous_moves()
        lives_str = 'Lives:' + str(self.lives)
        hints_str = 'HINT:' + str(self.hints)
        self.draw_button(6.55, 8.275, 2.5, 0.70, LIGHT_GREY, hints_str, BLACK, text_size=35)
        self.draw_button(0.3, 8.275, 3, 0.70, RED, lives_str, BLACK, text_size=40)
        self.draw_button(3.55, 8.275, 2.75, 0.70, WHITE, self.move_in_chess_notation, BLACK)
        pg.display.flip()

    def draw_grid(self):
        for i in range(8):
            for j in range(8):
                colour = BLUE if (i + j) % 2 == 0 else DARK_BLUE
                pg.draw.rect(self.screen, colour, (i * TILESIZE, j * TILESIZE, TILESIZE, TILESIZE))

    def show_possible_moves(self):
        if self.piece_grabber.holding:
            piece = self.piece_grabber.piece
            for move in piece.moves:
                colour = LIGHT_GREY if (move.final.row + move.final.col) % 2 == 0 else GREY
                pg.draw.rect(self.screen, colour, (move.final.col * TILESIZE, move.final.row * TILESIZE, TILESIZE, TILESIZE))
            if piece.moves:
                initial = piece.moves[0].initial
                colour = GREY if (initial.row + initial.col) % 2 != 0 else LIGHT_GREY
                pg.draw.rect(self.screen, colour, (initial.col * TILESIZE, initial.row * TILESIZE, TILESIZE, TILESIZE))

    def show_move_hint(self):
        pg.draw.rect(self.screen, RED, (self.move_hint.final.col * TILESIZE, self.move_hint.final.row * TILESIZE, TILESIZE, TILESIZE))
        pg.draw.rect(self.screen, RED, (self.move_hint.initial.col * TILESIZE, self.move_hint.initial.row * TILESIZE, TILESIZE, TILESIZE))

    # ── Puzzle loading ────────────────────────────────────────────────────────

    def get_chess_comp(self):
        squares = [[Square(row, col) for col in range(COLS)] for row in range(ROWS)]
        num = random.randint(1, 19)
        puzzle_path = _PROJECT_ROOT / 'compositions' / f'puzzle_{num:02d}.txt'

        chess_note = ''
        moves = []

        with open(str(puzzle_path), 'r') as f:
            for count, line in enumerate(f):
                if count < 8:
                    for i in range(8):
                        pos = i * 2
                        colour = BLACK if line[pos] == 'B' else WHITE
                        squares = self.add_piece(squares, colour, line[pos + 1], count, i)
                else:
                    for char in line:
                        if char == ',' and chess_note == '':
                            self.player_colour = BLACK
                            self.player = BLACK
                        elif char == ',':
                            moves.append(chess_note)
                            chess_note = ''
                        else:
                            chess_note += char

        if self.player_colour is None:
            self.player_colour = WHITE
        self.board.squares = squares
        self.expected_moves = moves

    def add_piece(self, squares, colour, piece_letter, row, col):
        piece_class = _PIECE_CLASS_MAP.get(piece_letter)
        if piece_class is not None:
            squares[row][col].piece = piece_class(colour)
        return squares

    # ── Response move ─────────────────────────────────────────────────────────

    def make_move_response(self):
        if not self.expected_moves:
            self.game_over = True
            return

        response_colour = BLACK if self.player_colour == WHITE else WHITE
        move = self.convert_chess_notation_into_move(self.expected_moves[0], response_colour)
        if move:
            piece = move.moved_piece
            if self.board.valid_move(piece, move):
                self.add_move_to_stack(piece, move)
                self.board.move(piece, move)
                self.player_turn()
                self.expected_moves.pop(0)
        self.move_in_chess_notation = ''
