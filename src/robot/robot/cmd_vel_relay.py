from geometry_msgs.msg import Twist

import rclpy
from rclpy.node import Node


class CmdVelRelay(Node):
    def __init__(self):
        super().__init__('cmd_vel_relay')
        self.declare_parameter('input_topic', '/cmd_vel_nav')
        self.declare_parameter('output_topic', '/cmd_vel')

        input_topic = self.get_parameter('input_topic').value
        output_topic = self.get_parameter('output_topic').value

        self.publisher = self.create_publisher(Twist, output_topic, 10)
        self.subscription = self.create_subscription(
            Twist,
            input_topic,
            self.publisher.publish,
            10,
        )


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelRelay()
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
