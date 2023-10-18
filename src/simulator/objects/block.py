import pygame

from src.simulator.utils.constants import px_in_m

class Block:
    def __init__(
            self,
            x,
            y,
            w=1,
            h=1,
            color=(100,100,100),
    ):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.bb = pygame.Rect(0,0,0,0)
        self.update_bb()

        self.color = color

    def update_bb(self):
        self.bb.x = self.x * px_in_m
        self.bb.y = self.y * px_in_m
        self.bb.w = self.w * px_in_m
        self.bb.h = self.h * px_in_m