# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Test Commands

```bash
# Build the ROS2 workspace (from repo root)
colcon build --symlink-install
source install/setup.bash

# Build only the robot package
colcon build --symlink-install --packages-select robot

# Run all tests
colcon test --packages-select robot

# Run a specific test category
colcon test --packages-select robot --pytest-args "-k flake8"
colcon test --packages-select robot --pytest-args "-k pep257"
colcon test --packages-select robot --pytest-args "-k copyright"

# View test output
colcon test-result --all --verbose
```

## Architecture

This is a ROS2 (Humble/Iron) workspace for a differential-drive mobile robot. The repo contains a single ament_python package named `robot` under `src/robot/`.

### Robot Model (URDF/Xacro)

The robot is defined as a modular Xacro assembly:

- **`urdf/car.urdf.xacro`** — Top-level file that includes all sub-components and defines Gazebo plugins (DiffDrive controller and JointStatePublisher). Always process this file, not the fragments.
- **`urdf/car_base.urdf.xacro`** — Base body (`base_link` + `base_footprint`) with a 4-wheel macro. Uses xacro macros from `common_inertia.xacro` for inertial calculations.
- **`urdf/car_laser.urdf.xacro`** — LiDAR link, fixed joint to `base_link`.
- **`urdf/car_camera.urdf.xacro`** — Camera link, fixed joint to `base_link`.
- **`urdf/common_inertia.xacro`** — Reusable inertia macros (`box_inertia`, `cylinder_inertia`, `sphere_inertia`).
- **`urdf/car_base2.urdf`** — Alternative URDF model using STL meshes. References `sim01_urdf` package — this is an external dependency not included in this repo.

The DiffDrive plugin publishes odometry at 50Hz to `/odom`, subscribes to `/cmd_vel`, and publishes wheel TF frames. Robot parameters: wheel separation 0.4m, wheel radius 0.0415m, max linear velocity 0.5 m/s.

### Launch Files

- **`display.launch.py`** — RViz2 visualization only (no simulation). Starts `robot_state_publisher`, `joint_state_publisher`, and `rviz2`. Accepts a `model` launch argument to override the URDF path.
- **`gazebo_sim_world.launch.py`** — Full simulation stack. Launches Ignition Gazebo with the `house.sdf` world, spawns the robot at (-4, 0, 0.01), runs `display.launch.py` for state publishing + RViz, and starts `ros_gz_bridge` to bridge `/cmd_vel`, `/odom`, `/tf`, `/clock`, and `/joint_states` between ROS2 and Gazebo.

### Simulation Stack

This project uses **Ignition Gazebo** (formerly Gazebo Ignition, not classic Gazebo). Key packages: `ros_gz_sim`, `ros_gz_bridge`. The bridge maps ROS2 topics to Gazebo transport messages — critical for control and sensor data flow.

### What Exists vs. What is Planned

The README and directory comments reference several files that do **not** exist yet:
- `launch/slam.launch.py`, `launch/nav.launch.py`, `launch/yolo.launch.py`
- `config/cartographer.yaml`, `config/nav2_params.yaml`, `config/yolo_params.yaml`
- No ROS2 node source files (Python or C++) — `robot/__init__.py` is empty, and `setup.py` has zero `console_scripts` entry points
- No `meshes/` directory (the alternative URDF references meshes from a different package)

The currently functional scope is: robot URDF modeling + Gazebo simulation with differential drive control + RViz2 visualization.

### Key Dependencies

From `package.xml`: `rviz2`, `xacro`, `robot_state_publisher`, `joint_state_publisher`, `ros2launch`. Runtime-only: `ros_gz_sim`, `ros_gz_bridge` (for simulation). Test: `ament_copyright`, `ament_flake8`, `ament_pep257`, `pytest`.

### Coordinate Frames

Standard ROS2 convention: `odom` → `base_footprint` → `base_link` → (sensors: `laser`, `camera`) + (wheels: `*_wheel`). The DiffDrive plugin manages the `odom` → `base_footprint` transform.
