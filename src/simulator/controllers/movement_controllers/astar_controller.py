
import networkx as nx
from matplotlib import pyplot as plt

from simulator.controllers.base_controllers.base_graph_controller import BaseGraphController
from src.simulator.objects.block import Block
from src.simulator.objects.point_mass import PointMass
from src.simulator.utils.vect_2d import Vect2d


class AstarController(BaseGraphController):

    def __init__(
            self,
            managed_point: PointMass,
            destination_point: Vect2d | PointMass,
            canvas_dim: Vect2d,
            blocks: [Block],
            gap_between_nodes: float = 1 / 2,
            steps_ahead: int = 1,
    ):
        super().__init__(
            canvas_dim,
            blocks,
            gap_between_nodes
        )

        self._managed_point: PointMass = managed_point
        self._destination_point: Vect2d | PointMass = destination_point
        self._steps_ahead: int = steps_ahead

        self.f = Vect2d(0, 0)

    def apply(self, t, dt) -> None:
        d_f = self.update(t, dt)
        self._managed_point.add_force(d_f)

    def update(self, t, dt) -> Vect2d:
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
                return Vect2d(0, 0)

            next_point = next_point / used_points

            v = self._managed_point.get_velocity()
            desired_v = (next_point - self._managed_point.center)
            distance = desired_v.norm()
            desired_v /= distance
            desired_v *= min(5.0, distance / dt * 0.05)

            desired_a = (desired_v - v) / dt * 0.1
            a_value = min(5.0, desired_a.norm())
            desired_a *= a_value / desired_a.norm()

            # d = (next_point - self._managed_point.center)
            # d /= d.norm()
            # desired_a = d * 4.


            new_f = desired_a * self._managed_point.m

            # @FIXME: consider friction force

            d_f = new_f - self.f
            self.f = new_f
            return d_f

        if len(astar_path) == 1:
            f = -1*self.f
            self.f *= 0
            return f

    def _get_astar_path(self):
        dest = None
        if isinstance(self._destination_point, PointMass):
            dest = self._destination_point.center
        elif isinstance(self._destination_point, Vect2d):
            dest = self._destination_point
        if dest is None:
            raise Exception("Invalid destination point type")

        astar_path = nx.astar_path(
            self._graph, # @FIXME: consider subgraph form base graph controller
            self.cord_to_node(
                tuple(self._managed_point.center),
                find_closest_for_nonexistent=True
            ),
            self.cord_to_node(
                tuple(dest),
                find_closest_for_nonexistent=True
            )
        )
        return astar_path

    def plot_path(self):
        astar_path = self._get_astar_path()

        fig, ax = plt.subplots()
        self.plot_graph(
            ax,
            plot_nodes=False,
            plot_edges=False,
        )
        astar_x, astar_y = zip(*[self.node_to_cord(c) for c in astar_path])
        ax.plot(
            astar_x,
            astar_y,
            c="red",
            linewidth=5,
            zorder=2
        )
        fig.gca().invert_yaxis()
        fig.show()

    @staticmethod
    def get_type():
        return "AstarController"
