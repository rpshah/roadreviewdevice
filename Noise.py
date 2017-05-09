import spidev
import time
import os
from math import log

class Noise:

    def __init__(self,bus):
        self.spi = bus
        self.noise = 2
        self.delay = 0.2
         
    def ReadChannel(self,channel):
        adc = self.spi.xfer2([1,(8+channel)<<4,0])
        data = ((adc[1]&3) << 8) + adc[2]
        return data
 
    def ConvertVolts(self,data,place):
        volts = (data * 3.3) / float(1023)
        volts = round(volts,place)
        return volts

    def ConvertDecibles(self,data,maxreading,place):
        if data == 0 :
           data = 1 
        val = maxreading/float(data)
        db = 16.801 * (log(val)) + 9.875
        return round(db, place)
 
    def getNoise(self):
        noise_value = 0
        for i in range(0,5):
            noise_value += self.ReadChannel(self.noise)
            time.sleep(self.delay)

        noise_value /= 5.0
        noise = self.ConvertDecibles(noise_value,1023,2)
        return noise
    


