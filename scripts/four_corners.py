#!/usr/bin/env python

import numpy
import rospy
import random
import turtlesim.srv
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import time

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

