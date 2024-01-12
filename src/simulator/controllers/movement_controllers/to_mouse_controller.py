from simulator.controllers.base_controllers.base_controller import BaseController
from src.simulator.utils.vect_2d import Vect2d
from src.simulator.objects.point_mass import PointMass


class ToMouseController(BaseController):
    def __init__(
            self,
            managed_point: PointMass,
            mouse_point: PointMass,
    ):
        super().__init__()
        self._managed_point: PointMass = managed_point
        self._mouse_point: PointMass = mouse_point

        self.f_act = False
        self.f: Vect2d = Vect2d(0, 0)

    def apply(self, t: float, dt: float) -> None:
        if self._mouse_point.m > 1:
            self.f_act = True
            new_f = self.get_force_between(
                self._managed_point.center,
                self._mouse_point.center,
            )
            d_f = new_f - self.f
            self._managed_point.add_force(d_f)
            self.f = new_f
        else:
            if self.f_act:
                self._managed_point.subtract_force(self.f)
                self.f_act = False
                self.f *= 0

    def update(self, t: float, dt: float) -> Vect2d:
        raise NotImplementedError("ToMouseController does not implement update()")

    @staticmethod
    def get_type():
        return "ToMouseController"