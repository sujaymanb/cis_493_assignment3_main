#!/usr/bin/env python

import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from math import radians, degrees
from actionlib_msgs.msg import *
from geometry_msgs.msg import Point

class map_nav():
    def __init__(self):
        self.xssw = 0.477
        self.yssw = 0.086
        self.xsse = 0.364
        self.ysse =-3.218
        self.xnne = 8.181
        self.ynne =-4.418
        self.xwnw = 8.244
        self.ywnw =-0.510
        rospy.init_node('map_nav', anonymous=False)
        self.goalReached = self.moveToGoal(self.xssw, self.yssw)

        if(self.goalReached):
            rospy.loginfo("SSW corner reached")
        else:
            rospy.loginfo("Failed to reach goal")

        self.goalReached = self.moveToGoal(self.xsse,self.ysse)

        if(self.goalReached):
            rospy.loginfo("SSE corner reached")
        else:
            rospy.loginfo("Failed to reach goal")

        self.goalReached = self.moveToGoal(self.xnne,self.ynne)

        if(self.goalReached):
            rospy.loginfo("NNE corner reached")
        else:
            rospy.loginfo("Failed to reach goal")

        self.goalReached = self.moveToGoal(self.xwnw,self.ywnw)

        if(self.goalReached):
            rospy.loginfo("WNW corner reached")
        else:
            rospy.loginfo("Failed to reach goal")

    def shutdown(self):
        rospy.loginfo("Exiting...")
        rospy.sleep()

    def moveToGoal(self,xGoal,yGoal):
        ac = actionlib.SimpleActionClient("move_base", MoveBaseAction)

        while(not ac.wait_for_server(rospy.Duration.from_sec(5.0))):
            rospy.loginfo("Waiting for move_base action server to respond")

        goal = MoveBaseGoal()

        # the header

        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()

        # point and orientation

        goal.target_pose.pose.position = Point(xGoal,yGoal,0)
        goal.target_pose.pose.orientation.x = 0.0
        goal.target_pose.pose.orientation.y = 0.0
        goal.target_pose.pose.orientation.z = 0.0
        goal.target_pose.pose.orientation.w = 1.0
        
        rospy.loginfo("Sending goal...")
        ac.send_goal(goal)

        ac.wait_for_result(rospy.Duration(60))

        if(ac.get_state() == GoalStatus.SUCCEEDED):
            rospy.loginfo("Goal successful")
            return True
        else:
            rospy.loginfo("Goal falied")
            return False

if __name__ == '__main__':
    try:
        map_nav()
        rospy.spin()
    except rospy.ROSInterruptException:
        rospy.loginfo("map_nav node terminated")
