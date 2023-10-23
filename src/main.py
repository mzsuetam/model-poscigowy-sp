import matplotlib.pyplot as plt

from src.simulator.controllers.base_graph_controller import BaseGraphController
from src.simulator.simulator import simulator

from src.simulator.controllers.to_mouse_controller import ToMouseController


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
    sim = simulator(
        # canvas_w=20,
        # canvas_h=20
    )

    sim.add_block(15, 5, h=2)

    p1 = sim.add_point_mass(10, 10, enable_focus=True)

    blocks = sim.get_blocks()

    sim.add_block(9, 15)

    mc = ToMouseController(p1, sim.get_mouse_point(), blocks, sim.get_mouse())
    sim.add_controller(mc)

    bgc = BaseGraphController(sim.get_canvas_dim(), blocks)
    sim.add_controller(bgc)

    sim.start()

    # df_history.to_csv("history.csv", index=False)
    # plot_history(df_history)


if __name__ == "__main__":
    main()
