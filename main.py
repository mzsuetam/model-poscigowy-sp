import pygame
import matplotlib.pyplot as plt
import pandas as pd

from objects.point_mass import PointMass
from objects.force import Force, GravityFroce
from objects.vect_2d import Vect2d
from objects.block import Block

class ViewBox:
    def __init__(self, x, y, w, h):
        self._x = x
        self._y = y
        self.w = w
        self.h = h
        self._zoom = 1


    def get_subsurface(self, surface):
        new_w = min(max(0, int(self.w / self._zoom)), surface.get_width())
        new_h = min(max(0, int(self.h / self._zoom)), surface.get_height())
        new_x = min(self._x, surface.get_width()-new_w)
        new_y = min(self._y, surface.get_height()-new_h)

        return surface.subsurface(new_x, new_y, new_w, new_h)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if value < 0 or value > canvas_w - int(self.w/self._zoom):
            return
        self._x = int(value)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        if value < 0 or value > canvas_h - int(self.h/self._zoom):
            return
        self._y = int(value)

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        if value < 0 or self.w / value > canvas_w or self.h /value > canvas_h:
            return
        self._zoom = value

    def __str__(self):
        return f"ViewBox(x={self._x}, y={self._y}, w={self.w}, h={self.h}, zoom={self._zoom})"

FPS = 60
px_in_m = 50

root_w, root_h = 1600, 960
root = pygame.display.set_mode((root_w, root_h))

canvas_w, canvas_h = root_w * 2, root_h * 2
canvas = pygame.Surface((root_w * 2, root_h * 2))

view_box = ViewBox(0, 0, root_w, root_h)

pygame.display.set_caption("PMS - Point Mass Simulator")

WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

def draw_window(points, blocks):
    # draw background
    canvas.fill(BLACK)
    for i, x in enumerate(range(0, canvas_w, px_in_m)):
        if view_box.zoom >= 1 or i%10 == 0:
            pygame.draw.line(canvas, GRAY, (x, 0), (x, canvas_h), 1 if i % 10 != 0 else 3)
    for i, y in enumerate(range(0, canvas_h, px_in_m)):
        if view_box.zoom >= 1 or i%10 == 0:
            pygame.draw.line(canvas, GRAY, (0, y), (canvas_w, y), 1 if i % 10 != 0 else 3)

    # plot blocks
    for bl in blocks:
        pygame.draw.rect(canvas, bl.color, bl.bb)

    # plot points
    for pt in points:
        center = (int(pt.x * px_in_m), int(pt.y * px_in_m))
        # pygame.draw.rect(canvas, (255,255,0), pt.bb) # bounding box
        pygame.draw.circle(canvas, pt.color, center, pt.radius*px_in_m)

    # draw canvas on root
    vb = view_box.get_subsurface(canvas)
    scaled_vb = pygame.transform.scale(vb, (root.get_width(), root.get_height()))
    root.blit(scaled_vb, (0, 0))

    pygame.display.update()

def simulate():
    mouse = PointMass(0,0)
    points = []
    blocks = []

    wall_w = Block(0,0, h=canvas_h/px_in_m, px_in_m=px_in_m)
    blocks.append(wall_w)
    wall_e = Block(canvas_w/px_in_m - 1, 0, h=canvas_h/px_in_m, px_in_m=px_in_m)
    blocks.append(wall_e)
    wall_n = Block(0, 0, w = canvas_w/px_in_m, px_in_m=px_in_m)
    blocks.append(wall_n)
    wall_s = Block(0, canvas_h/px_in_m -1, w = canvas_w/px_in_m, px_in_m=px_in_m)
    blocks.append(wall_s)

    b1 = Block(15,9, h=2, px_in_m=px_in_m )
    blocks.append(b1)

    p1 = PointMass(10, 10, color=RED)
    # p2 = PointMass(5, 10, color=RED)
    points.append(p1)
    # points.append(p2)

    mouse_force = Force()
    # f1 = Force(Vect2d(9.81*5e-2,0))
    # f1 = Force(Vect2d(,0))
    # p1.attach_force(f1)

    # f2 = GravityFroce()
    # f3 = GravityFroce()
    # p2.attach_force(f2)
    # p1.attach_force(f3)
    #
    # p1.v.y = 1
    # p2.v.y = -1

    focus_point = True
    df_history = pd.DataFrame(columns=["id", "t", "x", "y", "v_x", "v_y", "a_x", "a_y"])
    frame = -1
    game_run = True
    game_clock = pygame.time.Clock()
    while game_run:  # infinite loop in which all events are being checked
        frame += 1
        game_clock.tick(FPS)  # controlling speed of main_loop
        t = frame / float(FPS)
        if t % 1 == 0:
            print(f"t = {t} [s]")
            for p in points:
                print(p)
            # print(view_box)

        # PYGAME_EVENTS_CHECKING
        for event in pygame.event.get():  # testing all events in pygame
            # WINDOW_EXIT
            if event.type == pygame.QUIT:  # checking if event1 happened in this checking loop
                game_run = False  # event1 consequences
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_run = False
                    break
            if event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[2]: # 0-lmb, 1-mmb, 2-pmb
                    focus_point = False
                    dx, dy = pygame.mouse.get_rel()
                    # @FIXME: moving canvas makes 'jumps'
                    view_box.x -= dx / view_box.zoom
                    view_box.y -= dy / view_box.zoom
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[1]: # 0-lmb, 1-mmb, 2-pmb
                    focus_point = not focus_point

            if event.type == pygame.MOUSEWHEEL:
                # view_box.zoom += event.y * 0.1
                if event.y > 0:
                    view_box.zoom /= 1.1
                else:
                    view_box.zoom *= 1.1

        for pt in points:
            pt.check_block_colliderect(blocks)

        if focus_point:
            view_box.x = p1.x * px_in_m - view_box.w //2
            view_box.y = p1.y * px_in_m - view_box.h //2

        mouse.x, mouse.y = pygame.mouse.get_pos()
        mouse.x = (view_box.x + mouse.x / view_box.zoom) // px_in_m
        mouse.y = (view_box.y + mouse.y / view_box.zoom) // px_in_m

        if pygame.mouse.get_pressed()[0]:
            if mouse_force not in p1.forces:
                p1.attach_force(mouse_force)
            mouse_force.pull_to(mouse)
        elif mouse_force in p1.forces:
            p1.detach_force(mouse_force)

        # f2.pull_to(p1)
        # f3.pull_to(p2)

        for i, pt in enumerate(points):
            stats = pt.__dict__()
            stats["id"] = i
            stats["t"] = t
            df_history = pd.concat([df_history, pd.DataFrame(stats, index=[0])], ignore_index=True)

            pt.update_position(1 / FPS, blocks)

        draw_window(points, blocks)

    pygame.quit()

    df_history.to_csv("history.csv", index=False)

    df_hist_1 = df_history[df_history['id']==0]
    fig, axs = plt.subplots(3, 2)
    fig.suptitle("Point mass simulation")
    axs[0][0].plot(df_hist_1["t"], df_hist_1["x"])
    axs[0][0].set_xlabel("t [s]")
    axs[0][0].set_ylabel("x [m]")
    axs[0][0].grid()
    axs[1][0].plot(df_hist_1["t"], df_hist_1["v_x"])
    axs[1][0].set_xlabel("t [s]")
    axs[1][0].set_ylabel("v_x [m/s]")
    axs[1][0].grid()
    axs[2][0].plot(df_hist_1["t"], df_hist_1["a_x"])
    axs[2][0].set_xlabel("t [s]")
    axs[2][0].set_ylabel("a_x [m/s^2]")
    axs[2][0].grid()
    axs[0][1].plot(df_hist_1["t"], df_hist_1["y"])
    axs[0][1].set_xlabel("t [s]")
    axs[0][1].set_ylabel("y [m]")
    axs[0][1].grid()
    axs[1][1].plot(df_hist_1["t"], df_hist_1["v_y"])
    axs[1][1].set_xlabel("t [s]")
    axs[1][1].set_ylabel("v_y [m/s]")
    axs[1][1].grid()
    axs[2][1].plot(df_hist_1["t"], df_hist_1["a_y"])
    axs[2][1].set_xlabel("t [s]")
    axs[2][1].set_ylabel("a_y [m/s^2]")
    axs[2][1].grid()
    # plt.show()

if __name__ == "__main__":
    simulate()
