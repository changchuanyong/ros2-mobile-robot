# ROS2 Mobile Robot Simulation

基于 ROS2 Jazzy 的移动机器人 Gazebo 仿真项目，包含小车模型、Gazebo 室内环境、激光雷达、差速驱动、ROS-Gazebo bridge、RViz 可视化和 SLAM Toolbox 建图。

## 功能

- Xacro / URDF 小车模型
- Gazebo 室内 `house.sdf` 仿真环境
- 差速驱动 Gazebo 插件
- Gazebo lidar 仿真雷达与 ROS2 `/scan` 桥接
- `/cmd_vel`、`/odom`、`/tf`、`/joint_states`、`/clock` 桥接
- RViz2 机器人模型、TF、雷达、里程计和地图显示
- SLAM Toolbox 在线建图
- 键盘遥控小车运动

## 仓库结构

```text
ros2-mobile-robot-main/
├── src/
│   └── robot/
│       ├── config/
│       │   └── slam_toolbox.yaml
│       ├── launch/
│       │   ├── display.launch.py
│       │   ├── gazebo_sim_world.launch.py
│       │   └── slam.launch.py
│       ├── rviz/
│       │   ├── display.rviz
│       │   └── slam.rviz
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
- Gazebo Sim 8
- `colcon`
- `rviz2`
- `xacro`
- `robot_state_publisher`
- `ros_gz_sim`
- `ros_gz_bridge`
- `slam_toolbox`
- `teleop_twist_keyboard`

## 编译

```bash
cd ros2-mobile-robot-main
colcon build --symlink-install
source install/setup.bash
```

## 运行模型显示

只显示机器人模型和 RViz：

```bash
ros2 launch robot display.launch.py
```

## 运行 Gazebo 仿真

启动 Gazebo、机器人模型、RViz 和 ROS-Gazebo bridge：

```bash
ros2 launch robot gazebo_sim_world.launch.py
```

不启动 RViz：

```bash
ros2 launch robot gazebo_sim_world.launch.py use_rviz:=false
```

## 运行 SLAM 建图

一键启动 Gazebo、机器人模型、ROS-Gazebo bridge、SLAM Toolbox 和 RViz：

```bash
ros2 launch robot slam.launch.py
```

只启动 Gazebo 和 SLAM，不启动 RViz：

```bash
ros2 launch robot slam.launch.py slam_rviz:=false
```

SLAM 相关坐标系和话题：

```text
map_frame: map
odom_frame: odom
base_frame: base_footprint
scan_topic: /scan
```

启动成功后可看到以下话题：

```text
/map
/map_metadata
/scan
/odom
/tf
/cmd_vel
/slam_toolbox/graph_visualization
/slam_toolbox/scan_visualization
```

## 键盘遥控

另开一个终端：

```bash
cd ros2-mobile-robot-main
source install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/cmd_vel
```

常用按键：

```text
i  前进
,  后退
j  左转
l  右转
k  停止
q  提高速度
z  降低速度
```

## 保存地图

建图完成后可保存地图：

```bash
ros2 run nav2_map_server map_saver_cli -f my_map
```

如果系统没有安装 `nav2_map_server`，需要先安装对应 ROS2 Jazzy 包。

## 当前限制

- `car_camera.urdf.xacro` 目前只定义相机外形，还没有 Gazebo camera sensor，因此不会发布图像话题。
- 当前实现到 SLAM 建图阶段，尚未接入 Navigation2 自主导航。
- 如果用于真实机器人，还需要添加串口/CAN 底盘通信节点和真实传感器标定参数。

## 后续扩展建议

1. 添加 Gazebo camera sensor 并桥接图像话题。
2. 添加 Navigation2 参数、地图加载和导航 launch。
3. 添加 AMCL 或 SLAM Toolbox localization 模式。
4. 添加真实底盘通信节点和硬件接口文档。
5. 增加地图保存目录和导航示例地图。
