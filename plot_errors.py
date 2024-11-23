import argparse
import matplotlib.pyplot as plt
from utilities import FileReader
from planner import planner

def plot_errors(filename):

    headers, values = FileReader(filename).read_file()

    time_list = []

    first_stamp = values[0][-1]

    for val in values:
        time_list.append(val[-1] - first_stamp)

    fig, axes = plt.subplots(2, 1, figsize=(10, 6))
    fig.subplots_adjust(hspace=0.4)

    axes[0].plot([lin[len(headers) - 3] for lin in values], [lin[len(headers) - 2] for lin in values])
    x,y=map(list, zip(*planner.trajectory_planner()))
    # axes[0].plot(x,y, marker='.')
    axes[0].set_title("State Space")
    axes[0].set_xlabel("x Position (m)")
    axes[0].set_ylabel("y Position (m)")
    axes[0].grid()

    axes[1].set_title("Each Individual State")
    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("State Value")
    axes[1].grid()
    lines = []
    for i in range(0, len(headers) - 1):
        lines.append(axes[1].plot(time_list, [lin[i] for lin in values], label=headers[i]))

    leg = axes[1].legend()
    lined = {}
    for legline, origline in zip(leg.get_lines(), lines):
        legline.set_picker(5)  # 5 pts tolerance
        lined[legline] = origline[0]

    def onpick(event):
        # on the pick event, find the orig line corresponding to the
        # legend proxy line, and toggle the visibility
        legline = event.artist
        origline = lined[legline]
        vis = not origline.get_visible()
        origline.set_visible(vis)
        # Change the alpha on the line in the legend so we can see what lines
        # have been toggled
        if vis:
            legline.set_alpha(1.0)
        else:
            legline.set_alpha(0.2)
        fig.canvas.draw()
    fig.canvas.mpl_connect('pick_event', onpick)
    plt.show()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument('--files', nargs='+', required=True, help='List of files to process')

    args = parser.parse_args()

    print("plotting the files", args.files)

    filenames = args.files
    for filename in filenames:
        plot_errors(filename)