import pygame
from src.simulator.controllers.base_controller import BaseController
from src.simulator.objects.force import Force
from src.simulator.objects.vect_2d import Vect2d
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
        self._mouse = mosue

        self.f: Force = Force(Vect2d(0, 0))
        self._managed_point.attach_force(self.f)

    def update(self, t):
        if self._mouse.get_pressed()[0]:
            self.f.pull_to(self._mouse_point)
        else:
            self._managed_point.detach_force(self.f)
            self.f = Force(Vect2d(0, 0))
            self._managed_point.attach_force(self.f)