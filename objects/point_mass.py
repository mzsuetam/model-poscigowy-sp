import pygame

from .force import Force
from .vect_2d import Vect2d

class PointMass:
    def __init__(self,
                 x=0,
                 y=0,
                 m=1,
                 radius=0.25,
                 color=(255,255,255),
                 friction_factor=5e-2,
                 save_for_plot=False,
                 px_in_m=50
                 ):
        self.px_in_m = px_in_m
        self.eps = 10

        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

        self.bb = pygame.Rect(0,0,0,0)

        self.v = Vect2d(0, 0)
        self.a = Vect2d(0, 0)

        if m <= 0 :
            raise ValueError()
        self.m = m

        self.forces: [Force] = []

        self.friction_factor = friction_factor

        self.v_eps = 1e-2

    @property
    def center(self):
        return Vect2d(self.x, self.y)

    def update_position(self, t, blocks):

        friction = self.friction_factor * self.m * 9.81

        fw = Force(Vect2d(0,0))
        for f in self.forces:
            fw += f

        friction = Vect2d(friction, friction)
        v_1, v_2 = abs(self.v) > self.v_eps
        curr_v = self.v * Vect2d(int(v_1), int(v_2))
        cv_x, cv_y = curr_v.compare(Vect2d(0,0))

        frict_bigger_x, frict_bigger_y = abs(fw.val) < abs(friction)
        mask = Vect2d(
            int(abs(cv_x) or not frict_bigger_x),
            int(abs(cv_y) or not frict_bigger_y)
        )


        cf_x, cf_y = fw.val.compare(Vect2d(0,0))
        cv_x = cv_x if cv_x != 0 else cf_x
        cv_y = cv_y if cv_y != 0 else cf_y
        friction *= Vect2d(cv_x, cv_y)

        fw.val -= friction
        fw.val *= mask

        self.a = fw.val/self.m

        # update position
        d = self.v * t + self.a * t ** 2 / 2
        self.x += d.x
        self.y += d.y
        # step=100
        # for i in range(int(d.x//step)):
        #     self.x += step
        #     self.update_bb()
        #     self.check_block_colliderect(blocks)
        # self.x += d.x % step
        # for i in range(int(d.y//step)):
        #     self.y += step
        #     self.update_bb()
        #     self.check_block_colliderect(blocks)
        # self.y += d.y % step
        self.update_bb()

        new_v = self.v + self.a * t
        new_v_x, new_v_y = abs(new_v) > self.v_eps
        self.v = new_v * Vect2d(int(new_v_x), int(new_v_y))

    def update_bb(self):
        self.bb.x = (self.x - self.radius) * self.px_in_m
        self.bb.y = (self.y - self.radius) * self.px_in_m
        self.bb.w = self.radius*2 * self.px_in_m
        self.bb.h = self.radius*2 * self.px_in_m

    def attach_force(self, force: Force):
        force.anchor = self
        self.forces.append(force)

    def detach_force(self, force:Force):
        force.release_anchor()
        self.forces.remove(force)

    def __str__(self):
        return f"(x,y)=({round(self.x, 2)},{round(self.y, 2)}), v={self.v}, a={self.a}"

    def __dict__(self):
        return {
            "x": self.x,
            "y": self.y,
            "v_x": self.v.x,
            "v_y": self.v.y,
            "a_x": self.a.x,
            "a_y": self.a.y,
        }

    def check_block_colliderect(self, blocks):
        for bl in blocks:
            if self.bb.colliderect(bl.bb):
                if abs(self.bb.top - bl.bb.bottom) < self.eps:
                    # coll from top
                    self.v.y *= 0
                    self.y = (bl.bb.bottom + self.bb.h // 2) / self.px_in_m
                if abs(self.bb.bottom - bl.bb.top) < self.eps:
                    # coll from bottom
                    self.v.y *= 0
                    self.y = (bl.bb.top - self.bb.h // 2) / self.px_in_m
                if abs(self.bb.right - bl.bb.left) < self.eps:
                    # coll from right
                    self.v.x *= 0
                    self.x = (bl.bb.left - self.bb.w // 2) / self.px_in_m
                if abs(self.bb.left - bl.bb.right) < self.eps:
                    # coll from left
                    self.v.x *= 0
                    self.x = (bl.bb.right + self.bb.w // 2) / self.px_in_m

