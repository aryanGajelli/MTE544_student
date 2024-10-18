# Imports


import argparse
import sys

from utilities import euler_from_quaternion, calculate_angular_error, calculate_linear_error
from pid import PID_ctrl

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

from rclpy.qos import QoSProfile
from nav_msgs.msg import Odometry as odom

from localization import localization, rawSensor

from planner import TRAJECTORY_PLANNER, POINT_PLANNER, planner
from controller import controller, trajectoryController

# You may add any other imports you may need/want to use below
# import ...


class decision_maker(Node):

    def __init__(self, publisher_msg, publishing_topic, qos_publisher, goalPoint=None, rate=10, motion_type=POINT_PLANNER):

        super().__init__("decision_maker")

        self.motion_type = motion_type

        # TODO Part 4: Create a publisher for the topic responsible for robot's motion
        self.publisher = self.create_publisher(publisher_msg, topic=publishing_topic, qos_profile=qos_publisher)

        publishing_period = 1/rate

        # Instantiate the controller
        # TODO Part 5: Tune your parameters here


        if motion_type == POINT_PLANNER:
            self.controller = controller(klp=3.0, klv=1.0, kli=1, kap=3.0, kav=1, kai = 0)
            self.planner = planner(POINT_PLANNER)
            # Instantiate the planner
            # NOTE: goalPoint is used only for the pointPlanner
            self.goal = self.planner.plan(goalPoint)


        elif motion_type == TRAJECTORY_PLANNER:
            self.controller = trajectoryController(klp=3.0, klv=1.0, kli=1, kap=2.3, kav=1, kai = 0.7)
            self.planner = planner(TRAJECTORY_PLANNER)
            # Instantiate the planner
            # NOTE: goalPoint is used only for the pointPlanner
            self.goal = self.planner.plan(goalPoint, trajectory_f=planner.sigmoid, upper_limit=2.5, num_divisions=20)
            print(self.goal)
        else:
            print("Error! you don't have this planner", file=sys.stderr)

        # Instantiate the localization, use rawSensor for now
        self.localizer = localization(rawSensor)

        self.create_timer(publishing_period, self.timerCallback)

    def timerCallback(self):

        # TODO Part 3: Run the localization node
        rclpy.spin_once(self.localizer)    # Remember that this file is already running the decision_maker node.

        pose = self.localizer.getPose()
        if pose is None:
            print("waiting for odom msgs ....")
            return

        vel_msg = Twist()

        # TODO Part 3: Check if you reached the goal

        if self.motion_type == TRAJECTORY_PLANNER:
            reached_goal = calculate_linear_error(pose, self.goal[-1]) < 0.01
        else:
            reached_goal = calculate_linear_error(pose, self.goal) < 0.01

        if reached_goal:
            print("reached goal")
            self.publisher.publish(vel_msg)  # 0 vel cmd if reached goal

            self.controller.PID_angular.logger.save_log()
            self.controller.PID_linear.logger.save_log()

            # TODO Part 3: exit the spin
            self.localizer.destroy_node()
            raise SystemExit

        velocity, yaw_rate = self.controller.vel_request(self.localizer.getPose(), self.goal, True)

        # TODO Part 4: Publish the velocity to move the robot
        vel_msg.linear.x = velocity
        vel_msg.angular.z = yaw_rate
        self.publisher.publish(vel_msg)


def main(args=None):

    rclpy.init()

    # TODO Part 3: You migh need to change the QoS profile based on whether you're using the real robot or in simulation.
    # Remember to define your QoS profile based on the information available in "ros2 topic info /odom --verbose" as explained in Tutorial 3

    odom_qos = QoSProfile(reliability=2, durability=2, history=1, depth=10)

    # TODO Part 4: instantiate the decision_maker with the proper parameters for moving the robot
    if args.motion.lower() == "point":
        DM = decision_maker(Twist, "/cmd_vel", qos_publisher=10, motion_type=POINT_PLANNER, goalPoint=[-3.0, -4.0])
    elif args.motion.lower() == "trajectory":
        DM = decision_maker(Twist, "/cmd_vel", qos_publisher=10, motion_type=TRAJECTORY_PLANNER)
    else:
        print("invalid motion type", file=sys.stderr)

    try:
        rclpy.spin(DM)
    except SystemExit:
        print(f"reached there successfully {DM.localizer.pose}")


if __name__ == "__main__":

    argParser = argparse.ArgumentParser(description="point or trajectory")
    argParser.add_argument("--motion", type=str, default="point")
    args = argParser.parse_args()

    main(args)
