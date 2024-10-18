import math
import numpy as np
# Type of planner
POINT_PLANNER=0; TRAJECTORY_PLANNER=1

class planner:
    def __init__(self, type_):

        self.type=type_

    @staticmethod
    def parabola(t):
        return t, t*t

    @staticmethod
    def sigmoid(t):
        return t, 2.0/(1+np.exp(-2*t))-1.0
    
    def plan(self, goalPoint=[-1.0, -1.0], trajectory_f=parabola, upper_limit=1.5, num_divisions=10):
        
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
        return np.squeeze(np.dstack(trajectory_f(points)))
        # the return should be a list of trajectory points: [ [x1,y1], ..., [xn,yn]]
        # return 

