import copy

import pygame as pg

from src.ai.bot import ChessBot
from src.core.board import Board
from src.core.move import Move
from src.core.piece import Pawn, Knight, Bishop, Rook, Queen, King
from src.core.square import Square
from src.settings import (
    BLACK, WHITE, RED, GREEN, BLUE, DARK_GREY, LIGHT_BLUE, LIGHT_GREY, GREY,
    TILESIZE, ROWS, COLS, TITLE,
    rows_as_characters, cols_as_letters,
    king_character, queen_character, rook_character, bishop_character, knight_character,
    piece_characters,
)
from src.ui.piece_grabber import PieceGrabber


class Game:
    """Two-player chess game."""

    def __init__(self, screen, running, clock, playing):
        self.screen = screen
        pg.font.init()
        self.clock = clock
        self.player = WHITE
        self.running = running
        self.playing = playing
        self.one_player = False
        self.show_game_menu = False
        self.game_over = False
        self.game_draw = False
        self.get_draw = False
        self.board = Board()
        self.temp_board = None
        self.piece_grabber = PieceGrabber()
        self.chess_bot = ChessBot(self.player, self.board)
        self.previous_moves = []
        self.result = ''
        self.player_result = ''
        self.white_board_val = 0
        self.black_board_val = 0
        self.move_in_chess_notation = ''
        self.t_box_active = False

    def new(self):
        self.run()

    def run(self):
        while self.playing:
            self.events()
            self.draw()

    # ── Shared helpers ────────────────────────────────────────────────────────

    def _calculate_board_value(self, colour):
        return self.chess_bot.evaluate_piece_value(self.board, colour) // 100 - 100

    def _check_game_over(self, colour):
        if not self.board.has_legal_moves(colour):
            self.black_board_val = self._calculate_board_value(BLACK)
            self.white_board_val = self._calculate_board_value(WHITE)
            if self.board.in_check(colour, copy.deepcopy(self.board)):
                self.player_result = 'White' if colour == BLACK else 'Black'
                self.result = 'Checkmate'
            else:
                self.result = 'Stalemate'
            self.game_over = True
            self.playing = False
            return True
        return False

    def _set_draw_result(self):
        self.black_board_val = self._calculate_board_value(BLACK)
        self.white_board_val = self._calculate_board_value(WHITE)
        self.result = 'DRAW'
        self.game_over = True
        self.playing = False
        self.game_draw = False

    # ── Event handling ────────────────────────────────────────────────────────

    def events(self):
        if self.game_draw and not self.get_draw:
            self._set_draw_result()
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
                elif self.get_draw:
                    self.get_draw_events(clicked_row, clicked_col)
                elif clicked_row == 8 and 2.4 < clicked_col < 6.4:
                    self.t_box_active = not self.t_box_active
                elif Square.in_range(clicked_row, clicked_col) and self.board.squares[clicked_row][clicked_col].has_piece():
                    piece = self.board.squares[clicked_row][clicked_col].piece
                    if piece.colour == self.player:
                        self.board.calculate_moves(piece, clicked_row, clicked_col, check_for_check=True)
                        self.piece_grabber.save_initial_pos(event.pos)
                        self.piece_grabber.grab_piece(piece)
                        self.show_possible_moves()

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
                        self._check_game_over(self.player)

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
        self.show_last_move()
        if self.piece_grabber.holding:
            self.show_possible_moves()
        self.show_pieces(self.screen)
        if self.previous_moves:
            self.show_previous_moves()
        self.draw_button(6.8, 8.275, 2, 0.70, RED, 'UNDO', BLACK)
        self.draw_button(0.3, 8.275, 2, 0.70, RED, 'DRAW', BLACK)
        self.draw_button(2.55, 8.275, 4, 0.70, WHITE, self.move_in_chess_notation, BLACK)

        if self.get_draw and isinstance(self, OnePlayerGameMixin):
            if self.start_tick == 0:
                self.start_tick = pg.time.get_ticks()
            seconds = (pg.time.get_ticks() - self.start_tick) / 1000
            self.show_get_draw()
            if seconds > 3:
                self.get_draw = False
        elif self.get_draw:
            self.show_get_draw()

        pg.display.flip()

    def draw_grid(self):
        for i in range(8):
            for j in range(8):
                colour = WHITE if (i + j) % 2 == 0 else DARK_GREY
                pg.draw.rect(self.screen, colour, (i * TILESIZE, j * TILESIZE, TILESIZE, TILESIZE))

    def draw_coordinates(self):
        self.draw_button(8, 0, 0.3, 9.5, LIGHT_GREY, '', WHITE)
        for i in range(8):
            self.text_to_screen(rows_as_characters[i], 8.05 * TILESIZE, (i + 0.45) * TILESIZE, size=17, colour=BLACK)
            self.text_to_screen(cols_as_letters[i], (i + 0.45) * TILESIZE, 8.05 * TILESIZE, size=17)

    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece
                    if self.piece_grabber.holding:
                        self.piece_grabber.update_grabber(self.screen)
                    if piece is not self.piece_grabber.piece:
                        piece.set_texture(size=80)
                        img = pg.image.load(piece.texture)
                        img_center = (col * TILESIZE + TILESIZE // 2, row * TILESIZE + TILESIZE // 2)
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.texture_rect)

    def show_possible_moves(self):
        if self.piece_grabber.holding:
            piece = self.piece_grabber.piece
            for move in piece.moves:
                colour = LIGHT_BLUE if (move.final.row + move.final.col) % 2 == 0 else BLUE
                pg.draw.rect(self.screen, colour, (move.final.col * TILESIZE, move.final.row * TILESIZE, TILESIZE, TILESIZE))
            if piece.moves:
                initial = piece.moves[0].initial
                colour = BLUE if (initial.row + initial.col) % 2 != 0 else LIGHT_BLUE
                pg.draw.rect(self.screen, colour, (initial.col * TILESIZE, initial.row * TILESIZE, TILESIZE, TILESIZE))

    def show_last_move(self):
        if self.previous_moves:
            move = self.previous_moves[-1]
            pg.draw.rect(self.screen, RED, (move.final.col * TILESIZE, move.final.row * TILESIZE, TILESIZE, TILESIZE))
            pg.draw.rect(self.screen, RED, (move.initial.col * TILESIZE, move.initial.row * TILESIZE, TILESIZE, TILESIZE))

    def show_get_draw(self):
        pg.draw.rect(self.screen, BLACK, (0.5 * TILESIZE, 2.5 * TILESIZE, TILESIZE * 7, TILESIZE * 4))
        self.text_to_screen('Agree To Draw?', 1.1 * TILESIZE, 3 * TILESIZE, size=40)
        self.draw_button(0.75, 5, 3, 1, GREEN, 'AGREE', BLACK, text_size=45)
        self.draw_button(4.25, 5, 3, 1, RED, 'DISAGREE', BLACK, text_size=40)

    def get_draw_events(self, clicked_row, clicked_col):
        if clicked_row == 5:
            if 3.75 > clicked_col > 0.75:
                self.get_draw = False
                self.game_draw = True
            elif 4.25 < clicked_col < 7.25:
                self.get_draw = False
                self.game_draw = False

    def show_previous_moves(self):
        count = min(len(self.previous_moves), 8)
        for i in range(count):
            move = self.previous_moves[-(1 + i)]
            self.text_to_screen(move.move_in_chess_notation, 8.3 * TILESIZE, i * TILESIZE, colour=move.colour)

    # ── Move history ──────────────────────────────────────────────────────────

    def undo_move(self, row):
        length = len(self.previous_moves)
        cap = min(length, 8)
        if row == 0:
            self.temp_board = self.board
            self.board = self.previous_moves[-1].board
        else:
            for i in range(cap):
                if i == row:
                    self.temp_board = self.board
                    self.board = self.previous_moves[-(1 + i)].board
                    break

    def redo_move(self):
        self.board = self.temp_board
        self.temp_board = None

    def add_move_to_stack(self, piece, move, save_board=True):
        initial = move.initial
        final = move.final
        if save_board:
            move.board = copy.deepcopy(self.board)
        move.move_in_chess_notation = self.convert_move_into_chess_notation(piece, initial, final)
        move.colour = GREY if piece.colour == BLACK else piece.colour
        self.previous_moves.append(move)

    # ── Chess notation ────────────────────────────────────────────────────────

    def convert_move_into_chess_notation(self, piece, initial, final):
        col_letters = cols_as_letters
        row_chars = rows_as_characters
        is_capture = self.board.squares[final.row][final.col].has_enemy_piece(piece.colour)
        capture_str = 'x' if is_capture else ''
        dest = col_letters[final.col] + row_chars[final.row]

        if isinstance(piece, Pawn):
            if is_capture:
                return col_letters[initial.col] + 'x' + dest
            return dest
        elif isinstance(piece, Bishop):
            return bishop_character + capture_str + dest
        elif isinstance(piece, Knight):
            return knight_character + capture_str + dest
        elif isinstance(piece, Rook):
            return rook_character + capture_str + dest
        elif isinstance(piece, Queen):
            return queen_character + capture_str + dest
        elif isinstance(piece, King):
            return king_character + capture_str + dest
        return ''

    def convert_chess_notation_into_move(self, chess_notation, colour):
        final_col = -1
        final_row = -1
        for char in chess_notation:
            row = self.compare_char_to_row_char(char)
            col = self.compare_char_to_col_char(char)
            if col != -1:
                final_col = col
            elif row != -1:
                final_row = row

        if final_row == -1 or final_col == -1:
            return None
        piece = self.get_piece_from_char(chess_notation[0])
        if piece is None:
            return None
        return self.find_piece_on_board(piece, colour, final_row, final_col)

    def compare_char_to_row_char(self, char):
        for row in range(8):
            if rows_as_characters[row] == char:
                return row
        return -1

    def compare_char_to_col_char(self, char):
        for col in range(8):
            if cols_as_letters[col] == char:
                return col
        return -1

    def get_piece_from_char(self, char):
        if char == king_character:
            return King
        elif char == queen_character:
            return Queen
        elif char == rook_character:
            return Rook
        elif char == bishop_character:
            return Bishop
        elif char == knight_character:
            return Knight
        elif self.compare_char_to_col_char(char) != -1:
            return Pawn
        return None

    def find_piece_on_board(self, piece_class, colour, final_row, final_col):
        move = None
        for row in range(8):
            for col in range(8):
                sq = self.board.squares[row][col]
                if sq.has_team_piece(colour) and isinstance(sq.piece, piece_class):
                    self.board.calculate_moves(sq.piece, row, col)
                    for m in sq.piece.moves:
                        if m.final.row == final_row and m.final.col == final_col:
                            move = m
                            move.moved_piece = sq.piece
        return move

    def text_box_event(self, event, colour):
        if event.key == pg.K_RETURN:
            move = self.convert_chess_notation_into_move(self.move_in_chess_notation, colour)
            if move:
                piece = move.moved_piece
                if self.board.valid_move(piece, move):
                    self.add_move_to_stack(piece, move)
                    self.board.move(piece, move)
                    self.player_turn()
            self.move_in_chess_notation = ''
        elif event.key == pg.K_BACKSPACE:
            self.move_in_chess_notation = self.move_in_chess_notation[:-1]
        else:
            self.move_in_chess_notation += event.unicode

    # ── UI helpers ────────────────────────────────────────────────────────────

    def player_turn(self):
        self.player = BLACK if self.player == WHITE else WHITE

    def text_to_screen(self, text, x, y, size=25, colour=WHITE, font_type='Lucida Console'):
        font = pg.font.SysFont(font_type, size)
        rendered = font.render(str(text), True, colour)
        self.screen.blit(rendered, (x, y))

    def draw_button(self, col_pos, row_pos, col_size, row_size, colour, text, text_colour, text_size=50):
        rect = (col_pos * 63.5, row_pos * 64.5, col_size * TILESIZE, row_size * 54)
        pg.draw.rect(self.screen, colour, rect)
        self.text_to_screen(text, col_pos * TILESIZE, row_pos * TILESIZE, size=text_size, colour=text_colour)

    def press_undo_button(self):
        if self.previous_moves:
            self.board = self.previous_moves[-1].board
            if self.previous_moves[-1].colour != self.player:
                self.player_turn()
            self.previous_moves.pop()

    # ── Game over / menu screens ──────────────────────────────────────────────

    def draw_game_over_screen(self):
        for i in range(10):
            for j in range(10):
                colour = WHITE if (i + j) % 2 == 0 else DARK_GREY
                if j != 9:
                    pg.draw.rect(self.screen, colour, (i * TILESIZE, j * TILESIZE, TILESIZE, TILESIZE))
                else:
                    pg.draw.rect(self.screen, colour, (i * TILESIZE, j * TILESIZE, TILESIZE * 0.3, TILESIZE))
        self.draw_button(9.05, 0, 0.3, 10.75, LIGHT_GREY, '', WHITE)
        self.draw_menu_title(1, 2, 'GAME OVER', colour=RED)
        self.draw_game_results(2, 2.5)
        self.draw_player_value(str(self.white_board_val), 5.1, 5, WHITE)
        self.draw_player_value(str(self.black_board_val), 0.4, 5, BLACK)
        self.draw_button(4.86, 8, 4, 1, RED, 'Menu Screen', BLACK, text_size=38)
        self.draw_button(0.15, 8, 4, 1, BLUE, 'Play Again', BLACK, text_size=40)
        pg.display.flip()

    def draw_game_results(self, pos_col, pos_row):
        pg.draw.rect(self.screen, BLACK, (pos_col * TILESIZE, pos_row * TILESIZE, TILESIZE * 5, TILESIZE * 2))
        if self.player_result:
            winner = self.player_result + 'Wins'
            self.text_to_screen(winner, (pos_col + 0.45) * TILESIZE, (pos_row + 0.1) * TILESIZE, size=50, colour=LIGHT_GREY)
            self.text_to_screen(self.result, (pos_col + 0.45) * TILESIZE, (pos_row + 1.1) * TILESIZE, size=50, colour=LIGHT_GREY)
        elif self.result in ('Stalemate', 'Complete'):
            self.text_to_screen(self.result, (pos_col + 0.45) * TILESIZE, (pos_row + 0.1) * TILESIZE, size=60, colour=WHITE)
        else:
            self.text_to_screen(self.result, (pos_col + 1) * TILESIZE, (pos_row + 0.1) * TILESIZE, size=80, colour=WHITE)

    def draw_player_value(self, player_value, pos_col, pos_row, colour):
        if colour == WHITE:
            opposite = BLACK
            text = 'White Piece'
            colour = LIGHT_GREY
        else:
            opposite = LIGHT_GREY
            text = 'Black Piece'
        pg.draw.rect(self.screen, opposite, ((pos_col - 0.25) * TILESIZE, (pos_row - 0.25) * TILESIZE, TILESIZE * 4, TILESIZE * 3))
        pg.draw.rect(self.screen, colour, (pos_col * TILESIZE, pos_row * TILESIZE, TILESIZE * 3.5, TILESIZE * 2.5))
        self.text_to_screen(text, pos_col * TILESIZE, (pos_row + 0.4) * TILESIZE, size=30, colour=opposite)
        self.text_to_screen('Value:' + player_value, pos_col * TILESIZE, (pos_row + 1.4) * TILESIZE, size=30, colour=opposite)

    def game_over_events(self):
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos_x, mouse_pos_y = event.pos
                clicked_row = mouse_pos_y // TILESIZE
                clicked_col = mouse_pos_x // TILESIZE
                if clicked_row == 8:
                    if 4 > clicked_col > 0:
                        self.playing = True
                        self.game_over = False
                        self.show_game_menu = False
                    elif 5 < clicked_col < 8:
                        self.show_game_menu = True
                        self.game_over = False
                        self.running = False
            if event.type == pg.QUIT:
                pg.quit()

    def draw_game_menu(self):
        from src.settings import ONE_PLAYER, TWO_PLAYER
        for i in range(10):
            for j in range(10):
                colour = WHITE if (i + j) % 2 == 0 else DARK_GREY
                if j != 9:
                    pg.draw.rect(self.screen, colour, (i * TILESIZE, j * TILESIZE, TILESIZE, TILESIZE))
                else:
                    pg.draw.rect(self.screen, colour, (i * TILESIZE, j * TILESIZE, TILESIZE * 0.3, TILESIZE))
        self.draw_menu_title(1, 2, TITLE)
        self.draw_game_menu_button(4, 5.25, TWO_PLAYER, 'Two Player', 'Game')
        self.draw_game_menu_button(4, 0.75, ONE_PLAYER, 'One Player', 'Game')
        pg.display.flip()

    def draw_game_menu_button(self, pos_row, pos_col, colour, first_line, second_line, text_colour=BLACK, bool=True):
        pg.draw.rect(self.screen, BLACK, ((pos_col - 0.25) * TILESIZE, (pos_row - 0.25) * TILESIZE, TILESIZE * 3.5, TILESIZE * 2.5))
        pg.draw.rect(self.screen, colour, (pos_col * TILESIZE, pos_row * TILESIZE, TILESIZE * 3, TILESIZE * 2))
        self.text_to_screen(first_line, pos_col * TILESIZE, pos_row * TILESIZE, size=30, colour=text_colour)
        if bool:
            pos_col += 1
        self.text_to_screen(second_line, pos_col * TILESIZE, (pos_row + 1) * TILESIZE, size=30, colour=text_colour)

    def draw_menu_title(self, position_row, position_col, title, colour=WHITE):
        pg.draw.rect(self.screen, BLACK, (position_col * TILESIZE, position_row * TILESIZE, TILESIZE * 5, TILESIZE))
        if title == TITLE:
            self.text_to_screen(title, (position_col + 0.1) * TILESIZE, (position_row + 0.1) * TILESIZE, size=50, colour=colour)
        else:
            self.text_to_screen(title, (position_col + 0.45) * TILESIZE, (position_row + 0.1) * TILESIZE, size=50, colour=colour)

    def game_menu_events(self):
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos_x, mouse_pos_y = event.pos
                clicked_row = mouse_pos_y // TILESIZE
                clicked_col = mouse_pos_x // TILESIZE
                if clicked_row in (4, 5):
                    if 4 > clicked_col > 0:
                        self.one_player = True
                        self.show_game_menu = False
                    elif 5 < clicked_col < 8:
                        self.playing = True
                        self.show_game_menu = False
            if event.type == pg.QUIT:
                if self.playing or self.show_game_menu:
                    self.show_game_menu = False
                    self.playing = False
                self.running = False


# Sentinel mixin used only for isinstance checks in draw()
class OnePlayerGameMixin:
    pass
