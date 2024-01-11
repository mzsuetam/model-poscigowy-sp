from src.simulator.controllers.astar_controller import AstarController
from src.simulator.objects.block import Block
from src.simulator.objects.point_mass import PointMass
from src.simulator.utils.vect_2d import Vect2d


class ForecastingController(AstarController):
    def __init__(self,
                 managed_point: PointMass,
                 target: PointMass,
                 canvas_dim: Vect2d,
                 blocks: [Block],
                 gap_between_nodes: float = 1 / 2,
                 steps_ahead: int = 1
                 ):
        super().__init__(managed_point, target, canvas_dim, blocks, gap_between_nodes, steps_ahead)
        self._target = target

    def update(self, t: float, dt: float) -> None:
        self._destination_point = self._predict()

        astar_path = self._get_astar_path()

        if len(astar_path) > 1:
            next_point = Vect2d(0, 0)
            used_points = 0
            for i in range(1, int(self._steps_ahead / self._gap_between_nodes) + 1):
                idx = i + 1 if len(astar_path) > i + 1 else -1
                next_node = astar_path[idx]
                next_cord = self.node_to_cord(next_node)
                next_point += Vect2d(*next_cord)
                used_points += 1

            if used_points == 0:
                return

            next_point = next_point / used_points

            v = self._managed_point.get_velocity()
            desired_v = (next_point - self._managed_point.center)
            distance = desired_v.norm()
            desired_v /= distance
            desired_v *= min(5.0, distance / dt * 0.05)

            desired_a = (desired_v - v) / dt * 0.1
            a_value = min(5.0, desired_a.norm())
            desired_a *= a_value / desired_a.norm()

            new_f = desired_a * self._managed_point.m

            # @FIXME: consider friction force

            d_f = new_f - self.f
            self._managed_point.add_force(d_f)
            self.f = new_f

        if len(astar_path) == 1:
            self._managed_point.subtract_force(self.f)
            self.f *= 0

    def _predict(self) -> Vect2d:
        c = self._target.center
        v = self._target.get_velocity()
        a = self._target.get_acceleration()

        return Vect2d(
            c.x + v.x + a.x / 2,
            c.y + v.y + a.y / 2
        )

    @staticmethod
    def get_type():
        return "ForecastingController"
