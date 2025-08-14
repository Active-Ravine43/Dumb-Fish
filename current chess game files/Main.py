import pygame as pg
from Game import *
from settings import *

#Main class that runs the 4 different game modes
class Main:

    #initialize Main class attributes
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((width, height))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.show_main_menu = True
        self.playing = False
        self.play_new_game = False
        self.play_training_game = False
        self.game = Game(self.screen, self.running, self.clock, self.playing)
        self.single_player_game = One_Player_Game(self.screen, self.running, self.clock, self.playing)
        self.practice_game = Practice_Game(self.screen, self.running, self.clock, self.playing)
        self.chess_comp = Chess_Compositions(self.screen, self.running, self.clock, self.playing)

    #loads game mode chosen by the player
    def run_main(self):
        #show main menu (training game or new game selection screen)
        self.ShowMainMenuScreen()
        while self.running:
            #resets all the games for replaying
            self.game = Game(self.screen, self.running, self.clock, self.playing)
            self.single_player_game = One_Player_Game(self.screen, self.running, self.clock, self.playing)
            self.practice_game = Practice_Game(self.screen, self.running, self.clock, self.playing)
            self.chess_comp = Chess_Compositions(self.screen, self.running, self.clock, self.playing)
            #shows menu for one or two player options and runs selected option
            if self.play_new_game:
                self.One_or_Two_players()
                self.play_new_game = False
                self.ShowMainMenuScreen()
            #shows practice game selection menu and runs selected option
            elif self.play_training_game:
                self.Practice_or_ChessComp()
                self.play_training_game = False
                self.ShowMainMenuScreen()

    #shows player selection menu and runs the selected game mode
    def One_or_Two_players(self):
        self.show_main_menu = False
        self.game.show_game_menu = True
        #show game mode selection screen
        self.ShowMenuScreen()
        while self.game.running:
            #if two player game selected
            if self.game.playing:
                #runs the two player game
                self.run_game()
            elif self.game.game_over:
                #shows game over screen
                self.GameOverScreen(self.game)
                # reset game if playing game mode again
                if self.game.previous_moves:
                    self.game.board = self.game.previous_moves[0].board
                self.game.previous_moves = []
                self.game.player = WHITE
            #if single player game mode is selected
            elif self.single_player_game.playing:
                self.run_single_player_game()
            elif self.single_player_game.game_over:
                #shows game over screen
                self.GameOverScreen(self.single_player_game)
                #reset game if playing game mode again
                if self.single_player_game.previous_moves:
                    self.single_player_game.board = self.single_player_game.previous_moves[0].board
                self.single_player_game.previous_moves = []
                self.single_player_game.player = WHITE
        #if game now longer running, return to menu
        self.show_main_menu = True

    # shows player selection menu and runs the selected game
    def Practice_or_ChessComp(self):
        self.show_main_menu = False
        self.practice_game.show_game_menu = True
        #shows the Training game selection screen
        self.ShowTrainingMenu()
        while self.practice_game.running:
            #if practice game selected run the practice game
            if self.practice_game.playing:
                self.run_practice_game()
            #if practice game is over show game over screen
            elif self.practice_game.game_over:
                self.GameOverScreen(self.practice_game)
                #reset game values if play game again
                if self.practice_game.previous_moves:
                    self.practice_game.board = self.practice_game.previous_moves[0].board
                self.practice_game.previous_moves = []
                self.practice_game.player = WHITE
            #if chess puzzle selected then run the chess puzzle
            elif self.chess_comp.playing:
                self.run_chess_comp()
            #if chess puzzle is over show game over screen
            elif self.chess_comp.game_over:
                self.GameOverScreen(self.chess_comp)
                self.chess_comp.previous_moves = []

        # if practice game now longer running, return to menu
        self.show_main_menu = True

    #runs the main menu screen
    def ShowMainMenuScreen(self):
        #main menu loop
        while self.show_main_menu:
            self.main_menu_events()
            self.draw_main_menu()

    #handle the main menu events
    def main_menu_events(self):
        for event in pg.event.get():
            #event: mouse click
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos_x, mouse_pos_y = event.pos
                clicked_row = mouse_pos_y // TILESIZE
                clicked_col = mouse_pos_x // TILESIZE
                if clicked_row == 4 or 5:
                    #if training game button clicked
                    if 4 > clicked_col > 0:
                        self.play_training_game = True
                        #break main menu loop
                        self.show_main_menu = False
                    #if new game button clicked
                    elif 5 < clicked_col < 8:
                        self.play_new_game = True
                        # break main menu loop
                        self.show_main_menu = False


            if event.type == pg.QUIT:
                pg.quit()

    #draws the main menu
    def draw_main_menu(self):
        #draws the grid on left side of screen
        for i in range (0, 5):
            for j in range (0, 10):
                if i < 4:
                    if (i+j) % 2 == 0:
                        colour = GREEN
                    else:
                        colour = DARK_GREEN
                    rect = (i * TILESIZE, j * TILESIZE, TILESIZE, TILESIZE)
                    pg.draw.rect(self.screen, colour, rect)
                #draws middle black line
                else:
                    rect = (i * TILESIZE, j * TILESIZE, TILESIZE, TILESIZE)
                    pg.draw.rect(self.screen, BLACK, rect)
        #draws the grid on the right side of the screen
        for i in range(0, 5):
            for j in range(0, 10):
                if i < 4:
                    if (i + j) % 2 == 0:
                        colour = WHITE
                    else:
                        colour = DARK_GREY
                    rect = ((i+5) * TILESIZE, j * TILESIZE, TILESIZE, TILESIZE)
                    pg.draw.rect(self.screen, colour, rect)
                #fills gap on right side of the screen
                else:
                    rect = ((i+5) * TILESIZE, j * TILESIZE, TILESIZE * 0.3, TILESIZE)
                    pg.draw.rect(self.screen, LIGHT_GREY, rect)
        #draw main menu title
        self.game.draw_menu_title(1, 2, TITLE)
        #draw the training game button
        self.game.draw_game_menu_button(4, 0.5, DARK_GREY, ' Training', 'Game', text_colour=DARK_GREEN)
        #draw the new game button
        self.game.draw_game_menu_button(4, 5.5, GREEN, '    New', 'Game')
        #flip the display
        pg.display.flip()

    #shows select new game menu
    def ShowMenuScreen(self):
        # reset value incase of replay
        self.game.one_player = False
        #new game menu screen loop
        while self.game.show_game_menu:
            self.game.game_menu_events()
            self.game.draw_game_menu()
        #if player 1 selected 1 player game is playing
        if self.game.one_player:
            self.single_player_game.playing = True

    #Shows select new training game menu
    def ShowTrainingMenu(self):
        #resets value in case of replay
        self.practice_game.chess_comp = False
        #select training game menu loop
        while self.practice_game.show_game_menu:
            self.practice_game.training_game_menu_events()
            self.practice_game.draw_training_game_menu()
        #if chess puzzle selected then chess puzzle is playing
        if self.practice_game.chess_comp:
            self.chess_comp.playing = True

    # shows the game over screen
    def GameOverScreen(self, game):
        #game over screen loop
        while game.game_over:
            game.game_over_events()
            game.draw_game_over_screen()
        #if returning to main menu
        if game.show_game_menu:
            #return from a training game to menu screen
            if isinstance(game, Practice_Game) or isinstance(game, Chess_Compositions):
                self.practice_game.running = False
            #return from a standard game to menu screen
            elif isinstance(game, One_Player_Game)  or isinstance(game, Game):
                self.game.running = False
            #show the main menu screen
            self.show_main_menu = True

    # runs a two player game
    def run_game(self):
        self.game.playing = True
        #2 player game loop
        while self.game.playing:
            self.clock.tick(FPS)
            self.main_events()
            self.game.new()

    # runs 1 player game
    def run_single_player_game(self):
        self.single_player_game.playing = True
        #1 player game loop
        while self.single_player_game.playing:
            self.clock.tick(FPS)
            self.main_events()
            self.single_player_game.new()

    #run a practice game
    def run_practice_game(self):
        self.practice_game.playing = True
        #practice game loop
        while self.practice_game.playing:
            self.clock.tick(FPS)
            self.main_events()
            self.practice_game.new()

    #run a chess puzzle
    def run_chess_comp(self):
        self.chess_comp.playing = True
        #chess puzzle game loop
        while self.chess_comp.playing:
            self.clock.tick(FPS)
            self.main_events()
            self.chess_comp.new()

    #handles the main events
    def main_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()


#exectutes the program:
m = Main()
m.run_main()
pg.quit()