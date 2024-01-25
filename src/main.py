import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import sys
import os

from simulator.simulator import Simulator


def plot_history(df_history, id_to_name=None):
    df_history = df_history.groupby("id")

    plt.figure()
    fig, axs = plt.subplots(2, 2, figsize=(10, 10), sharex=True)
    axs = axs.reshape(-1)

    labels = [id_to_name[id] for id in df_history.groups.keys()] \
        if id_to_name \
        else df_history.groups.keys()

    fig.suptitle("Point mass simulation\n"
              "Points velocities and accelerations",
              fontsize=24
    )

    # df_history["x"].plot(ax=axs[0][0])
    # axs[0][0].set_xlabel("t [s]")
    # axs[0][0].set_ylabel("x [m]")
    # axs[0][0].grid()
    # axs[0][0].legend(
    #     labels=labels,
    # )

    df_history["v_x"].plot(ax=axs[0])
    axs[0].set_xlabel("t [s]")
    axs[0].set_ylabel("v_x [m/s]")
    axs[0].grid()
    axs[0].legend(
        labels=labels,
    )
    df_history["a_x"].plot(ax=axs[1])
    axs[1].set_xlabel("t [s]")
    axs[1].set_ylabel("a_x [m/s^2]")
    axs[1].grid()
    axs[1].legend(
        labels=labels,
    )
    df_history["v_y"].plot(ax=axs[2])
    axs[2].set_xlabel("t [s]")
    axs[2].set_ylabel("v_y [m/s]")
    axs[2].grid()
    axs[2].legend(
        labels=labels,
    )
    df_history["a_y"].plot(ax=axs[3])
    axs[3].set_xlabel("t [s]")
    axs[3].set_ylabel("a_y [m/s^2]")
    axs[3].grid()
    axs[3].legend(
        labels=labels,
    )

    fig.show()


def plot_paths(df_history, id_to_name=None, canvas_dim=None, blocks=None):
    df_history = df_history.groupby("id")

    fig, ax = plt.subplots()

    fig.suptitle("Point mass simulation\n"
              "Points positions",
              fontsize=16
    )

    for block in blocks:
        ax.add_patch(Rectangle(
            (block.x, block.y),
            block.w,
            block.h,
            # edgecolor='pink',
            facecolor='gray',
            fill=True,
            # lw=5
        ))

    for group in df_history.groups:
        ax.scatter(
            df_history.get_group(group)["x"][0],
            df_history.get_group(group)["y"][0],
            # label=id_to_name[group] + " start",
        )
        ax.plot(
            df_history.get_group(group)["x"],
            df_history.get_group(group)["y"],
            label=id_to_name[group],
        )

    fig.gca().invert_yaxis()
    if canvas_dim:
        ax.set_xbound(lower=0, upper=canvas_dim.x)
        ax.set_ybound(lower=0, upper=canvas_dim.y)
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.legend()
    ax.grid()
    fig.show()


def main():
    # sim = Simulator(
    #     # canvas_w=30,
    #     # canvas_h=30
    # )
    if sys.platform.startswith('win'):
        directory = os.path.join(os.path.dirname(os.getcwd()), 'assets', 'map2.json')
        print(directory)
        sim = Simulator.from_file(directory)
    else:
        sim = Simulator.from_file('assets/labyrinth.json')

    df_history = sim.run(
        verbose=True,
    )

    # df_history.to_csv("history.csv", index=False)
    # plot_history(
    #     df_history,
    #     sim.get_id_to_name(),
    # )
    # plot_paths(
    #     df_history,
    #     sim.get_id_to_name(),
    #     sim.get_canvas_dim(),
    #     sim.get_blocks(),
    # )


if __name__ == "__main__":
    main()
