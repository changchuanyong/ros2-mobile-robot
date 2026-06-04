import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    robot_share_dir = get_package_share_directory("robot")
    fast_lio_params_file = os.path.join(robot_share_dir, "config", "fast_lio.yaml")
    slam_rviz_file = os.path.join(robot_share_dir, "rviz", "slam.rviz")

    use_rviz = LaunchConfiguration("rviz")
    use_time_adapter = LaunchConfiguration("use_time_adapter")
    lidar_topic = LaunchConfiguration("lidar_topic")
    imu_topic = LaunchConfiguration("imu_topic")
    adapted_lidar_topic = LaunchConfiguration("adapted_lidar_topic")
    fast_lio_package = LaunchConfiguration("fast_lio_package")
    fast_lio_executable = LaunchConfiguration("fast_lio_executable")

    pointcloud_time_adapter = Node(
        package="robot",
        executable="pointcloud_time_adapter",
        name="pointcloud_time_adapter",
        output="screen",
        parameters=[{
            "input_topic": lidar_topic,
            "output_topic": adapted_lidar_topic,
            "use_sim_time": False,
        }],
        condition=IfCondition(use_time_adapter),
    )

    fast_lio_direct = Node(
        package=fast_lio_package,
        executable=fast_lio_executable,
        name="fast_lio",
        output="screen",
        parameters=[fast_lio_params_file, {"use_sim_time": False}],
        remappings=[
            ("lidar", lidar_topic),
            ("imu", imu_topic),
        ],
        condition=UnlessCondition(use_time_adapter),
    )

    fast_lio_adapted = Node(
        package=fast_lio_package,
        executable=fast_lio_executable,
        name="fast_lio",
        output="screen",
        parameters=[fast_lio_params_file, {"use_sim_time": False}],
        remappings=[
            ("lidar", adapted_lidar_topic),
            ("imu", imu_topic),
        ],
        condition=IfCondition(use_time_adapter),
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", slam_rviz_file],
        parameters=[{"use_sim_time": False}],
        condition=IfCondition(use_rviz),
        output="screen",
    )

    return LaunchDescription([
        DeclareLaunchArgument("rviz", default_value="true"),
        DeclareLaunchArgument("use_time_adapter", default_value="false"),
        DeclareLaunchArgument("lidar_topic", default_value="/points"),
        DeclareLaunchArgument("imu_topic", default_value="/imu"),
        DeclareLaunchArgument("adapted_lidar_topic", default_value="/points/fast_lio"),
        DeclareLaunchArgument("fast_lio_package", default_value="spark_fast_lio"),
        DeclareLaunchArgument("fast_lio_executable", default_value="spark_lio_mapping"),
        LogInfo(msg="FAST-LIO robot: no Gazebo, no simulation bridges."),
        pointcloud_time_adapter,
        fast_lio_direct,
        fast_lio_adapted,
        rviz,
    ])
