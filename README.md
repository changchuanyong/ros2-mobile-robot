# ROS2 移动机器人 Gazebo 仿真演示

本仓库当前实现的是一个 ROS2 Jazzy 下的小车模型显示与 Gazebo 仿真示例，包含：

- Xacro/URDF 小车模型
- Gazebo world 环境
- Gazebo lidar 仿真雷达与 ROS2 `/scan` 桥接
- 差速驱动 Gazebo 插件
- Gazebo 与 ROS2 的 `/cmd_vel`、`/odom`、`/tf`、`/joint_states`、`/clock` 桥接
- RViz2 模型与 TF 可视化

> 注意：当前代码还没有实现 SLAM、Navigation2、YOLO 目标检测或 STM32 串口通信。仓库中也没有 `slam.launch.py`、`nav.launch.py`、`yolo.launch.py`。

## 仓库结构

```text
robot_ws/
├── src/
│   └── robot/
│       ├── launch/
│       │   ├── display.launch.py
│       │   └── gazebo_sim_world.launch.py
│       ├── rviz/
│       │   └── display.rviz
│       ├── urdf/
│       │   ├── car.urdf.xacro
│       │   ├── car_base.urdf.xacro
│       │   ├── car_camera.urdf.xacro
│       │   └── car_laser.urdf.xacro
│       ├── world/
│       │   └── house.sdf
│       ├── package.xml
│       └── setup.py
├── README.md
└── .gitignore
```

## 环境要求

- ROS2 Jazzy
- `colcon`
- `rviz2`
- `xacro`
- `robot_state_publisher`
- `joint_state_publisher`
- `ros_gz_sim`
- `ros_gz_bridge`

## 编译

```bash
cd ros2-mobile-robot-main
colcon build --symlink-install
source install/setup.bash
```

## 运行

只显示机器人模型和 RViz：

```bash
ros2 launch robot display.launch.py
```

启动 Gazebo 仿真、机器人模型、RViz 和 ROS-Gazebo bridge：

```bash
ros2 launch robot gazebo_sim_world.launch.py
```

## 运行后可用话题

典型话题包括：

```text
/clock
/cmd_vel
/joint_states
/odom
/scan
/robot_description
/tf
/tf_static
```

可以用键盘控制节点发布速度命令，例如：

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/cmd_vel
```

## 当前限制

- `car_camera.urdf.xacro` 目前只定义相机外形，还没有 Gazebo camera sensor，因此不会发布图像话题。
- 尚未接入 SLAM Toolbox、Cartographer、Navigation2 或 YOLO。
- README 中未来如果加入这些功能，应同时提交对应 launch、config 和节点源码。

## 后续扩展建议

1. 给雷达 link 添加 Gazebo lidar sensor，并桥接到 `/scan`。
2. 给相机 link 添加 camera sensor，并桥接图像话题。
3. 添加 SLAM Toolbox 或 Cartographer 配置与 launch。
4. 添加 Nav2 map、planner/controller 参数与 bringup launch。
5. 如需真实机器人，再添加串口通信节点和底盘协议文档。
