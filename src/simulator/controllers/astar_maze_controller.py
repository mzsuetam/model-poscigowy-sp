import heapq
import networkx as nx

from src.simulator.controllers.astar_controller import AstarController
from src.simulator.objects.block import Block
from src.simulator.objects.point_mass import PointMass
from src.simulator.utils.vect_2d import Vect2d


class AstarMazeController(AstarController):
    def __init__(
            self,
            managed_point: PointMass,
            destination_point: Vect2d | PointMass,
            canvas_dim: Vect2d,
            blocks: [Block]):
        super().__init__(
            managed_point,
            destination_point,
            canvas_dim,
            blocks)
        self._priority_queue = [(0, self.cord_to_node(
            tuple(self._managed_point.center),
            find_closest_for_nonexistent=True
        ), [])]
        self._destination_point = self.cord_to_node(
            tuple(self._managed_point.center),
            find_closest_for_nonexistent=True
        )

    def _get_astar_path(self):
        self._update_priority_queue()
        dest = None
        if isinstance(self._destination_point, PointMass):
            dest = self._destination_point.center
        elif isinstance(self._destination_point, Vect2d):
            dest = self._destination_point
        if dest is None:
            raise Exception("Invalid destination point type")

        astar_path = nx.astar_path(
            self._graph,
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

    def _update_priority_queue(self):

        if self._priority_queue:
            current_cost, current_node, path = heapq.heappop(self._priority_queue)

            if self.is_goal(current_node):
                return path + [current_node]

            for neighbor in self._graph.neighbors(current_node):
                total_cost = current_cost + 1 + self.heuristic(neighbor)
                heapq.heappush(self._priority_queue, (total_cost, neighbor, path + [current_node]))

    def is_goal(self, current_node) -> bool:
        return current_node == self._destination_point

    def heuristic(self, node):
        return 1

    @staticmethod
    def get_type():
        return "AstarMazeController"
