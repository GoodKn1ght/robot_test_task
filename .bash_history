ros2 run teleop_twist_keyboard teleop_twist_keyboard
source /opt/ros_ws/install/setup.sh
cd /opt/ros_ws
ros2 launch nav2_bringup navigation_launch.py use_sim_time:=true
