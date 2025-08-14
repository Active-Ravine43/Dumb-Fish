import os
from settings import *

#parent piece class
class Piece:

    #initializes piece attributes
    def __init__(self, name, colour, value, texture=None, texture_rect=None):
        self.name = name
        self.colour = colour
        value_sign = 1 if colour == WHITE else -1
        self.value = value * value_sign
        self.moves = []
        self.moved = False
        self.moved_twice = False
        self.texture = texture
        self.set_texture()
        self.texture_rect = texture_rect
        self.pieces_threatening = []
        self.piece_guarding = []
        self.is_guarded = False
        self.is_threatened = False

    #sets the image of a piece
    def set_texture(self, size=80):
        if self.colour == WHITE:
            Piece_Colour = 'white'
        else:
            Piece_Colour = 'black'
        self.texture = os.path.join(
            f'assets/images/imgs-{size}px/{Piece_Colour}_{self.name}.png')

    #adds a move to piece moves
    def add_moves(self, move):
        self.moves.append(move)

    #clears the piece moves
    def clear_moves(self):
        self.moves = []

#subclass pawn
class Pawn(Piece):

    #initialize pawn attributes
    def __init__(self, colour):
        self.dir = -1 if colour == WHITE else 1
        #piece eval table - how the bot evaluates the position
        self.piece_eval_table = [(0,0,0,0,0,0,0,0),
                                 (50,50,50,50,50,50,50,50),
                                 (10,10,20,30,30,20,10,10),
                                 (5,5,10,25,25,10,5,5),
                                 (0,0,0,20,20,0,0,0),
                                 (5,-5,-10,0,0,-10,-5,5),
                                 (5,10,10,-20,-20,10,10,5),
                                 (0,0,0,0,0,0,0,0)
                                 ] if colour == WHITE else [(0,0,0,0,0,0,0,0),
                                                            (5,10,10,-20,-20,10,10,5),
                                                            (5,-5,-10,0,0,-10,-5,5),
                                                            (0,0,0,20,20,0,0,0),
                                                            (5,5,10,25,25,10,5,5),
                                                            (10,10,20,30,30,20,10,10),
                                                            (50,50,50,50,50,50,50,50),
                                                            (0,0,0,0,0,0,0,0)]
        super().__init__('Pawn', colour, 1.0)

#subclass knight
class Knight(Piece):

    #initialize knight attributes
    def __init__(self, colour):
        self.dir = -1 if colour == WHITE else 1
        # piece eval table - how the bot evaluates the position
        self.piece_eval_table = [(-50,-40,-30,-30,-30,-30,-40,-50),
                                 (-40,-20,0,0,0,0,-20,-40),
                                 (-30,0,10,15,15,10,0,-30),
                                 (-30,5,15,20,20,15,5,-30),
                                 (-30,0,15,20,20,15,5,-30),
                                 (-30,5,10,15,15,10,5,-30),
                                 (-40,-20,0,5,5,0,-20,-40),
                                 (-50,-40,-30,-30,-30,-30,-40,-50)]
        super().__init__('Knight', colour, 3.0)

#subclass bishop
class Bishop(Piece):

    #initialize bishop attributes
    def __init__(self, colour):
        self.dir = -1 if colour == WHITE else 1
        # piece eval table - how the bot evaluates the position
        self.piece_eval_table = [(-20,-10,-10,-10,-10,-10,-10,-20),
                                 (-10,0,0,0,0,0,0,-10),
                                 (-10,0,5,10,10,5,0,-10),
                                 (-10,5,5,10,10,5,5,-10),
                                 (-10,0,10,10,10,10,0,-10),
                                 (-10,10,10,10,10,10,10,-10),
                                 (-10,5,0,0,0,0,5,-10),
                                 (-20,-10,-10,-10,-10,-10,-10,-20)] if colour == WHITE else [(-20,-10,-10,-10,-10,-10,-10,-20),
                                                                                             (-10,5,0,0,0,0,5,-10),
                                                                                             (-10,10,10,10,10,10,10,-10),
                                                                                             (-10,0,10,10,10,10,0,-10),
                                                                                             (-10,5,5,100,10,5,5,-10),
                                                                                             (-10,0,5,10,10,5,0,-10),
                                                                                             (-10,0,0,0,0,0,0,-10),
                                                                                             (-20,-10,-10,-10,-10,-10,-10,-20)]
        super().__init__('Bishop', colour, 3.001)

#subclass rook
class Rook(Piece):

    #initialize rook attributes
    def __init__(self, colour):
        self.dir = -1 if colour == WHITE else 1
        # piece eval table - how the bot evaluates the position
        self.piece_eval_table = [(0,0,0,0,0,0,0,0),
                                 (5,10,10,10,10,10,10,5),
                                 (-5,0,0,0,0,0,0,-5),
                                 (-5,0,0,0,0,0,0,-5),
                                 (-5, 0, 0, 0, 0, 0, 0, -5),
                                 (-5, 0, 0, 0, 0, 0, 0, -5),
                                 (-5, 0, 0, 0, 0, 0, 0, -5),
                                 (0,0,0,5,5,0,0,0),
                                 ] if colour == WHITE else [(0,0,0,5,5,0,0,0),
                                                            (-5, 0, 0, 0, 0, 0, 0, -5),
                                                            (-5, 0, 0, 0, 0, 0, 0, -5),
                                                            (-5, 0, 0, 0, 0, 0, 0, -5),
                                                            (-5, 0, 0, 0, 0, 0, 0, -5),
                                                            (-5, 0, 0, 0, 0, 0, 0, -5),
                                                            (5,10,10,10,10,10,10,5),
                                                            (0,0,0,0,0,0,0,0)
                                                            ]
        super().__init__('Rook', colour, 6.0)

#subclass queen
class Queen(Piece):

    #initialize rook attributes
    def __init__(self, colour):
        self.dir = -1 if colour == WHITE else 1
        # piece eval table - how the bot evaluates the position
        self.piece_eval_table = [(-20,-10,-10,-5,-5,-10,-10,-20),
                                 (-10,0,0,0,0,0,0,-10),
                                 (-10,0,5,5,5,5,0,-10),
                                 (-10,0,5,5,5,5,0,-10),
                                 (-10,0,5,5,5,5,0,-10),
                                 (-10,5,5,5,5,5,0,-10),
                                 (-10, 0, 5, 0, 0, 0, 0, -10),
                                 (-20, -10, -10, -5, -5, -10, -10, -20),
                                 ] if colour == WHITE else  [(-20,-10,-10,-5,-5,-10,-10,-20),
                                 (-10,0,0,0,0,5,0,-10),
                                 (-10,0,5,5,5,5,5,-10),
                                 (-10,0,5,5,5,5,0,-10),
                                 (-10,0,5,5,5,5,0,-10),
                                 (-10,0,5,5,5,5,0,-10),
                                 (-10, 0, 0, 0, 0, 0, 0, -10),
                                 (-20, -10, -10, -5, -5, -10, -10, -20),]
        super().__init__('Queen', colour, 9.0)

#sublass king
class King(Piece):

    #initialize king attributes
    def __init__(self, colour):
        self.left_rook = None
        self.right_rook = None
        self.dir = -1 if colour == WHITE else 1
        # piece eval table - how the bot evaluates the position
        self.piece_eval_table = [(-30,-40,-40,-50,-50,-40,-40,-30),
                                 (-30,-40,-40,-50,-50,-40,-40,-30),
                                 (-30,-40,-40,-50,-50,-40,-40,-30),
                                 (-30,-40,-40,-50,-50,-40,-40,-30),
                                 (-20,-30,-30,-40,-40,-30,-30,-20),
                                 (-10,-20,-20,-20,-20,-20,-20,-10),
                                 (20,20,0,0,0,0,20,20),
                                 (20,30,10,0,0,10,30,20)] if colour == WHITE else [(20,30,10,0,0,10,30,20),
                                                                                   (20,20,0,0,0,0,20,20),
                                                                                   (-10,-20,-20,-20,-20,-20,-20,-10),
                                                                                   (-20,-30,-30,-40,-40,-30,-30,-20),
                                                                                   (-30,-40,-40,-50,-50,-40,-40,-30),
                                                                                   (-30,-40,-40,-50,-50,-40,-40,-30),
                                                                                   (-30,-40,-40,-50,-50,-40,-40,-30),
                                                                                   (-30,-40,-40,-50,-50,-40,-40,-30),
                                                                                   ]
        super().__init__('King', colour, 1000.0)













        
