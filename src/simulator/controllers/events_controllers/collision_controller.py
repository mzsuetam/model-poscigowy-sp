from simulator.utils.vect_2d import Vect2d
from simulator.controllers.base_controllers.base_controller import BaseController
from src.simulator.objects.point_mass import PointMass


class CollisionController(BaseController):
    def __init__(
            self,
            point_1: PointMass,
            point_2: PointMass,
            function_to_call: callable,
    ):
        super().__init__()
        self._point_1: PointMass = point_1
        self._point_2: PointMass = point_2
        self._function_to_call: callable = function_to_call
        self._iter = 0
        self._iter_max = 60

    def apply(self, t: float, dt: float) -> None:
        self.update(t, dt)

    def update(self, t: float, dt: float) -> Vect2d:
        self._iter = (self._iter + 1) % self._iter_max
        if self._iter and self._point_1.is_colliding_with(self._point_2):
            self._function_to_call()
        return Vect2d(0, 0)

    @staticmethod
    def get_type():
        return "CollisionController"
