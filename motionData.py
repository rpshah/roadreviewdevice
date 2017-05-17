#!/usr/bin/python

from mpu6050 import mpu6050
import math
import time
from gyroAnalyzer import DataQueue


def dist(a,b):
    return math.sqrt((a*a)+(b*b))

def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)

try:
    sensor = mpu6050(0x68)
except:
    pass
    #what to do if sensor is not working?
    
#DataQueues
gx_queue = DataQueue()
gy_queue = DataQueue()
gz_queue = DataQueue()

while True :
    accelerometer_data = sensor.get_accel_data(True)
    gyroscope_data= sensor.get_gyro_data()

    #print "gyro data"
    #print "---------"
    gyro_xout = gyroscope_data['x']
    gyro_yout = gyroscope_data['y']
    gyro_zout = gyroscope_data['z']

    #print "gyro_xout: ", gyro_xout, " scaled: ", (gyro_xout / 131)
    #print "gyro_yout: ", gyro_yout, " scaled: ", (gyro_yout / 131)
    #print "gyro_zout: ", gyro_zout, " scaled: ", (gyro_zout / 131)

    #analysis
    gx_queue.add(gyro_xout / 131 * 100)
    gy_queue.add(gyro_yout / 131 * 100)
    gz_queue.add(gyro_zout / 131 * 100)
    #print
    #print "Standard Dev (x,y,z):  (", gx_queue.getStdDev(), " , ", gy_queue.getStdDev(), " ,", gz_queue.getStdDev(), " )"

    #print
    #print "accelerometer data"
    #print "------------------"

    accel_xout = accelerometer_data['x']
    accel_yout = accelerometer_data['y']
    accel_zout = accelerometer_data['z']

    accel_xout_scaled = accel_xout / 16384.0
    accel_yout_scaled = accel_yout / 16384.0
    accel_zout_scaled = accel_zout / 16384.0

    #print "accel_xout: ", accel_xout, " scaled: ", accel_xout_scaled
    #print "accel_yout: ", accel_yout, " scaled: ", accel_yout_scaled
    #print "accel_zout: ", accel_zout, " scaled: ", accel_zout_scaled

    #print "x rotation: " , get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
    #print "y rotation: " , get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)

    time.sleep(0.2)

    gxMotion = gx_queue.getMotionStatus()
    gyMotion = gy_queue.getMotionStatus()
    gzMotion = gz_queue.getMotionStatus()

    if(gxMotion == 0 and gyMotion == 0 and gzMotion == 0):
        print "No Motion"
    elif(gxMotion == 3 or gyMotion == 3 or gzMotion == 3):
        print "Pothole Detected"
    elif(gxMotion == 2 or gyMotion == 2 or gzMotion == 2):
        print "Vibrations Detected"
    elif(gxMotion == 1 or gyMotion == 1 or gzMotion == 1):
        print "Vehicle in Normal Motion"
