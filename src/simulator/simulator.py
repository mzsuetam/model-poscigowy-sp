import pygame
import pandas as pd

from src.simulator.objects.point_mass import PointMass
from src.simulator.objects.force import Force
from src.simulator.objects.block import Block
from src.simulator.view_box import ViewBox
from src.simulator.utils import colors


class simulator:

    def __init__(self,
                 window_w=1600,
                 window_h=960,
                 canvas_w=None,
                 canvas_h=None,
                 log=False
                 ):
        self.FPS = 60
        self.px_in_m = 50

        self.root_w, self.root_w = window_w, window_h
        self.root = pygame.display.set_mode((window_w, window_h))

        canvas_w = window_w * 2 if canvas_w is None else window_w
        canvas_h = window_w * 2 if canvas_h is None else window_h
        self.canvas = pygame.Surface((canvas_w, canvas_h))

        self.view_box = ViewBox(self.root, 0, 0, window_w, window_h)

        self.log = log

        self.simulation_elements = {
            "points": [],
            "blocks": []
        }

        pygame.display.set_caption("Model Pościgowy")

    def _draw_window(self, points, blocks):
        # draw background
        self.canvas.fill(colors.BLACK)
        for i, x in enumerate(range(0, self.canvas.get_width(), self.px_in_m)):
            if self.view_box.zoom >= 1 or i % 10 == 0:
                pygame.draw.line(self.canvas, colors.GRAY, (x, 0), (x, self.canvas.get_height()),
                                 1 if i % 10 != 0 else 3)
        for i, y in enumerate(range(0, self.canvas.get_height(), self.px_in_m)):
            if self.view_box.zoom >= 1 or i % 10 == 0:
                pygame.draw.line(self.canvas, colors.GRAY, (0, y), (self.canvas.get_width(), y),
                                 1 if i % 10 != 0 else 3)

        # plot blocks
        for bl in blocks:
            pygame.draw.rect(self.canvas, bl.color, bl.bb)

        # plot points
        for pt in points:
            center = (int(pt.x * self.px_in_m), int(pt.y * self.px_in_m))
            # pygame.draw.rect(canvas, (255,255,0), pt.bb) # bounding box
            pygame.draw.circle(self.canvas, pt.color, center, pt.radius * self.px_in_m)

        # draw canvas on root
        vb = self.view_box.get_subsurface(self.canvas)
        scaled_vb = pygame.transform.scale(vb, (self.root.get_width(), self.root.get_height()))
        self.root.blit(scaled_vb, (0, 0))

        pygame.display.update()

    def simulate(self):
        print("Initializing simulation...")
        mouse = PointMass(0, 0)
        points = []
        blocks = []

        wall_w = Block(0, 0, h=self.canvas.get_height() / self.px_in_m, px_in_m=self.px_in_m)
        blocks.append(wall_w)
        wall_e = Block(self.canvas.get_width() / self.px_in_m - 1, 0, h=self.canvas.get_height() / self.px_in_m,
                       px_in_m=self.px_in_m)
        blocks.append(wall_e)
        wall_n = Block(0, 0, w=self.canvas.get_width() / self.px_in_m, px_in_m=self.px_in_m)
        blocks.append(wall_n)
        wall_s = Block(0, self.canvas.get_height() / self.px_in_m - 1, w=self.canvas.get_width() / self.px_in_m,
                       px_in_m=self.px_in_m)
        blocks.append(wall_s)

        b1 = Block(15, 9, h=2, px_in_m=self.px_in_m)
        blocks.append(b1)

        p1 = PointMass(10, 10, color=colors.RED)
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
        print("Starting simulation...")
        while game_run:  # infinite loop in which all events are being checked
            frame += 1
            game_clock.tick(self.FPS)  # controlling speed of main_loop
            t = frame / float(self.FPS)
            if t % 1 == 0:
                if self.log:
                    print(f"t = {t} [s]")
                    for p in points:
                        print(p)

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
                    if pygame.mouse.get_pressed()[2]:  # 0-lmb, 1-mmb, 2-pmb
                        focus_point = False
                        dx, dy = pygame.mouse.get_rel()
                        # @FIXME: moving canvas makes 'jumps'
                        self.view_box.x -= dx / self.view_box.zoom
                        self.view_box.y -= dy / self.view_box.zoom
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.mouse.get_pressed()[1]:  # 0-lmb, 1-mmb, 2-pmb
                        focus_point = not focus_point

                if event.type == pygame.MOUSEWHEEL:
                    # self.view_box.zoom += event.y * 0.1
                    if event.y > 0:
                        self.view_box.zoom /= 1.1
                    else:
                        self.view_box.zoom *= 1.1

            for pt in points:
                pt.check_block_colliderect(blocks)

            if focus_point:
                self.view_box.x = p1.x * self.px_in_m - self.view_box.w // 2
                self.view_box.y = p1.y * self.px_in_m - self.view_box.h // 2

            mouse.x, mouse.y = pygame.mouse.get_pos()
            mouse.x = (self.view_box.x + mouse.x / self.view_box.zoom) // self.px_in_m
            mouse.y = (self.view_box.y + mouse.y / self.view_box.zoom) // self.px_in_m

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

                pt.update_position(1 / self.FPS, blocks)

            self._draw_window(points, blocks)

        pygame.quit()
        return df_history

    def add_point_mass(
            x=None,
            y=None,
            **kwargs
    ):
        pass
