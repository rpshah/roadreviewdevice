import serial
import RPi.GPIO as GPIO      
import os, time
from decimal import *

delay = 1

GPIO.setmode(GPIO.BOARD)    

def find(str, ch):
    for i, ltr in enumerate(str):
        if ltr == ch:
            yield i


class Location:

    def __init__(self):
        self.port = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=1)

    
    def getLocation(self):
        """ Get Latitude,Longitude"""

        #clean the buffers before reading and read fresh data everytime
        self.port.reset_input_buffer()
        self.port.reset_output_buffer()                        

        cd=1   
        while cd <= 3:
            ck=0
            fd=''
            while ck <= 50:
                rcv = self.port.read(10)
                fd=fd+rcv
                ck=ck+1

            try:
               #print fd
               if '$GPRMC' in fd:
                    ps=fd.find('$GPRMC')
                    dif=len(fd)-ps
                    #print dif
                    if dif > 50:
                        data=fd[ps:(ps+50)]
                        #print data
                        p=list(find(data, ","))
                        lat=data[(p[2]+1):p[3]]
                        lon=data[(p[4]+1):p[5]]

                        s1=lat[2:len(lat)]
                        s1=Decimal(s1)
                        s1=s1/60
                        s11=int(lat[0:2])
                        s1=s11+s1

                        s2=lon[3:len(lon)]
                        s2=Decimal(s2)
                        s2=s2/60
                        s22=int(lon[0:3])
                        s2=s22+s2

                        #print s1
                        #print s2

                        return float("{0:.6f}".format(round(s1,6))),float("{0:.6f}".format(round(s2,6)))
            except:
                 pass
                 #print "No Reading"
                 #print " "

            cd=cd+1
            #print cd

        return 0,0

    def __del__(self):
        self.port.close()


def main():
    loc = Location()
    print loc.getLocation()


if __name__ == "__main__": main()    


    
