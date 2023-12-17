import pygame
from src.simulator.controllers.base_controller import BaseController
from src.simulator.utils.vect_2d import Vect2d
from src.simulator.objects.point_mass import PointMass
from src.simulator.objects.block import Block


class CollisionController(BaseController):
    def __init__(
            self,
            point_1: PointMass,
            point_2: PointMass,
            funtion_to_call: callable,
    ):
        super().__init__()
        self._point_1: PointMass = point_1
        self._point_2: PointMass = point_2
        self._funtion_to_call: callable = funtion_to_call

    def update(self, t: float, dt: float) -> None:
        if self._point_1.is_colliding_with(self._point_2):
            self._funtion_to_call()

    @staticmethod
    def get_type():
        return "CollisionController"