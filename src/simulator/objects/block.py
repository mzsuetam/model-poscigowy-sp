import pygame

from src.simulator.utils.colors import Color, DARKGRAY
from src.simulator.utils.constants import px_in_m


class Block:
    def __init__(
            self,
            id: int,
            x: float,
            y: float,
            w: float = 1,
            h: float = 1,
            color: Color = DARKGRAY
    ) -> None:
        self.id: int = id

        self.x: float = x  # [m]
        self.y: float = y  # [m]
        self.w: float = w  # [m]
        self.h: float = h  # [m]

        self.bb: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.update_bb()

        self.color: Color = color

    def update_bb(self) -> None:
        self.bb.x = self.x * px_in_m
        self.bb.y = self.y * px_in_m
        self.bb.w = self.w * px_in_m
        self.bb.h = self.h * px_in_m

    def __str__(self) -> str:
        return f"Block(id={self.id}, x={self.x}, y={self.y}, w={self.w}, h={self.h}, color={self.color})"
