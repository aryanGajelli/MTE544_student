from math import atan2, asin, sqrt
import csv
M_PI=3.1415926535

import numpy as np

class Logger:
    def __init__(self, filename, headers=["e", "e_dot", "e_int", "stamp"]):
        self.filename = filename

        with open(self.filename, 'w') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(headers)

    def log_values(self, values_list):

        with open(self.filename, 'a') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(values_list)

    def save_log(self):
        pass


class FileReader:
    def __init__(self, filename):
        
        self.filename = filename
        
        
    def read_file(self):
        
        read_headers=False

        table=[]
        headers=[]
        with open(self.filename, 'r') as file:
            # Skip the header line
            if not read_headers:
                for line in file:
                    values=line.strip().split(',')

                    for val in values:
                        if val=='':
                            break
                        headers.append(val.strip())

                    read_headers=True
                    break
            
            next(file)
            
            # Read each line and extract values
            for line in file:
                values = line.strip().split(',')
                
                row=[]                
                
                for val in values:
                    if val=='':
                        break
                    row.append(float(val.strip()))

                table.append(row)
        
        return headers, table
    
    
# Conversion from Quaternion to Euler Angles
def euler_from_quaternion(q):
    """
    Convert quaternion (w in last place) to euler roll, pitch, yaw.
    quat = [x, y, z, w]
    """

    yaw = atan2(2.0*(q.w*q.z + q.x*q.y), 1-2*(q.y*q.y + q.z*q.z))
    pitch = asin(-2.0*(q.x*q.z - q.w*q.y))
    roll = atan2(2.0*(q.x*q.y + q.w*q.z), q.w*q.w + q.x*q.x - q.y*q.y - q.z*q.z)

    return yaw


# Calculation of the linear error
def calculate_linear_error(current_pose: list, goal_pose: list):

    # Compute the linear error in x and y
    # Remember that current_pose = [x,y, theta, time stamp] and goal_pose = [x,y]
    # Remember to use the Euclidean distance to calculate the error.
    error_linear = dist(current_pose[:2], goal_pose)

    return error_linear

# Calculation of the angular error
def calculate_angular_error(current_pose, goal_pose):

    # Compute the linear error in x and y
    # Remember that current_pose = [x,y, theta, time stamp] and goal_pose = [x,y]
    # Use atan2 to find the desired orientation
    # Remember that this function returns the difference in orientation between where the robot currently faces and where it should face to reach the goal

    error_angular = atan2(goal_pose[1] - current_pose[1], goal_pose[0] - current_pose[0]) - current_pose[2]

    # Remember to handle the cases where the angular error might exceed the range [-π, π]

    if error_angular > M_PI:
        error_angular -= 2*M_PI
    elif error_angular < -M_PI:
        error_angular += 2*M_PI

    return error_angular