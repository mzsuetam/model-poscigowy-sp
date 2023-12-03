import pygame
import pandas as pd
import json

from src.simulator.controllers.vision_controller import VisionController
from src.simulator.controllers.astar_controller import AstarController
from src.simulator.controllers.to_mouse_controller import ToMouseController
from src.simulator.objects.point_mass import PointMass
from src.simulator.objects.block import Block
from src.simulator.utils.vect_2d import Vect2d
from src.simulator.view_box import ViewBox
from src.simulator.utils import colors
from src.simulator.utils.constants import px_in_m


class Simulator:

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

        self._points_by_names = {}

        self._mouse_point = self.add_point_mass(10, 10, show=False, save_history=False)  # mouse point

        self.focusable_points = []

        self._controllers = []

        self.add_block(0, 0, h=self._canvas.get_height() // px_in_m)
        self.add_block(self._canvas.get_width() / px_in_m - 1, 0, h=self._canvas.get_height() // px_in_m)
        self.add_block(0, 0, w=self._canvas.get_width() // px_in_m)
        self.add_block(0, self._canvas.get_height() / px_in_m - 1, w=self._canvas.get_width() // px_in_m)

        pygame.display.set_caption("Model Pościgowy")

        self._pygame_run = False

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
        self._pygame_run = True
        game_clock = pygame.time.Clock()

        print("Starting simulation...")
        while self._pygame_run:  # infinite loop in which all events are being checked
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
                    self._pygame_run = False  # event1 consequences
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._pygame_run = False
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
                c.update(t, 1 / self._FPS)

            # POINTS_UPDATE
            for pt in self._simulation_elements['points']:
                pt.update_position(1 / self._FPS, self._simulation_elements['blocks'])

                if pt.save_history:
                    stats = pt.__dict__()
                    df_history = pd.concat([df_history, pd.DataFrame(stats, index=[t])])

            # WINDOW_DRAW
            self._draw_window(
                draw_vectors=True,
                draw_bb=False
            )

        pygame.quit()

        return df_history

    def stop(self):
        self._pygame_run = False

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
            save_history=True,
            friction_factor=5e-2,
            enable_focus=False,
            name=None
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
            save_history=save_history,
            friction_factor=friction_factor
        )
        if name is not None:
            if name in self._points_by_names:
                raise ValueError(f"Point with name '{name}' already exists")
        else:
            name = f"point_{id}"
        self._points_by_names[name] = pt

        self._simulation_elements['points'].append(pt)
        if enable_focus:
            self.focusable_points.append(pt)
        return pt

    def get_canvas_dim(self):
        return Vect2d(self.canvas_w, self.canvas_h)

    def get_mouse(self):
        return pygame.mouse

    def get_mouse_point(self):
        return self._mouse_point

    def get_point_mass_by_name(self, name):
        return self._points_by_names.get(name)

    def get_blocks(self, include_borders=False):
        if include_borders:
            return self._simulation_elements['blocks']
        return self._simulation_elements['blocks'][4:]

    def add_controller(self, controller):
        self._controllers.append(controller)

    def _log(self, msg, indent=1):
        if self._is_log:
            print("\t" * indent, msg, sep="")

    def _log_header(self, msg):
        self._log(msg, indent=0)

    def get_id_to_name(self):
        return {pt.id: name for name, pt in self._points_by_names.items()}

    @staticmethod
    def from_file(path):
        if not path.endswith(".json"):
            raise ValueError("File must be .json")

        try:
            with open(path, "r") as f:
                json_txt = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File {path} not found")

        config = json.loads(json_txt)

        window_w = config["window"]["w_px"]
        window_h = config["window"]["h_px"]
        canvas_w = config["canvas"]["w"]
        canvas_h = config["canvas"]["h"]
        sim = Simulator(
            window_w=window_w,
            window_h=window_h,
            canvas_w=canvas_w,
            canvas_h=canvas_h
        )

        objects = config["objects"]

        blocks = objects["blocks"]
        for block in blocks:
            sim.add_block(
                block["x"],
                block["y"],
                block["w"] if "w" in block else 1,
                block["h"] if "h" in block else 1,
                block["color"] if "color" in block else colors.DARKGRAY
            )
        print(f"Added blocks ({len(blocks)})")

        points = objects["points"]
        for point in points:
            sim.add_point_mass(
                point["x"],
                point["y"],
                point["m"] if "m" in point else 1,
                point["radius"] if "radius" in point else 0.2,
                point["color"] if "color" in point else colors.RED,
                point["show"] if "show" in point else True,
                point["save_history"] if "save_history" in point else True,
                point["friction_factor"] if "friction_factor" in point else 5e-2,
                point["enable_focus"] if "enable_focus" in point else False,
                point["name"] if "name" in point else None
            )
            print(f"Added point {point['name']} at ({point['x']}, {point['y']})")

        controllers = config["controllers"]
        for controller in controllers:
            if controller["type"] == ToMouseController.get_type():
                managed_point = sim.get_point_mass_by_name(controller["managed_point"])
                mouse_point = sim.get_mouse_point()
                mouse = sim.get_mouse()
                sim.add_controller(
                    ToMouseController(
                        managed_point,
                        mouse_point,
                        mouse
                    )
                )
            elif controller["type"] == AstarController.get_type() or \
                    controller["type"] == VisionController.get_type():
                managed_point = sim.get_point_mass_by_name(controller["managed_point"])
                # destination point object or string
                if isinstance(controller["destination_point"], str):
                    destination_point = sim.get_point_mass_by_name(controller["destination_point"])
                else:
                    destination_point = Vect2d(controller["destination_point"]["x"],
                                               controller["destination_point"]["y"])
                gap_between_nodes = controller["gap_between_nodes"] if "gap_between_nodes" in controller else 1 / 2
                if controller["type"] == AstarController.get_type():
                    sim.add_controller(
                        AstarController(
                            managed_point,
                            destination_point,
                            sim.get_canvas_dim(),
                            sim.get_blocks(),
                            gap_between_nodes=gap_between_nodes
                        )
                    )
                elif controller["type"] == VisionController.get_type():
                    sim.add_controller(
                        VisionController(
                            managed_point,
                            destination_point,
                            sim.get_canvas_dim(),
                            sim.get_blocks(),
                            gap_between_nodes=gap_between_nodes
                        )
                    )

            print(f"Added controller: {controller['type']}")

        return sim
