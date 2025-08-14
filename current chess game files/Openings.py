import random
from random import randint

from settings import *

class Openings:

    def __init__ (self):
        self.opening = None
        self.ponziani_opening_moves = ['e4', 'e5', 'Nf3', 'Nc6', 'c3']
        self.queens_gambit_moves = ['d4','d5','c4']
        pass

    def get_opening_moves(self, previous_moves, colour):
        move = ''
        ponz = False
        queen_gam = False
        if colour == BLACK and len(previous_moves) <= 5:
            for m in range(0, len(previous_moves)):
                if self.ponziani_opening_moves[m] == previous_moves[m].moves_in_chess_notation:
                    ponz = True
                elif self.queens_gambit_moves[m] == previous_moves[m].moves_in_chess_notation:
                    queen_gam = True
            if ponz:
                if len(self.ponziani_opening_moves)>len(previous_moves):
                    move = self.ponziani_opening_moves[len(previous_moves)]
                else:
                    self.opening = Ponziani()
            elif queen_gam:
                if len(self.queens_gambit_moves)>len(previous_moves):
                    move = self.queens_gambit_moves[len(previous_moves)]
                else:
                    self.opening = Queens_gambit()
        else:
            if not previous_moves:
                num = randint(0,1)
                if num == 1:
                    move = self.ponziani_opening_moves[0]
                    self.opening = Ponziani()
                elif num == 0:
                    move = self.queens_gambit_moves[0]
                    self.opening = Queens_gambit()
            else:
                if isinstance(self.opening, Ponziani):
                    if len(previous_moves)<len(self.ponziani_opening_moves):
                        move = self.ponziani_opening_moves[len(previous_moves)]
                if isinstance(self.opening, Queens_gambit):
                    if len(previous_moves) < len(self.queens_gambit_moves):
                        move = self.queens_gambit_moves[len(previous_moves)]

        return move




class Queens_gambit(Openings):
    #[1:d4,d5 2:c4,dxc4 (black accepts gambit) 3:e4,e5
    #[1:d4,d5 2:c4,dxc4 (black accepts gambit) 3:Nf3,Nf6 4:e3,e6 5:Bxc4,c5
    #[1:d4,d5 2:c4,e6 (black declines gambit) 3:Nc3,Nf6 4:Nf3,Be7 5:Bg5,0-0 6:e3
    #[1:d4,d5 2:c4,e6 (black declines gambit) 3:Nc3,c5 (tarrasch defense)
    #[1:d4,d5 2:c4,e6 (black declines gambit catalan) 3:Nf3,Nf6 4:g3,Be7 5:Bg2,dxc4 6: 0-0
    #[1:d4,d5 2:c4,c6 (the slav defense) 3:Nc3,Nf6 4:Nf3,dxc4 5:a4,Bf5 6:e3,e6 7:Bxc4,Bb4
    #[1:d4,d5 2:c4,c6 (the slav defense) 3:Nc3,Nf6 4:Nf3,e6 (the semi slav defense)
    #[1:d4,d5 2:c4,e5 (The albin counter-gambit) 3:dxe5,d4 4:Nf3,Nc6 5:g3,Ng6 6:Bg2,Nxe5 7:0-0
    def __init__(self):
        super().__init__()
        self.list_of_games = []


class Ponziani(Openings):
    #[1:e4,e5 2: Nf3, Nc6 3:c3, d6 4:d4, exd4 5: cxd4
    #[1:e4,e5 2: Nf3, Nc6 3:c3, Nf6 4:d4, Nxe4 5: d5, Ne7 6: Nxe5, Ng6
    #[1:e4,e5 2: Nf3, Nc6 3:c3, Nf6 4:d4, exd4 5: e5, Nd5 6: cxd4, Bb4(check) 7: Bd2, Bxd2 8: Qxd2, d6
    #[1:e4,e5 2: Nf3, Nc6 3:c3, d5 4: Qa4, Bd6 5: exd5
    #[1:e4,e5 2: Nf3, Nc6 3:c3, d5 4: Qa4, Bd7 5: exd5, Nd4 6:
    #[1:e4,e5 2: Nf3, Nc6 3:c3, d5 4: Qa4, exd4 5: Nxe5
    #[1:e4,e5 2: Nf3, Nc6 3:c3, d5 4: Qa4, f6 5: Bb5, Ne7 (best for Black)

    def __init__(self):
        super().__init__()
        self.list_of_games = []

class Sicilian_defence(Openings):

    def __init__(self):
        pass


class Caro_Kann_defence(Openings):

    def __init__(self):
        pass

