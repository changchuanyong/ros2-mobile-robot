import os
import signal
import subprocess
import threading

import rclpy
from rclpy.node import Node


class MapAutosaver(Node):
    def __init__(self):
        super().__init__('map_autosaver')
        self.declare_parameter('map_path', 'maps/house_slam')
        self.declare_parameter('save_interval_sec', 30.0)
        self.declare_parameter('save_on_startup', False)
        self.declare_parameter('save_on_shutdown', True)

        self.map_path = os.path.abspath(self.get_parameter('map_path').value)
        self.save_interval_sec = (
            self.get_parameter('save_interval_sec').get_parameter_value().double_value
        )
        self.save_on_shutdown = (
            self.get_parameter('save_on_shutdown').get_parameter_value().bool_value
        )
        self._saving_lock = threading.Lock()
        self._shutdown_requested = False

        os.makedirs(os.path.dirname(self.map_path), exist_ok=True)

        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

        if self.get_parameter('save_on_startup').value:
            self.save_map('startup')

        if self.save_interval_sec > 0.0:
            self.timer = self.create_timer(self.save_interval_sec, self._timer_callback)
        else:
            self.timer = None

        self.get_logger().info(
            f'Autosaving /map to {self.map_path} every '
            f'{self.save_interval_sec:.1f}s'
        )

    def _timer_callback(self):
        self.save_map('timer')

    def _handle_signal(self, signum, _frame):
        if self._shutdown_requested:
            return
        self._shutdown_requested = True
        self.get_logger().info(f'Received signal {signum}; saving map before exit.')
        if self.save_on_shutdown:
            self.save_map('shutdown')
        if rclpy.ok():
            rclpy.shutdown()

    def save_map(self, reason):
        if not self._saving_lock.acquire(blocking=False):
            self.get_logger().warn('Map save already running; skipping this request.')
            return

        try:
            cmd = [
                'ros2',
                'run',
                'nav2_map_server',
                'map_saver_cli',
                '-f',
                self.map_path,
                '--ros-args',
                '-p',
                'use_sim_time:=true',
            ]
            self.get_logger().info(f'Saving map ({reason}) to {self.map_path}')
            result = subprocess.run(
                cmd,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=15.0,
            )
            if result.returncode == 0:
                self.get_logger().info('Map save completed.')
            else:
                self.get_logger().warn(
                    f'Map save failed with exit code {result.returncode}: '
                    f'{result.stdout.strip()}'
                )
        except subprocess.TimeoutExpired:
            self.get_logger().warn('Map save timed out.')
        finally:
            self._saving_lock.release()


def main(args=None):
    rclpy.init(args=args)
    node = MapAutosaver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        if node.save_on_shutdown:
            node.save_map('keyboard interrupt')
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
