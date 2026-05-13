import copy
import random

import pygame as pg

from src.core.move import Move
from src.core.square import Square
from src.settings import (
    BLACK, WHITE, RED, GREEN, DARK_GREEN, DARK_GREY, BLUE, DARK_BLUE, LIGHT_GREY, TILESIZE, TITLE,
)
from src.ui.game import Game, OnePlayerGameMixin


class PracticeGame(Game, OnePlayerGameMixin):
    """Player vs AI with move hints."""

    def __init__(self, screen, running, clock, playing):
        super().__init__(screen, running, clock, playing)
        self.start_tick = 0
        self.ai_player = self.chess_bot
        self.ai_player.colour = self.get_random_colour()
        self.move_hint = None
        self.chess_comp = False

    # ── Game loop ─────────────────────────────────────────────────────────────

    def run(self):
        if self.get_draw:
            self.start_tick = pg.time.get_ticks()
        while self.playing:
            if self.ai_player.colour == self.player:
                self.ai_events()
            else:
                self.events()
            self.draw()
        self.start_tick = 0

    # ── Rendering ─────────────────────────────────────────────────────────────

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_grid()
        self.draw_coordinates()
        self.show_last_move()
        if self.move_hint is not None:
            self.show_move_hint()
        if self.piece_grabber.holding:
            self.show_possible_moves()
        self.show_pieces(self.screen)
        if self.previous_moves:
            self.show_previous_moves()
        self.draw_button(7.2, 8.275, 2, 0.70, RED, 'UNDO', BLACK)
        self.draw_button(0.1, 8.275, 2, 0.70, RED, 'DRAW', BLACK)
        self.draw_button(5.1, 8.275, 1.9, 0.7, LIGHT_GREY, 'HINT', BLACK)
        self.draw_button(2.35, 8.275, 2.5, 0.70, WHITE, self.move_in_chess_notation, BLACK)
        if self.get_draw:
            if self.start_tick == 0:
                self.start_tick = pg.time.get_ticks()
            seconds = (pg.time.get_ticks() - self.start_tick) / 1000
            self.show_get_draw()
            if seconds > 3:
                self.get_draw = False
        pg.display.flip()

    def draw_grid(self):
        for i in range(8):
            for j in range(8):
                colour = GREEN if (i + j) % 2 == 0 else DARK_GREEN
                pg.draw.rect(self.screen, colour, (i * TILESIZE, j * TILESIZE, TILESIZE, TILESIZE))

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
                elif clicked_row == 8 and 2.4 < clicked_col < 5:
                    self.t_box_active = not self.t_box_active
                elif clicked_row == 8 and clicked_col in (5, 6):
                    self.move_hint = self.ai_player.find_best_moves(copy.deepcopy(self.board), self.player)
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
                        self.move_hint = None
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

        ai_move = self.ai_player.make_move(self.board)
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

    def show_move_hint(self):
        pg.draw.rect(self.screen, DARK_BLUE, (self.move_hint.final.col * TILESIZE, self.move_hint.final.row * TILESIZE, TILESIZE, TILESIZE))
        pg.draw.rect(self.screen, DARK_BLUE, (self.move_hint.initial.col * TILESIZE, self.move_hint.initial.row * TILESIZE, TILESIZE, TILESIZE))

    # ── Utilities ─────────────────────────────────────────────────────────────

    def get_random_colour(self):
        return WHITE if random.randint(1, 2) == 1 else BLACK

    def press_undo_button(self):
        if self.player != self.ai_player.colour and self.previous_moves:
            self.board = self.previous_moves[-2].board
            if len(self.previous_moves) > 1:
                self.previous_moves.pop()
                self.previous_moves.pop()

    # ── Training menu ─────────────────────────────────────────────────────────

    def draw_training_game_menu(self):
        for i in range(10):
            for j in range(10):
                if i < 4:
                    colour = GREEN if (i + j) % 2 == 0 else DARK_GREEN
                elif i == 4:
                    colour = BLACK
                elif i < 9:
                    colour = BLUE if (i + j) % 2 == 0 else DARK_BLUE
                else:
                    colour = LIGHT_GREY
                pg.draw.rect(self.screen, colour, (i * TILESIZE, j * TILESIZE, TILESIZE, TILESIZE))
        self.draw_menu_title(1, 2, TITLE)
        self.draw_game_menu_button(4, 0.5, DARK_BLUE, ' Practice', 'Game', text_colour=DARK_GREEN)
        self.draw_game_menu_button(4, 5.5, DARK_GREEN, '  Chess', '  Puzzle', text_colour=DARK_BLUE, bool=False)
        pg.display.flip()

    def training_game_menu_events(self):
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos_x, mouse_pos_y = event.pos
                clicked_row = mouse_pos_y // TILESIZE
                clicked_col = mouse_pos_x // TILESIZE
                if clicked_row in (4, 5):
                    if 4 > clicked_col > 0:
                        self.playing = True
                        self.show_game_menu = False
                    elif 5 < clicked_col < 8:
                        self.chess_comp = True
                        self.show_game_menu = False
            if event.type == pg.QUIT:
                if self.playing or self.show_game_menu:
                    self.show_game_menu = False
                    self.playing = False
                self.running = False
