from simulator.controllers.base_controllers.base_graph_controller import BaseGraphController
from src.simulator.objects.block import Block
from src.simulator.objects.point_mass import PointMass
from src.simulator.utils.vect_2d import Vect2d


class TremauxController(BaseGraphController):
    def __init__(
            self,
            managed_point: PointMass,
            destination_point: Vect2d | PointMass,
            canvas_dim: Vect2d,
            blocks: [Block],
            gap_between_nodes: float = 1 / 2,
            steps_ahead: int = 1
    ) -> None:
        super().__init__(
            canvas_dim,
            blocks,
            gap_between_nodes
        )
        self._managed_point = managed_point
        self._visited_nodes = set()
        self._traversed_edges = {}
        self._stack = [self.cord_to_node(
            tuple(self._managed_point.center),
            find_closest_for_nonexistent=True
        )]

    def apply(self, t: float, dt: float) -> None:
        self.update(t, dt)

    def update(self, t: float, dt: float) -> Vect2d:
        current_node = self._stack[-1]
        neighbors = list(self._graph.neighbors(current_node))

        # If there are unvisited neighbors
        unvisited_neighbors = [n for n in neighbors if n not in self._visited_nodes]
        if unvisited_neighbors:
            next_node = unvisited_neighbors[0]
            self._stack.append(next_node)
            self._traversed_edges[(current_node, next_node)] = 1  # Mark the edge as visited
            self._visited_nodes.add(next_node)
        else:
            # Backtrack
            self._stack.pop()

        return Vect2d(0, 0)

    @staticmethod
    def get_type():
        return "TremauxController"
