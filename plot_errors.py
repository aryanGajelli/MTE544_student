import matplotlib.pyplot as plt
from utilities import FileReader
import numpy as np
from planner import planner


def plot_errors(filename, traj=None):
    
    headers, values=FileReader(filename).read_file()
    
    time_list=[]
    
    first_stamp=values[0][-1]
    
    for val in values:
        time_list.append(val[-1] - first_stamp)

    
    
    fig, axes = plt.subplots(1,2, figsize=(14,6))


    axes[0].plot([lin[0] for lin in values], [lin[1] for lin in values])
    axes[0].set_title("state space")
    axes[0].grid()

    if traj =="parabola":
        points = np.linspace(0, 1.5, 20)
        func_results = planner.parabola(points)
        axes[0].plot(func_results[0], func_results[1], label="parabola")
    elif traj=="sigmoid":
        points = np.linspace(0, 2.5, 20)
        func_results = planner.sigmoid(points)
        axes[0].plot(func_results[0], func_results[1], label="sigmoid", marker='o')

    axes[1].set_title("each individual state")
    for i in range(0, len(headers) - 1):
        axes[1].plot(time_list, [lin[i] for lin in values], label= headers[i]+ " linear")

    axes[1].legend()
    axes[1].grid()

    plt.show()
    
    





import argparse

if __name__=="__main__":

    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument('--files', nargs='+', required=True, help='List of files to process')
    parser.add_argument('--traj', required=False,  default=None, help='Trajectory type')

    args = parser.parse_args()
    
    print("plotting the files", args.files)

    filenames=args.files
    for filename in filenames:
        plot_errors(filename, args.traj)