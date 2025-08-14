import random
from Chess_Ai import *
from Piece_Grabber import *

#Parent Game class (runs standard two player game)
class Game:

    #initiliaze game attributes
    def __init__(self, screen, running, clock, playing):
        #initialise game window, etc
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
        self.Piece_Grabber = Piece_Grabber()
        self.Chess_bot = Chess_Bot(self.player, self.board)
        self.previous_moves = []
        self.result = ''
        self.player_result = ''
        self.white_board_val = 0
        self.black_board_val = 0
        self.move_in_chess_notation = ''
        self.t_box_active = False

    # start a new game
    def new(self):
        self.run()

    #runs the game
    def run(self):
        #game loop
        while self.playing:
            self.events()
            self.draw()

    #handles in game events
    def events(self):
        #if the game is a draw
        if self.game_draw and not self.get_draw:
            #sets the piece value of black pieces left at end of game
            self.black_board_val = self.Chess_bot.evaluate_piece_value(self.board, BLACK) // 100
            self.black_board_val = self.black_board_val - 100
            #sets the piece value of white pieces left at end of game
            self.white_board_val = self.Chess_bot.evaluate_piece_value(self.board, WHITE) // 100
            self.white_board_val = self.white_board_val - 100
            #sets how the game ended
            self.result = 'DRAW'
            self.game_over = True
            self.playing = False
            self.game_draw = False

        for event in pg.event.get():
            #event: mouse click
            if event.type == pg.MOUSEBUTTONDOWN:
                self.Piece_Grabber.update_mouse(event.pos)

                clicked_row = self.Piece_Grabber.MouseY // TILESIZE
                clicked_col = self.Piece_Grabber.MouseX // TILESIZE
                #checks to see if a move was clicked
                if clicked_col == 8 and clicked_row != 8:
                    self.undo_move(clicked_row)
                #if undo button was clicked
                elif clicked_row == 8 and (clicked_col == 7 or clicked_col == 8):
                    self.press_undo_button()
                #if draw button clicked
                elif clicked_row == 8 and (clicked_col == 0 or clicked_col == 1):
                    self.get_draw = True
                #draw is suggested
                elif self.get_draw:
                    self.get_draw_events(clicked_row, clicked_col)
                #if the text box is clicked
                elif clicked_row == 8 and 2.4<clicked_col<6.4:
                    self.t_box_active = not self.t_box_active
                #does clicked square have a piece
                elif self.board.squares[clicked_row][clicked_col].has_piece():
                    piece = self.board.squares[clicked_row][clicked_col].piece
                    #check valid player turn
                    if piece.colour == self.player:
                        #calculates the pieces legal moves
                        self.board.calculate_moves(piece, clicked_row, clicked_col, bool=True)
                        #saves the pieces initial position
                        self.Piece_Grabber.save_initial_pos(event.pos)
                        #lets the game know the piece is attached to or 'grabbed' by mouse
                        self.Piece_Grabber.Grab_Piece(piece)
                        #shows the legal possible moves of a piece
                        self.show_possible_moves()

            elif event.type == pg.MOUSEMOTION:
            #if the event is the mouse moving and a piece is attached too/'grabbed' by the mouse
                if  self.Piece_Grabber.Holding:
                    self.Piece_Grabber.update_mouse(event.pos)
                    self.Piece_Grabber.update_grabber(self.screen)


            elif event.type == pg.MOUSEBUTTONUP:
            #if holding piece and player lets go
                if self.Piece_Grabber.Holding:
                    self.Piece_Grabber.update_mouse(event.pos)
                    released_row = self.Piece_Grabber.MouseY // TILESIZE
                    released_col = self.Piece_Grabber.MouseX // TILESIZE
                    #creates the move the player is attempting to make
                    initial = Square(self.Piece_Grabber.initial_row, self.Piece_Grabber.initial_col)
                    final = Square(released_row, released_col)
                    move = Move(initial, final, self.Piece_Grabber.piece)
                    #checks the players move is a valid move
                    if self.board.valid_move(self.Piece_Grabber.piece, move):
                        #adds the move to previous moves
                        self.add_move_to_stack(self.Piece_Grabber.piece, move)
                        #makes the player move on the board
                        self.board.move(self.Piece_Grabber.piece, move)
                        #switch player
                        self.player_turn()

                        #checks for checkmate
                        if not self.board.has_legal_moves(self.player) and self.board.in_check(self.player, copy.deepcopy(self.board)):
                            #identifies the winning player
                            if self.player == BLACK:
                                self.player_result = 'White'
                            else:
                                self.player_result = 'Black'
                            #sets the value of the black pieces left at game over
                            self.black_board_val = self.Chess_bot.evaluate_piece_value(self.board, BLACK) // 100
                            self.black_board_val = self.black_board_val - 100
                            # sets the value of the white pieces left at game over
                            self.white_board_val = self.Chess_bot.evaluate_piece_value(self.board, WHITE) // 100
                            self.white_board_val = self.white_board_val - 100
                            #sets how game ended
                            self.result = 'Checkmate'
                            self.game_over = True
                            self.playing = False

                        #checks for stalemate
                        elif not self.board.has_legal_moves(self.player):
                            # sets the value of the black pieces left at game over
                            self.black_board_val = self.Chess_bot.evaluate_piece_value(self.board, BLACK) // 100
                            self.black_board_val = self.black_board_val - 100
                            # sets the value of the white pieces left at game over
                            self.white_board_val = self.Chess_bot.evaluate_piece_value(self.board, WHITE) // 100
                            self.white_board_val = self.white_board_val - 100
                            #sets how game ended
                            self.result = 'Stalemate'
                            self.game_over = True
                            self.playing = False

                    # unattaches/'ungrabs' the held piece from the mouse
                    self.Piece_Grabber.UnGrab_Piece()
                #if showing a previous board state, reset back to original board state
                elif self.temp_board:
                    self.redo_move()

            elif event.type == pg.KEYDOWN:
                #if player typing and text box is active
                if self.t_box_active:
                    self.text_box_event(event, self.player)

            if event.type == pg.QUIT:
                pg.quit()

    #displays everything in a game
    def draw(self):
        self.screen.fill(BLACK)
        self.draw_grid()
        self.draw_coordinates()
        self.show_last_move()
        if self.Piece_Grabber.Holding:
            #show the possible moves of the piece being held
            self.show_possible_moves()
        self.show_pieces(self.screen)
        #displays the previous moves made in chess notation
        if self.previous_moves:
            self.show_previous_moves()
        #draw undo button
        self.draw_button(6.8, 8.275, 2, 0.70, RED, 'UNDO', BLACK)
        #display game draw button
        self.draw_button(0.3, 8.275, 2, 0.70, RED, 'DRAW', BLACK)
        #display text box
        self.draw_button(2.55 , 8.275, 4, 0.70, WHITE, self.move_in_chess_notation, BLACK)
        #shows Bots decision on Game draw
        if self.get_draw and isinstance(self, One_Player_Game):
            if self.start_tick == 0:
                self.start_tick = pg.time.get_ticks()
            seconds = (pg.time.get_ticks() - self.start_tick) / 1000
            self.show_get_draw()
            if seconds > 3:
                self.get_draw = False
        #shows accept or decline draw
        elif self.get_draw :
            self.show_get_draw()
        #flip the display
        pg.display.flip()

    # displays the board squares
    def draw_grid(self):
        for i in range (0,8):
            for j in range (0,8):
                if (i+j) % 2 == 0:
                    colour = WHITE
                else:
                    colour = DARK_GREY
                rect = (i * TILESIZE, j * TILESIZE, TILESIZE, TILESIZE)
                pg.draw.rect(self.screen, colour, rect)

    #draws the boards coordinates
    def draw_coordinates(self):
        self.draw_button(8, 0, 0.3, 9.5, LIGHT_GREY, '', WHITE)
        for i in range (0, 8):
            self.text_to_screen(rows_as_characters[i], 8.05*TILESIZE, (i + 0.45)*TILESIZE, size=17, colour=BLACK)
            self.text_to_screen(cols_as_letters[i], (i + 0.45 )* TILESIZE, 8.05 * TILESIZE, size=17)

    # draws the pieces on the screen
    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                # if there is piece in the square
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece
                    #draw any piece that is held where mouse is
                    if self.Piece_Grabber.Holding:
                        self.Piece_Grabber.update_grabber(self.screen)
                    #draw all stationary pieces
                    if piece is not self.Piece_Grabber.piece:
                        piece.set_texture(size=80)
                        img = pg.image.load(piece.texture)
                        img_center = col * TILESIZE + TILESIZE //2, row * TILESIZE + TILESIZE //2
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.texture_rect)

    #shows the possible moves of a piece being held
    def show_possible_moves(self):
        if self.Piece_Grabber.Holding:
            piece = self.Piece_Grabber.piece
            #colours in all the squares the piece can move to
            for move in piece.moves:
                if (move.final.row + move.final.col) % 2 == 0:
                    colour = LIGHT_BLUE
                else:
                    colour = BLUE
                rect = (move.final.col * TILESIZE, move.final.row * TILESIZE, TILESIZE, TILESIZE)
                pg.draw.rect(self.screen, colour, rect)
            #colours in the square the piece is sat on
            if piece.moves:
                initial = piece.moves[0].initial
                if (initial.row + initial.col) % 2 != 0:
                    colour = BLUE
                else:
                    colour = LIGHT_BLUE
                rect = (initial.col * TILESIZE, initial.row * TILESIZE, TILESIZE, TILESIZE)
                pg.draw.rect(self.screen, colour, rect)

    #shows the previous move made
    def show_last_move(self):
        if self.previous_moves:
            move = self.previous_moves[-1]
            rect = (move.final.col * TILESIZE, move.final.row * TILESIZE, TILESIZE, TILESIZE)
            rect2 = (move.initial.col * TILESIZE, move.initial.row * TILESIZE, TILESIZE, TILESIZE)
            pg.draw.rect(self.screen, RED, rect)
            pg.draw.rect(self.screen, RED, rect2)

    #shows the agree or disagree to draw screen
    def show_get_draw(self):
        rect = (0.5 * TILESIZE, 2.5 *TILESIZE, TILESIZE * 7, TILESIZE * 4)
        pg.draw.rect(self.screen, BLACK, rect)
        self.text_to_screen('Agree To Draw?', 1.1*TILESIZE, 3*TILESIZE, size=40)
        self.draw_button(0.75, 5, 3, 1, GREEN, 'AGREE', BLACK, text_size=45)
        self.draw_button(4.25, 5, 3, 1, RED, 'DISAGREE', BLACK, text_size=40)

    #agree or disagree to draw screen events
    def get_draw_events(self, clicked_row, clicked_col):
        if clicked_row == 5:
            #if clicked agree button
            if 3.75 > clicked_col > 0.75:
                self.get_draw = False
                self.game_draw = True
            #if clicked disagree button
            elif 4.25 < clicked_col < 7.25:
                self.get_draw = False
                self.game_draw = False

    #show the previous 8 moves made in the game
    def show_previous_moves(self):
        #if less than 8 moves have been made
        if len(self.previous_moves) < 8:
            for i in range (0, len(self.previous_moves)):
                display_move = self.previous_moves[-(1+i)].move_in_chess_notation
                move_colour = self.previous_moves[-(1+i)].colour
                self.text_to_screen(display_move, 8.3 * TILESIZE, i * TILESIZE, colour=move_colour)
        else:
            for i in range (0, 8):
                display_move = self.previous_moves[-(1 + i)].move_in_chess_notation
                move_colour = self.previous_moves[-(1 + i)].colour
                self.text_to_screen(display_move, 8.3 * TILESIZE, i * TILESIZE, colour=move_colour)

    #if previous move clicked show that board state
    def undo_move(self, row):
        length = len(self.previous_moves)
        #if less than 8 moves have been made
        if length < 8:
            for i in range(0, length):
                if i == row and i != 0:
                    #save current board state
                    self.temp_board = self.board
                    #set the board to previous board state
                    self.board = self.previous_moves[-(1+i)].board
            if row == 0:
                # save current board state
                self.temp_board = self.board
                # set the board to previous board state
                self.board = self.previous_moves[-1].board
        else:
            for i in range (0, 8):
                if i == row and row != 0:
                    # save current board state
                    self.temp_board = self.board
                    # set the board to previous board state
                    self.board = self.previous_moves[-(1+i)].board
            if row == 0:
                # save current board state
                self.temp_board = self.board
                # set the board to previous board state
                self.board = self.previous_moves[-1].board

    #resets board state after player stops viewing previous board state
    def redo_move(self):
        self.board = self.temp_board
        self.temp_board = None

    #displays text onto the screen
    def text_to_screen(self, text, x, y, size=25, colour = WHITE, font_type= 'Lucida Console'):

        text = str(text)
        font = pg.font.SysFont(font_type, size)
        text = font.render(text, True, colour)
        self.screen.blit(text, (x, y))

    #switches the player turn
    def player_turn(self):
        if self.player == WHITE:
            self.player = BLACK
        else:
            self.player = WHITE

    #adds move to previous moves
    def add_move_to_stack(self, piece, move, bool=True):
        initial = move.initial
        final = move.final
        if bool:
            move.board = copy.deepcopy(self.board)
        #assigns move chess notation
        move.move_in_chess_notation = self.convert_move_into_chess_notation(piece, initial, final)
        #assigns the move colour
        if piece.colour == BLACK:
            move.colour = GREY
        else:
            move.colour = piece.colour
        #adds the move to previous moves
        self.previous_moves.append(move)

    #converts a given move into chess notation
    def convert_move_into_chess_notation(self, piece, initial, final):

        chess_notation = ''
        initial_position = initial.col
        final_position_col = final.col
        final_position_row = final.row

        if isinstance(piece, Pawn):
            #if the move is a capture
            if self.board.squares[final.row][final.col].has_enemy_piece(piece.colour):
                chess_notation = cols_as_letters[initial_position] + 'x' + cols_as_letters[final_position_col] + rows_as_characters[final_position_row]
            else:
                chess_notation = cols_as_letters[final_position_col] + rows_as_characters[final_position_row]

        if isinstance(piece, Bishop):
            # if the move is a capture
            if self.board.squares[final.row][final.col].has_enemy_piece(piece.colour):
                chess_notation =  bishop_character + 'x' + cols_as_letters[final_position_col] + rows_as_characters[final_position_row]
            else:
                chess_notation = bishop_character + cols_as_letters[final_position_col] + rows_as_characters[final_position_row]

        if isinstance(piece, Knight):
            # if the move is a capture
            if self.board.squares[final.row][final.col].has_enemy_piece(piece.colour):
                chess_notation =  knight_character + 'x' + cols_as_letters[final_position_col] + rows_as_characters[final_position_row]
            else:
                chess_notation = knight_character + cols_as_letters[final_position_col] + rows_as_characters[final_position_row]

        if isinstance(piece, Rook):
            # if the move is a capture
            if self.board.squares[final.row][final.col].has_enemy_piece(piece.colour):
                chess_notation = rook_character + 'x' + cols_as_letters[final_position_col] + rows_as_characters[final_position_row]
            else:
                chess_notation = rook_character + cols_as_letters[final_position_col] + rows_as_characters[final_position_row]

        if isinstance(piece, Queen):
            # if the move is a capture
            if self.board.squares[final.row][final.col].has_enemy_piece(piece.colour):
                chess_notation =  queen_character + 'x' + cols_as_letters[final_position_col] + rows_as_characters[final_position_row]
            else:
                chess_notation = queen_character + cols_as_letters[final_position_col] + rows_as_characters[final_position_row]

        if isinstance(piece, King):
            # if the move is a capture
            if self.board.squares[final.row][final.col].has_enemy_piece(piece.colour):
                chess_notation =  king_character + 'x' + cols_as_letters[final_position_col] + rows_as_characters[final_position_row]
            else:
                chess_notation = king_character + cols_as_letters[final_position_col] + rows_as_characters[final_position_row]

        return chess_notation

    #converts a chess notation into a board move
    def convert_chess_notation_into_move(self, chess_notation, colour):
        final_col = -1
        final_row = -1
        move = None
        for char in chess_notation:
            #compares the char to a row position, returns -1 if not found
            row = self.compare_char_to_row_char(char)
            # compares the char to a col position, returns -1 if not found
            col = self.compare_char_to_col_char(char)
            #if column found
            if col != -1:
                final_col = col
            #if row found
            elif row != -1:
                final_row = row

        if final_row != -1 and final_col != -1:
            piece = self.get_piece_from_char(chess_notation[0])
            if piece is not None:
                move = self.find_piece_on_board(piece, colour, final_row, final_col)
        return move

    #compares a character in a chess notation to the different row positions
    def compare_char_to_row_char(self, char):
        actual_row = -1
        #compares the character to all the possible row characters
        for row in range(0, 8):
            if rows_as_characters[row] == char:
                actual_row = row
        #returns either the actual row or -1 if not found
        return actual_row

    #compares a character in a chess notation to the different column positions
    def compare_char_to_col_char(self,char):
        actual_col = -1
        for col in range(0,8):
            if cols_as_letters[col] == char:
                actual_col = col
        return actual_col

    #returns the piece from a char
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
        else:
            return None

    #searches for a piece on the board based on the final position of a piece move
    def find_piece_on_board(self, piece, colour, final_row, final_col):
        move = None
        for row in range(0,8):
            for col in range(0,8):
                square = self.board.squares[row][col]
                if square.has_team_piece(colour):
                    if isinstance(square.piece, piece):
                        self.board.calculate_moves(square.piece, row, col)
                        for m in square.piece.moves:
                            if m.final.row == final_row and m.final.col == final_col:
                                move = m
                                move.moved_piece = square.piece
        return move

    #handles the text box events
    def text_box_event(self, event, colour):
        if event.key == pg.K_RETURN:
            #if pressed enter convert chess notation into move
            move = self.convert_chess_notation_into_move(self.move_in_chess_notation, colour)
            if move:
                piece = move.moved_piece
                if self.board.valid_move(piece, move):
                    # if both a move and a valid move are returned add to previous moves
                    self.add_move_to_stack(piece, move)
                    #move piece on board
                    self.board.move(piece, move)
                    #switch the player turn
                    self.player_turn()
            #reset the text box
            self.move_in_chess_notation = ''
        elif event.key == pg.K_BACKSPACE:
            #if backspace remove last character of chess notation
            self.move_in_chess_notation = self.move_in_chess_notation[:-1]
        else:
            #add character pressed to chess notation
            self.move_in_chess_notation += event.unicode

    #draws the game over screen
    def draw_game_over_screen(self):
        #draws background
        for i in range(0, 10):
            for j in range(0, 10):
                if (i + j) % 2 == 0:
                    colour = WHITE
                else:
                    colour = DARK_GREY
                if j != 9:
                    rect = (i * TILESIZE, j * TILESIZE, TILESIZE, TILESIZE)
                    pg.draw.rect(self.screen, colour, rect)
                else:
                    rect = (i * TILESIZE, j * TILESIZE, TILESIZE * 0.3, TILESIZE)
                    pg.draw.rect(self.screen, colour, rect)
        white_board_value = str(self.white_board_val)
        black_board_value = str(self.black_board_val)
        self.draw_button(9.05, 0, 0.3, 10.75, LIGHT_GREY, '', WHITE)
        #draw game over title
        self.draw_menu_title(1, 2, 'GAME OVER', colour=RED)
        #show how game ended
        self.draw_game_results(2, 2.5)
        #show white piece value at end of game
        self.draw_player_value(white_board_value, 5.1, 5, WHITE)
        #show Black piece value at end of game
        self.draw_player_value(black_board_value, 0.4, 5, BLACK)
        #draw back to menu screen button
        self.draw_button(4.86, 8, 4, 1, RED, 'Menu Screen', BLACK, text_size=38)
        #draw play again button
        self.draw_button(0.15, 8, 4, 1, BLUE, 'Play Again', BLACK, text_size=40)
        pg.display.flip()

    #draws the result dependent on how game ended
    def draw_game_results(self, pos_col, pos_row):
        rect = (pos_col * TILESIZE, pos_row * TILESIZE, TILESIZE * 5, TILESIZE * 2)
        pg.draw.rect(self.screen, BLACK, rect)
        winner = self.player_result + 'Wins'
        result = self.result
        #if there is a winner
        if self.player_result != '':
            self.text_to_screen(winner, (pos_col+0.45) * TILESIZE, (pos_row+0.1) * TILESIZE, size=50, colour=LIGHT_GREY)
            self.text_to_screen(result, (pos_col+0.45) * TILESIZE, (pos_row+1.1) * TILESIZE, size=50, colour=LIGHT_GREY)
        #if the result is stalemate
        elif result == 'Stalemate' or result == 'Complete':
            self.text_to_screen(result, (pos_col+0.45) * TILESIZE, (pos_row+0.1 )* TILESIZE, size=60, colour=WHITE)
        else:
            self.text_to_screen(result, (pos_col + 1) * TILESIZE, (pos_row + 0.1) * TILESIZE, size=80, colour=WHITE)

    #draws the box with piece value at end of the game
    def draw_player_value(self, player_value, pos_col, pos_row, colour):
        if colour == WHITE:
            opposite_colour = BLACK
            text = 'White Piece'
            colour = LIGHT_GREY
        else:
            opposite_colour = LIGHT_GREY
            text = 'Black Piece'
        rect = (pos_col * TILESIZE, pos_row * TILESIZE, TILESIZE * 3.5, TILESIZE * 2.5)
        rect2 = ((pos_col-0.25) * TILESIZE, (pos_row-0.25) * TILESIZE, TILESIZE * 4, TILESIZE * 3)
        pg.draw.rect(self.screen, opposite_colour, rect2)
        pg.draw.rect(self.screen, colour, rect)
        self.text_to_screen(text, pos_col * TILESIZE, (pos_row+0.4) * TILESIZE, size=30, colour=opposite_colour)
        self.text_to_screen('Value:'+ player_value, pos_col * TILESIZE, (pos_row + 1.4) * TILESIZE, size=30, colour=opposite_colour)

    #handles the game over screen events
    def game_over_events(self):
        for event in pg.event.get():
            #if mouse button clicked
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos_x, mouse_pos_y = event.pos
                clicked_row = mouse_pos_y // TILESIZE
                clicked_col = mouse_pos_x // TILESIZE
                if clicked_row == 8:
                    #if play again button clicked
                    if 4 > clicked_col > 0:
                        self.playing = True
                        self.game_over = False
                        self.show_game_menu = False
                    #if menu screen button clicked
                    elif 5 < clicked_col < 8:
                        self.show_game_menu = True
                        self.game_over = False
                        self.running = False

            #if close window
            if event.type == pg.QUIT:
                pg.quit()

    #Draws the single and two player game mode selection
    def draw_game_menu(self):
        #draws background
        for i in range(0, 10):
            for j in range(0, 10):
                if (i + j) % 2 == 0:
                    colour = WHITE
                else:
                    colour = DARK_GREY
                if j != 9:
                    rect = (i * TILESIZE, j * TILESIZE, TILESIZE, TILESIZE)
                    pg.draw.rect(self.screen, colour, rect)
                else:
                    rect = (i * TILESIZE, j * TILESIZE, TILESIZE*0.3, TILESIZE)
                    pg.draw.rect(self.screen, colour, rect)
        self.draw_menu_title(1, 2, TITLE)
        #draw select two players button
        self.draw_game_menu_button(4, 5.25, TWO_PLAYER, 'Two Player', 'Game')
        #draw select one player button
        self.draw_game_menu_button(4, 0.75, ONE_PLAYER, 'One Player', 'Game')
        pg.display.flip()

    #draws the game selection buttons
    def draw_game_menu_button(self, pos_row, pos_col, colour, first_line, second_line, text_colour=BLACK, bool=True):
        rect = ((pos_col-0.25) * TILESIZE, (pos_row -0.25)* TILESIZE, TILESIZE*3.5, TILESIZE*2.5)
        pg.draw.rect(self.screen, BLACK, rect)
        rect = (pos_col * TILESIZE, pos_row * TILESIZE, TILESIZE*3, TILESIZE*2)
        pg.draw.rect(self.screen, colour, rect)
        self.text_to_screen(first_line, pos_col*TILESIZE, pos_row*TILESIZE, size=30, colour=text_colour)
        if bool:
            pos_col += 1
        self.text_to_screen(second_line,pos_col*TILESIZE , (pos_row+1)*TILESIZE, size=30, colour=text_colour)

    #draws the title for menu screens
    def draw_menu_title(self, position_row, position_col, title, colour=WHITE):
        rect = (position_col * TILESIZE, position_row * TILESIZE, TILESIZE*5, TILESIZE)
        pg.draw.rect(self.screen, BLACK, rect)
        if title == TITLE:
            self.text_to_screen(title, (position_col+0.1) * TILESIZE, (position_row+0.1) * TILESIZE, size = 50, colour=colour)
        else:
            self.text_to_screen(title, (position_col+0.45) * TILESIZE, (position_row + 0.1) * TILESIZE, size=50, colour=colour)

    #handles the two and one player selection menu events
    def game_menu_events(self):
        for event in pg.event.get():
            #event: mouse click
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos_x, mouse_pos_y = event.pos
                clicked_row = mouse_pos_y // TILESIZE
                clicked_col = mouse_pos_x // TILESIZE
                if clicked_row == 4 or 5:
                    #if one player selection button clicked
                    if 4 > clicked_col > 0:
                        self.one_player = True
                        self.show_game_menu = False
                    #if two player selection button clickd
                    elif 5 < clicked_col < 8:
                        self.playing = True
                        self.show_game_menu = False
            #if window exit button clicked
            if event.type == pg.QUIT:
                if self.playing or self.show_game_menu:
                    self.show_game_menu = False
                    self.playing = False
                self.running = False

    #draws a game button
    def draw_button(self, col_pos, row_pos, col_size, row_size, colour, text, text_colour, text_size=50):
        rect = (col_pos * 63.5, row_pos * 64.5, col_size*TILESIZE, row_size*54)
        pg.draw.rect(self.screen, colour, rect)
        self.text_to_screen(text, col_pos*TILESIZE, row_pos*TILESIZE, size=text_size, colour=text_colour)

    #if the undo button clicked
    def press_undo_button(self):
        if self.previous_moves:
            self.board = self.previous_moves[-1].board
            if self.previous_moves[-1].colour != self.player:
                self.player_turn()
            self.previous_moves.pop()

#Game against bot
class One_Player_Game(Game):

    #initialise subclass attributes
    def __init__(self, screen, running, clock, playing):

        super().__init__(screen, running, clock, playing)
        self.screen = screen
        pg.font.init()
        self.clock = clock
        self.player = WHITE
        self.running = running
        self.playing = playing
        self.board = Board()
        self.temp_board = None
        self.Piece_Grabber = Piece_Grabber()
        self.previous_moves = []
        self.Ai_Player = Chess_Bot(self.get_random_colour(), self.board)
        self.game_over = False
        self.start_tick = 0
        self.difficulty = 0
        self.show_diff_men = False

    #runs single player game
    def run(self):
        #select bot difficulty
        self.difficulty_menu()
        if self.get_draw:
            #assign start tick
            self.start_tick = pg.time.get_ticks()
        # game loop
        while self.playing:
            if self.Ai_Player.colour == self.player:
                #handles the bot moves
                self.Ai_events()
            else:
                #handles the player moves
                self.events()
            #draws everything for the game
            self.draw()
        #reset start tick
        self.start_tick = 0

    #handles the player move/turn events
    def events(self):
        #if draw
        if self.game_draw and not self.get_draw:
            #assign the black piece value
            self.black_board_val = self.Chess_bot.evaluate_piece_value(self.board, BLACK) // 100
            self.black_board_val = self.black_board_val - 100
            #assign the white piece value
            self.white_board_val = self.Chess_bot.evaluate_piece_value(self.board, WHITE) // 100
            self.white_board_val = self.white_board_val - 100
            #asign game result
            self.result = 'DRAW'
            self.game_over = True
            self.playing = False
            self.game_draw = False
        #if checkmate
        if not self.board.has_legal_moves(self.player) and self.board.in_check(self.player, copy.deepcopy(self.board)):
            #assigns which player wins
            if self.player == BLACK:
                self.player_result = 'White'
            else:
                self.player_result = 'Black'
            #assign the black piece value
            self.black_board_val = self.Chess_bot.evaluate_piece_value(self.board, BLACK) // 100
            self.black_board_val = self.black_board_val - 100
            #assign the white piece value
            self.white_board_val = self.Chess_bot.evaluate_piece_value(self.board, WHITE) // 100
            self.white_board_val = self.white_board_val - 100
            #assign game result
            self.result = 'Checkmate'
            self.game_over = True
            self.playing = False
        # checks for stalemate
        elif not self.board.has_legal_moves(self.player):
            #assigns black board piece value
            self.black_board_val = self.Chess_bot.evaluate_piece_value(self.board, BLACK) // 100
            self.black_board_val = self.black_board_val - 100
            #assigns white board piece value
            self.white_board_val = self.Chess_bot.evaluate_piece_value(self.board, WHITE) // 100
            self.white_board_val = self.white_board_val - 100
            #assign game result
            self.result = 'Stalemate'
            self.game_over = True
            self.playing = False

        for event in pg.event.get():
            # event: mouse click
            if event.type == pg.MOUSEBUTTONDOWN:
                self.Piece_Grabber.update_mouse(event.pos)

                clicked_row = self.Piece_Grabber.MouseY // TILESIZE
                clicked_col = self.Piece_Grabber.MouseX // TILESIZE
                # checks to see if a move was clicked
                if clicked_col == 8 and clicked_row != 8:
                    self.undo_move(clicked_row)
                #checks if the undo button is clicked
                elif clicked_row == 8 and (clicked_col == 7 or clicked_col == 8):
                    self.press_undo_button()
                #checks if draw button is clicked
                elif clicked_row == 8 and (clicked_col == 0 or clicked_col == 1):
                    self.get_draw = True
                    self.get_draw_events(clicked_row, clicked_col)
                #text box clicked
                elif clicked_row == 8 and 2.4 < clicked_col < 6.4:
                    self.t_box_active = not self.t_box_active
                # does clicked square have a piece
                elif self.board.squares[clicked_row][clicked_col].has_piece():
                    piece = self.board.squares[clicked_row][clicked_col].piece
                    # check valid player turn
                    if piece.colour == self.player:
                        #calculates legal moves of the piece in that square
                        self.board.calculate_moves(piece, clicked_row, clicked_col, bool=True)
                        self.Piece_Grabber.save_initial_pos(event.pos)
                        #assigns piece as holding
                        self.Piece_Grabber.Grab_Piece(piece)

            elif event.type == pg.MOUSEMOTION:
                if self.Piece_Grabber.Holding:
                    #if mouse is moving and piece is being held
                    self.Piece_Grabber.update_mouse(event.pos)
                    self.Piece_Grabber.update_grabber(self.screen)

            elif event.type == pg.MOUSEBUTTONUP:
                if self.Piece_Grabber.Holding:
                    #if mouse button up and mouse is holding piece
                    self.Piece_Grabber.update_mouse(event.pos)
                    #create row and col postion of move
                    released_row = self.Piece_Grabber.MouseY // TILESIZE
                    released_col = self.Piece_Grabber.MouseX // TILESIZE
                    #create move
                    initial = Square(self.Piece_Grabber.initial_row, self.Piece_Grabber.initial_col)
                    final = Square(released_row, released_col)
                    move = Move(initial, final, self.Piece_Grabber.piece)
                    #if valid move
                    if self.board.valid_move(self.Piece_Grabber.piece, move):
                        #add move to previous moves
                        self.add_move_to_stack(self.Piece_Grabber.piece, move)
                        #make the move on the board
                        self.board.move(self.Piece_Grabber.piece, move)
                        #next players turn
                        self.player_turn()

                    self.Piece_Grabber.UnGrab_Piece()


                elif self.temp_board:
                    #if showing previous board state then redo move
                    self.redo_move()

            elif event.type == pg.KEYDOWN:
                if self.t_box_active:
                    #if text box is active and a key is clicked
                    self.text_box_event(event, self.player)

            if event.type == pg.QUIT:
                pg.quit()

    #handles the bot move/turn events
    def Ai_events(self):
        #if draw
        if self.game_draw and not self.get_draw:
            #assign black piece value
            self.black_board_val = self.Chess_bot.evaluate_piece_value(self.board, BLACK) // 100
            self.black_board_val = self.black_board_val - 100
            #assign white piece value
            self.white_board_val = self.Chess_bot.evaluate_piece_value(self.board, WHITE) // 100
            self.white_board_val = self.white_board_val - 100
            self.result = 'DRAW'
            self.game_over = True
            self.playing = False
        #makes move on board
        ai_move = self.Ai_Player.make_move(self.board, difficulty=self.difficulty)
        if ai_move is None:
            #if checkmate
            if self.board.in_check(self.Ai_Player.colour, self.board):
                #assigns the winning colour
                if self.Ai_Player.colour == BLACK:
                    self.player_result = 'White'
                else:
                    self.player_result = 'Black'
                # assign black piece value
                self.black_board_val = self.Chess_bot.evaluate_piece_value(self.board, BLACK) // 100
                self.black_board_val = self.black_board_val - 100
                # assign white piece value
                self.white_board_val = self.Chess_bot.evaluate_piece_value(self.board, WHITE) // 100
                self.white_board_val = self.white_board_val - 100
                self.result = 'Checkmate'
                self.game_over = True
                self.playing = False
            #if stalemate
            else:
                # assign black piece value
                self.black_board_val = self.Chess_bot.evaluate_piece_value(self.board, BLACK) // 100
                self.black_board_val = self.black_board_val - 100
                # assign white piece value
                self.white_board_val = self.Chess_bot.evaluate_piece_value(self.board, WHITE) // 100
                self.white_board_val = self.white_board_val - 100
                self.result = 'Stalemate'
                self.game_over = True
                self.playing = False
        else:
            #add the bots move to previous move
            self.add_move_to_stack(ai_move.moved_piece, ai_move, bool=False)
        #switch the player turn
        self.player_turn()


        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()

    #handles the events when draw button clicked
    def get_draw_events(self, clicked_row, clicked_col):
        #evaluate board value
        board_val = self.Ai_Player.evaluate_material(self.board, self.Ai_Player.colour)
        if 0 >= board_val:
            self.game_draw = True
        else:
            self.get_draw = False

    #show whether the bot agrees to draw
    def show_get_draw(self):
        rect = (0.5 * TILESIZE, 2.5 *TILESIZE, TILESIZE * 7, TILESIZE * 4)
        pg.draw.rect(self.screen, BLACK, rect)
        if self.game_draw:
            decision = 'Agreed'
        else:
            decision = 'Disagreed'
        if self.Ai_Player.colour == BLACK:
            name = 'Black'
        else:
            name = 'White'
        self.text_to_screen(name+' has '+decision, 1.1*TILESIZE, 3*TILESIZE, size=40)
        self.text_to_screen('to the Draw', 1.1 * TILESIZE, 4 * TILESIZE, size=40)

    #returns either black or white randomly
    def get_random_colour(self):
        number = random.randint(1, 2)
        if number == 1:
            return WHITE
        else:
            return BLACK

    #if undo button clicked
    def press_undo_button(self):
        if not self.player == self.Ai_Player.colour and self.previous_moves:
            self.board = self.previous_moves[-2].board
            if len(self.previous_moves) > 1:
                #pop both player and bot move
                for i in range (0,2):
                    self.previous_moves.pop()

    #runs the get diffcultty menu
    def difficulty_menu(self):
        self.show_diff_men = True
        self.difficulty = 0
        #show diff menu loop
        while self.show_diff_men:
            self.diff_menu_events()
            self.draw_diff_menu()

    #draws the difficulty menu
    def draw_diff_menu(self):
        #draw the background grid
        for i in range(0, 10):
            for j in range(0, 10):
                if (i + j) % 2 == 0:
                    colour = WHITE
                else:
                    colour = DARK_GREY
                if j != 9:
                    rect = (i * TILESIZE, j * TILESIZE, TILESIZE, TILESIZE)
                    pg.draw.rect(self.screen, colour, rect)
                else:
                    rect = (i * TILESIZE, j * TILESIZE, TILESIZE * 0.3, TILESIZE)
                    pg.draw.rect(self.screen, colour, rect)
        self.draw_menu_title(1, 2, TITLE)
        self.draw_game_menu_button(3, 5.25, ORANGE, 'Difficulty:', 'Medium')
        self.draw_game_menu_button(3, 0.75, GREEN, 'Difficulty:', 'Easy')
        self.draw_game_menu_button(6, 3, DARK_RED, 'Difficulty:', 'Hard')
        pg.display.flip()

    #handles the difficulty menu events
    def diff_menu_events(self):
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos_x, mouse_pos_y = event.pos
                clicked_row = mouse_pos_y // TILESIZE
                clicked_col = mouse_pos_x // TILESIZE
                if 4>= clicked_row >=3:
                    #if easy difficulty button clicked
                    if 0.75 <= clicked_col <= 3.75:
                        self.difficulty = 1
                        self.show_diff_men = False
                    #if medium difficulty button clicked
                    elif 5.25 <= clicked_col <= 8.25:
                        self.difficulty = 2
                        self.show_diff_men = False
                #if hard difficulty button clicked
                elif clicked_row == 6:
                    if 3 <= clicked_col <= 6:
                        self.difficulty = 3
                        self.show_diff_men = False
            if event.type == pg.QUIT:
                pg.quit()

#Practice game against bot with move hints
class Practice_Game(Game):

    #initialize game attributes
    def __init__(self, screen, running, clock, playing):
        super().__init__(screen, running, clock, playing)
        self.start_tick = 0
        self.Ai_Player = self.Chess_bot
        self.Ai_Player.colour = self.get_random_colour()
        self.move_hint = None
        self.chess_comp = False

    #run practice game
    def run(self):
        if self.get_draw:
            #assign start tick
            self.start_tick = pg.time.get_ticks()
        #practice game loop
        while self.playing:
            if self.Ai_Player.colour == self.player:
                #bot player turn
                self.Ai_events()
            else:
                #player turn
                self.events()
            #draw the practice game
            self.draw()
        #reset start tick
        self.start_tick = 0

    #draws the practice game
    def draw(self):
        self.screen.fill(BLACK)
        #draw board squares
        self.draw_grid()
        self.draw_coordinates()
        #show the last move made on the board
        self.show_last_move()
        if self.move_hint is not None:
            #if hint button has been clicked then show_move_hint
            self.show_move_hint()
        if self.Piece_Grabber.Holding:
            #show the possible legal moves of a piece being held
            self.show_possible_moves()
        self.show_pieces(self.screen)
        if self.previous_moves:
            self.show_previous_moves()
        self.draw_button(7.2, 8.275, 2, 0.70, RED, 'UNDO', BLACK)
        self.draw_button(0.1, 8.275, 2, 0.70, RED, 'DRAW', BLACK)
        self.draw_button(5.1, 8.275, 1.9, 0.7, LIGHT_GREY, 'HINT', BLACK)
        self.draw_button(2.35 , 8.275, 2.5, 0.70, WHITE, self.move_in_chess_notation, BLACK)
        if self.get_draw:
            #show whether bot agrees to a draw
            if self.start_tick == 0:
                self.start_tick = pg.time.get_ticks()
            seconds = (pg.time.get_ticks() - self.start_tick) / 1000
            self.show_get_draw()
            if seconds > 3:
                self.get_draw = False
        pg.display.flip()

    #shows the board squares
    def draw_grid(self):
        for i in range (0,8):
            for j in range (0,8):
                if (i+j) % 2 == 0:
                    colour = GREEN
                else:
                    colour = DARK_GREEN
                rect = (i * TILESIZE, j * TILESIZE, TILESIZE, TILESIZE)
                pg.draw.rect(self.screen, colour, rect)

    #handles player events
    def events(self):
        # if draw
        if self.game_draw and not self.get_draw:
            # assign the black piece value
            self.black_board_val = self.Chess_bot.evaluate_piece_value(self.board, BLACK) // 100
            self.black_board_val = self.black_board_val - 100
            # assign the white piece value
            self.white_board_val = self.Chess_bot.evaluate_piece_value(self.board, WHITE) // 100
            self.white_board_val = self.white_board_val - 100
            # asign game result
            self.result = 'DRAW'
            self.game_over = True
            self.playing = False
            self.game_draw = False
        # if checkmate
        if not self.board.has_legal_moves(self.player) and self.board.in_check(self.player, copy.deepcopy(self.board)):
            # assigns which player wins
            if self.player == BLACK:
                self.player_result = 'White'
            else:
                self.player_result = 'Black'
            # assign the black piece value
            self.black_board_val = self.Chess_bot.evaluate_piece_value(self.board, BLACK) // 100
            self.black_board_val = self.black_board_val - 100
            # assign the white piece value
            self.white_board_val = self.Chess_bot.evaluate_piece_value(self.board, WHITE) // 100
            self.white_board_val = self.white_board_val - 100
            # assign game result
            self.result = 'Checkmate'
            self.game_over = True
            self.playing = False
        # checks for stalemate
        elif not self.board.has_legal_moves(self.player):
            # assigns black board piece value
            self.black_board_val = self.Chess_bot.evaluate_piece_value(self.board, BLACK) // 100
            self.black_board_val = self.black_board_val - 100
            # assigns white board piece value
            self.white_board_val = self.Chess_bot.evaluate_piece_value(self.board, WHITE) // 100
            self.white_board_val = self.white_board_val - 100
            # assign game result
            self.result = 'Stalemate'
            self.game_over = True
            self.playing = False

        for event in pg.event.get():
            # event: mouse click
            if event.type == pg.MOUSEBUTTONDOWN:
                self.Piece_Grabber.update_mouse(event.pos)

                clicked_row = self.Piece_Grabber.MouseY // TILESIZE
                clicked_col = self.Piece_Grabber.MouseX // TILESIZE
                # checks to see if a move was clicked
                if clicked_col == 8 and clicked_row != 8:
                    self.undo_move(clicked_row)
                # checks if the undo button is clicked
                elif clicked_row == 8 and (clicked_col == 7 or clicked_col == 8):
                    self.press_undo_button()
                # checks if draw button is clicked
                elif clicked_row == 8 and (clicked_col == 0 or clicked_col == 1):
                    self.get_draw = True
                    self.get_draw_events(clicked_row, clicked_col)
                # text box clicked
                elif clicked_row == 8 and 2.4 < clicked_col < 5:
                    self.t_box_active = not self.t_box_active
                #if hint button clicked
                elif clicked_row == 8 and (5 == clicked_col or clicked_col  == 6):
                    self.move_hint = self.Ai_Player.find_best_moves(copy.deepcopy(self.board), self.player)
                # does clicked square have a piece
                elif self.board.squares[clicked_row][clicked_col].has_piece():
                    piece = self.board.squares[clicked_row][clicked_col].piece
                    # check valid player turn
                    if piece.colour == self.player:
                        # calculates legal moves of the piece in that square
                        self.board.calculate_moves(piece, clicked_row, clicked_col, bool=True)
                        self.Piece_Grabber.save_initial_pos(event.pos)
                        # assigns piece as holding
                        self.Piece_Grabber.Grab_Piece(piece)

            elif event.type == pg.MOUSEMOTION:
                if self.Piece_Grabber.Holding:
                    # if mouse is moving and piece is being held
                    self.Piece_Grabber.update_mouse(event.pos)
                    self.Piece_Grabber.update_grabber(self.screen)

            elif event.type == pg.MOUSEBUTTONUP:
                if self.Piece_Grabber.Holding:
                    # if mouse button up and mouse is holding piece
                    self.Piece_Grabber.update_mouse(event.pos)
                    # create row and col postion of move
                    released_row = self.Piece_Grabber.MouseY // TILESIZE
                    released_col = self.Piece_Grabber.MouseX // TILESIZE
                    # create move
                    initial = Square(self.Piece_Grabber.initial_row, self.Piece_Grabber.initial_col)
                    final = Square(released_row, released_col)
                    move = Move(initial, final, self.Piece_Grabber.piece)
                    # if valid move
                    if self.board.valid_move(self.Piece_Grabber.piece, move):
                        # add move to previous moves
                        self.add_move_to_stack(self.Piece_Grabber.piece, move)
                        # make the move on the board
                        self.board.move(self.Piece_Grabber.piece, move)
                        #reset move hint
                        self.move_hint = None
                        # next players turn
                        self.player_turn()

                    self.Piece_Grabber.UnGrab_Piece()


                elif self.temp_board:
                    # if showing previous board state then redo move
                    self.redo_move()

            elif event.type == pg.KEYDOWN:
                if self.t_box_active:
                    # if text box is active and a key is clicked
                    self.text_box_event(event, self.player)

            if event.type == pg.QUIT:
                pg.quit()

    #handles the bot events
    def Ai_events(self):
        # if draw
        if self.game_draw and not self.get_draw:
            # assign black piece value
            self.black_board_val = self.Chess_bot.evaluate_piece_value(self.board, BLACK) // 100
            self.black_board_val = self.black_board_val - 100
            # assign white piece value
            self.white_board_val = self.Chess_bot.evaluate_piece_value(self.board, WHITE) // 100
            self.white_board_val = self.white_board_val - 100
            self.result = 'DRAW'
            self.game_over = True
            self.playing = False
        # makes move on board
        ai_move = self.Ai_Player.make_move(self.board)
        if ai_move is None:
            # if checkmate
            if self.board.in_check(self.Ai_Player.colour, self.board):
                # assigns the winning colour
                if self.Ai_Player.colour == BLACK:
                    self.player_result = 'White'
                else:
                    self.player_result = 'Black'
                # assign black piece value
                self.black_board_val = self.Chess_bot.evaluate_piece_value(self.board, BLACK) // 100
                self.black_board_val = self.black_board_val - 100
                # assign white piece value
                self.white_board_val = self.Chess_bot.evaluate_piece_value(self.board, WHITE) // 100
                self.white_board_val = self.white_board_val - 100
                self.result = 'Checkmate'
                self.game_over = True
                self.playing = False
            # if stalemate
            else:
                # assign black piece value
                self.black_board_val = self.Chess_bot.evaluate_piece_value(self.board, BLACK) // 100
                self.black_board_val = self.black_board_val - 100
                # assign white piece value
                self.white_board_val = self.Chess_bot.evaluate_piece_value(self.board, WHITE) // 100
                self.white_board_val = self.white_board_val - 100
                self.result = 'Stalemate'
                self.game_over = True
                self.playing = False
        else:
            # add the bots move to previous move
            self.add_move_to_stack(ai_move.moved_piece, ai_move, bool=False)
        # switch the player turn
        self.player_turn()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()

    #gets whether bot agrees to draw
    def get_draw_events(self, clicked_row, clicked_col):
        #evaluate the board value
        board_val = self.Ai_Player.evaluate_material(self.board, self.Ai_Player.colour)
        if 0 >= board_val:
            self.game_draw = True
        else:
            print('draw = False')
            self.get_draw = False

    #draws the bots decision on whether agree to draw
    def show_get_draw(self):
        rect = (0.5 * TILESIZE, 2.5 * TILESIZE, TILESIZE * 7, TILESIZE * 4)
        pg.draw.rect(self.screen, BLACK, rect)
        if self.game_draw:
            decision = 'Agreed'
        else:
            decision = 'Disagreed'
        if self.Ai_Player.colour == BLACK:
            name = 'Black'
        else:
            name = 'White'
        self.text_to_screen(name + ' has ' + decision, 1.1 * TILESIZE, 3 * TILESIZE, size=40)
        self.text_to_screen('to the Draw', 1.1 * TILESIZE, 4 * TILESIZE, size=40)

    #shows the move hint suggested by bot
    def show_move_hint(self):
        rect = (self.move_hint.final.col * TILESIZE, self.move_hint.final.row * TILESIZE, TILESIZE, TILESIZE)
        rect2 = (self.move_hint.initial.col * TILESIZE, self.move_hint.initial.row * TILESIZE, TILESIZE, TILESIZE)
        pg.draw.rect(self.screen, DARK_BLUE, rect)
        pg.draw.rect(self.screen, DARK_BLUE, rect2)

    #returns either white or black randomly
    def get_random_colour(self):
        number = random.randint(1, 2)
        if number == 1:
            return WHITE
        else:
            return BLACK

    #undoes the last to moves if undo button clicked
    def press_undo_button(self):
        if not self.player == self.Ai_Player.colour and self.previous_moves:
            self.board = self.previous_moves[-2].board
            if len(self.previous_moves) > 1:
                for i in range(0, 2):
                    self.previous_moves.pop()

    #draws the practice or puzzle menu
    def draw_training_game_menu(self):
        #draw background grid left side
        for i in range(0, 5):
            for j in range(0, 10):
                if i < 4:
                    if (i + j) % 2 == 0:
                        colour = GREEN
                    else:
                        colour = DARK_GREEN
                    rect = (i * TILESIZE, j * TILESIZE, TILESIZE, TILESIZE)
                    pg.draw.rect(self.screen, colour, rect)
                else:
                    #draw black line in the middle
                    rect = (i * TILESIZE, j * TILESIZE, TILESIZE, TILESIZE)
                    pg.draw.rect(self.screen, BLACK, rect)
        #draw right side background
        for i in range(0, 5):
            for j in range(0, 10):
                if i < 4:
                    if (i + j) % 2 == 0:
                        colour = BLUE
                    else:
                        colour = DARK_BLUE
                    rect = ((i + 5) * TILESIZE, j * TILESIZE, TILESIZE, TILESIZE)
                    pg.draw.rect(self.screen, colour, rect)
                else:
                    #fill gap on right side
                    rect = ((i + 5) * TILESIZE, j * TILESIZE, TILESIZE * 0.3, TILESIZE)
                    pg.draw.rect(self.screen, LIGHT_GREY, rect)
        self.draw_menu_title(1, 2, TITLE)
        self.draw_game_menu_button(4, 0.5, DARK_BLUE, ' Practice', 'Game', text_colour=DARK_GREEN)
        self.draw_game_menu_button(4, 5.5, DARK_GREEN, '  Chess', '  Puzzle', text_colour=DARK_BLUE, bool=False)
        pg.display.flip()

    #handles events for practice or puzzle menu
    def training_game_menu_events(self):
        for event in pg.event.get():
            # event: mouse click
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos_x, mouse_pos_y = event.pos
                clicked_row = mouse_pos_y // TILESIZE
                clicked_col = mouse_pos_x // TILESIZE
                if clicked_row == 4 or 5:
                    if 4 > clicked_col > 0:
                        #if practice game selected
                        self.playing = True
                        self.show_game_menu = False
                    elif 5 < clicked_col < 8:
                        #if chess puzzle selected
                        self.chess_comp = True
                        self.show_game_menu = False

            if event.type == pg.QUIT:
                if self.playing or self.show_game_menu:
                    self.show_game_menu = False
                    self.playing = False
                self.running = False

#Chess puzzles with 3 live and hints
class Chess_Compositions(Game):

    #initiliaze the chess puzzle attributes
    def __init__(self, screen, running, clock, playing):
        super().__init__(screen, running, clock, playing)
        self.expected_moves = []
        self.player_colour = None
        self.lives = 3
        self.hints = 3
        self.move_hint = None

    #runs a chess puzzle
    def run(self):
        #gets a random chess puzzle
        self.get_chess_comp()
        #game loop
        while self.playing:
            if self.player_colour == self.player:
                #player events
                self.events()
            else:
                #makes the response in the sequence of moves
                self.make_move_response()
            self.draw()

    #handles game events
    def events(self):
        for event in pg.event.get():
            # event: mouse click
            if event.type == pg.MOUSEBUTTONDOWN:
                self.Piece_Grabber.update_mouse(event.pos)

                clicked_row = self.Piece_Grabber.MouseY // TILESIZE
                clicked_col = self.Piece_Grabber.MouseX // TILESIZE
                # checks to see if a move was clicked
                if clicked_col == 8 and clicked_row != 8:
                    self.undo_move(clicked_row)
                #if hint button clicked
                elif clicked_row == 8 and (clicked_col == 7 or clicked_col == 8) and self.hints > 0:
                    self.move_hint = self.convert_chess_notation_into_move(self.expected_moves[0], self.player_colour)
                    self.hints = self.hints - 1
                #if textbox is clicked
                elif clicked_row == 8 and 2.4 < clicked_col < 6.4:
                    self.t_box_active = not self.t_box_active
                # does clicked square have a piece
                elif self.board.squares[clicked_row][clicked_col].has_piece():
                    piece = self.board.squares[clicked_row][clicked_col].piece
                    # check valid player turn
                    if piece.colour == self.player:
                        #calculates the legal moves of the clicked piece
                        self.board.calculate_moves(piece, clicked_row, clicked_col, bool=True)
                        self.Piece_Grabber.save_initial_pos(event.pos)
                        #sets clicked piece to being held by mouse
                        self.Piece_Grabber.Grab_Piece(piece)

            elif event.type == pg.MOUSEMOTION:
                if self.Piece_Grabber.Holding:
                    #if a piece is being held and the mouse is holding a piece
                    self.Piece_Grabber.update_mouse(event.pos)
                    self.Piece_Grabber.update_grabber(self.screen)

            elif event.type == pg.MOUSEBUTTONUP:

                if self.Piece_Grabber.Holding:
                    self.Piece_Grabber.update_mouse(event.pos)

                    released_row = self.Piece_Grabber.MouseY // TILESIZE
                    released_col = self.Piece_Grabber.MouseX // TILESIZE
                    #create move
                    initial = Square(self.Piece_Grabber.initial_row, self.Piece_Grabber.initial_col)
                    final = Square(released_row, released_col)
                    move = Move(initial, final, self.Piece_Grabber.piece)

                    if self.board.valid_move(self.Piece_Grabber.piece, move):
                        if self.expected_moves:
                            if self.expected_moves[0] == self.convert_move_into_chess_notation(self.Piece_Grabber.piece, move.initial, move.final):
                                #if player move is a legal move and is the expected move
                                #add move to previous moves
                                self.add_move_to_stack(self.Piece_Grabber.piece, move)
                                #move piece on board
                                self.board.move(self.Piece_Grabber.piece, move)
                                #reset move hint
                                self.move_hint = None
                                #dequeue an item from expected moves
                                self.expected_moves.pop(0)
                                #switch the player turn
                                self.player_turn()

                            else:
                                #if not expected move take away a life
                                self.lives = self.lives - 1


                        # checks for lost all lives
                        if self.lives == 0:
                            #evaluate black piece value
                            self.black_board_val = self.Chess_bot.evaluate_piece_value(self.board, BLACK) // 100
                            self.black_board_val = self.black_board_val - 100
                            #evaluate white piece value
                            self.white_board_val = self.Chess_bot.evaluate_piece_value(self.board, WHITE) // 100
                            self.white_board_val = self.white_board_val - 100
                            #assign how game ended
                            self.result = 'FAIL...'
                            self.game_over = True
                            self.playing = False



                        # checks for if complete
                        elif not self.expected_moves and self.lives > 0:
                            #evaluate the black piece value
                            self.black_board_val = self.Chess_bot.evaluate_piece_value(self.board, BLACK) // 100
                            self.black_board_val = self.black_board_val - 100
                            #evaluate the white piece value
                            self.white_board_val = self.Chess_bot.evaluate_piece_value(self.board, WHITE) // 100
                            self.white_board_val = self.white_board_val - 100
                            #assign how game ended
                            self.result = 'Complete'
                            self.game_over = True
                            self.playing = False
                    #sets piece to not being held
                    self.Piece_Grabber.UnGrab_Piece()


                elif self.temp_board:
                    #if viewing previous board state, redo move
                    self.redo_move()

            elif event.type == pg.KEYDOWN:
                if self.t_box_active:
                    self.text_box_event(event, self.player)

            if event.type == pg.QUIT:
                pg.quit()

    #draws the game screen
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
        lives = 'Lives:'+str(self.lives)
        hints = 'HINT:'+str(self.hints)
        self.draw_button(6.55, 8.275, 2.5, 0.70, LIGHT_GREY, hints, BLACK, text_size=35)
        self.draw_button(0.3, 8.275, 3, 0.70, RED, lives, BLACK, text_size=40)
        self.draw_button(3.55, 8.275, 2.75, 0.70, WHITE, self.move_in_chess_notation, BLACK)
        pg.display.flip()

    #draws the board squares
    def draw_grid(self):
        for i in range(0, 8):
            for j in range(0, 8):
                if (i + j) % 2 == 0:
                    colour = BLUE
                else:
                    colour = DARK_BLUE
                rect = (i * TILESIZE, j * TILESIZE, TILESIZE, TILESIZE)
                pg.draw.rect(self.screen, colour, rect)

    #show the possible moves of a held piece
    def show_possible_moves(self):
        if self.Piece_Grabber.Holding:
            piece = self.Piece_Grabber.piece
            for move in piece.moves:
                if (move.final.row + move.final.col) % 2 == 0:
                    colour = LIGHT_GREY
                else:
                    colour = GREY
                rect = (move.final.col * TILESIZE, move.final.row * TILESIZE, TILESIZE, TILESIZE)
                pg.draw.rect(self.screen, colour, rect)
            if piece.moves:
                initial = piece.moves[0].initial
                if (initial.row + initial.col) % 2 != 0:
                    colour = GREY
                else:
                    colour = LIGHT_GREY
                rect = (initial.col * TILESIZE, initial.row * TILESIZE, TILESIZE, TILESIZE)
                pg.draw.rect(self.screen, colour, rect)

    #gets a random txt file that contains a chess puzzle
    def get_chess_comp(self):
        chess_note = ''
        moves = []
        squares =  [[0,0,0,0,0,0,0,0] for col in range(COLS)]
        #creates and adds squares to the board
        squares = self.create_board_state(squares)
        num = random.randint(1, 17)
        num = str(num)
        #the random file generated
        file = 'chess_comp'+num+'.txt'
        file = os.path.join(f'Chess_Comp/'+file)
        #open txt file
        chess_comp = open(file, 'r')
        count = 0
        for line in chess_comp:
            if count < 8:
                for i in range (0,8):
                    pos = i * 2 # times i by 2 as the actual length of line is 16
                    if line[pos] == 'B':
                        squares = self.add_piece(squares, BLACK, line[pos+1], count, i)
                    else:
                        squares = self.add_piece(squares, WHITE, line[pos+1], count, i)
            else:
                for char in line:
                    if char == ',' and chess_note == '':
                        #if black to move
                        self.player_colour = BLACK
                        self.player = BLACK
                    elif char == ',':
                        moves.append(chess_note)
                        chess_note = ''
                    else:
                        chess_note += char
            count += 1
        if self.player_colour is None:
            #if the colour wasn't assign then white to move
            self.player_colour = WHITE
        #assigns the new list of squares
        self.board.squares = squares
        #assign the list of the expected moves
        self.expected_moves = moves
        #close the file
        chess_comp.close()

    #makes the response in the move order
    def make_move_response(self):
        if self.expected_moves:
            if self.player_colour == WHITE:
                move = self.convert_chess_notation_into_move(self.expected_moves[0], BLACK)
                if move:
                    piece = self.board.squares[move.initial.row][move.initial.col].piece
                    if self.board.valid_move(piece, move):
                        #add move to previous moves
                        self.add_move_to_stack(piece, move)
                        #make move on the board
                        self.board.move(piece, move)
                        #next player turn
                        self.player_turn()
                        #dequeue expected move
                        self.expected_moves.pop(0)
                self.move_in_chess_notation = ''
            else:
                move = self.convert_chess_notation_into_move(self.expected_moves[0], WHITE)
                if move:
                    piece = move.moved_piece
                    if self.board.valid_move(piece, move):
                        #add move to previous moves
                        self.add_move_to_stack(piece, move)
                        #make move on board
                        self.board.move(piece, move)
                        #next player turn
                        self.player_turn()
                        #dequeue expected move
                        self.expected_moves.pop(0)
                self.move_in_chess_notation = ''
        else:
            self.game_over = True

    #shows the suggested move by the bot
    def show_move_hint(self):
        rect = (self.move_hint.final.col * TILESIZE, self.move_hint.final.row * TILESIZE, TILESIZE, TILESIZE)
        rect2 = (self.move_hint.initial.col * TILESIZE, self.move_hint.initial.row * TILESIZE, TILESIZE, TILESIZE)
        pg.draw.rect(self.screen, RED, rect)
        pg.draw.rect(self.screen, RED, rect2)

    #creates a 2d list of squares
    def create_board_state(self, squares):
        for row in range (ROWS):
            for col in range (COLS):
                squares[row][col] = Square(row, col)
        return squares

    #adds the pieces to the squares after reading txt file
    def add_piece(self, squares, colour, piece_letter, row, col):
        if piece_letter == 'P':
            if colour == BLACK:
                squares[row][col].piece = Pawn(BLACK)
            else:
                squares[row][col].piece = Pawn(WHITE)
        elif piece_letter == 'N':
            if  colour == BLACK:
                squares[row][col].piece = Knight(BLACK)
            else:
                squares[row][col].piece = Knight(WHITE)
        elif piece_letter == 'B':
            if  colour == BLACK:
                squares[row][col].piece = Bishop(BLACK)
            else:
                squares[row][col].piece = Bishop(WHITE)
        elif piece_letter == 'R':
            if  colour == BLACK:
                squares[row][col].piece = Rook(BLACK)
            else:
                squares[row][col].piece = Rook(WHITE)
        elif piece_letter == 'Q':
            if  colour == BLACK:
                squares[row][col].piece = Queen(BLACK)
            else:
                squares[row][col].piece = Queen(WHITE)
        elif piece_letter == 'K':
            if  colour == BLACK:
                squares[row][col].piece = King(BLACK)
            else:
                squares[row][col].piece = King(WHITE)
        return squares

