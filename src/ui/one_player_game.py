import copy
import random

import pygame as pg

from src.ai.bot import ChessBot
from src.core.board import Board
from src.core.move import Move
from src.core.square import Square
from src.settings import (
    BLACK, WHITE, RED, ORANGE, GREEN, DARK_RED, DARK_GREY, TILESIZE, TITLE,
)
from src.ui.game import Game, OnePlayerGameMixin
from src.ui.piece_grabber import PieceGrabber


class OnePlayerGame(Game, OnePlayerGameMixin):
    """Player vs AI chess game."""

    def __init__(self, screen, running, clock, playing):
        super().__init__(screen, running, clock, playing)
        self.ai_player = ChessBot(self.get_random_colour(), self.board)
        self.start_tick = 0
        self.difficulty = 0
        self.show_diff_menu = False

    # ── Game loop ─────────────────────────────────────────────────────────────

    def run(self):
        self.difficulty_menu()
        if self.get_draw:
            self.start_tick = pg.time.get_ticks()
        while self.playing:
            if self.ai_player.colour == self.player:
                self.ai_events()
            else:
                self.events()
            self.draw()
        self.start_tick = 0

    # ── Event handling ────────────────────────────────────────────────────────

    def events(self):
        if self.game_draw and not self.get_draw:
            self._set_draw_result()
            return
        if self._check_game_over(self.player):
            return

        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                self.piece_grabber.update_mouse(event.pos)
                clicked_row = self.piece_grabber.mouse_y // TILESIZE
                clicked_col = self.piece_grabber.mouse_x // TILESIZE

                if clicked_col == 8 and clicked_row != 8:
                    self.undo_move(clicked_row)
                elif clicked_row == 8 and (clicked_col == 7 or clicked_col == 8):
                    self.press_undo_button()
                elif clicked_row == 8 and (clicked_col == 0 or clicked_col == 1):
                    self.get_draw = True
                    self.get_draw_events(clicked_row, clicked_col)
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
                        self.add_move_to_stack(self.piece_grabber.piece, move)
                        self.board.move(self.piece_grabber.piece, move)
                        self.player_turn()
                    self.piece_grabber.ungrab_piece()
                elif self.temp_board:
                    self.redo_move()

            elif event.type == pg.KEYDOWN:
                if self.t_box_active:
                    self.text_box_event(event, self.player)

            if event.type == pg.QUIT:
                pg.quit()

    def ai_events(self):
        if self.game_draw and not self.get_draw:
            self._set_draw_result()
            return

        ai_move = self.ai_player.make_move(self.board, difficulty=self.difficulty)
        if ai_move is None:
            self.black_board_val = self._calculate_board_value(BLACK)
            self.white_board_val = self._calculate_board_value(WHITE)
            if self.board.in_check(self.ai_player.colour, self.board):
                self.player_result = 'White' if self.ai_player.colour == BLACK else 'Black'
                self.result = 'Checkmate'
            else:
                self.result = 'Stalemate'
            self.game_over = True
            self.playing = False
        else:
            self.add_move_to_stack(ai_move.moved_piece, ai_move, save_board=False)
        self.player_turn()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()

    # ── Draw offer ────────────────────────────────────────────────────────────

    def get_draw_events(self, clicked_row, clicked_col):
        board_val = self.ai_player.evaluate_material(self.board, self.ai_player.colour)
        if board_val <= 0:
            self.game_draw = True
        else:
            self.get_draw = False

    def show_get_draw(self):
        pg.draw.rect(self.screen, BLACK, (0.5 * TILESIZE, 2.5 * TILESIZE, TILESIZE * 7, TILESIZE * 4))
        decision = 'Agreed' if self.game_draw else 'Disagreed'
        name = 'Black' if self.ai_player.colour == BLACK else 'White'
        self.text_to_screen(name + ' has ' + decision, 1.1 * TILESIZE, 3 * TILESIZE, size=40)
        self.text_to_screen('to the Draw', 1.1 * TILESIZE, 4 * TILESIZE, size=40)

    # ── Utilities ─────────────────────────────────────────────────────────────

    def get_random_colour(self):
        return WHITE if random.randint(1, 2) == 1 else BLACK

    def press_undo_button(self):
        if self.player != self.ai_player.colour and self.previous_moves:
            self.board = self.previous_moves[-2].board
            if len(self.previous_moves) > 1:
                self.previous_moves.pop()
                self.previous_moves.pop()

    # ── Difficulty menu ───────────────────────────────────────────────────────

    def difficulty_menu(self):
        self.show_diff_menu = True
        self.difficulty = 0
        while self.show_diff_menu:
            self.diff_menu_events()
            self.draw_diff_menu()

    def draw_diff_menu(self):
        for i in range(10):
            for j in range(10):
                colour = WHITE if (i + j) % 2 == 0 else DARK_GREY
                if j != 9:
                    pg.draw.rect(self.screen, colour, (i * TILESIZE, j * TILESIZE, TILESIZE, TILESIZE))
                else:
                    pg.draw.rect(self.screen, colour, (i * TILESIZE, j * TILESIZE, TILESIZE * 0.3, TILESIZE))
        self.draw_menu_title(1, 2, TITLE)
        self.draw_game_menu_button(3, 5.25, ORANGE, 'Difficulty:', 'Medium')
        self.draw_game_menu_button(3, 0.75, GREEN, 'Difficulty:', 'Easy')
        self.draw_game_menu_button(6, 3, DARK_RED, 'Difficulty:', 'Hard')
        pg.display.flip()

    def diff_menu_events(self):
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos_x, mouse_pos_y = event.pos
                clicked_row = mouse_pos_y // TILESIZE
                clicked_col = mouse_pos_x // TILESIZE
                if 3 <= clicked_row <= 4:
                    if 0.75 <= clicked_col <= 3.75:
                        self.difficulty = 1
                        self.show_diff_menu = False
                    elif 5.25 <= clicked_col <= 8.25:
                        self.difficulty = 2
                        self.show_diff_menu = False
                elif clicked_row == 6 and 3 <= clicked_col <= 6:
                    self.difficulty = 3
                    self.show_diff_menu = False
            if event.type == pg.QUIT:
                pg.quit()
