class VisionNode:
    def __init__(self, position, distance_from_node, heuristic_cost):
        self.position = position
        self.distance_from_node = distance_from_node
        self.heuristic_cost = heuristic_cost

    def __lt__(self, other):
        return (self.heuristic_cost * self.distance_from_node) < \
            (other.heuristic_cost * other.distance_from_node)

    def __eq__(self, other):
        if isinstance(other, VisionNode):
            return (self.position == other.position) and \
                   (self.distance_from_node == other.distance_from_node) and \
                   (self.heuristic_cost == other.heuristic_cost)
        return False
