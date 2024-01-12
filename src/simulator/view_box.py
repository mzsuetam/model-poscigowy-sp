import pygame as pg
class ViewBox:
    def __init__(
            self,
            canvas,
            x = None,
            y = None,
            zoom = None
    ):
        self.canvas: pg.Surface = canvas

        if x is None:
            x = 0
        if y is None:
            y = 0
        self._x = x # [px]
        self._y = y # [px]

        if zoom is None:
            zoom = 1
        self._zoom = zoom

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = int(value)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = int(value)

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        if value > 2:
            value = 2
        if value < .4:
            value = .4
        self._zoom = value

    def get_height(self):
        return self.canvas.get_height()

    def get_width(self):
        return self.canvas.get_width()

    def get_canvas(self):
        return self.canvas