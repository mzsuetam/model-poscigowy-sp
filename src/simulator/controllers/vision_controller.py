import networkx as nx
import numpy as np
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
                 unknown_score: int = 1000,
                 crossroads_score: int = 100,
                 known_score: int = 1000,
                 edge_threshold: int = 4,
                 priority_queue_size: int = 1000
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
        # SCORES
        self._goal_score = goal_score
        self._unknown_score = unknown_score
        self._known_score = known_score
        self._crossroads_score = crossroads_score
        # VISION
        self._edge_threshold = edge_threshold
        self._priority_queue_size = priority_queue_size
        # self._unvisited_nodes =
        self._vision_nodes = set({(x, y) for x in range(self._canvas_dim.x) for y in range(self._canvas_dim.y)
                                  if (x, y) in self._graph})
        self._target_nodes = self._vision_nodes.copy()
        self._visited_nodes = set()
        self._seen_crossroads = set()
        self._crossroads_threshold = 3
        self._previous_len = 0
        self._priority_queue = []

    def update(self, t, dt) -> None:
        self._priority_queue = []
        self.clear_target_nodes()
        for angle in range(0, 360, self._angle_step):
            self.view_length(angle)
        self.target_update()
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

    def view_length(self, angle) -> int:
        view_length = 1
        current_position = (self._managed_point.x, self._managed_point.y)
        while True:
            end_view_position = hlp.calc_end_line(
                current_position, angle, view_length)
            if self.view_collision(end_view_position, angle):
                return view_length
            view_length += 1

    def view_collision(self, cord, angle) -> bool:
        cord = (int(cord[0]), int(cord[1]))
        if cord[0] < 0 or cord[0] > self._canvas_dim.x \
                or cord[1] < 0 or cord[1] > self._canvas_dim.y:
            return True
        # At the edge of the map
        if cord[0] == 0 or cord[0] == self._canvas_dim.x \
                or cord[1] == 0 or cord[1] == self._canvas_dim.y:
            if cord in self._target_nodes:
                self._visited_nodes.add(cord)
                self._target_nodes.remove(cord)
            return True
        # collision with block
        for bl in self._blocks[4:]:
            if bl.x <= cord[0] <= bl.x + bl.w and bl.y + bl.h >= cord[1] >= bl.y:
                if cord in self._target_nodes:
                    self._visited_nodes.add(cord)
                    self._target_nodes.remove(cord)
                return True
        # found destination point
        if int(cord[0]) == self._destination_point.x and int(cord[1]) == self._destination_point.y:
            self._visited_nodes.add(cord)
            return True
        if cord in self._target_nodes:
            self._visited_nodes.add(cord)
            self._target_nodes.remove(cord)
        return False

    def clear_target_nodes(self):
        if self._target_nodes:
            target_node = (self._destination_point.x, self._destination_point.y)
            if target_node not in self._visited_nodes:
                target_node = None
            self._target_nodes = [node for node in self._target_nodes if node not in self._visited_nodes]
            if target_node:
                self._target_nodes.append(target_node)

    def target_update(self):
        for node in self._target_nodes:
            dist = hlp.calc_euclidean_dist(
                node, (self._managed_point.x, self._managed_point.y))
            if node[0] == self._destination_point.x and node[1] == self._destination_point.y and node in self._visited_nodes:
                heapq.heappush(self._priority_queue, (VisionNode(node, dist, self._goal_score)))
            else:
                heapq.heappush(self._priority_queue, (VisionNode(node, dist, self._unknown_score)))

    def add_crossroads(self, view_length, angle) -> None:
        current_position = (self._managed_point.x, self._managed_point.y)
        end_view_position = hlp.calc_end_line(current_position, angle, view_length)
        previous_position = hlp.calc_end_line(current_position, angle - self._angle_step, self._previous_len)
        crossroads_position = ((end_view_position[0] + previous_position[0]) // 2,
                               (end_view_position[1] + previous_position[1]) // 2)
        crossroads_length = hlp.calc_euclidean_dist(crossroads_position, current_position)
        if crossroads_position not in self._seen_crossroads \
                and all(hlp.calc_euclidean_dist(crossroads_position, seen_position) > self._crossroads_threshold
                        for seen_position in self._seen_crossroads):
            heapq.heappush(self._priority_queue,
                           VisionNode(crossroads_position, crossroads_length, self._crossroads_score))
            self._seen_crossroads.add(crossroads_position)

    def clean_current_location(self):
        current_position = (int(self._managed_point.x), int(self._managed_point.y))
        self._priority_queue = \
            [node for node in self._priority_queue if hlp.calc_euclidean_dist(node.position, current_position) > 1
             and node.heuristic_cost != self._goal_score]

    def lazy_update(self) -> bool:
        # Instead of updating all nodes each time, the agent moves,
        # we check the value of a node when it's picked as the most desired one.
        temporary_goal = heapq.heappop(self._priority_queue)
        while True:
            # if temporary_goal.heuristic_cost == self._unknown_score and \
            #         temporary_goal.position in self._visited_nodes:
            #     temporary_goal.heuristic_cost = self._known_score
            updated_position = hlp.calc_euclidean_dist(temporary_goal.position,
                                                       (self._managed_point.x, self._managed_point.y))
            temporary_goal.distance_from_node = updated_position
            heapq.heappush(self._priority_queue, temporary_goal)
            if self._priority_queue[0].distance_from_node < 0.6 and \
                    self._priority_queue[0].heuristic_cost != self._goal_score:
                heapq.heappop(self._priority_queue)
            elif temporary_goal == self._priority_queue[0]:
                self._priority_queue = heapq.nsmallest(
                    self._priority_queue_size, self._priority_queue)
                print("goal set:", temporary_goal.position,
                      temporary_goal.heuristic_cost, temporary_goal.distance_from_node)
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
