import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from simulator.controllers.collision_controller import CollisionController
from src.simulator.simulator import Simulator


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

    for group in df_history.groups:
        df_history.get_group(group).plot(
            ax=ax,
            x="x",
            y="y",
            label=id_to_name[group],
            legend=True
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

    fig.gca().invert_yaxis()
    if canvas_dim:
        ax.set_xlim(0, canvas_dim.x)
        ax.set_ylim(canvas_dim.y, 0)
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.grid()
    fig.show()


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

    end_sim_coll_cont = CollisionController(
        sim.get_point_mass_by_name("p1"),
        sim.get_point_mass_by_name("destination_point"),
        sim.stop
    )
    sim.add_controller(end_sim_coll_cont)

    df_history = sim.start()

    # df_history.to_csv("history.csv", index=False)
    plot_history(
        df_history,
        sim.get_id_to_name(),
    )
    plot_paths(
        df_history,
        sim.get_id_to_name(),
        sim.get_canvas_dim(),
        sim.get_blocks(),
    )


if __name__ == "__main__":
    main()
