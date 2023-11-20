import matplotlib.pyplot as plt

from src.simulator.controllers.astar_controller import AstarController
from src.simulator.simulator import Simulator

from src.simulator.controllers.to_mouse_controller import ToMouseController
from src.simulator.utils.vect_2d import Vect2d


def plot_history(df_history):
    df_history = df_history.groupby("id")

    fig, axs = plt.subplots(3, 2, figsize=(10, 10), sharex=True)

    fig.suptitle("Point mass simulation")
    df_history["x"].plot(ax=axs[0][0])
    axs[0][0].set_xlabel("t [s]")
    axs[0][0].set_ylabel("x [m]")
    axs[0][0].grid()
    df_history["v_x"].plot(ax=axs[1][0])
    axs[1][0].set_xlabel("t [s]")
    axs[1][0].set_ylabel("v_x [m/s]")
    axs[1][0].grid()
    df_history["a_x"].plot(ax=axs[2][0])
    axs[2][0].set_xlabel("t [s]")
    axs[2][0].set_ylabel("a_x [m/s^2]")
    axs[2][0].grid()
    df_history["y"].plot(ax=axs[0][1])
    axs[0][1].set_xlabel("t [s]")
    axs[0][1].set_ylabel("y [m]")
    axs[0][1].grid()
    df_history["v_y"].plot(ax=axs[1][1])
    axs[1][1].set_xlabel("t [s]")
    axs[1][1].set_ylabel("v_y [m/s]")
    axs[1][1].grid()
    df_history["a_y"].plot(ax=axs[2][1])
    axs[2][1].set_xlabel("t [s]")
    axs[2][1].set_ylabel("a_y [m/s^2]")
    axs[2][1].grid()

    plt.show()


def main():
    # sim = Simulator(
    #     # canvas_w=30,
    #     # canvas_h=30
    # )

    sim = Simulator.from_file('assets/map1.json')

    # p1 = sim.get_point_mass_by_name("p1")

    # blocks = sim.get_blocks()
    #
    # mc = ToMouseController(p1, sim.get_mouse_point(), blocks, sim.get_mouse())
    # sim.add_controller(mc)
    #
    # ac = AstarController(
    #     p1,
    #     Vect2d(25, 25),
    #     sim.get_canvas_dim(),
    #     blocks,
    #     gap_between_nodes=1/2
    # )
    # sim.add_controller(ac)

    # @TODO:
    # - pola widzenia
    # http://ai.berkeley.edu/project_overview.html for guard
    # - Dijkstra fields for thief (?)
    # - Project 4: Ghostbusters

    sim.start()

    # df_history.to_csv("history.csv", index=False)
    # plot_history(df_history)


if __name__ == "__main__":
    main()
