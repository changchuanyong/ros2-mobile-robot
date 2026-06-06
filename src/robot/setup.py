from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (
            os.path.join('share', package_name, 'launch'),
            glob(os.path.join('launch', '*.launch.py')),
        ),
        (
            os.path.join('share', package_name, 'urdf'),
            glob(os.path.join('urdf', '*.*')),
        ),
        (
            os.path.join('share', package_name, 'rviz'),
            glob(os.path.join('rviz', '*.rviz')),
        ),
        (
            os.path.join('share', package_name, 'config'),
            glob(os.path.join('config', '*.yaml')),
        ),
        (
            os.path.join('share', package_name, 'world'),
            glob(os.path.join('world', '*.sdf')),
        ),
        (
            os.path.join('share', package_name, 'maps'),
            glob(os.path.join('..', '..', 'maps', '*.*')),
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='chang',
    maintainer_email='1984715306@qq.com',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pointcloud_time_adapter = robot.pointcloud_time_adapter:main',
            'cmd_vel_relay = robot.cmd_vel_relay:main',
            'map_autosaver = robot.map_autosaver:main',
            'initial_pose_publisher = robot.initial_pose_publisher:main',
        ],
    },
)
