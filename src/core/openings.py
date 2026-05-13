from random import randint
from src.settings import *


class Openings:

    def __init__(self):
        self.opening = None
        self.ponziani_opening_moves = ['e4', 'e5', 'Nf3', 'Nc6', 'c3']
        self.queens_gambit_moves = ['d4', 'd5', 'c4']

    def get_opening_moves(self, previous_moves, colour):
        move = ''
        ponz = False
        queen_gam = False
        if colour == BLACK and len(previous_moves) <= 5:
            for m in range(0, len(previous_moves)):
                if self.ponziani_opening_moves[m] == previous_moves[m].move_in_chess_notation:
                    ponz = True
                elif self.queens_gambit_moves[m] == previous_moves[m].move_in_chess_notation:
                    queen_gam = True
            if ponz:
                if len(self.ponziani_opening_moves) > len(previous_moves):
                    move = self.ponziani_opening_moves[len(previous_moves)]
                else:
                    self.opening = Ponziani()
            elif queen_gam:
                if len(self.queens_gambit_moves) > len(previous_moves):
                    move = self.queens_gambit_moves[len(previous_moves)]
                else:
                    self.opening = QueensGambit()
        else:
            if not previous_moves:
                num = randint(0, 1)
                if num == 1:
                    move = self.ponziani_opening_moves[0]
                    self.opening = Ponziani()
                elif num == 0:
                    move = self.queens_gambit_moves[0]
                    self.opening = QueensGambit()
            else:
                if isinstance(self.opening, Ponziani):
                    if len(previous_moves) < len(self.ponziani_opening_moves):
                        move = self.ponziani_opening_moves[len(previous_moves)]
                if isinstance(self.opening, QueensGambit):
                    if len(previous_moves) < len(self.queens_gambit_moves):
                        move = self.queens_gambit_moves[len(previous_moves)]

        return move


class QueensGambit(Openings):
    # 1:d4,d5  2:c4,dxc4 (gambit accepted) or 2:c4,e6 (declined) or 2:c4,c6 (Slav)

    def __init__(self):
        super().__init__()
        self.list_of_games = []


class Ponziani(Openings):
    # 1:e4,e5  2:Nf3,Nc6  3:c3

    def __init__(self):
        super().__init__()
        self.list_of_games = []


class SicilianDefence(Openings):
    pass


class CaroKannDefence(Openings):
    pass
