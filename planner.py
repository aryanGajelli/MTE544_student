import math
import numpy as np
from typing import Callable
# Type of planner
POINT_PLANNER=0; TRAJECTORY_PLANNER=1

class planner:
    def __init__(self, type_):

        self.type=type_

    @staticmethod
    def parabola(t):
        return t, t*t # parabola function, parametrized by t

    @staticmethod
    def sigmoid(t):
        return t, 2.0/(1+np.exp(-2*t))-1.0 # sigmoid function, parametrized by t
    
    def plan(self, goalPoint=[-1.0, -1.0], trajectory_f: Callable[[float], float]=parabola, upper_limit=1.5, num_divisions=10):
        """
        Plan the path to the goalPoint or follow the trajectory_f
        If the planner is a point planner, it will return the goalPoint
        If the planner is a trajectory planner, it will return the set of points generated when calling trajectory_f on np.linspace(0, upper_limit, num_divisions)
        """
        if self.type==POINT_PLANNER:
            return self.point_planner(goalPoint)
        
        elif self.type==TRAJECTORY_PLANNER:
            return self.trajectory_planner(trajectory_f, upper_limit, num_divisions)


    def point_planner(self, goalPoint):
        x = goalPoint[0]
        y = goalPoint[1]
        return x, y

    # TODO Part 6: Implement the trajectories here
    @staticmethod
    def trajectory_planner(trajectory_f, upper_limit, num_divisions):
        points = np.linspace(0, upper_limit, num_divisions)
        return np.squeeze(np.dstack(trajectory_f(points))) # return is a list of trajectory points: [ [x1,y1], ..., [xn,yn]]

