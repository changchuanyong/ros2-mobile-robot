import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, IncludeLaunchDescription, LogInfo, RegisterEventHandler
from launch.conditions import IfCondition
from launch.events import matches_action
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import AndSubstitution, LaunchConfiguration, NotSubstitution
from launch_ros.actions import LifecycleNode, Node
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from lifecycle_msgs.msg import Transition


def generate_launch_description():
    robot_share_dir = get_package_share_directory("robot")
    slam_params_file = os.path.join(robot_share_dir, "config", "slam_toolbox.yaml")
    slam_rviz_file = os.path.join(robot_share_dir, "rviz", "slam.rviz")

    use_rviz = LaunchConfiguration("use_rviz")
    autostart = LaunchConfiguration("autostart")
    use_lifecycle_manager = LaunchConfiguration("use_lifecycle_manager")

    declare_use_rviz = DeclareLaunchArgument(
        "use_rviz",
        default_value="true",
        description="Start RViz with the SLAM display configuration.",
    )
    declare_autostart = DeclareLaunchArgument(
        "autostart",
        default_value="true",
        description="Automatically configure and activate slam_toolbox.",
    )
    declare_use_lifecycle_manager = DeclareLaunchArgument(
        "use_lifecycle_manager",
        default_value="false",
        description="Let an external lifecycle manager activate slam_toolbox.",
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(robot_share_dir, "launch", "gazebo_sim_world.launch.py")
        ),
        launch_arguments={
            "use_rviz": "false",
        }.items(),
    )

    slam_toolbox = LifecycleNode(
        package="slam_toolbox",
        executable="async_slam_toolbox_node",
        name="slam_toolbox",
        namespace="",
        output="screen",
        parameters=[
            slam_params_file,
            {
                "use_lifecycle_manager": use_lifecycle_manager,
                "use_sim_time": True,
            },
        ],
    )

    configure_slam_toolbox = EmitEvent(
        event=ChangeState(
            lifecycle_node_matcher=matches_action(slam_toolbox),
            transition_id=Transition.TRANSITION_CONFIGURE,
        ),
        condition=IfCondition(AndSubstitution(autostart, NotSubstitution(use_lifecycle_manager))),
    )

    activate_slam_toolbox = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=slam_toolbox,
            start_state="configuring",
            goal_state="inactive",
            entities=[
                LogInfo(msg="[slam.launch.py] Activating slam_toolbox."),
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=matches_action(slam_toolbox),
                        transition_id=Transition.TRANSITION_ACTIVATE,
                    )
                ),
            ],
        ),
        condition=IfCondition(AndSubstitution(autostart, NotSubstitution(use_lifecycle_manager))),
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", slam_rviz_file],
        condition=IfCondition(use_rviz),
        output="screen",
    )

    return LaunchDescription([
        declare_use_rviz,
        declare_autostart,
        declare_use_lifecycle_manager,
        gazebo,
        slam_toolbox,
        configure_slam_toolbox,
        activate_slam_toolbox,
        rviz,
    ])
