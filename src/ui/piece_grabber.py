import pygame as pg

from src.settings import TILESIZE


class PieceGrabber:

    def __init__(self):
        self.piece = None
        self.holding = False
        self.mouse_x = 0
        self.mouse_y = 0
        self.initial_row = 0
        self.initial_col = 0

    def grab_piece(self, piece):
        self.piece = piece
        self.holding = True

    def ungrab_piece(self):
        self.piece = None
        self.holding = False

    def update_mouse(self, pos):
        self.mouse_x, self.mouse_y = pos

    def save_initial_pos(self, pos):
        self.initial_row = pos[1] // TILESIZE
        self.initial_col = pos[0] // TILESIZE

    def update_grabber(self, surface):
        self.piece.set_texture(size=128)
        img = pg.image.load(self.piece.texture)
        self.piece.texture_rect = img.get_rect(center=(self.mouse_x, self.mouse_y))
        surface.blit(img, self.piece.texture_rect)
