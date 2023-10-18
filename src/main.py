import matplotlib.pyplot as plt

from src.simulator.simulator import simulator

from src.simulator.controllers.to_mouse_controller import ToMouseController


def main():
    sim = simulator(log=True)

    sim.add_block(15, 9, h=2)

    p1 = sim.add_point_mass(10, 10, enable_focus=True)

    blocks = sim.get_blocks()

    sim.add_block(9,15, color=(255,0,0))

    mc = ToMouseController(p1, sim.get_mouse_point(), blocks, sim.get_mouse())
    sim.add_controller(mc)

    df_history = sim.start()

    # df_history.to_csv("history.csv", index=False)

    df_hist_1 = df_history[df_history['id'] == 0]
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
    main()
