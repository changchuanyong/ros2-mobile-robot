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
- Navigation2 自主导航（支持加载已保存地图或在线 SLAM，DWB 局部规划 + Navfn 全局规划 + 碰撞监控）
- 键盘遥控小车运动

## 仓库结构

```text
ros2-mobile-robot-main/
├── src/
│   ├── robot/
│   │   ├── config/
│   │   │   ├── slam_toolbox.yaml      # SLAM Toolbox 2D 建图参数
│   │   │   ├── fast_lio.yaml          # FAST-LIO 3D 建图参数
│   │   │   ├── nav2_params.yaml       # Nav2 导航栈参数
│   │   │   ├── ros_gz_bridge.yaml     # ROS-Gazebo 普通话题桥接
│   │   │   └── ros_gz_tf_bridge.yaml  # Gazebo TF 桥接
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
│   │   │   ├── pointcloud_time_adapter.py  # 点云时间戳适配节点
│   │   │   ├── initial_pose_publisher.py   # Nav2 初始位姿发布
│   │   │   ├── map_autosaver.py            # SLAM 地图自动保存
│   │   │   └── cmd_vel_relay.py            # 速度转发工具节点
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
- `nav2_amcl`
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

一键启动 Gazebo、Navigation2 和 RViz：

```bash
ros2 launch robot nav2_sim.launch.py
```

启动逻辑已经写在 `nav2_sim.launch.py` 里：

- 如果当前目录存在 `maps/house_slam.yaml`，自动加载该地图，并启动 `map_server + AMCL` 做离线定位导航。
- 如果没有 `maps/house_slam.yaml`，自动启动 SLAM Toolbox 在线建图，并每 30 秒保存一次地图到 `maps/house_slam`，退出时也会再保存一次。

需要重新建图时，先移走或删除 `maps/house_slam.yaml` 和 `maps/house_slam.pgm`，再运行同一个启动命令。

在 RViz 中使用 "2D Pose Estimate" 校准初始位姿，然后使用 "2D Goal Pose" 工具点击目标点，机器人将自动规划路径并导航。在线 SLAM 模式下，刚启动时先点已建图区域内、离机器人较近的目标点；目标点超出当前 `/map` 可通行区域时会规划失败。主要配置：
- DWB 局部规划器（max_vel_x=0.34 m/s, max_vel_theta=1.1 rad/s）
- Navfn 全局规划器
- 2D 激光 `/scan` 作为局部和全局 costmap 障碍物来源
- Navigation2 控制链路：`/cmd_vel_nav -> velocity_smoother -> /cmd_vel_smoothed`
- Gazebo 速度桥接：`/cmd_vel_smoothed -> /model/mycar/cmd_vel`
- 碰撞监控保留在 Nav2 中，但仿真底盘默认直接使用平滑后的速度，避免碰撞监控输出卡住导致小车不动
- `map -> odom -> base_footprint` 坐标链

启动成功后可看到以下话题：

```text
/map              # 已加载或 SLAM 构建的栅格地图
/map_metadata
/scan             # 2D 激光扫描
/odom             # 里程计
/tf               # 坐标变换
/cmd_vel_nav      # Nav2 控制器输出
/cmd_vel_smoothed # 平滑后的底盘速度指令，桥接到 Gazebo
/cmd_vel          # 碰撞监控输出，保留用于调试
/plan             # 全局规划路径
/local_plan       # 局部规划路径
```

如果 RViz 已经能看到地图但发送目标后不运动，先检查 Nav2 lifecycle 节点是否为 `active`，以及 `/cmd_vel_smoothed` 是否有速度输出：

```bash
ros2 lifecycle nodes
ros2 topic echo /cmd_vel_smoothed
ros2 topic info /cmd_vel_smoothed -v
```

也可以发送一个近距离目标验证 Nav2：

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: 0.8, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

如果 ROS 命令短时间内发现不到节点或话题，重启 ROS daemon 后再查：

```bash
ros2 daemon stop
ros2 daemon start
ros2 node list
ros2 topic list
```

## 键盘遥控

另开一个终端：

```bash
cd ros2-mobile-robot-main
source install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/cmd_vel_smoothed
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

## 地图保存和读取

仓库已有示例地图：

```text
maps/house_slam.yaml
maps/house_slam.pgm
```

`nav2_sim.launch.py` 默认优先读取当前目录的 `maps/house_slam.yaml`。如果该文件不存在，会自动进入在线 SLAM 模式并保存到 `maps/house_slam`，生成 `.yaml` 和 `.pgm` 文件。仍然可以手动保存：

```bash
mkdir -p maps
ros2 run nav2_map_server map_saver_cli -f maps/house_slam
```

如果系统没有安装 `nav2_map_server`，需要先安装对应 ROS2 Jazzy 包。

## 当前限制

- `car_camera.urdf.xacro` 目前只定义相机外形，还没有 Gazebo camera sensor，因此不会发布图像话题。
- `car_base2.urdf` 引用外部 `sim01_urdf` 包中的 STL 网格，该包不在本仓库中。
- Nav2 导航目前仅配置用于仿真（`use_sim_time: true`），用于真实机器人需要调整参数。
- 如果用于真实机器人，还需要添加串口/CAN 底盘通信节点和真实传感器标定参数。

## 后续扩展建议

1. 添加 Gazebo camera sensor 并桥接图像话题。
2. 将 Nav2 参数适配到真实硬件（传感器模型、速度限制、碰撞模型等）。
3. 添加真实底盘通信节点和硬件接口文档。
4. 将 FAST-LIO 地图导出为栅格地图供 Nav2 使用。
