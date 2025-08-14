from Piece import Pawn

#square object class
class Square:

    #initialize game attributes
    def __init__(self, row, col, piece=None):
        self.row = row
        self.col = col
        self.piece = piece

    #tells object to compare object attributes not object identifier
    def __eq__(self,other):
        return self.row == other.row and  self.col == other.col

    #checks if the square has a piece
    def has_piece(self):
        return self.piece != None

    #checks if square is empty
    def isempty(self):
        return not self.has_piece()

    #checks if square has a team piece
    def has_team_piece(self, colour):
        return self.has_piece() and self.piece.colour == colour

    #checks if square has enemy piece
    def has_enemy_piece(self, colour):
        return self.has_piece() and self.piece.colour != colour

    #checks if square is empty or if it has an enemy piece
    def isempty_or_enemy(self, colour):
        return self.isempty() or self.has_enemy_piece(colour)

    #checks whether pawn has moved twice
    def has_pawn_moved_twice(self):
        if isinstance(self.piece, Pawn):
            if self.piece.moved_twice:
                return True
            else:
                return False
        return False

    #checks that clicked area is within the range of the board
    @staticmethod
    def in_range(*args):
        for arg in args:
            if arg < 0 or arg > 7:
                return False

        return True





