import networkx as nx
import heapq
import matplotlib.pyplot as plt

import src.simulator.utils.helpers as hlp
from src.simulator.utils.vision_node import VisionNode
from src.simulator.controllers.base_graph_controller import BaseGraphController
from src.simulator.objects.block import Block
from src.simulator.objects.point_mass import PointMass
from src.simulator.utils.vect_2d import Vect2d


class VisionController(BaseGraphController):
    def __init__(self,
                 managed_point: PointMass,
                 destination_point: Vect2d | PointMass,
                 canvas_dim: Vect2d,
                 blocks: [Block],
                 gap_between_nodes: float = 1 / 2,
                 steps_ahead: int = 1,
                 angle_step: int = 4,
                 goal_score: int = 1,
                 unknown_score: int = 10,
                 known_score: int = 1000
                 ):
        super().__init__(
            canvas_dim,
            blocks,
            gap_between_nodes
        )
        self._blocks: [Block] = blocks  # [m]
        self._managed_point: PointMass = managed_point
        self._destination_point: Vect2d | PointMass = destination_point
        self._canvas_dim: Vect2d = canvas_dim
        self._gap_between_nodes = gap_between_nodes
        self._angle_step = angle_step
        self._steps_ahead = steps_ahead
        self.f = Vect2d(0, 0)
        self._goal_score = goal_score
        self._unknown_score = unknown_score
        self._known_score = known_score
        self._priority_queue = []


    def update(self, t, dt) -> None:
        for angle in range(0, 360, self._angle_step):
            self.view_length(angle)
        self.lazy_update()
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

    def view_length(self, angle):
        view_radius = 1
        current_position = (self._managed_point.x, self._managed_point.y)
        while True:
            end_view_position = hlp.calc_end_line(current_position, angle, view_radius)
            if self.view_collision(end_view_position, angle):
                break
            view_radius += 1

    def view_collision(self, cord, angle) -> bool:
        cord = (int(cord[0]), int(cord[1]))
        if cord[0] < 0 or cord[0] > self._canvas_dim.x \
                or cord[1] < 0 or cord[1] > self._canvas_dim.y:
            return True
        distance = hlp.calc_euclidean_dist(cord, (self._managed_point.x, self._managed_point.y))
        # At the edge of the map
        if cord[0] == 0 or cord[0] == self._canvas_dim.x \
                or cord[1] == 0 or cord[1] == self._canvas_dim.y:
            heapq.heappush(self._priority_queue, VisionNode(cord, distance, self._known_score))
            return True
        # collision with block
        for bl in self._blocks[4:]:
            if bl.x <= cord[0] <= bl.x + bl.w and bl.y + bl.h >= cord[1] >= bl.y:
                heapq.heappush(self._priority_queue, VisionNode(cord, distance, self._known_score))
                return True
        # found destination point
        if int(cord[0]) == self._destination_point.x and int(cord[1]) == self._destination_point.y:
            heapq.heappush(self._priority_queue, VisionNode(cord, distance, self._goal_score))
            print("\tGOOOOOL: ", angle)
            return True
        # heapq.heappush(self._priority_queue, VisionNode(cord, distance, self._known_score))
        return False

    def lazy_update(self) -> bool:
        # Instead of updating all nodes each time, the agent moves,
        # we check the value of a node when it's picked as the most desired one.
        temporary_goal = heapq.heappop(self._priority_queue)
        while True:
            updated_position = hlp.calc_euclidean_dist(temporary_goal.position,
                                                       (self._managed_point.x, self._managed_point.y))
            temporary_goal.distance_from_node = updated_position
            heapq.heappush(self._priority_queue, temporary_goal)
            if temporary_goal == self._priority_queue[0]:
                return True
            temporary_goal = heapq.heappop(self._priority_queue)

    def _get_astar_path(self):
        dest = self._priority_queue[0]
        astar_path = nx.astar_path(
            self._graph,
            self.cord_to_node(
                tuple(self._managed_point.center),
                find_closest_for_nonexistent=True
            ),
            self.cord_to_node(
                tuple(dest.position),
                find_closest_for_nonexistent=True
            )
        )
        return astar_path

    @staticmethod
    def get_type():
        return "VisionController"
