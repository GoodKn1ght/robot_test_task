# What had I changed? 
1. New node 'safety_system.py'. It's made to check commands from teleop and prevents collisions with threshold 0.3 m.
2. New topic '/cmd_vel_request' for requesting from teleop to safety system node before asking gazebo to do it 
3. Safety system node now decides which command to use truly no not collide
-- You can still move left and right and back. It's only forward move which is blocked. By the way, it can be regained if you move back 

# How to start?

## Installation & Build

```bash
cd /root/ros2_ws
colcon build
source install/setup.bash
```

## Running the Robot with Safety System

**Terminal 1 - Launch Gazebo + RViz:**
```bash
ros2 launch my_diff_robot robot.launch.py
```
Wait 5-10 seconds for Gazebo to fully load.

**Terminal 2 - Start Safety System (after ~10 seconds):**
```bash
python3 src/my_diff_robot/scripts/safety_system.py
```

**Terminal 3 - Start Teleop Controller:**
```bash
python3 src/my_diff_robot/scripts/simple_teleop.py
```
## Safety Features

**Collision Avoidance**: Robot automatically stops when obstacle is detected within 0.3m  
**Automatic Unlock**: Forward movement is re-enabled after moving backward and clearing obstacle  
**Backward Movement**: Always allowed even when forward is blocked  
**Rotation**: Left/right rotation works independently of collision detection  

## Architecture

```
simple_teleop.py (user input)
    ↓ publishes to /cmd_vel_request
safety_system.py (safety checks)
    ↓ filters unsafe commands
    ↓ publishes to /diff_drive_controller/cmd_vel
Gazebo simulator (executes safe commands)
```