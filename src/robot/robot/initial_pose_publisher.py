import math

from geometry_msgs.msg import PoseWithCovarianceStamped

import rclpy
from rclpy.node import Node


class InitialPosePublisher(Node):
    def __init__(self):
        super().__init__('initial_pose_publisher')
        self.declare_parameter('x', 0.0)
        self.declare_parameter('y', 0.0)
        self.declare_parameter('yaw', 0.0)
        self.declare_parameter('publish_count', 10)
        self.declare_parameter('publish_period_sec', 0.5)

        self.x = self.get_parameter('x').get_parameter_value().double_value
        self.y = self.get_parameter('y').get_parameter_value().double_value
        self.yaw = self.get_parameter('yaw').get_parameter_value().double_value
        self.remaining = self.get_parameter('publish_count').get_parameter_value().integer_value
        period = self.get_parameter('publish_period_sec').get_parameter_value().double_value

        self.publisher = self.create_publisher(PoseWithCovarianceStamped, '/initialpose', 10)
        self.timer = self.create_timer(period, self.publish_initial_pose)
        self.get_logger().info(
            f'Publishing initial pose x={self.x:.3f}, y={self.y:.3f}, yaw={self.yaw:.3f}'
        )

    def publish_initial_pose(self):
        if self.remaining <= 0:
            self.timer.cancel()
            return

        msg = PoseWithCovarianceStamped()
        # A zero stamp lets AMCL use the latest available TF during startup.
        msg.header.stamp.sec = 0
        msg.header.stamp.nanosec = 0
        msg.header.frame_id = 'map'
        msg.pose.pose.position.x = self.x
        msg.pose.pose.position.y = self.y

        half_yaw = self.yaw * 0.5
        msg.pose.pose.orientation.z = math.sin(half_yaw)
        msg.pose.pose.orientation.w = math.cos(half_yaw)

        msg.pose.covariance[0] = 0.25
        msg.pose.covariance[7] = 0.25
        msg.pose.covariance[35] = 0.06853891909122467

        self.publisher.publish(msg)
        self.remaining -= 1


def main(args=None):
    rclpy.init(args=args)
    node = InitialPosePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
