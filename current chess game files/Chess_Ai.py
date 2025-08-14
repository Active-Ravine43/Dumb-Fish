import math
from Board_Class import *


#chess bot class
class Chess_Bot:

    #initialize bot attributes
    def __init__(self, colour, board):
        self.colour = colour
        self.board = board

    #make a move on the board
    def make_move(self, board, difficulty=3):
        #get the best move
        move = self.find_best_moves(copy.deepcopy(board), self.colour, depth=difficulty)
        if move is not None:
            #get piece to be moved
            initial_square = board.squares[move.initial.row][move.initial.col]
            piece = initial_square.piece
            move.board = copy.deepcopy(board)

            if piece is not None:
                #add move to board
                board.move(piece, move)

        return move

    #finds the best move
    def find_best_moves(self, board, colour, depth=3, alpha=-math.inf, beta=math.inf):
        if depth <= 0:
            evaluation = self.eval_board(board, colour)
            dummy_move = self.create_dummy_move(evaluation)
            return dummy_move

        best_move = None
        all_moves = self.generate_all_moves(board, colour)

        if not all_moves:
            return None

        if all_moves and depth != 0:
            for m in all_moves:
                piece = m.moved_piece
                #make the move on the board
                board.move(piece, m, testing=True)
                #evaluate the board state and assign the move a value
                self.assign_move_value(board, m)
                #evaluate the opponents response to the move
                opponent_move = self.find_best_moves(board, self.opposite_colour(colour), depth=depth - 1, alpha=-beta, beta=-alpha)
                #undo the move made
                self.undo_move(board, m, piece)
                if opponent_move is not None and hasattr(opponent_move, 'move_value'):
                    current_value = - opponent_move.move_value
                    m.move_value = m.move_value + current_value
                    if current_value > alpha:
                        #if response in bots favour
                        alpha = current_value
                        best_move = m

                    if alpha <= beta:
                        #stop evaluating move
                        break

            return best_move

    #creates a fake move which has a value evaluated based on the board
    def create_dummy_move(self, move_value):
        dummy_move = Dummy_Move(move_value)
        return dummy_move

    #generates all the best piece moves
    def generate_all_moves(self, board, colour):
        best = -math.inf
        moves = []
        for row in range(ROWS):
            for col in range(COLS):
                if board.squares[row][col].has_team_piece(colour):
                    piece = board.squares[row][col].piece
                    #returns the pieces best moves
                    piece_moves = self.generate_piece_moves(board, piece, row, col, best)
                    if piece_moves:
                        #add the piece moves to end of moves
                        moves.extend(piece_moves)
        if moves:
            #sort the moves to make searching faster
            moves = self.sort_moves(moves)
        return moves

    #generate all a pieces best moves
    def generate_piece_moves(self, board, piece, row, col, best):
        best_moves = []
        #calculate all the moves of the piece
        board.calculate_moves(piece, row, col)
        count = 0
        for m in piece.moves:
            if board.valid_move(piece, m):
                #estimate the move value
                self.estimate_move_value(board, m, piece)
                #if move is better than previous best
                if m.estimate_val > best:
                    best = m.estimate_val
                    best_moves = [m]
                    count = 0
                elif m.estimate_val == best or not count > 3:
                    best_moves.append(m)
                    count += 1
        return best_moves

    #assigns how good the move is
    def assign_move_value(self, board, move):
        capture_value = 0
        #evaluate if capture and what capture is worth
        if move.captured_piece is not None:
            capture_value = self.what_piece(move.captured_piece)
        #eval the position
        evaluation = self.eval_board(board, move.colour) + capture_value
        #assign the move value
        move.move_value = evaluation

    #assigns the estimate value
    def estimate_move_value(self, board, move, piece):
        #evaluate capture and what piece captured
        capture_value = 0
        if move.captured_piece is not None:
            capture_value = self.what_piece(move.captured_piece)
        #evaluate the positional value of the piece
        positional_evaluation = piece.piece_eval_table[move.final.row][move.final.col]
        #evaluate bot material value
        material_evaluation_self = self.evaluate_piece_value(board, move.colour)
        #evaluate player material value
        material_evaluation_opponent =  - self.evaluate_piece_value(board, self.opposite_colour(piece.colour))
        #takeaway any captures
        material_evaluation_opponent = material_evaluation_opponent - capture_value
        #assign the estimate move value
        move.estimate_val = positional_evaluation + (material_evaluation_self - material_evaluation_opponent)

    #evaluates the positional, material and if move gives check
    def eval_board(self, board, colour):
        value = 0
        for row in range(ROWS):
            for col in range(COLS):
                square = board.squares[row][col]
                if square.has_team_piece(colour):
                    #add the material value of piece
                    value += self.what_piece(square.piece)
                    #add the positional value of piece
                    value += square.piece.piece_eval_table[row][col]
                elif square.has_enemy_piece(colour):
                    #evaluate opponents piece value
                    value = value - self.what_piece(square.piece)
                    #evaluate opponents positional value
                    value += square.piece.piece_eval_table[row][col]
        #evalautes whether move is check
        is_move_check = self.evaluate_if_gives_check(board, colour)
        value += is_move_check
        return value

    #evaluates the material value of the bot
    def evaluate_material(self, board, colour):
        board_value = self.evaluate_piece_value(board,colour) - self.evaluate_piece_value(board,self.opposite_colour(colour))
        return board_value

    #evaluates the value of pieces left of the given colour
    def evaluate_piece_value(self, board, colour):
        team_value = 0
        for row in range (ROWS):
            for col in range (COLS):
                possible_piece = board.squares[row][col]
                if possible_piece.has_team_piece(colour):
                    team_value += self.what_piece(possible_piece.piece)
        return team_value

    #evaluate whether position is check
    def evaluate_if_gives_check(self, board, colour):
        value = 0
        if board.in_check(self.opposite_colour(colour), board):
            #return a value of 500 if check
            value = 500
        return value

    #recieves a piece and returns the value of the piece
    def what_piece(self, piece):
        if isinstance(piece, Pawn):
            return PVALUE
        elif isinstance(piece, Knight):
            return NVALUE
        elif isinstance(piece, Bishop):
            return BVALUE
        elif isinstance(piece, Rook):
            return RVALUE
        elif isinstance(piece, Queen):
            return QVALUE
        elif isinstance(piece, King):
            return KVALUE

    #recieves black or white and returns the opposite
    def opposite_colour(self, colour):
        if colour == WHITE:
            return BLACK
        else:
            return WHITE

    #function for sort key
    def return_move_estimate_val(self, move):
        return move.estimate_val

    #undoes a searching move
    def undo_move(self, board, move, piece):
        if move.captured_piece:
            #reset moved piece to initial square
            board.squares[move.initial.row][move.initial.col].piece = piece
            #reset captured piece to final square
            board.squares[move.final.row][move.final.col].piece = move.captured_piece
            move.captured_piece = None
        else:
            #reset piece to the initial square
            board.squares[move.initial.row][move.initial.col].piece = piece
            #remove the piece out of the final square
            board.squares[move.final.row][move.final.col].piece = None

    #sorts the moves in order of estimate value
    def sort_moves(self, moves):
        best_moves = []
        best_value = - math.inf
        #python built in sort function - Tim sort
        moves.sort(key=self.return_move_estimate_val, reverse=True)
        if len(moves) > 3:
            for i in range (0, 3):
                if moves[i].estimate_val >= best_value:
                    best_value = moves[i].estimate_val
                    best_moves.append(moves[i])
        else:
            best_moves = moves

        return best_moves
