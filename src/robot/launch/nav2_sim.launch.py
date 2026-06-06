import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import EmitEvent, IncludeLaunchDescription, LogInfo, RegisterEventHandler
from launch.events import matches_action
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import LifecycleNode, Node
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from lifecycle_msgs.msg import Transition


AUTOSTART = True
MAP_SAVE_INTERVAL_SEC = 30.0
USE_LIFECYCLE_MANAGER_FOR_SLAM = False


def generate_launch_description():
    robot_share_dir = get_package_share_directory('robot')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    slam_params_file = os.path.join(robot_share_dir, 'config', 'slam_toolbox.yaml')
    nav2_params_file = os.path.join(robot_share_dir, 'config', 'nav2_params.yaml')
    nav2_rviz_file = os.path.join(robot_share_dir, 'rviz', 'nav2.rviz')

    map_save_path = os.path.abspath(os.path.join(os.getcwd(), 'maps', 'house_slam'))
    workspace_map_file = map_save_path + '.yaml'
    package_map_file = os.path.join(robot_share_dir, 'maps', 'house_slam.yaml')
    map_file = workspace_map_file if os.path.exists(workspace_map_file) else package_map_file
    use_saved_map = os.path.exists(map_file)

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(robot_share_dir, 'launch', 'gazebo_sim_world.launch.py')
        ),
        launch_arguments={
            'use_rviz': 'false',
            'bridge_tf': 'true',
            'on_exit_shutdown': 'true',
        }.items(),
    )

    nav2_navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'params_file': nav2_params_file,
            'autostart': 'true' if AUTOSTART else 'false',
            'use_composition': 'False',
        }.items(),
    )


    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', nav2_rviz_file],
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    actions = [gazebo]

    if use_saved_map:
        actions.extend([
            LogInfo(msg=f'[nav2_sim.launch.py] Loading map: {map_file}'),
            Node(
                package='nav2_map_server',
                executable='map_server',
                name='map_server',
                output='screen',
                parameters=[
                    nav2_params_file,
                    {
                        'use_sim_time': True,
                        'yaml_filename': map_file,
                    },
                ],
            ),
            Node(
                package='nav2_amcl',
                executable='amcl',
                name='amcl',
                output='screen',
                parameters=[nav2_params_file, {'use_sim_time': True}],
            ),
            Node(
                package='nav2_lifecycle_manager',
                executable='lifecycle_manager',
                name='lifecycle_manager_localization',
                output='screen',
                parameters=[{
                    'use_sim_time': True,
                    'autostart': AUTOSTART,
                    'node_names': ['map_server', 'amcl'],
                }],
            ),
            Node(
                package='robot',
                executable='initial_pose_publisher',
                name='initial_pose_publisher',
                output='screen',
                parameters=[{
                    'x': 0.0,
                    'y': 0.0,
                    'yaw': 0.0,
                    'publish_count': 10,
                    'publish_period_sec': 0.5,
                }],
            ),
        ])
    else:
        slam_toolbox = LifecycleNode(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            namespace='',
            output='screen',
            parameters=[
                slam_params_file,
                {
                    'use_lifecycle_manager': USE_LIFECYCLE_MANAGER_FOR_SLAM,
                    'use_sim_time': True,
                },
            ],
        )

        configure_slam_toolbox = EmitEvent(
            event=ChangeState(
                lifecycle_node_matcher=matches_action(slam_toolbox),
                transition_id=Transition.TRANSITION_CONFIGURE,
            ),
        )

        activate_slam_toolbox = RegisterEventHandler(
            OnStateTransition(
                target_lifecycle_node=slam_toolbox,
                start_state='configuring',
                goal_state='inactive',
                entities=[
                    LogInfo(msg='[nav2_sim.launch.py] Activating slam_toolbox.'),
                    EmitEvent(
                        event=ChangeState(
                            lifecycle_node_matcher=matches_action(slam_toolbox),
                            transition_id=Transition.TRANSITION_ACTIVATE,
                        )
                    ),
                ],
            )
        )

        actions.extend([
            LogInfo(
                msg=(
                    '[nav2_sim.launch.py] No saved map found; starting SLAM and '
                    f'autosaving to {map_save_path}'
                )
            ),
            slam_toolbox,
            configure_slam_toolbox,
            activate_slam_toolbox,
            Node(
                package='robot',
                executable='map_autosaver',
                name='map_autosaver',
                output='screen',
                parameters=[{
                    'map_path': map_save_path,
                    'save_interval_sec': MAP_SAVE_INTERVAL_SEC,
                    'save_on_shutdown': True,
                }],
            ),
        ])

    actions.extend([
        nav2_navigation,
        rviz,
    ])

    return LaunchDescription(actions)
