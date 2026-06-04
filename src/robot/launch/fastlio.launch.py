import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    robot_share_dir = get_package_share_directory("robot")

    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(robot_share_dir, "launch", "fastlio_sim.launch.py")
        ),
        launch_arguments={
            "rviz": LaunchConfiguration("rviz"),
            "start_fast_lio": LaunchConfiguration("start_fast_lio"),
            "fast_lio_package": LaunchConfiguration("fast_lio_package"),
            "fast_lio_executable": LaunchConfiguration("fast_lio_executable"),
        }.items(),
    )

    return LaunchDescription([
        DeclareLaunchArgument("rviz", default_value="true"),
        DeclareLaunchArgument("start_fast_lio", default_value="true"),
        DeclareLaunchArgument("fast_lio_package", default_value="spark_fast_lio"),
        DeclareLaunchArgument("fast_lio_executable", default_value="spark_lio_mapping"),
        LogInfo(msg="fastlio.launch.py is kept for compatibility; prefer fastlio_sim.launch.py."),
        sim_launch,
    ])
