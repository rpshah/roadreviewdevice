import spidev
import time
import os
import json
from Ldr import Ldr
from Noise import Noise
from Air import Air
from Temperature import Temperature
from Location import Location

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
 
myMQTTClient.connect() 
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
        print envData
        
        
        
        myMQTTClient.publish("EnvironmentData",envData_json,0)
        #print "--------------------------------------"
        #print "Light : "
        #print lightPer
 
        time.sleep(1)
    
#myMQTTClient.disconnect()
