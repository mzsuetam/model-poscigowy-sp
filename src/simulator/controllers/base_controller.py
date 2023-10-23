from src.simulator.utils.vect_2d import Vect2d


class BaseController:
    def __init__(self) -> None:
        pass

    def _get_force_between(self, p1: Vect2d, p2: Vect2d) -> Vect2d:
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        d = Vect2d(dx, dy)
        return d

    def update(self, t: float, dt: float) -> None:
        pass