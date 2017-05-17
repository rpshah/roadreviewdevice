import spidev
import time
import os
import json
from Ldr import Ldr
from Noise import Noise
from Air import Air
from Temperature import Temperature
from Location import Location

#for motion
from mpu6050 import mpu6050
import math
#import time
from gyroAnalyzer import DataQueue
from Queue import Queue
from threading import Thread
import sys

# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# For certificate based connection
myMQTTClient = AWSIoTMQTTClient("LDRTesting")
# For TLS mutual authentication
myMQTTClient.configureEndpoint("a2h72bxx1czemj.iot.us-west-2.amazonaws.com", 8883)
myMQTTClient.configureCredentials("/home/pi/Desktop/IOT_THING_RoadReviewPublisher/rootca.pem", "/home/pi/Desktop/IOT_THING_RoadReviewPublisher/private.pem.key", "/home/pi/Desktop/IOT_THING_RoadReviewPublisher/certi.txt")
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

device_id=1234
spi = spidev.SpiDev()
spi.open(0,0)

ldr = Ldr(spi)
noise = Noise(spi)
air = Air(spi)
weather = Temperature()
loc = Location()

#for motion
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
    sys.exit()
    #what to do if sensor is not working?

def sense_motion(motionQueue):
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
            #print "No Motion"
            try:
                motionQueue.put_nowait(0);
            except:
                pass
            
        elif(gxMotion == 3 or gyMotion == 3 or gzMotion == 3):
            #print "Pothole Detected"
            try:
                motionQueue.put_nowait(3);
            except:
                pass
        elif(gxMotion == 2 or gyMotion == 2 or gzMotion == 2):
            #print "Vibrations Detected"
            try:
                motionQueue.put_nowait(2);
            except:
                pass
        elif(gxMotion == 1 or gyMotion == 1 or gzMotion == 1):
            #print "Vehicle in Normal Motion"
            try:
                motionQueue.put_nowait(1);
            except:
                pass


myMQTTClient.connect() 

motionQueue = Queue(maxsize=0)
motionThread = Thread(target=sense_motion , args=(motionQueue,))
motionThread.setDaemon(True)
motionThread.start()
  
while True:
        lightPer = ldr.getLdrPer()
        noiseData = noise.getNoise()
        LPG,CO,SMOKE = air.getData()
        tempData,humData = weather.getData()
        lati,longi = loc.getLocation()
        currenttime=time.time()
        envData={}
        envData['DeviceId']=device_id
        envData['Timestamp']=currenttime
        envData['LightIntensity']=lightPer
        envData['Noise']=noiseData
        envData['LPG']=LPG
        envData['CO']=CO
        envData['SMOKE']=SMOKE
        envData['Temperature']=tempData
        envData['Humidity']=humData
        envData['Latitude']=lati
        envData['Longitude']=longi
        envData_json=json.dumps(envData)

        #print envData     
        
        myMQTTClient.publish("EnvironmentData",envData_json,0)

        #for motion
        endlati,endlongi = loc.getLocation()
        heavyforce = 0
        vibrations = 0
        while not motionQueue.empty():
            motionGot = motionQueue.get()
            if(motionGot == 3):
                heavyforce = heavyforce + 1;
            elif(motionGot == 2):
                vibrations = vibrations + 1;
                
        motionQueue.task_done()
        
        roadData={}
        roadData['DeviceId']=device_id
        roadData['Timestamp']=currenttime
        roadData['StartLatitude']=lati
        roadData['StartLongitude']=longi
        roadData['HeavyForce']=heavyforce
        roadData['Vibrations']=vibrations
        roadData['EndLatitude']=endlati
        roadData['EndLongitude']=endlongi
        roadData_json=json.dumps(roadData)

        #print roadData     
        
        myMQTTClient.publish("RoadCondition",roadData_json,0)

        time.sleep(30)
    
myMQTTClient.disconnect()
motionQueue.join()
