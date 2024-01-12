from src.simulator.controllers.base_controller import BaseController
from src.simulator.objects.point_mass import PointMass


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
        self._function_to_call: callable = funtion_to_call
        self._iter = 0
        self._iter_max = 60

    def update(self, t: float, dt: float) -> None:
        self._iter = (self._iter + 1) % self._iter_max
        if self._iter and self._point_1.is_colliding_with(self._point_2):
            self._function_to_call()

    @staticmethod
    def get_type():
        return "CollisionController"
