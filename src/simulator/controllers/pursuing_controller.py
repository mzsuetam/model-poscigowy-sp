import time

from simulator.controllers.base_controllers.base_controller import BaseController
from simulator.controllers.movement_controllers.astar_controller import AstarController
from simulator.controllers.movement_controllers.forecasting_controller import ForecastingController
from simulator.objects.block import Block
from simulator.objects.point_mass import PointMass
from simulator.utils.vect_2d import Vect2d

import numpy as np


class PursuingController(BaseController):

    def __init__(
            self,
            managed_point: PointMass,
            target_point: PointMass,
            canvas_dim: Vect2d,
            blocks: [Block],
            gap_between_nodes: float = 1 / 2,
            steps_ahead: int = 1,
            probabilistic: bool = False,
    ):
        super().__init__()
        self._managed_point: PointMass = managed_point
        self._target_point: PointMass = target_point

        self._probabilistic = probabilistic

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

        self._probability_matrix = np.zeros(
            (canvas_dim * int(1 / gap_between_nodes)).__tuple__()
        )

    def apply(self, t: float, dt: float) -> None:
        d_f = self.update(t, dt)
        self._managed_point.add_force(d_f)

    def update(self, t: float, dt: float) -> Vect2d:

        d = (self._target_point.center - self._managed_point.center).norm()
        if d < 2 and len([
            b for b in self._astar_controller._blocks if b.has_point_inside(
                (self._target_point.center + self._managed_point.center) / 2
            )
        ]) == 0:
            print("PursuingController: target reached")
            f = self.get_force_between(
                self._managed_point.center,
                self._target_point.center,
            )
            if f.norm() > 0:
                f = f / f.norm() * 4
            curr_a = self._managed_point.get_acceleration()
            f -=  curr_a * self._managed_point.m
            return f


        if not self._probabilistic:
            next_center = self._calculate_next_center_inertia(t, dt)
        else:

            ic = self._calculate_next_center_inertia(t, dt).__tuple__()

            self._probability_matrix = self._calculate_probability_matrix(t, dt, ic)
            mx = self._probability_matrix

            cs = np.cumsum(mx, axis=0)
            rs = np.cumsum(mx, axis=1)
            rc_x = np.random.rand()
            rc_y = np.random.rand()
            i, j = ic
            for i in range(cs.shape[0]):
                if rc_x < cs[i, 0]:
                    break
            for j in range(rs.shape[1]):
                if rc_y < rs[0, j]:
                    break
            next_center = Vect2d(i, j)

        # go there
        self._astar_controller.destination_point = next_center
        astar_f = self._astar_controller.update(t, dt)

        return astar_f

    def _calculate_next_center_inertia(self, t: float, dt: float) -> Vect2d:
        # where is the target going to head
        forecast_f = self._forecasting_controller.update(t, dt)

        # where is the target going to be => where should I go
        m = self._managed_point.m
        a = forecast_f / m
        v = self._target_point.get_velocity()
        t = 5
        s = v * t + a * t ** 2 / 2
        return self._target_point.center + s

    def _calculate_probability_matrix(self, t: float, dt: float, ic) -> np.array:

        cc = self._astar_controller.cord_to_node(
            self._target_point.center.__tuple__()
        )

        ic = self._astar_controller.cord_to_node(
            ic
        )

        dx = ic[0] - cc[0]
        dy = ic[1] - cc[1]
        r = int(np.sqrt(dx ** 2 + dy ** 2))
        d_step = min(abs(dx), abs(dy))
        dx = dx / d_step if d_step != 0 else 0
        dy = dy / d_step if d_step != 0 else 0
        d = Vect2d(dx, dy)

        c = Vect2d.from_tuple(cc)
        for i in range(int(d_step)):
            if len(
                    [b for b in self._astar_controller._blocks if b.has_point_inside(c+d)]
            ) > 0:
                break
            if (c+d).__lt__(Vect2d.from_singleton(0)).any() \
                    or (c+d).__gt__(self._astar_controller._canvas_dim).any():
                break
            c += d

        mx_padded = np.zeros(
            tuple([
                d + 2 * r for d in
                self._probability_matrix.shape
            ])
        )

        gf = self._generate_gaussuian_filter(2 * r + 1)

        from_x = int(np.floor(c.x))
        from_y = int(np.floor(c.y))
        mx_padded[
            from_x: from_x + 2 * r + 1,
            from_y: from_y + 2 * r + 1
        ] = gf

        # @FIXME: this part of the code is taking 10 times longer than the rest
        indexes = np.where(mx_padded.flatten() > 0)
        if len(indexes) == 0:
            return mx_padded
        for i in range(len(indexes[0])):
            x = i % mx_padded.shape[0]
            y = i // mx_padded.shape[0]
            if mx_padded[x, y] != 0:
                calculated_node = self._astar_controller.cord_to_node((x, y))
                if calculated_node in self._astar_controller._graph.nodes:
                    mx_padded[x, y] = 0

        if r != 0:
            mx_padded = mx_padded[r:-r, r:-r]
        norm_val = sum(mx_padded.flatten())
        if norm_val != 0:
            mx_padded /= norm_val

        return mx_padded

    def _generate_gaussuian_filter(self, kernel_size: int, sigma: float = 1, muu: float = 0):
        # Initializing value of x,y as grid of kernel size
        # in the range of kernel size

        x, y = np.meshgrid(
            np.linspace(-1, 1, kernel_size),
            np.linspace(-1, 1, kernel_size)
        )
        dst = np.sqrt(x ** 2 + y ** 2)

        # lower normal part of gaussian
        normal = 1 / (2.0 * np.pi * sigma ** 2)

        # Calculating Gaussian filter
        gauss = np.exp(-((dst - muu) ** 2 / (2.0 * sigma ** 2))) * normal

        return gauss / sum(sum(gauss))

    @staticmethod
    def get_type():
        return "PursuingController"
