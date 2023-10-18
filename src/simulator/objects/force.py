from src.simulator.utils.vect_2d import Vect2d


class Force:
    def __init__(
            self,
            val = Vect2d(0,0)
    ) -> None:
        self._anchor = None
        self.val: Vect2d = val

    @property
    def anchor(self):
        return self._anchor

    @anchor.setter
    def anchor(self, point_mass) -> None:
        if self._anchor is not None:
            raise RuntimeError()
        self._anchor = point_mass

    def release_anchor(self) -> None:
        self._anchor = None

    def pull_to(self, point_mass) -> None:
        end = point_mass.center
        start = self.anchor.center
        self.val = end - start

    def __add__(self, other):
        return Force(self.val + other.val)

    def __sub__(self,other):
        return Force(self.val - other.val)

    def __truediv__(self, other):
        if type(other) is int or type(other) is float:
            if other == 0:
                raise ZeroDivisionError()
            return Force(self.val/other)
        raise RuntimeError()

    def __mul__(self, other):
        if type(other) is int or type(other) is float:
            return Force(self.val*other)
        raise RuntimeError()
