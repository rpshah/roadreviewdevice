import spidev
import time
import os

class Ldr:

    def __init__(self,bus):
        self.spi = bus
        self.ldr = 0
        self.delay = 0.2
         
    def ReadChannel(self,channel):
        adc = self.spi.xfer2([1,(8+channel)<<4,0])
        data = ((adc[1]&3) << 8) + adc[2]
        return data
 
    def ConvertVolts(self,data,place):
        volts = (data * 3.3) / float(1023)
        volts = round(volts,place)
        return volts
 
    def getLdrPer(self):
        ldr_value = 0
        for i in range(0,5):
            ldr_value += self.ReadChannel(self.ldr)
        #ldr_volts = ConvertVolts(ldr_value,2)
 
        #print "--------------------------------------"
        #print("Light : {} ({}V)".format(ldr_value,ldr_volts))
            time.sleep(self.delay)

        ldr_value /= 5.0
        lightPer = self.translate(ldr_value,0,1023,0,100)
        return lightPer
    

    def translate(self,value, leftMin, leftMax, rightMin, rightMax):
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)
    
