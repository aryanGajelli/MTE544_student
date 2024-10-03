# Imports
import argparse
import rclpy

from rclpy.node import Node

from utilities import Logger, euler_from_quaternion
from rclpy.qos import QoSProfile

# TODO Part 3: Import message types needed:
# For sending velocity commands to the robot: Twist
# For the sensors: Imu, LaserScan, and Odometry
# Check the online documentation to fill in the lines below
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu, LaserScan
from nav_msgs.msg import Odometry

from rclpy.time import Time

# You may add any other imports you may need/want to use below
import math
from pathlib import Path


CIRCLE = 0
SPIRAL = 1
ACC_LINE = 2
motion_types = ['circle', 'spiral', 'line']


class motion_executioner(Node):

    def __init__(self, motion_type=0):
        super().__init__("motion_types")

        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True, parents=True)
        self.type = motion_type

        self.radius_ = 0.0

        self.successful_init = False
        self.imu_initialized = False
        self.odom_initialized = False
        self.laser_initialized = False

        # TODO Part 3: Create a publisher to send velocity commands by setting the proper parameters in (...)
        self.vel_publisher = self.create_publisher(Twist, topic="/cmd_vel", qos_profile=10)

        # loggers
        self.imu_logger = Logger(self.log_dir / f'imu_content_{motion_types[motion_type]}.csv', headers=["acc_x", "acc_y", "angular_z", "stamp"])
        self.odom_logger = Logger(self.log_dir / f'odom_content_{motion_types[motion_type]}.csv', headers=["x", "y", "th", "stamp"])
        self.laser_logger = Logger(self.log_dir / f'laser_content_{motion_types[motion_type]}.csv', headers=["ranges", "angle_increment", "stamp"])

        # TODO Part 3: Create the QoS profile by setting the proper parameters in (...)
        qos_profile = QoSProfile(reliability=2, durability=2, history=1, depth=10)

        # TODO Part 5: Create below the subscription to the topics corresponding to the respective sensors
        # IMU subscription
        self.imu_subsciber = self.create_subscription(Imu, topic="/imu", callback=self.imu_callback, qos_profile=qos_profile)
        self.imu_initialized = True

        # ODOM subscription
        self.odom_subsciber = self.create_subscription(Odometry, topic="/odom", callback=self.odom_callback, qos_profile=qos_profile)
        self.odom = Odometry()
        self.odom_initialized = True

        # LaserScan subscription
        self.laser_subsciber = self.create_subscription(LaserScan, topic="/scan", callback=self.laser_callback, qos_profile=qos_profile)
        self.laser_initialized = True

        self.create_timer(0.1, self.timer_callback)

        self.start_time = self.now

    @property
    def now(self) -> Time:
        return self.get_clock().now()

    @property
    def t(self) -> float:
        return (self.now - self.start_time).nanoseconds / 1e9

    # TODO Part 5: Callback functions: complete the callback functions of the three sensors to log the proper data.
    # To also log the time you need to use the rclpy Time class, each ros msg will come with a header, and then
    # inside the header you have a stamp that has the time in seconds and nanoseconds, you should log it in nanoseconds as
    # such: Time.from_msg(imu_msg.header.stamp).nanoseconds
    # You can save the needed fields into a list, and pass the list to the log_values function in utilities.py

    def imu_callback(self, imu_msg: Imu):
        # log imu msgs
        self.imu_logger.log_values([imu_msg.linear_acceleration.x, imu_msg.linear_acceleration.y, imu_msg.angular_velocity.z, self.t])

    def odom_callback(self, odom_msg: Odometry):
        # log odom msgs
        self.odom_logger.log_values([odom_msg.pose.pose.position.x, odom_msg.pose.pose.position.y, euler_from_quaternion(odom_msg.pose.pose.orientation), self.t])
        # track odometry data for correcting the robot's orientation in make_acc_line_twist
        self.odom = odom_msg

    def laser_callback(self, laser_msg: LaserScan):
        # log laser msgs with position msg at that time
        self.laser_logger.log_values([laser_msg.ranges, laser_msg.angle_increment, self.t])

    def timer_callback(self):
        if self.odom_initialized and self.laser_initialized and self.imu_initialized:
            self.successful_init = True

        if not self.successful_init:
            return

        cmd_vel_msg = Twist()

        if self.type == CIRCLE:
            cmd_vel_msg = self.make_circular_twist()

        elif self.type == SPIRAL:
            cmd_vel_msg = self.make_spiral_twist()

        elif self.type == ACC_LINE:
            cmd_vel_msg = self.make_acc_line_twist()

        else:
            print("type not set successfully, 0: CIRCLE 1: SPIRAL and 2: ACCELERATED LINE")
            raise SystemExit

        self.vel_publisher.publish(cmd_vel_msg)

    # TODO Part 4: Motion functions: complete the functions to generate the proper messages corresponding to the desired motions of the robot
    def make_circular_twist(self):
        msg = Twist()
        # fill up the twist msg for circular motion
        msg.linear.x = 1.
        msg.angular.z = 1.
        return msg

    def make_spiral_twist(self):
        msg = Twist()

        # fill up the twist msg for spiral motion

        # Spiral motion for robot. Limit the linear velocity to prevent the robot from spinning out of control.
        msg.linear.x = min(self.t/10, 2.)
        msg.angular.z = 1.
        return msg

    def make_acc_line_twist(self):
        msg = Twist()
        # fill up the twist msg for line motion
        # 45 deg motion in a straight line

        # Turn to 45 degrees using a P controller and move forwards in straight line.
        # Correct the orientation of the robot to 45 degrees if it veers off course.

        yaw = euler_from_quaternion(self.odom.pose.pose.orientation)
        kP = 0.5
        error = math.pi/4 - yaw
        FIVE_DEG = 0.1
        if abs(error) > FIVE_DEG:
            msg.angular.z = kP * error
        else:
            msg.angular.z = 0.
            msg.linear.x = 1.

        return msg


if __name__ == "__main__":

    argParser = argparse.ArgumentParser(description="input the motion type")

    argParser.add_argument("--motion", type=str, default="circle")

    rclpy.init()

    args = argParser.parse_args()

    if args.motion.lower() == "circle":
        ME = motion_executioner(motion_type=CIRCLE)
    elif args.motion.lower() == "line":
        ME = motion_executioner(motion_type=ACC_LINE)
    elif args.motion.lower() == "spiral":
        ME = motion_executioner(motion_type=SPIRAL)
    else:
        print(f"we don't have {args.motion.lower()} motion type")

    try:
        rclpy.spin(ME)
    except KeyboardInterrupt:
        print("Exiting")
