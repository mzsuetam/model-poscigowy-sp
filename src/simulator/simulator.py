import pygame
import pandas as pd

from src.simulator.objects.point_mass import PointMass
from src.simulator.objects.block import Block
from src.simulator.utils.vect_2d import Vect2d
from src.simulator.view_box import ViewBox
from src.simulator.utils import colors
from src.simulator.utils.constants import px_in_m


class simulator:

    def __init__(self,
                 window_w=1600, # [px]
                 window_h=960,  # [px]
                 canvas_w=None, # [m]
                 canvas_h=None, # [m]
                 ):
        self._FPS = 60

        self._root_w = window_w # [px]
        self._root_h = window_h # [px]
        self._root = pygame.display.set_mode((window_w, window_h))

        self.canvas_w = 50 if canvas_w is None else canvas_w # [m]
        self.canvas_h = 50 if canvas_h is None else canvas_h # [m]
        self._canvas = pygame.Surface((self.canvas_w * px_in_m, self.canvas_h * px_in_m))

        self._view_box = ViewBox(self._canvas, 0, 0, window_w, window_h)

        self._is_log = True

        self._simulation_elements = {
            "points": [],
            "blocks": []
        }

        self._mouse_point = self.add_point_mass(10, 10, show=False)  # mouse point

        self.focusable_points = []

        self._controllers = []

        self.add_block(0, 0, h=self._canvas.get_height() // px_in_m)
        self.add_block(self._canvas.get_width() / px_in_m - 1, 0, h=self._canvas.get_height() // px_in_m)
        self.add_block(0, 0, w=self._canvas.get_width() // px_in_m)
        self.add_block(0, self._canvas.get_height() / px_in_m - 1, w=self._canvas.get_width() // px_in_m)

        pygame.display.set_caption("Model Pościgowy")

    def _draw_window(self, draw_vectors=False, draw_bb=False):
        # draw background
        self._canvas.fill(colors.BLACK)
        for i, x in enumerate(range(0, self._canvas.get_width(), px_in_m)):
            if self._view_box.zoom >= 1 or i % 10 == 0:
                pygame.draw.line(self._canvas, colors.GRAY, (x, 0), (x, self._canvas.get_height()),
                                 1 if i % 10 != 0 else 3)
        for i, y in enumerate(range(0, self._canvas.get_height(), px_in_m)):
            if self._view_box.zoom >= 1 or i % 10 == 0:
                pygame.draw.line(self._canvas, colors.GRAY, (0, y), (self._canvas.get_width(), y),
                                 1 if i % 10 != 0 else 3)

        # plot blocks
        for bl in self._simulation_elements['blocks']:
            pygame.draw.rect(self._canvas, bl.color, bl._bb)

        # plot points
        for pt in self._simulation_elements['points']:
            center = tuple((pt.center * px_in_m).as_ints())
            if pt.show:
                if draw_vectors:
                    pygame.draw.line(self._canvas, colors.BLUE, center, tuple(((pt.center + pt._v) * px_in_m).as_ints()),
                                     2)
                    pygame.draw.line(self._canvas, colors.GREEN, center,
                                     tuple(((pt.center + pt.get_acceleration()) * px_in_m).as_ints()), 2)
                if draw_bb:
                    pygame.draw.rect(self._canvas, (255, 255, 0), pt._bb)  # bounding box
                pygame.draw.circle(self._canvas, pt.color, center, pt.radius * px_in_m)

        # draw canvas on root
        vb = self._view_box.get_subsurface(self._canvas)
        # @FIXME: too small canvas is oddly streched
        scaled_vb = pygame.transform.scale(vb, (self._root.get_width(), self._root.get_height()))
        self._root.blit(scaled_vb, (0, 0))

        pygame.display.update()

    def start(self, log=False):
        self._is_log = log
        print("Initializing simulation...")

        focus_point = -1
        df_history = pd.DataFrame(columns=["id", "x", "y", "v_x", "v_y", "a_x", "a_y"])
        frame = -1
        game_run = True
        game_clock = pygame.time.Clock()

        print("Starting simulation...")
        while game_run:  # infinite loop in which all events are being checked
            frame += 1
            game_clock.tick(self._FPS)  # controlling speed of main_loop
            t = frame / float(self._FPS)
            if t % 1 == 0:
                if self._is_log:
                    self._log_header(f"t = {t} [s]")
                    self._log(self._view_box)
                    for pt in self._simulation_elements['points']:
                        if pt.show:
                            self._log(pt)

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
                        focus_point = -1
                        dx, dy = pygame.mouse.get_rel()
                        self._view_box.x -= dx / self._view_box.zoom
                        self._view_box.y -= dy / self._view_box.zoom
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.mouse.get_pressed()[1]:  # 0-lmb, 1-mmb, 2-pmb
                        # next focus point
                        if focus_point + 1 < len(self.focusable_points):
                            focus_point += 1
                        else:
                            focus_point = -1
                if event.type == pygame.MOUSEWHEEL:
                    # self.view_box.zoom += event.y * 0.1
                    if event.y < 0:
                        self._view_box.zoom /= 1.1
                    else:
                        self._view_box.zoom *= 1.1

            # FOCUS_POINT
            if focus_point != -1:
                self._view_box.x = (self.focusable_points[focus_point].x * px_in_m
                                    - self._view_box.w // 2)
                self._view_box.y = (self.focusable_points[focus_point].y * px_in_m
                                    - self._view_box.h // 2)

            # MOUSE_POSITION
            self._mouse_point.x, self._mouse_point.y = pygame.mouse.get_pos()
            self._mouse_point.x = (self._view_box.x + self._mouse_point.x / self._view_box.zoom) / px_in_m
            self._mouse_point.y = (self._view_box.y + self._mouse_point.y / self._view_box.zoom) / px_in_m

            # CONTROLLERS_UPDATE
            for c in self._controllers:
                c.update(t)

            # POINTS_UPDATE
            for pt in self._simulation_elements['points']:
                pt.update_position(1 / self._FPS, self._simulation_elements['blocks'])

                if pt.show:
                    stats = pt.__dict__()
                    df_history = pd.concat([df_history, pd.DataFrame(stats, index=[t])])

            # WINDOW_DRAW
            self._draw_window(
                draw_vectors=True,
                draw_bb=False
            )

        pygame.quit()

        return df_history

    def add_block(self, x, y, w=1, h=1, color=colors.DARKGRAY):
        # @TODO: add check if block
        #  - is not inside block
        #  - is inside canvas

        id = len(self._simulation_elements['blocks'])
        bl = Block(id, x, y, w, h, color)
        self._simulation_elements['blocks'].append(bl)
        return bl

    def add_point_mass(
            self,
            x=0,
            y=0,
            m=1,
            radius=0.2,
            color=colors.RED,
            show=True,
            friction_factor=5e-2,
            enable_focus=False
    ):
        # @TODO: add check if point
        #  - is not inside block
        #  - is inside canvas

        id = len(self._simulation_elements['points'])
        pt = PointMass(
            id=id,
            x=x,
            y=y,
            m=m,
            radius=radius,
            color=color,
            show=show,
            friction_factor=friction_factor
        )
        self._simulation_elements['points'].append(pt)
        if enable_focus:
            self.focusable_points.append(pt)
        return pt

    def get_canvas_dim(self):
        return Vect2d(self.canvas_w, self.canvas_h)

    def get_mouse_point(self):
        return self._mouse_point

    def get_mouse(self):
        return pygame.mouse

    def get_blocks(self):
        return self._simulation_elements['blocks']

    def add_controller(self, controller):
        self._controllers.append(controller)

    def _log(self, msg, indent=1):
        if self._is_log:
            print("\t" * indent, msg, sep="")

    def _log_header(self, msg):
        self._log(msg, indent=0)
