import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_share = get_package_share_directory('my_diff_robot')

    # Paths
    urdf_file = os.path.join(pkg_share, 'urdf', 'robot.urdf')
    rviz_config = os.path.join(pkg_share, 'rviz', 'robot.rviz')
    controllers_config = os.path.join(pkg_share, 'config', 'controllers.yaml')
    world_file = os.path.join(pkg_share, 'worlds', 'empty.sdf')
    gz_bridge_config = os.path.join(pkg_share, 'config', 'gz_bridge.yaml')

    # Read URDF
    with open(urdf_file, 'r') as f:
        robot_description = f.read()
    robot_description = robot_description.replace('CONTROLLER_YAML_PATH', controllers_config)

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True
        }]
    )

    # Gazebo Sim
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            ])
        ]),
        launch_arguments={
            'gz_args': f'-r {world_file}',
            'on_exit_shutdown': 'true'
        }.items()
    )

    # Spawn robot in Gazebo
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'diff_drive_robot',
            '-topic', 'robot_description',
            '-x', '0',
            '-y', '0',
            '-z', '0.1'
        ],
        output='screen'
    )

    # ROS-Gazebo Bridge
    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'
        ],
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    # Spawn controllers
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    diff_drive_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    # RViz
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        robot_state_publisher,
        gazebo,
        spawn_robot,
        gz_bridge,
        joint_state_broadcaster_spawner,
        diff_drive_controller_spawner,
        rviz,
    ])
