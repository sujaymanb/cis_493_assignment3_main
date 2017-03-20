#!/usr/bin/env python
'''
import rospy
import turtlesim.srv
import geometry_msgs/PoseStamped.msg
import time

#'{header: {stamp: now, frame_id: "map"}, pose: {position: {x: 1.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}'

runner_pose = Pose()
my_pose = Pose()

def getRunnerPose(data):
	global runner_pose
	runner_pose = data

def getMyPose(data):
	global my_pose
	my_pose = data

def spawnRunner():
	# random spawn bounds x = 0 - 11, y = 0 - 11, theta = 0 - 2 * pi?
	rospy.wait_for_service('spawn')
	spawner = rospy.ServiceProxy('spawn', turtlesim.srv.Spawn)
	spawner(random.uniform(1, 11) , random.uniform(1, 11), 0, 'runner')

def checkIfDead():
	if(runner_pose.x == None and runner_pose.y == None):
		return		

	distance_to_runner = numpy.sqrt((runner_pose.x - my_pose.x) ** 2 + (runner_pose.y - my_pose.y) ** 2)
	
	print("distance: %s"%distance_to_runner)
	if(distance_to_runner < 1):
		try:
			rospy.wait_for_service('kill')
			killer = rospy.ServiceProxy('kill', turtlesim.srv.Kill)
			killer('runner')
			runner_pose.x = None
			runner_pose.y = None
			spawnRunner()
		except rospy.ServiceException, e:
			print "Service call falied: %s"%e

def chase():
	velocity_publisher = rospy.Publisher('/hunter/cmd_vel', Twist, queue_size=10)
	vel_msg = Twist()
	speed = 1

	while not rospy.is_shutdown():
		rospy.Subscriber("runner/pose", Pose, getRunnerPose)
		rospy.Subscriber("hunter/pose", Pose, getMyPose)
		if(runner_pose.x != None and runner_pose.y != None):		
				angle_to_runner = numpy.arctan2((runner_pose.y - my_pose.y), (runner_pose.x - my_pose.x))	
		angle_difference = angle_to_runner - my_pose.theta
		if angle_difference < -numpy.pi:
			angle_difference += 2 * numpy.pi

		if angle_difference > numpy.pi:
			angle_difference -= 2 * numpy.pi

		print("Angle Difference: %s"%angle_difference)
		vel_msg.linear.x = speed
		vel_msg.linear.y = 0
		vel_msg.linear.z = 0
		vel_msg.angular.x = 0
		vel_msg.angular.y = 0
		vel_msg.angular.z = angle_difference
		velocity_publisher.publish(vel_msg)
		checkIfDead()
		time.sleep(0.1)
	  
def killDefault():
	try:
		rospy.wait_for_service('kill')
		killer = rospy.ServiceProxy('kill', turtlesim.srv.Kill)
		killer('turtle1')
	except rospy.ServiceException, e:
		print "Service call failed: %s"%e
		print "turtle1 could be dead already"

def spawn():
	try:
		rospy.wait_for_service('spawn')
		spawner = rospy.ServiceProxy('spawn', turtlesim.srv.Spawn)
		spawner(random.uniform(0, 11), random.uniform(0, 11), random.uniform(0, 2 * numpy.pi), 'hunter')
	except rospy.ServiceException, e:
		print "Service call falied: %s"%e
		print "does hunter already exist?"

if __name__ == "__main__":
	try:
		rospy.init_node('hunter')
		random.seed()
		killDefault()
		spawn()
		chase()
	except rospy.ROSInterruptException: pass
'''

import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from math import radians, degrees
from actionlib_msgs.msg import *
from geometry_msgs.msg import Point

class map_nav():
    def __init__(self):
        self.xssw = 0.365
        self.yssw = -0.347
        
        rospy.init_node('map_nav', anonymous=False)
        self.goalReached = self.moveToGoal(self.xssw, self.yssw)

        if(self.goalReached):
            rospy.loginfo("SSW corner reached")
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

def goal_client():
    client = actionlib.SimpleActionClient(
