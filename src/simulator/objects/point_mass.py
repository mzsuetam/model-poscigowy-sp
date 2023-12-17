import numpy as np
import pygame

from src.simulator.utils.vect_2d import Vect2d
from src.simulator.utils import colors
from src.simulator.utils.colors import Color
from src.simulator.utils.constants import px_in_m, eps_px, v_eps


class PointMass:
    def __init__(self,
                 id,
                 x=0,
                 y=0,
                 m=1,
                 radius=0.2,
                 color=colors.RED,
                 show=True,
                 save_history=True,
                 friction_factor=5e-2,
                 ):
        self.id: int = id

        self.x: float = x  # [m]
        self.y: float = y  # [m]
        if m <= 0:
            raise ValueError()
        self.m: float = m
        self.radius: float = radius  # [m]
        self.color: Color = color
        self.show: bool = show
        self.save_history: bool = save_history
        self.friction_factor: float = friction_factor

        self._bb: pygame.Rect = pygame.Rect(0, 0, 0, 0)

        self._v: Vect2d = Vect2d(0, 0)

        self._f_resultant: Vect2d = Vect2d(0, 0)

    @property
    def center(self) -> Vect2d:
        return Vect2d(self.x, self.y)

    def update_position(self, dt, blocks) -> None:
        # consult friction force and update acceleration
        a = self.get_acceleration()

        # update velocity
        prev_v = self._v.copy()
        new_v = self._v + a * dt
        new_v_x, new_v_y = abs(new_v) > v_eps
        self._v = new_v * Vect2d(int(new_v_x), int(new_v_y))

        # update position
        d = prev_v * dt + a * dt ** 2 / 2

        sections = 100
        for _ in np.linspace(0, d.x, sections):
            if abs(self._v.x) > 0:
                self.x += d.x / sections
            if abs(self._v.y) > 0:
                self.y += d.y / sections
            self._update_bb()
            correct_pos = self._check_collision_with_objects(blocks)
            if correct_pos.x != -1:
                self.x = correct_pos.x
                self._v.x *= 0
            if correct_pos.y != -1:
                self.y = correct_pos.y
                self._v.y *= 0
        self._update_bb()

    def _check_collision_with_objects(self, objects) -> Vect2d:
        corr_x, corr_y = -1, -1
        for bl in objects:
            if self._bb.colliderect(bl._bb):
                if abs(self._bb.top - bl._bb.bottom) < eps_px / 2:
                    # coll from top
                    corr_y = (bl._bb.bottom + self._bb.h // 2) / px_in_m
                if abs(self._bb.bottom - bl._bb.top) < eps_px / 2:
                    # coll from bottom
                    corr_y = (bl._bb.top - self._bb.h // 2) / px_in_m
                if abs(self._bb.right - bl._bb.left) < eps_px / 2:
                    # coll from right
                    corr_x = (bl._bb.left - self._bb.w // 2) / px_in_m
                if abs(self._bb.left - bl._bb.right) < eps_px / 2:
                    # coll from left
                    corr_x = (bl._bb.right + self._bb.w // 2) / px_in_m

        corr = Vect2d(corr_x, corr_y)
        if corr_x != -1 and corr_y != -1:
            pass
        return corr

    def is_colliding_with(self, other) -> bool:
        d = (self.center - other.center).norm()
        return d <= self.radius + other.radius

    def _update_bb(self) -> None:
        self._bb.x = (self.x - self.radius) * px_in_m
        self._bb.y = (self.y - self.radius) * px_in_m
        self._bb.w = self.radius * 2 * px_in_m
        self._bb.h = self.radius * 2 * px_in_m

    def consult_friction_force(self, f: Vect2d) -> Vect2d:

        friction_val = self.friction_factor * self.m * 9.81
        friction = Vect2d(friction_val, friction_val)

        v = abs(self._v) > v_eps
        curr_v = self._v * v.as_ints()
        cv_x, cv_y = curr_v.compare(Vect2d(0, 0))

        frict_bigger_x, frict_bigger_y = abs(f) < abs(friction)
        mask = Vect2d(
            int(abs(cv_x) or not frict_bigger_x),
            int(abs(cv_y) or not frict_bigger_y)
        )

        cf_x, cf_y = f.compare(Vect2d(0, 0))
        cv_x = cv_x if cv_x != 0 else cf_x
        cv_y = cv_y if cv_y != 0 else cf_y
        friction *= Vect2d(cv_x, cv_y)

        f_resultant = f - friction
        f_resultant *= mask

        return f_resultant

    def add_force(self, force: Vect2d) -> None:
        self._f_resultant += force

    def subtract_force(self, force: Vect2d) -> None:
        self._f_resultant -= force

    def get_velocity(self) -> Vect2d:
        return self._v

    def get_acceleration(self) -> Vect2d:
        f = self.consult_friction_force(self._f_resultant)
        return f / self.m

    def __str__(self) -> str:
        return (f"PointMass(id={self.id}, x={round(self.x, 2)}, y={round(self.y, 2)}),"
                f" v={self._v}, a={self.get_acceleration()}")

    def __dict__(self) -> dict:
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "v_x": self._v.x,
            "v_y": self._v.y,
            "a_x": self.get_acceleration().x,
            "a_y": self.get_acceleration().y,
        }
