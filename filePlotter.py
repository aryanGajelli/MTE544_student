# You can use this file to plot the loged sensor data
# Note that you need to modify/adapt it to your own files
# Feel free to make any modifications/additions here

import matplotlib.pyplot as plt
import numpy as np
# from utilities import FileReader
import csv
def plot_errors(filename , odom=False, laser=True):
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
    for i in range(0, len(headers) - 1):
        plt.plot(time_list, [lin[i] for lin in values], label= headers[i]+ " linear")
    
    #plt.plot([lin[0] for lin in values], [lin[1] for lin in values])
    plt.legend()
    plt.grid()

    if odom:
        # 2D Trajectory Plot
        plt.subplot(2, 1, 2)
        plt.plot([lin[0] for lin in values], [lin[1] for lin in values], label="x vs. y")
        plt.legend()
        plt.grid()

    plt.show()

def plot_laser(filename):
    with open(filename, 'r') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)
        # plot only 1st row of laser scan data
        scan, inc, t = next(csv_reader)
        inc = float(inc)
        t = float(t)
        scan = scan.removeprefix("array('f',").removesuffix(')').strip().removeprefix('[').removesuffix(']')
        scan = [float(a) for a in scan.split(',')]
    theta = 0
    x = []
    y = []
    for r in scan:
        x.append(r*np.cos(theta))
        y.append(r*np.sin(theta))
        theta += inc

    plt.scatter(x, y, marker='.')
    plt.title(f"X-Y scatter plot of robot at {t=}")
    plt.grid()
    plt.legend()
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
        if args.laser:
            plot_laser(filename)
        else:
            plot_errors(filename, args.odom)
