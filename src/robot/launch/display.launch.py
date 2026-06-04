from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    robot_share_dir = get_package_share_directory("robot")
    default_model_path = os.path.join(robot_share_dir, "urdf", "car.urdf.xacro")
    default_rviz_path = os.path.join(robot_share_dir, "rviz", "display.rviz")

    model = DeclareLaunchArgument(name="model", default_value=default_model_path)
    use_joint_state_publisher = DeclareLaunchArgument(
        name="use_joint_state_publisher",
        default_value="true",
        description="Start joint_state_publisher for standalone RViz display.",
    )
    use_rviz = DeclareLaunchArgument(
        name="use_rviz",
        default_value="true",
        description="Start RViz with the package display configuration.",
    )
    use_sim_time = DeclareLaunchArgument(
        name="use_sim_time",
        default_value="true",
        description="Use simulation clock for Gazebo/RViz workflows.",
    )

    robot_description = ParameterValue(
        Command(["xacro ", LaunchConfiguration("model")]),
        value_type=str,
    )
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            {
                "robot_description": robot_description,
                "use_sim_time": LaunchConfiguration("use_sim_time"),
            }
        ],
    )
    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        condition=IfCondition(LaunchConfiguration("use_joint_state_publisher")),
        parameters=[{"use_sim_time": LaunchConfiguration("use_sim_time")}],
    )
    rviz2 = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", default_rviz_path],
        condition=IfCondition(LaunchConfiguration("use_rviz")),
        parameters=[{"use_sim_time": LaunchConfiguration("use_sim_time")}],
    )

    return LaunchDescription([
        model,
        use_joint_state_publisher,
        use_rviz,
        use_sim_time,
        robot_state_publisher,
        joint_state_publisher,
        rviz2,
    ])
