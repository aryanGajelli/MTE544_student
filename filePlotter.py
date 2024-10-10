# You can use this file to plot the loged sensor data
# Note that you need to modify/adapt it to your own files
# Feel free to make any modifications/additions here

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
# from utilities import FileReader
import csv

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

def low_pass_filter(adata: np.ndarray, bandlimit: int = 500, sampling_rate: int = 10000) -> np.ndarray:
        # translate bandlimit from Hz to dataindex according to sampling rate and data size
        bandlimit_index = int(bandlimit * adata.size / sampling_rate)
    
        fsig = np.fft.fft(adata)
        
        for i in range(bandlimit_index + 1, len(fsig) - bandlimit_index ):
            fsig[i] = 0
            
        adata_filtered = np.fft.ifft(fsig)
    
        return np.real(adata_filtered)


def plot_errors(filename , odom=False, label="line"):
    with open(filename, 'r') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)
        values = []
        for line in csv_reader:
            values.append([float(val) for val in line])
    time_list=[]
    first_stamp=values[0][-1]
    
    for val in values:
        time_list.append(val[-1] - first_stamp)

    if odom:
        plt.subplot(2, 1, 1)
    
    avg = 20
    for i in range(0, len(headers) - 1):
        plt.plot(time_list[:-avg+1], moving_average(np.array([lin[i] for lin in values]), avg), label= headers[i]+ " linear")

    data_type = "odometery" if odom else "imu"
    state_label = "state [meters, rad]" if odom else "linear acc. & angular vel. [m/s^2, rad/s]"
    #plt.plot([lin[0] for lin in values], [lin[1] for lin in values])
    plt.xlabel("time [s]")
    plt.ylabel(state_label)
    plt.legend()
    plt.title(f"Robot {data_type} for {label}")
    plt.grid()

    if odom:
        # 2D Trajectory Plot
        plt.subplot(2, 1, 2)
        plt.plot([lin[0] for lin in values], [lin[1] for lin in values], label="x vs. y")
        plt.xlabel("x [meters]")
        plt.ylabel("y [meters]")
        plt.title(f"Robot trajectory for {label}")
        plt.grid()

    plt.subplots_adjust(hspace=0.5, wspace=0.5)
    plt.show()

def plot_laser(filename, label="line"):
    data = []
    with open(filename, 'r') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)
        # plot only 1st row of laser scan data
        for line in csv_reader:
            scan, inc, t = line
            inc = float(inc)
            t = float(t)
            scan = scan.removeprefix("array('f',").removesuffix(')').strip().removeprefix('[').removesuffix(']')
            scan = [float(a) for a in scan.split(',')]
            data.append({"x": [], "y": [], "t": t})
            theta = 0
            
            for r in scan:
                data[-1]["x"].append(r*np.cos(theta))
                data[-1]["y"].append(r*np.sin(theta))
                theta += inc
    
    x = data[0]["x"]
    y = data[0]["y"]
    fig, ax = plt.subplots()
    plt.plot([0], [0], marker='o', markersize=5, color="red", label="Robot")
    scat = ax.scatter(x, y, marker='.')
    plt.title(f"X-Y scatter plot of robot laser scan at {t=:.3}s for {label} motion")
    plt.xlabel("x [meters]")
    plt.ylabel("y [meters]")
    plt.legend()
    plt.grid()


    def update(frame):
        x = data[frame]["x"]
        y = data[frame]["y"]
        t = data[frame]["t"]
        _data = np.stack([x, y]).T
        scat.set_offsets(_data)
        plt.title(f"X-Y scatter plot of robot laser scan at {t=:.3}s for {label} motion")
        return scat

    ani = animation.FuncAnimation(fig=fig, func=update, frames=len(data), interval=30)
    plt.show()

import argparse

if __name__=="__main__":

    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument('--files', nargs='+', required=True, help='List of files to process')

    # enable plotting trajectory for odometry data
    parser.add_argument('--odom', action=argparse.BooleanOptionalAction, help='Does the file contain odometry data?')
    parser.add_argument('--laser', action=argparse.BooleanOptionalAction, help='Does the file contain laser data?')
    
    
    args = parser.parse_args()
    
    print("plotting the files", args.files)

    filenames=args.files
    
    for filename in filenames:
        if "line" in filename:
            label = "line"
        elif "circle" in filename:
            label = "circle"
        elif "spiral" in filename:
            label = "spiral"
        if args.laser:
            plot_laser(filename, label=label)
        else:
            
            plot_errors(filename, args.odom, label=label)
