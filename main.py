import pygame as pg

from src.settings import (
    WHITE, BLACK, GREEN, DARK_GREEN, DARK_GREY, LIGHT_GREY,
    WIDTH, HEIGHT, TITLE, TILESIZE, FPS,
)
from src.ui.game import Game
from src.ui.one_player_game import OnePlayerGame
from src.ui.practice_game import PracticeGame
from src.ui.chess_compositions import ChessCompositions


class Main:

    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.show_main_menu = True
        self.playing = False
        self.play_new_game = False
        self.play_training_game = False
        self.game = Game(self.screen, self.running, self.clock, self.playing)
        self.single_player_game = OnePlayerGame(self.screen, self.running, self.clock, self.playing)
        self.practice_game = PracticeGame(self.screen, self.running, self.clock, self.playing)
        self.chess_comp = ChessCompositions(self.screen, self.running, self.clock, self.playing)

    # ── Main loop ─────────────────────────────────────────────────────────────

    def run_main(self):
        self.show_main_menu_screen()
        while self.running:
            self.game = Game(self.screen, self.running, self.clock, self.playing)
            self.single_player_game = OnePlayerGame(self.screen, self.running, self.clock, self.playing)
            self.practice_game = PracticeGame(self.screen, self.running, self.clock, self.playing)
            self.chess_comp = ChessCompositions(self.screen, self.running, self.clock, self.playing)
            if self.play_new_game:
                self.one_or_two_players()
                self.play_new_game = False
                self.show_main_menu_screen()
            elif self.play_training_game:
                self.practice_or_chess_comp()
                self.play_training_game = False
                self.show_main_menu_screen()

    # ── Game mode selectors ───────────────────────────────────────────────────

    def one_or_two_players(self):
        self.show_main_menu = False
        self.game.show_game_menu = True
        self.show_menu_screen()
        while self.game.running:
            if self.game.playing:
                self.run_game()
            elif self.game.game_over:
                self.game_over_screen(self.game)
                if self.game.previous_moves:
                    self.game.board = self.game.previous_moves[0].board
                self.game.previous_moves = []
                self.game.player = WHITE
            elif self.single_player_game.playing:
                self.run_single_player_game()
            elif self.single_player_game.game_over:
                self.game_over_screen(self.single_player_game)
                if self.single_player_game.previous_moves:
                    self.single_player_game.board = self.single_player_game.previous_moves[0].board
                self.single_player_game.previous_moves = []
                self.single_player_game.player = WHITE
        self.show_main_menu = True

    def practice_or_chess_comp(self):
        self.show_main_menu = False
        self.practice_game.show_game_menu = True
        self.show_training_menu()
        while self.practice_game.running:
            if self.practice_game.playing:
                self.run_practice_game()
            elif self.practice_game.game_over:
                self.game_over_screen(self.practice_game)
                if self.practice_game.previous_moves:
                    self.practice_game.board = self.practice_game.previous_moves[0].board
                self.practice_game.previous_moves = []
                self.practice_game.player = WHITE
            elif self.chess_comp.playing:
                self.run_chess_comp()
            elif self.chess_comp.game_over:
                self.game_over_screen(self.chess_comp)
                self.chess_comp.previous_moves = []
        self.show_main_menu = True

    # ── Menu screens ──────────────────────────────────────────────────────────

    def show_main_menu_screen(self):
        while self.show_main_menu:
            self.main_menu_events()
            self.draw_main_menu()

    def main_menu_events(self):
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos_x, mouse_pos_y = event.pos
                clicked_row = mouse_pos_y // TILESIZE
                clicked_col = mouse_pos_x // TILESIZE
                if clicked_row in (4, 5):
                    if 4 > clicked_col > 0:
                        self.play_training_game = True
                        self.show_main_menu = False
                    elif 5 < clicked_col < 8:
                        self.play_new_game = True
                        self.show_main_menu = False
            if event.type == pg.QUIT:
                pg.quit()

    def draw_main_menu(self):
        for i in range(10):
            for j in range(10):
                if i < 4:
                    colour = GREEN if (i + j) % 2 == 0 else DARK_GREEN
                    pg.draw.rect(self.screen, colour, (i * TILESIZE, j * TILESIZE, TILESIZE, TILESIZE))
                elif i == 4:
                    pg.draw.rect(self.screen, BLACK, (i * TILESIZE, j * TILESIZE, TILESIZE, TILESIZE))
                elif i < 9:
                    colour = WHITE if (i + j) % 2 == 0 else DARK_GREY
                    pg.draw.rect(self.screen, colour, (i * TILESIZE, j * TILESIZE, TILESIZE, TILESIZE))
                else:
                    pg.draw.rect(self.screen, LIGHT_GREY, (i * TILESIZE, j * TILESIZE, TILESIZE * 0.3, TILESIZE))

        self.game.draw_menu_title(1, 2, TITLE)
        self.game.draw_game_menu_button(4, 0.5, DARK_GREY, ' Training', 'Game', text_colour=DARK_GREEN)
        self.game.draw_game_menu_button(4, 5.5, GREEN, '    New', 'Game')
        pg.display.flip()

    def show_menu_screen(self):
        self.game.one_player = False
        while self.game.show_game_menu:
            self.game.game_menu_events()
            self.game.draw_game_menu()
        if self.game.one_player:
            self.single_player_game.playing = True

    def show_training_menu(self):
        self.practice_game.chess_comp = False
        while self.practice_game.show_game_menu:
            self.practice_game.training_game_menu_events()
            self.practice_game.draw_training_game_menu()
        if self.practice_game.chess_comp:
            self.chess_comp.playing = True

    # ── Game over screen ──────────────────────────────────────────────────────

    def game_over_screen(self, game):
        while game.game_over:
            game.game_over_events()
            game.draw_game_over_screen()
        if game.show_game_menu:
            if isinstance(game, (PracticeGame, ChessCompositions)):
                self.practice_game.running = False
            elif isinstance(game, (OnePlayerGame, Game)):
                self.game.running = False
            self.show_main_menu = True

    # ── Run individual modes ──────────────────────────────────────────────────

    def run_game(self):
        self.game.playing = True
        while self.game.playing:
            self.clock.tick(FPS)
            self.main_events()
            self.game.new()

    def run_single_player_game(self):
        self.single_player_game.playing = True
        while self.single_player_game.playing:
            self.clock.tick(FPS)
            self.main_events()
            self.single_player_game.new()

    def run_practice_game(self):
        self.practice_game.playing = True
        while self.practice_game.playing:
            self.clock.tick(FPS)
            self.main_events()
            self.practice_game.new()

    def run_chess_comp(self):
        self.chess_comp.playing = True
        while self.chess_comp.playing:
            self.clock.tick(FPS)
            self.main_events()
            self.chess_comp.new()

    def main_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()


if __name__ == '__main__':
    m = Main()
    m.run_main()
    pg.quit()
