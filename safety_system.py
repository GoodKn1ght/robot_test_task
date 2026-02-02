#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import TwistStamped
import math

class SafetySystem(Node):
    def __init__(self):
        super().__init__('safety_system')
        
        self.min_distance = 0.3
        self.blocked_forward = False
        
        # We takes commands from teleop for safety checking before sending to Gazebo
        self.cmd_sub = self.create_subscription(
            TwistStamped,
            '/cmd_vel_request',
            self.cmd_callback,
            10)
        
        # Listen to LIDAR data
        self.lidar_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.lidar_callback,
            10)
        
        # This topic is used to make move in simulation
        self.safe_pub = self.create_publisher(
            TwistStamped,
            '/diff_drive_controller/cmd_vel',
            10)
        
        self.last_request = None
        self.valid_ranges = []
        
        self.get_logger().info(f'Safety System готова (мін. дистанція: {self.min_distance}м)')

    def cmd_callback(self, msg: TwistStamped):
        self.last_request = msg

    def lidar_callback(self, msg: LaserScan):
        # Simply ignore invalid ranges
        self.valid_ranges = [r for r in msg.ranges 
                            if not math.isnan(r) and not math.isinf(r) and r > 0]
        
        if not self.valid_ranges or self.last_request is None:
            return

        # Find the closest obstacle
        min_distance = min(self.valid_ranges)
        safe_msg = self.check_safety(self.last_request, min_distance)
        self.safe_pub.publish(safe_msg)

    def check_safety(self, request: TwistStamped, min_distance: float) -> TwistStamped:
        # When moving forward, check lidar logs
        safe_msg = TwistStamped()
        safe_msg.header = request.header
        safe_msg.twist.angular.z = request.twist.angular.z 
        if request.twist.linear.x > 0.01:
            if min_distance < self.min_distance:
                if not self.blocked_forward:
                    self.get_logger().error(
                        f' Danger {min_distance:.2f}м < {self.min_distance}м'
                    )
                    self.blocked_forward = True
                # forcing to stop
                safe_msg.twist.linear.x = 0.0
                return safe_msg
            # when previously blocked but now clear
            elif self.blocked_forward and min_distance > 0.4:
                self.get_logger().info(f'✅ ВІЛЬНО! {min_distance:.2f}м')
                self.blocked_forward = False
            safe_msg.twist.linear.x = request.twist.linear.x
        
        # We can move backward freely when forward is blocked
        elif request.twist.linear.x < -0.01:
            if self.blocked_forward:
                self.blocked_forward = False
                self.get_logger().info('Moving backward, unblocking forward movement.')
            safe_msg.twist.linear.x = request.twist.linear.x
        else:
            safe_msg.twist.linear.x = 0.0
        
        return safe_msg

def main():
    rclpy.init()
    rclpy.spin(SafetySystem())
    rclpy.shutdown()

if __name__ == '__main__':
    main()