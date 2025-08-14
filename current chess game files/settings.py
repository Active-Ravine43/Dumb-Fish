#define colours RGB value
BLACK = (0, 0, 0)
WHITE = (225, 225, 225)
ORANGE = (255, 213, 128)
RED = (202, 95, 93)
DARK_RED = (186, 46, 44)
GREEN = (185, 224, 165)
DARK_GREEN = (82, 128, 87)
LIGHT_BLUE = (119, 141, 169)
BLUE = (85, 105, 135)
DARK_BLUE = (0, 48, 73)
DARK_GREY = (62, 63, 63)
GREY = (90,90,90)
LIGHT_GREY = (130,130,130)
ONE_PLAYER = (73,206,208) # one player button colour
TWO_PLAYER = (32,95,96) # two player button colour


#Game Options:

TITLE = "Chess Game"

    #board size
WIDTH = 512
HEIGHT = 512

    #Frames Per Second
FPS = 30

    #size of each square
TILESIZE = 64

    #screen size
width = WIDTH + 80
height = HEIGHT + TILESIZE

    #how many squares in column
COLS = 8
    #how many squares in row
ROWS = 8

    #stores the character values of row and col
rows_as_characters = ['8', '7', '6', '5','4','3','2','1']
cols_as_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

    #piece characters
king_character = 'K'
queen_character = 'Q'
rook_character = 'R'
bishop_character = 'B'
knight_character = 'N'
piece_characters = [king_character, queen_character, rook_character, bishop_character, knight_character]

    #value of each piece type
KVALUE = 10000
QVALUE = 900
RVALUE = 600
BVALUE = 300
NVALUE = 300
PVALUE = 100