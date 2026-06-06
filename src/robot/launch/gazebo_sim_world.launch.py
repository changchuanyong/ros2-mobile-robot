import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    this_pkg = get_package_share_directory("robot")
    pkg_ros_gz_sim = get_package_share_directory("ros_gz_sim")
    world_file = os.path.join(this_pkg, "world", "house.sdf")
    model_file = os.path.join(this_pkg, "urdf", "car.urdf.xacro")
    rviz_file = os.path.join(this_pkg, "rviz", "display.rviz")

    use_rviz = DeclareLaunchArgument(
        "use_rviz",
        default_value="true",
        description="Start RViz with the package display configuration.",
    )

    bridge_tf = DeclareLaunchArgument(
        "bridge_tf",
        default_value="true",
        description="Bridge Gazebo model TF. Disable when FAST-LIO publishes map->base_footprint.",
    )

    robot_description = ParameterValue(
        Command(["xacro ", model_file]),
        value_type=str,
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{
            "robot_description": robot_description,
            "use_sim_time": True,
        }],
        output="screen",
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", rviz_file],
        parameters=[{"use_sim_time": True}],
        condition=IfCondition(LaunchConfiguration("use_rviz")),
        output="screen",
    )

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={
            "gz_args": "-r " + world_file,
        }.items(),
    )

    spawn = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name", "mycar",
            "-x", "-4.5",
            "-y", "-2.5",
            "-z", "0.01",
            "-topic", "/robot_description",
        ],
        output="screen",
    )

    laser_frame_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        arguments=[
            "--x", "0", "--y", "0", "--z", "0.105",
            "--roll", "0", "--pitch", "0", "--yaw", "0",
            "--frame-id", "base_link",
            "--child-frame-id", "mycar/base_footprint/laser_sensor",
        ],
        output="screen",
    )

    point_lidar_frame_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        arguments=[
            "--x", "0", "--y", "0", "--z", "0.105",
            "--roll", "0", "--pitch", "0", "--yaw", "0",
            "--frame-id", "base_link",
            "--child-frame-id", "mycar/base_footprint/point_lidar",
        ],
        output="screen",
    )

    imu_frame_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        arguments=[
            "--x", "0", "--y", "0", "--z", "0.12",
            "--roll", "0", "--pitch", "0", "--yaw", "0",
            "--frame-id", "base_link",
            "--child-frame-id", "mycar/base_footprint/imu_sensor",
        ],
        output="screen",
    )

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/model/mycar/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist",
            "/model/mycar/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry",
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/world/empty/model/mycar/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model",
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
            "/imu@sensor_msgs/msg/Imu[gz.msgs.IMU",
        ],
        remappings=[
            ("/model/mycar/cmd_vel", "/cmd_vel"),
            ("/world/empty/model/mycar/joint_state", "/joint_states"),
            ("/model/mycar/odometry", "/odom"),
        ],
        output="screen",
    )

    gazebo_tf_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/model/mycar/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V",
        ],
        remappings=[
            ("/model/mycar/tf", "/tf"),
        ],
        condition=IfCondition(LaunchConfiguration("bridge_tf")),
        output="screen",
    )

    point_cloud_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/points/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked",
        ],
        output="screen",
    )

    return LaunchDescription([
        use_rviz,
        bridge_tf,
        gz_sim,
        robot_state_publisher,
        rviz,
        spawn,
        laser_frame_tf,
        point_lidar_frame_tf,
        imu_frame_tf,
        bridge,
        gazebo_tf_bridge,
        point_cloud_bridge,
    ])
