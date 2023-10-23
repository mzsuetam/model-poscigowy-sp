import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx

from src.simulator.controllers.base_controller import BaseController
from src.simulator.utils.vect_2d import Vect2d
from src.simulator.objects.block import Block


class BaseGraphController(BaseController):
    def __init__(
            self,
            canvas_dim: Vect2d,
            blocks: [Block],
            gap_between_nodes: float = 1 / 2
    ):
        super().__init__()
        self._blocks: [Block] = blocks  # [m]
        self._canvas_dim: Vect2d = canvas_dim  # [m]
        self._gap_between_nodes: float = gap_between_nodes  # [m]

        self._graph: nx.Graph = self._init_graph()

    def _init_graph(self):
        graph = nx.grid_2d_graph(
            self._canvas_dim.x * int(1 / self._gap_between_nodes) + 1,
            self._canvas_dim.y * int(1 / self._gap_between_nodes) + 1
        )

        def is_inside(node, block):
            x, y = node
            is_in_x = block.x <= x * self._gap_between_nodes <= block.x + block.w
            is_in_y = block.y <= y * self._gap_between_nodes <= block.y + block.h
            # is_in_y = self._canvas_dim.y - block.y - block.h <= y * self._step <= self._canvas_dim.y - block.y
            return is_in_x and is_in_y

        for block in self._blocks:
            for_deletion = []
            for node in graph.nodes:
                if is_inside(node, block):
                    for_deletion.append(node)
            for node in for_deletion:
                graph.remove_node(node)

        return graph

    def plot_graph(
            self,
            ax=None,
            plot_nodes=True,
            plot_edges=True,
            plot_blocks=True,
            plot_decorators=True
    ) -> None:
        fig = None
        if ax is None:
            fig, ax = plt.subplots()

        # nodes
        if plot_nodes:
            ax.scatter(
                [p[0] * self._gap_between_nodes for p in self._graph.nodes],
                [p[1] * self._gap_between_nodes for p in self._graph.nodes],
                s=5,
                c="black",
                zorder=1
            )

        # edges
        if plot_edges:
            for p in self._graph.edges:
                ax.plot(
                    [p[0][0] * self._gap_between_nodes, p[1][0] * self._gap_between_nodes],
                    [p[0][1] * self._gap_between_nodes, p[1][1] * self._gap_between_nodes],
                    c="gray",
                    zorder=-1
                )

        # blocks
        if plot_blocks:
            for bl in self._blocks:
                rect = patches.Rectangle(
                    (bl.x, bl.y),
                    bl.w, bl.h,
                    linewidth=1,
                    edgecolor=None,
                    facecolor='lightgray',
                    zorder=-2,
                )
                ax.add_patch(rect)

        # decorators
        if plot_decorators:
            ax.set_xlabel("x [m]")
            ax.set_ylabel("y [m]")

        if fig is not None:
            fig.show()

    def cord_to_node(self, cord: tuple[float, float], find_closest_for_nonexistent=False) -> tuple[int, int]:
        calculated_node = int(cord[0] / self._gap_between_nodes), int(cord[1] / self._gap_between_nodes)

        if find_closest_for_nonexistent and calculated_node not in self._graph.nodes:
            closest_node = min(self._graph.nodes, key=lambda n: Vect2d(*n).distance(Vect2d(*calculated_node)))
            return closest_node

        return calculated_node

    def node_to_cord(self, node: tuple[int, int]) -> tuple[float, float]:
        return (node[0] * self._gap_between_nodes, node[1] * self._gap_between_nodes)
