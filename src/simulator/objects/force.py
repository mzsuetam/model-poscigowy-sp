from .vect_2d import Vect2d
import math

class Force:
    def __init__(
            self,
            val = Vect2d(0,0)):
        self._anchor = None
        self.val = val

    @property
    def anchor(self):
        return self._anchor

    @anchor.setter
    def anchor(self, point_mass):
        if self._anchor is not None:
            raise RuntimeError()
        self._anchor = point_mass

    def release_anchor(self):
        self._anchor = None

    def pull_to(self, point_mass):
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


class GravityFroce(Force):
    G = 6.67 * 1e-2 # * 10e-11 who cares lol

    def __init__(
            self,
            val = Vect2d(0,0)):
        super().__init__(val)

    def pull_to(self, point_mass):
        M1 = self.anchor.m
        M2 = point_mass.m

        end = point_mass.center
        start = self.anchor.center
        R = end - start

        self.val = R * abs(R) * self.G * M1 * M2
