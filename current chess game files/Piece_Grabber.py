import pygame as pg
from settings import *

#piece holding class
class Piece_Grabber:

    #initialize piece grabber attributes
    def __init__(self):
        self.piece = None
        self.Holding = False
        self.MouseX = 0
        self.MouseY = 0
        self.initial_row = 0
        self.initial_col = 0

    #updates the position, size and location of piece when moving
    def update_grabber(self, surface):
        self.piece.set_texture(size=128)
        texture = self.piece.texture
        img = pg.image.load(texture)
        img_center = (self.MouseX, self.MouseY)
        self.piece.texture_rect = img.get_rect(center=img_center)
        surface.blit(img, self.piece.texture_rect)

    #update the mouse position
    def update_mouse(self, pos):
        self.MouseX, self.MouseY = pos

    #save the initial piece position
    def save_initial_pos(self, pos):
        self.initial_row = pos[1] // TILESIZE
        self.initial_col = pos[0] // TILESIZE

    #'picks up' the piece
    def Grab_Piece(self, piece):
        self.piece = piece
        self.Holding = True

    #puts the piece down
    def UnGrab_Piece(self):
        self.piece = None
        self.Holding = False

