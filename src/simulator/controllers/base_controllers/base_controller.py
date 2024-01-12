from src.simulator.utils.vect_2d import Vect2d


class BaseController:
    def __init__(self) -> None:
        pass

    def get_force_between(self, p1: Vect2d, p2: Vect2d, max_value=None) -> Vect2d:
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        d = Vect2d(dx, dy)
        if max_value is not None:
            if d.norm() > max_value:
                d = d / d.norm() * max_value
        return d

    # @TODO: add subgraph getter with support for wycinanie obszarów

    def apply(self, t: float, dt: float) -> None:
        raise NotImplementedError()
    def update(self, t: float, dt: float) -> Vect2d:
        raise NotImplementedError()

    @staticmethod
    def get_type():
        raise NotImplementedError()