# ROS2 移动机器人仿真

基于 ROS2 Jazzy 的移动机器人 Gazebo 仿真项目，包含小车模型、Gazebo 室内环境、激光雷达、IMU、差速驱动、ROS-Gazebo bridge、RViz 可视化、SLAM Toolbox 2D 建图、FAST-LIO 3D 激光-惯性仿真建图以及 Navigation2 自主导航。

## 功能

- Xacro / URDF 小车模型
- Gazebo 室内 `house.sdf` 仿真环境
- 差速驱动 Gazebo 插件
- 2D 激光雷达 + 16 线 3D 点云激光雷达 + IMU 传感器仿真
- `/cmd_vel`、`/odom`、`/tf`、`/joint_states`、`/clock`、`/scan`、`/imu`、`/points/points` 桥接
- RViz2 机器人模型、TF、雷达、里程计、地图和规划路径显示
- SLAM Toolbox 2D 异步在线建图
- FAST-LIO 3D 激光-惯性在线建图
- Navigation2 自主导航（DWB 局部规划 + Navfn 全局规划 + 碰撞监控）
- 键盘遥控小车运动

## 仓库结构

```text
ros2-mobile-robot-main/
├── src/
│   ├── robot/
│   │   ├── config/
│   │   │   ├── slam_toolbox.yaml      # SLAM Toolbox 2D 建图参数
│   │   │   ├── fast_lio.yaml          # FAST-LIO 3D 建图参数
│   │   │   └── nav2_params.yaml       # Nav2 导航栈参数
│   │   ├── launch/
│   │   │   ├── gazebo_sim_world.launch.py
│   │   │   ├── slam.launch.py         # SLAM Toolbox 建图
│   │   │   ├── fastlio.launch.py      # FAST-LIO 仿真建图
│   │   │   └── nav2_sim.launch.py     # Nav2 自主导航
│   │   ├── rviz/
│   │   │   ├── display.rviz
│   │   │   ├── slam.rviz
│   │   │   └── nav2.rviz
│   │   ├── urdf/
│   │   │   ├── car.urdf.xacro
│   │   │   ├── car_base.urdf.xacro
│   │   │   ├── car_camera.urdf.xacro
│   │   │   ├── car_laser.urdf.xacro
│   │   │   ├── car_imu.urdf.xacro
│   │   │   ├── common_inertia.xacro
│   │   │   └── car_base2.urdf
│   │   ├── world/
│   │   │   ├── house.sdf
│   │   │   └── visualize_lidar.sdf
│   │   ├── robot/
│   │   │   └── pointcloud_time_adapter.py  # 点云时间戳适配节点
│   │   ├── package.xml
│   │   ├── setup.py
│   │   └── setup.cfg
│   └── spark-fast-lio/                # FAST-LIO 子模块
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
- `nav2_bringup`
- `nav2_map_server`
- `teleop_twist_keyboard`
- `spark_fast_lio`（FAST-LIO，已作为 git 子模块包含）

## 编译

```bash
cd ros2-mobile-robot-main
git submodule update --init --recursive
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
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

### SLAM Toolbox（2D 激光建图）

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

### FAST-LIO（3D 激光-惯性建图）

启动 Gazebo、点云时间适配器、FAST-LIO 和 RViz：

```bash
ros2 launch robot fastlio.launch.py
```

FAST-LIO 使用 16 线点云激光雷达（`/points/points`）和 IMU（`/imu`）进行紧耦合融合。点云时间适配器 (`pointcloud_time_adapter`) 会自动为 Gazebo 点云添加 FAST-LIO 所需的 `time` 字段。

### 两种 SLAM 方案对比

| | SLAM Toolbox | FAST-LIO |
|---|---|---|
| 传感器 | 2D 激光雷达 | 16 线点云 + IMU |
| 维度 | 2D 栅格地图 | 3D 点云地图 |
| 启动文件 | `slam.launch.py` | `fastlio.launch.py` |
| bridge_tf | `true` | `false` |
| 适用场景 | 平面室内导航 | 仿真 3D 建图 |

## 运行 Nav2 自主导航

一键启动 Gazebo、SLAM Toolbox、Navigation2 导航栈和 RViz。当前导航模式使用 SLAM Toolbox 实时生成 `/map`，不是加载已有离线地图：

```bash
ros2 launch robot nav2_sim.launch.py
```

不启动 RViz：

```bash
ros2 launch robot nav2_sim.launch.py rviz:=false
```

使用自定义 Nav2 参数文件：

```bash
ros2 launch robot nav2_sim.launch.py params_file:=/absolute/path/to/nav2_params.yaml
```

在 RViz 中使用 "2D Goal Pose" 工具点击目标点，机器人将自动规划路径并导航。主要配置：
- DWB 局部规划器（max_vel_x=0.22 m/s, max_vel_theta=0.8 rad/s）
- Navfn 全局规划器
- 2D 激光 `/scan` 作为局部和全局 costmap 障碍物来源
- 速度平滑
- 碰撞监控（1.2s 预测）
- `map -> odom -> base_footprint` 坐标链

启动成功后可看到以下话题：

```text
/map              # SLAM 构建的栅格地图
/map_metadata
/scan             # 2D 激光扫描
/odom             # 里程计
/tf               # 坐标变换
/cmd_vel          # 速度指令
/plan             # 全局规划路径
/local_plan       # 局部规划路径
```

如果 RViz 已经能看到地图但发送目标后不运动，先检查 Nav2 lifecycle 节点是否为 `active`，以及 `/cmd_vel` 是否有速度输出：

```bash
ros2 lifecycle nodes
ros2 topic echo /cmd_vel
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
i   前进
,   后退
j   左转
l   右转
k   停止
q   提高速度
z   降低速度
```

## 保存地图

建图完成后可保存地图：

```bash
ros2 run nav2_map_server map_saver_cli -f my_map
```

如果系统没有安装 `nav2_map_server`，需要先安装对应 ROS2 Jazzy 包。

## 当前限制

- `car_camera.urdf.xacro` 目前只定义相机外形，还没有 Gazebo camera sensor，因此不会发布图像话题。
- `car_base2.urdf` 引用外部 `sim01_urdf` 包中的 STL 网格，该包不在本仓库中。
- Nav2 导航目前仅配置用于仿真（`use_sim_time: true`），用于真实机器人需要调整参数。
- 如果用于真实机器人，还需要添加串口/CAN 底盘通信节点和真实传感器标定参数。

## 后续扩展建议

1. 添加 Gazebo camera sensor 并桥接图像话题。
2. 添加 AMCL 或 SLAM Toolbox localization 模式，支持加载已有地图进行纯定位。
3. 将 Nav2 参数适配到真实硬件（传感器模型、速度限制、碰撞模型等）。
4. 添加真实底盘通信节点和硬件接口文档。
5. 增加地图保存目录和导航示例地图。
6. 将 FAST-LIO 地图导出为栅格地图供 Nav2 使用。
