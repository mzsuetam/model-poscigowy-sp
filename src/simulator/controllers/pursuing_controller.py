from simulator.controllers.base_controllers.base_controller import BaseController
from simulator.controllers.movement_controllers.astar_controller import AstarController
from simulator.controllers.movement_controllers.forecasting_controller import ForecastingController
from simulator.objects.block import Block
from simulator.objects.point_mass import PointMass
from simulator.utils.vect_2d import Vect2d


class PursuingController(BaseController):

    def __init__(
            self,
            managed_point: PointMass,
            target_point: PointMass,
             canvas_dim: Vect2d,
             blocks: [Block],
             gap_between_nodes: float = 1 / 2,
             steps_ahead: int = 1
    ):
        super().__init__()
        self._managed_point: PointMass = managed_point
        self._target_point: PointMass = target_point

        self._forecasting_controller = ForecastingController(
            managed_point,
            target_point,
            canvas_dim,
            blocks,
            gap_between_nodes,
            steps_ahead
        )

        self._astar_controller = AstarController(
            managed_point,
            target_point,
            canvas_dim,
            blocks,
            gap_between_nodes,
            steps_ahead
        )

        self.f_act = False
        self.f: Vect2d = Vect2d(0, 0)

    def apply(self, t: float, dt: float) -> None:
        d_f = self.update(t, dt)
        self._managed_point.add_force(d_f)

    def update(self, t: float, dt: float) -> Vect2d:
        # where is the target going to head
        forecast_f = self._forecasting_controller.update(t, dt)

        # where is the target going to be => where should I go
        m = self._managed_point.m
        a = forecast_f / m
        v = self._target_point.get_velocity()
        t = 2
        s = v * t + a*t**2/2
        next_center = self._target_point.center + s

        # go there
        self._astar_controller.destination_point = next_center
        astar_f = self._astar_controller.update(t, dt)

        # @FIXME: check: when close to the target, go as fast as possible

        return astar_f

    @staticmethod
    def get_type():
        return "PursuingController"