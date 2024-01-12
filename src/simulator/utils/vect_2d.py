import numpy as np


class Vect2d:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def __add__(self, other):
        if type(other) is Vect2d:
            return Vect2d(self.x + other.x, self.y + other.y)
        if type(other) is int or type(other) is float:
            return Vect2d(self.x + other, self.y + other)
        raise RuntimeError()

    def __sub__(self, other):
        if type(other) is Vect2d:
            return Vect2d(self.x - other.x, self.y - other.y)
        if type(other) is int or type(other) is float:
            return Vect2d(self.x - other, self.y - other)
        raise RuntimeError()

    def __mul__(self, other):
        if type(other) is int or type(other) is float:
            return Vect2d(other * self.x, other * self.y)
        if type(other) is Vect2d:
            return Vect2d(self.x * other.x, self.y * other.y)
        raise RuntimeError()

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if type(other) is int or type(other) is float:
            if other == 0:
                raise ZeroDivisionError()
            return Vect2d(self.x / other, self.y / other)
        raise RuntimeError()

    def __pow__(self, power, modulo=None):
        return Vect2d(self.x ** power, self.y ** power)

    def __abs__(self):
        return Vect2d(abs(self.x), abs(self.y))

    def __eq__(self, other):
        if type(other) is int or type(other) is float:
            return Vect2d(self.x == other, self.y == other)
        if type(other) is Vect2d:
            return Vect2d(self.x == other.x, self.y == other.y)

    def __gt__(self, other):
        if type(other) is int or type(other) is float:
            return Vect2d(self.x > other, self.y > other)
        if type(other) is Vect2d:
            return Vect2d(self.x > other.x, self.y > other.y)

    def __ge__(self, other):
        if type(other) is int or type(other) is float:
            return Vect2d(self.x >= other, self.y >= other)
        if type(other) is Vect2d:
            return Vect2d(self.x >= other.x, self.y >= other.y)

    def __lt__(self, other):
        if type(other) is int or type(other) is float:
            return other.__gt__(self)
        if type(other) is Vect2d:
            return other.__gt__(self)

    def __le__(self, other):
        if type(other) is int or type(other) is float:
            return other.__ge__(self)
        if type(other) is Vect2d:
            return other.__ge__(self)

    def copy(self):
        return Vect2d(self.x, self.y)

    def compare(self, other) -> (int, int):
        gt_x, gt_y = self > other
        eq_x, eq_y = self == other

        gt_x = 1 if gt_x else -1
        gt_y = 1 if gt_y else -1

        c_x = 0 if eq_x else gt_x
        c_y = 0 if eq_y else gt_y

        return (c_x, c_y)

    def norm(self):
        return float(np.sqrt(self.x ** 2 + self.y ** 2))

    def distance(self, other):
        return (self - other).norm()

    def __tuple__(self) -> (float, float):
        return (self.x, self.y)

    def as_ints(self) -> (int, int):
        return Vect2d(int(self.x), int(self.y))

    @staticmethod
    def from_singleton(val):
        if type(val) is int or type(val) is float:
            return Vect2d(val, val)
        raise RuntimeError()

    @staticmethod
    def from_tuple(tup):
        if type(tup) is tuple:
            if len(tup) == 2:
                return Vect2d(tup[0], tup[1])
        raise RuntimeError()

    def __iter__(self):
        yield self.x
        yield self.y

    def __str__(self):
        return f"({round(self.x, 2)},{round(self.y, 2)})"
