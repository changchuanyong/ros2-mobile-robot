import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    robot_share_dir = get_package_share_directory("robot")
    fast_lio_params_file = os.path.join(robot_share_dir, "config", "fast_lio.yaml")
    slam_rviz_file = os.path.join(robot_share_dir, "rviz", "slam.rviz")

    use_rviz = LaunchConfiguration("rviz")
    start_fast_lio = LaunchConfiguration("start_fast_lio")
    fast_lio_package = LaunchConfiguration("fast_lio_package")
    fast_lio_executable = LaunchConfiguration("fast_lio_executable")

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(robot_share_dir, "launch", "gazebo_sim_world.launch.py")
        ),
        launch_arguments={"use_rviz": "false", "bridge_tf": "false"}.items(),
    )

    pointcloud_time_adapter = Node(
        package="robot",
        executable="pointcloud_time_adapter",
        name="pointcloud_time_adapter",
        output="screen",
        parameters=[{
            "input_topic": "/points/points",
            "output_topic": "/points/fast_lio",
            "use_sim_time": True,
        }],
        condition=IfCondition(start_fast_lio),
    )

    fast_lio_node = Node(
        package=fast_lio_package,
        executable=fast_lio_executable,
        name="fast_lio",
        output="screen",
        parameters=[fast_lio_params_file, {"use_sim_time": True}],
        remappings=[
            ("lidar", "/points/fast_lio"),
            ("imu", "/imu"),
        ],
        condition=IfCondition(start_fast_lio),
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", slam_rviz_file],
        parameters=[{"use_sim_time": True}],
        condition=IfCondition(use_rviz),
        output="screen",
    )

    return LaunchDescription([
        DeclareLaunchArgument("rviz", default_value="true"),
        DeclareLaunchArgument("start_fast_lio", default_value="true"),
        DeclareLaunchArgument("fast_lio_package", default_value="spark_fast_lio"),
        DeclareLaunchArgument("fast_lio_executable", default_value="spark_lio_mapping"),
        gazebo,
        LogInfo(msg="FAST-LIO simulation: Gazebo + /points/fast_lio + /imu."),
        pointcloud_time_adapter,
        fast_lio_node,
        rviz,
    ])
