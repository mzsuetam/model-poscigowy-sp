import pygame

from src.simulator.utils.colors import DARKGRAY
from src.simulator.utils.constants import px_in_m


class Block:
    def __init__(
            self,
            id,
            x,
            y,
            w=1,
            h=1,
            color=DARKGRAY
    ):
        self.id = id

        self.x = x  # [m]
        self.y = y  # [m]
        self.w = w  # [m]
        self.h = h  # [m]

        self.bb = pygame.Rect(0, 0, 0, 0)
        self.update_bb()

        self.color = color

    def update_bb(self):
        self.bb.x = self.x * px_in_m
        self.bb.y = self.y * px_in_m
        self.bb.w = self.w * px_in_m
        self.bb.h = self.h * px_in_m

    def __str__(self):
        return f"Block(id={self.id}, x={self.x}, y={self.y}, w={self.w}, h={self.h}, color={self.color})"