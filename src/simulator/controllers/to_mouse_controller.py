import pygame
from src.simulator.controllers.base_controller import BaseController
from src.simulator.utils.vect_2d import Vect2d
from src.simulator.objects.point_mass import PointMass
from src.simulator.objects.block import Block


class ToMouseController(BaseController):
    def __init__(
            self,
            managed_point: PointMass,
            mouse_point: PointMass,
            blocks: [Block],
            mosue: pygame.mouse
    ):
        super().__init__()
        self._managed_point: PointMass = managed_point
        self._mouse_point: PointMass = mouse_point
        self._blocks: [Block] = blocks
        self._mouse: pygame.mouse = mosue

        self.f_act = False
        self.f: Vect2d = Vect2d(0, 0)

    def _generate_force_between(self) -> Vect2d:
        p1 = self._managed_point.center
        p2 = self._mouse_point.center
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        d = Vect2d(dx, dy)
        return d

    def update(self, t: float) -> None:
        if self._mouse.get_pressed()[0]:
            self.f_act = True
            new_f = self._generate_force_between()
            d_f = new_f - self.f
            self._managed_point.add_force(d_f)
            self.f = new_f
        else:
            if self.f_act:
                self._managed_point.subtract_force(self.f)
                self.f_act = False
                self.f *= 0
