import copy
from Move import *
from Piece import *
from Square import *


class Board:

    #initialize board attributes
    def __init__(self):
        self.squares = [[0,0,0,0,0,0,0,0] for col in range(COLS)]
        self._create()
        self._add_pieces(WHITE)
        self._add_pieces(BLACK)

    #makes a move on the board
    def move(self, piece, move, testing=False):
        initial = move.initial
        final = move.final
        #set initial square to having no piece
        self.squares[initial.row][initial.col].piece = None
        #adds a captured piece to move
        if self.squares[final.row][final.col].has_enemy_piece(piece.colour):
            move.captured_piece = self.squares[final.row][final.col].piece
            self.squares[final.row][final.col].piece = None
        self.squares[final.row][final.col].piece = piece

        if isinstance(piece, Pawn):
            #check whether pawn has reached final square and promoted to a queen
            self.check_pawn_promotion(piece, final)
            #check for en passant and set captured piece to none
            if self.squares[initial.row][final.col].has_enemy_piece(piece.colour) and not self.squares[initial.row][final.col].has_pawn_moved_twice():
                if isinstance(self.squares[initial.row][final.col].piece, Pawn):
                    self.squares[initial.row][final.col].piece = None

        if isinstance(piece, King):
            #moves rook that is castled
            if self.castling(initial, final) and not testing:
                diff = final.col - initial.col
                rook = piece.left_rook if (diff < 0) else piece.right_rook
                self.move(rook, rook.moves[-1])

        if piece.moved:
            piece.moved_twice = True
        piece.moved = True
        #clears the piece moves list
        piece.clear_moves()

    #checks if move is valid
    def valid_move(self, piece, move):
        return move in piece.moves

    #checks if pawn has reached final square
    def check_pawn_promotion(self, piece, final):
        if final.row == 0 or final.row == 7:
            self.squares[final.row][final.col].piece = Queen(piece.colour)

    #checks if castling by comparing initial and final position
    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2

    #evaluates if a move gives potential check
    def potential_check(self, piece, move):
        temp_piece = copy.deepcopy(piece)
        temp_board = copy.deepcopy(self)
        temp_board.move(temp_piece, move, testing=True)
        move_causes_check = self.in_check(temp_piece.colour, temp_board)
        return move_causes_check

    #evaluates whether colour given is in check
    def in_check(self, colour, board):
        temp_board = board
        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_enemy_piece(colour):
                    p = temp_board.squares[row][col].piece
                    temp_board.calculate_moves(p, row, col, bool = False)
                    for m in p.moves:
                        if isinstance(temp_board.squares[m.final.row][m.final.col].piece, King):

                            return True
        return False

    #evaluates whether the colour given has legal moves
    def has_legal_moves(self, colour):
        has_legal_move = False
        row = 0
        temp_board = copy.deepcopy(self)
        while not has_legal_move and row != 8:
            for col in range(COLS):
                if temp_board.squares[row][col].has_team_piece(colour):
                    p = temp_board.squares[row][col].piece
                    temp_board.calculate_moves(p, row, col)
                    if p.moves:
                        has_legal_move = True
            row = row + 1

        return has_legal_move

    # calculates all possible moves for a given piece
    def calculate_moves(self, piece, row, col, bool=True):
        #handles pawn moves
        def pawn_moves():
            if piece.moved:
                steps = 1
            else:
                steps = 2

            start = row + piece.dir
            end = row + (piece.dir * (1 + steps))
            for move_row in range(start, end, piece.dir):
                if Square.in_range(move_row):
                    if self.squares[move_row][col].isempty():
                        #create move
                        initial = Square(row, col)
                        final = Square(move_row, col)
                        move = Move(initial, final, piece)
                        #check for potential checks
                        if bool:
                            if not self.potential_check(piece, move):
                                #if move doesn't put player moving in check, add move to legal moves
                                piece.add_moves(move)
                        else:
                            #bool so potential check doesn't recurse when calling calculate moves
                            piece.add_moves(move)
                    else:
                        break
                else:
                    break
            #handles pawn captures
            possible_move_row = row + piece.dir
            possible_move_cols = [col - 1, col + 1]
            for possible_move_col in possible_move_cols:
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.colour):
                        #create move
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        move = Move(initial, final, piece)
                        #check for potential checks
                        if bool:
                            if not self.potential_check(piece, move):
                                #if move doesn't put player in check add to piece moves
                                piece.add_moves(move)
                            else: break
                        else:
                            #bool for when potential check called
                            piece.add_moves(move)
                    #handles en passant
                    if possible_move_row == 2 or possible_move_row == 5 :
                        if self.squares[row][possible_move_col].has_enemy_piece(piece.colour):
                            if not self.squares[row][possible_move_col].has_pawn_moved_twice():
                                #create move
                                initial = Square(row, col)
                                final_piece = self.squares[possible_move_row][possible_move_col].piece
                                final = Square(possible_move_row, possible_move_col, final_piece)
                                move = Move(initial, final, piece)
                                if bool:
                                    if not self.potential_check(piece, move):
                                        #if move doesn't put player in check
                                        piece.add_moves(move)
                                else:
                                    piece.add_moves(move)

        #handles the Knight moves
        def knight_moves():
            # 8 possible moves
            possible_moves = [
                (row-2, col+1),
                (row-1, col+2),
                (row+1, col+2),
                (row+2, col+1),
                (row+2, col-1),
                (row+1, col-2),
                (row-1, col-2),
                (row-2, col-1)]
            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.colour):
                    # create new move
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        move = Move(initial, final, piece)
                        if bool:
                            if not self.potential_check(piece, move):
                                #if move doesn't put player in check then add to piece moves
                                piece.add_moves(move)
                            else:
                                break
                        else:
                            piece.add_moves(move)

        #handles moves for pieces moving in a straight line (bishop,rook,queen)
        def straightline_moves(incrs):
            for incr in incrs:
                row_incr, col_incr = incr
                possible_move_row = row + row_incr
                possible_move_col = col + col_incr
                while True :
                    if Square.in_range(possible_move_row, possible_move_col):
                        #create move
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row,possible_move_col, final_piece)
                        move = Move(initial, final, piece)

                        if self.squares[possible_move_row][possible_move_col].isempty():
                            if bool:
                                if not self.potential_check(piece, move):
                                    #if move doesnt put player in check then add move to piece moves
                                    piece.add_moves(move)
                                else:
                                    break
                            else:
                                piece.add_moves(move)

                        elif self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.colour):
                            if bool:
                                if not self.potential_check(piece, move):
                                    # if move doesnt put player in check then add move to piece moves
                                    piece.add_moves(move)
                                else:
                                    break
                            else:
                                piece.add_moves(move)
                            break

                        elif self.squares[possible_move_row][possible_move_col].has_team_piece(piece.colour):
                            break

                    else:
                        break
                    possible_move_row = possible_move_row + row_incr
                    possible_move_col = possible_move_col + col_incr

        #handles the king moves
        def king_moves():
            adjs = [
                (row-1, col+0),
                (row-1, col+1),
                (row+0, col+1),
                (row+1, col+1),
                (row+1, col+0),
                (row+1, col-1),
                (row+0, col-1),
                (row-1, col-1)

            ]

            for possible_move in adjs:
                possible_move_row, possible_move_col = possible_move
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.colour):
                        #create move
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col)
                        move = Move(initial, final, piece)

                        if bool:
                            if not self.potential_check(piece, move):
                                # if move doesnt put player in check then add move to piece moves
                                piece.add_moves(move)
                        else:
                            piece.add_moves(move)
            if not piece.moved:
                #Queenside Castling
                left_rook = self.squares[row][0].piece
                if isinstance(left_rook, Rook):
                    if not left_rook.moved:
                        for i in range(1,4):
                            if self.squares[row][i].has_piece():
                                break
                            if i == 3:
                                piece.left_rook = left_rook

                                #rook move
                                initial = Square(row, 0)
                                final = Square(row, 3)
                                moveR = Move(initial, final, piece.left_rook)

                                #king move
                                initial = Square(row, col)
                                final = Square(row, 2)
                                moveK = Move(initial, final, piece)

                                if bool:
                                    if not self.potential_check(piece, moveK) and not self.potential_check(left_rook, moveR):
                                        # if move doesnt put player in check then add move to piece moves
                                        left_rook.add_moves(moveR)
                                        piece.add_moves(moveK)
                                    else:
                                        break
                                elif left_rook is not None:
                                    left_rook.add_moves(moveR)
                                    piece.add_moves(moveK)
                #kingside castling
                right_rook = self.squares[row][7].piece
                if isinstance(right_rook, Rook):
                    if not right_rook.moved:
                        for i in range(5, 7):
                            if self.squares[row][i].has_piece():
                                break

                            if i == 6:
                                piece.right_rook = right_rook

                                # rook move
                                initial = Square(row, 7)
                                final = Square(row, 5)
                                moveR = Move(initial, final, piece.right_rook)

                                # king move
                                initial = Square(row, col)
                                final = Square(row, 6)
                                moveK = Move(initial, final, piece)

                                if bool:
                                    if not self.potential_check(piece, moveK) and not self.potential_check(right_rook, moveR):
                                        # if move doesnt put player in check then add move to piece moves
                                        right_rook.add_moves(moveR)
                                        piece.add_moves(moveK)
                                    else:
                                        break
                                elif right_rook is not None:
                                    right_rook.add_moves(moveR)
                                    piece.add_moves(moveK)

        #runs the piece move calculations depending on what piece:

        if isinstance(piece, Pawn):
            pawn_moves()

        elif isinstance(piece, Knight):
            knight_moves()

        elif isinstance(piece, Bishop):
            straightline_moves([
                (-1,1),
                (-1,-1),
                (1,1),
                (1,-1)
            ])

        elif isinstance(piece, Rook):
            straightline_moves([
                (-1,0),
                (0,1),
                (1,0),
                (0,-1)
            ])

        elif isinstance(piece, Queen):
            straightline_moves([
                (-1, 1),
                (-1, -1),
                (1, 1),
                (1, -1),
                (-1, 0),
                (0, 1),
                (1, 0),
                (0, -1)
            ])

        elif isinstance(piece, King):
            king_moves()

    #creates the squares and adds them to the board
    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    # adds the pieces to the board
    def _add_pieces(self, colour):
        if colour == WHITE:
            row_pawn, row_other = (6, 7)
        else:
            row_pawn, row_other = (1, 0)
        #creates the pawns
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(colour))
        #creates the knights
        self.squares[row_other][1] = Square(row_other, 1, Knight(colour))
        self.squares[row_other][6] = Square(row_other, 6, Knight(colour))
        #creates the bishops
        self.squares[row_other][2] = Square(row_other, 2, Bishop(colour))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(colour))
        #creates the rooks
        self.squares[row_other][0] = Square(row_other, 0, Rook(colour))
        self.squares[row_other][7] = Square(row_other, 7, Rook(colour))
        #creates the queens
        self.squares[row_other][3] = Square(row_other, 3, Queen(colour))
        #creates the kings
        self.squares[row_other][4] = Square(row_other, 4, King(colour))






                


