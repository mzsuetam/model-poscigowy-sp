import pygame

class Block:
    def __init__(
            self,
            x,
            y,
            w=1,
            h=1,
            color=(100,100,100),
            px_in_m=50,
    ):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.bb = pygame.Rect(0,0,0,0)
        self.update_bb(px_in_m)

        self.color = color

    def update_bb(self, px_in_m):
        self.bb.x = self.x * px_in_m
        self.bb.y = self.y * px_in_m
        self.bb.w = self.w * px_in_m
        self.bb.h = self.h * px_in_m