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
            step: float = 1 / 2
    ):
        super().__init__()
        self._blocks: [Block] = blocks  # [m]
        self._canvas_dim: Vect2d = canvas_dim  # [m]
        self._step: float = step  # [m]

        self.graph: nx.Graph = self._init_graph()

        print(self.graph.nodes)
        astar_path = nx.astar_path(
            self.graph,
            self.cord_to_node((5, 5)),
            self.cord_to_node((17.5, 17.5))
        )

        fig, ax = plt.subplots()
        self.plot_graph(
            ax,
            plot_nodes=False,
            plot_edges=False,
        )

        astar_path = [self.node_to_cord(c) for c in astar_path]
        astar_x, astar_y = zip(*astar_path)
        ax.plot(
            astar_x,
            astar_y,
            c="red",
            linewidth=5,
            zorder=2
        )

        fig.show()

    def _init_graph(self):
        graph = nx.grid_2d_graph(
            self._canvas_dim.x * int(1 / self._step) + 1,
            self._canvas_dim.y * int(1 / self._step) + 1
        )

        def is_inside(node, block):
            x, y = node
            is_in_x = block.x <= x * self._step <= block.x + block.w
            is_in_y = self._canvas_dim.y - block.y - block.h <= y * self._step <= self._canvas_dim.y - block.y
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
                [p[0] * self._step for p in self.graph.nodes],
                [p[1] * self._step for p in self.graph.nodes],
                s=5,
                c="black",
                zorder=1
            )

        # edges
        if plot_edges:
            for p in self.graph.edges:
                ax.plot(
                    [p[0][0] * self._step, p[1][0] * self._step],
                    [p[0][1] * self._step, p[1][1] * self._step],
                    c="gray",
                    zorder=-1
                )

        # blocks
        if plot_blocks:
            for bl in self._blocks:
                rect = patches.Rectangle(
                    (bl.x, self._canvas_dim.y - bl.y - bl.h),
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

    def cord_to_node(self, cord: tuple[float, float]) -> tuple[int, int]:
        return int(cord[0] / self._step), int(cord[1] / self._step)

    def node_to_cord(self, node: tuple[int, int]) -> tuple[float, float]:
        return (node[0] * self._step, node[1] * self._step)

    def update(self, t: float) -> None:
        pass
