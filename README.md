
# ROS2 移动机器人系统架构与 SLAM 导航演示

> STM32 下位机 + 树莓派上位机 + Gazebo 仿真 + Cartographer SLAM + Navigation2 + YOLO 目标检测

## 项目简介

本项目展示了一个 **完整的 ROS2 移动机器人系统架构**，涵盖：

- **下位机 STM32** 控制底盘运动，串口与上位机交互  
- **上位机树莓派** 运行 ROS2 节点，实现 SLAM、路径规划、导航控制与 YOLO 环境感知  
- **Gazebo 仿真**：机器人建模、传感器模拟、运动验证  
- **SLAM & Navigation2**：二维激光 SLAM 建图 + 路径规划与导航  
- **RViz2 可视化**：实时显示地图、位姿、传感器数据与目标识别结果  



## 仓库结构

```

robot_ws/
├── src/
│   └── robot/
│       ├── launch/              # 启动文件
│       │   ├── slam.launch.py
│       │   ├── nav.launch.py
│       │   └── yolo.launch.py
│       ├── config/              # 参数配置文件
│       │   ├── cartographer.yaml
│       │   ├── nav2_params.yaml
│       │   └── yolo_params.yaml
│       ├── urdf/                # 机器人 URDF / Xacro
│       ├── meshes/              # 机器人三维模型
│       ├── src/                 # ROS2 节点源码（C++ / Python）
│       ├── CMakeLists.txt
│       └── package.xml
├── README.md
└── .gitignore

````

---

## 功能模块

### 1️⃣ 系统架构
- STM32 下位机控制底盘运动  
- 树莓派上位机运行 ROS2 节点  
- 串口通信完成控制指令与状态数据交互  

### 2️⃣ 机器人建模与仿真
- URDF/Xacro 描述机器人结构  
- Gazebo 仿真底盘、传感器（激光雷达、IMU、编码器）  
- 支持运动学和传感器数据验证  

### 3️⃣ SLAM & Navigation2
- Cartographer 实现二维激光 SLAM  
- Navigation2 路径规划与自主导航  
- 与 RViz2 联动，实时可视化地图、位姿与传感器数据  

### 4️⃣ YOLO 目标识别
- 集成 YOLO 模型，实现环境目标感知  
- 可与导航决策结合，完成任务优化  

---

## 安装与运行

### 1. 克隆仓库
```bash
git clone https://github.com/changchuanyong/robot_ws.git
cd robot_ws
````

### 2. 编译 ROS2 工作空间

```bash
colcon build --symlink-install
source install/setup.bash
```

### 3. 启动 Gazebo + SLAM + Navigation2 + YOLO

```bash
# 启动 SLAM
ros2 launch robot slam.launch.py

# 启动 Navigation2
ros2 launch robot nav.launch.py

# 启动 YOLO 目标检测
ros2 launch robot yolo.launch.py
```

> 可在 RViz2 中可视化 `/map`, `/tf`, `/scan`, `/robot_status`, `/yolo_objects` 等话题

---

## 技术亮点

* **完整系统架构**：节点化、模块化、上下位机协作
* **SLAM + Navigation2**：自主建图与导航，符合 ROS2 实习岗位技能
* **Gazebo + RViz2 仿真**：可快速验证机器人运动与算法
* **YOLO 环境感知**：可结合路径规划优化导航
* **可扩展性强**：支持多机器人、传感器和任务拓展

---

## 未来扩展建议

* 集成多机器人通信
* 增加传感器融合（IMU + 编码器 + 激光雷达）
* 加入动态目标避障与任务规划
* 支持真实机器人部署


