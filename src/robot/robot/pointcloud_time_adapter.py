import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import PointCloud2, PointField


class PointCloudTimeAdapter(Node):
    def __init__(self):
        super().__init__('pointcloud_time_adapter')
        self.declare_parameter('input_topic', '/points/points')
        self.declare_parameter('output_topic', '/points/fast_lio')

        input_topic = self.get_parameter('input_topic').value
        output_topic = self.get_parameter('output_topic').value

        qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
        )
        self.publisher = self.create_publisher(PointCloud2, output_topic, qos)
        self.subscription = self.create_subscription(
            PointCloud2, input_topic, self.pointcloud_callback, qos
        )

    def pointcloud_callback(self, msg):
        if any(field.name == 'time' for field in msg.fields):
            self.publisher.publish(msg)
            return

        out = PointCloud2()
        out.header = msg.header
        out.height = msg.height
        out.width = msg.width
        out.fields = list(msg.fields)
        out.is_bigendian = msg.is_bigendian
        out.is_dense = msg.is_dense

        time_field = PointField()
        time_field.name = 'time'
        time_field.offset = msg.point_step
        time_field.datatype = PointField.FLOAT32
        time_field.count = 1
        out.fields.append(time_field)

        out.point_step = msg.point_step + 4
        out.row_step = out.point_step * msg.width

        point_count = msg.width * msg.height
        if point_count == 0:
            out.data = b''
            self.publisher.publish(out)
            return

        src = np.frombuffer(msg.data, dtype=np.uint8)
        dst = np.zeros((point_count, out.point_step), dtype=np.uint8)

        if msg.row_step == msg.point_step * msg.width:
            src_points = src.reshape((point_count, msg.point_step))
            dst[:, :msg.point_step] = src_points
        else:
            for row in range(msg.height):
                src_begin = row * msg.row_step
                src_end = src_begin + msg.point_step * msg.width
                dst_begin = row * msg.width
                dst_end = dst_begin + msg.width
                dst[dst_begin:dst_end, :msg.point_step] = src[src_begin:src_end].reshape(
                    (msg.width, msg.point_step)
                )

        out.data = dst.tobytes()

        self.publisher.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = PointCloudTimeAdapter()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
