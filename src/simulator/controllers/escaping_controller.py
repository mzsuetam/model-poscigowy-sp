from simulator.controllers.base_controllers.base_controller import BaseController
from simulator.controllers.movement_controllers.astar_controller import AstarController
from simulator.controllers.movement_controllers.forecasting_controller import ForecastingController
from simulator.controllers.movement_controllers.vision_controller import VisionController
from simulator.objects.block import Block
from simulator.objects.point_mass import PointMass
from simulator.utils.vect_2d import Vect2d

import numpy as np


class EscapingController(BaseController):

    def __init__(
            self,
            managed_point: PointMass,
            target_point: Vect2d | PointMass,
            pursuing_point: PointMass,
            canvas_dim: Vect2d,
            blocks: [Block],
            gap_between_nodes: float = 1 / 2,
            steps_ahead: int = 1,
            angle_step: int = 4,
            goal_score: int = 1,
            unknown_score: int = 1000,
            crossroads_score: int = 100,
            known_score: int = 1000,
            edge_threshold: int = 4,
            priority_queue_size: int = 1000
    ):
        super().__init__()
        self._managed_point: PointMass = managed_point
        self._target_point: PointMass = target_point
        self._pursuing_point: PointMass = pursuing_point

        self._vision_controller = VisionController(
            managed_point,
            target_point,
            canvas_dim,
            blocks,
            gap_between_nodes,
            steps_ahead,
            angle_step,
            goal_score,
            unknown_score,
            crossroads_score,
            known_score,
            edge_threshold,
            priority_queue_size
        )

        self._astar_controller = AstarController(
            managed_point,
            target_point,
            canvas_dim,
            blocks,
            gap_between_nodes,
            steps_ahead
        )

        self.f_runaway: Vect2d = Vect2d(0, 0)
        self.f: Vect2d = Vect2d(0, 0)

    def apply(self, t: float, dt: float) -> None:
        d_f = self.update(t, dt)
        self._managed_point.add_force(d_f)

    def update(self, t: float, dt: float) -> Vect2d:
        f_vision = self._vision_controller.update(t, dt)
        t = 2

        f_runaway = Vect2d.from_singleton(1)
        d_runaway = Vect2d(
            self._pursuing_point.x - self._managed_point.x,
            self._pursuing_point.y - self._managed_point.y
        )
        if f_vision.x * d_runaway.x > 0:
            f_runaway.x *= -1
        if f_vision.y * d_runaway.y > 0:
            f_runaway.y *= -1
        f_runaway *= d_runaway / d_runaway.norm()

        d_critical = 4 * t
        if d_runaway.norm() >= d_critical:
            d_runaway = Vect2d.from_singleton(0)
            f_runaway = Vect2d.from_singleton(0)

        w_runaway = 1 - d_runaway.norm() / d_critical \
            if f_runaway.x != 0 and f_runaway.y != 0 \
            else 0
        w_runaway *= .25
        w_vision = 1 - w_runaway

        f_tmp = f_runaway - self.f_runaway
        self.f_runaway = f_runaway
        f_runaway = f_tmp

        f_new = f_vision * w_vision + f_runaway * w_runaway
        print(f_vision, w_vision, f_runaway, w_runaway, f_new)

        # x = self._managed_point.center
        # v = self._managed_point.get_velocity()
        # m = self._managed_point.m
        # a = self._managed_point.get_acceleration() + f_new / m
        # t = 1
        # x_new = x + a * t * t / 2
        # # x_new = x + v * t + a * t * t / 2
        # print(x_new)
        #
        # self._astar_controller._target_point = x_new
        # f_new = self._astar_controller.update(t, dt)

        return f_new



    @staticmethod
    def get_type():
        return "EscapingController"
