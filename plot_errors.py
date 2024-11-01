import argparse
import matplotlib.pyplot as plt
from utilities import FileReader
import numpy as np
from planner import planner
from pathlib import Path
try:
    import addcopyfighandler
except ImportError:
    print("addcopyfighandler not found. You can install it by running 'pip install addcopyfighandler'")

def plot_errors(filename: str, traj:str=None):
    headers, values = FileReader(filename).read_file()

    filename: Path = Path(filename)
    title = "Parabola trajectory PID controller"
    state_type = "robot pose" if filename.stem.startswith("robot") else "linear error" if filename.stem.startswith("linear") else "angular error"

    time_list = []

    first_stamp = values[0][-1]

    for val in values:
        time_list.append(val[-1] - first_stamp)

    # fig, axes = plt.subplots(1,2, figsize=(14,6))

    plt.figure(1)
    var = "x-y" if filename.stem.startswith("robot") else "e-e_dot"
    plt.title(f"{title}: state space of {state_type} [{var}]")

    plt.plot([lin[0] for lin in values], [lin[1] for lin in values], label=var)

    
    plt.grid()

    if traj == "parabola":
        points = np.linspace(0, 1.5, 15)
        func_results = planner.parabola(points)
        plt.plot(func_results[0], func_results[1], label="Defined parabola waypoints", marker='.')
    elif traj == "sigmoid":
        points = np.linspace(0, 2.5, 15)
        func_results = planner.sigmoid(points)
        plt.plot(func_results[0], func_results[1], label="Defined sigmoid waypoints", marker='.')

    xlabel = headers[0]
    ylabel = headers[1]
    y_unit = "meters" if filename.stem.startswith("robot") else "meters/s"
    plt.xlabel(f"{xlabel} [meters]")
    plt.ylabel(f"{ylabel} [{y_unit}]")
    plt.legend()

    plt.show()

    plt.figure(2)
    plt.title(f"{title}: individual states of {state_type}")

    for i in range(0, len(headers) - 1):
        plt.plot(time_list, [lin[i] for lin in values], label=headers[i])

    ylabel = "[meters, rad]" if filename.stem.startswith("robot") else "[meters]" if filename.stem.startswith("linear") else "[rad]"
    plt.ylabel(f"state {ylabel}")
    plt.xlabel("time [s]")
    plt.legend()
    plt.grid()

    plt.show()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument('--files', nargs='+', required=True, help='List of files to process')
    parser.add_argument('--traj', required=False,  default=None, help='Trajectory type')

    args = parser.parse_args()

    print("plotting the files", args.files)

    filenames = args.files
    for filename in filenames:
        plot_errors(filename, args.traj)
