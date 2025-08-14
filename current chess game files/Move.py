
#Move class
class Move:

    #initialize move attributes
    def __init__(self, initial, final, piece):
        self.initial = initial
        self.final = final
        self.colour = None
        self.move_in_chess_notation = ''
        self.move_value = 0
        self.moved_piece = piece
        self.board = None
        self.captured_piece = None
        self.estimate_val = 0

    # tells object to compare object attributes not object identifier
    def __eq__(self, other):
        return self.initial == other.initial and self.final == other.final
    
#'fake' move class
class Dummy_Move():

    def __init__(self, move_value):
        self.moved_piece = None
        self.move_value = move_value
        self.estimate_val = 0

