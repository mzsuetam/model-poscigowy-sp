
class ViewBox:
    def __init__(self, canvas, x, y, w, h):
        self.canvas = canvas

        self._x = x # [px]
        self._y = y # [px]
        self.w = w # [px]
        self.h = h # [px]

        self._zoom = 1

    def get_subsurface(self, surface):
        new_w = min(max(0, int(self.w / self._zoom)), surface.get_width())
        new_h = min(max(0, int(self.h / self._zoom)), surface.get_height())
        new_x = min(self._x, surface.get_width() - new_w)
        new_y = min(self._y, surface.get_height() - new_h)

        return surface.subsurface(new_x, new_y, new_w, new_h)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if value < 0 or value > self.canvas.get_width() - int(self.w / self._zoom):
            return
        self._x = int(value)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        if value < 0 or value > self.canvas.get_height() - int(self.h / self._zoom):
            return
        self._y = int(value)

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        if value < 0 or self.w / value > self.canvas.get_width() or self.h / value > self.canvas.get_height():
            return
        self._zoom = value

    def __str__(self):
        return f"ViewBox(x={self._x}, y={self._y}, w={self.w}, h={self.h}, zoom={self._zoom})"
