from collections import deque
import math

class DataQueue:
    
    def __init__(self):
        self.data = deque([0,0,0,0,0],5)

    def add(self,val):
        self.data.pop()
        self.data.appendleft(val)

    def getAvg(self):
        total = 0
        for val in self.data:
            total = total + val
        avg = total/5.0
        return avg

    def getStdDev(self):
        avg = self.getAvg()
        stdDev = 0
        for val in self.data:
            stdDev = (val-avg)*(val-avg)
        stdDev = stdDev/5.0
        stdDev = math.sqrt(stdDev)
        return stdDev 

    #returns current status of motion,for last readings in queue
    # 0 - No Motion
    # 1 - Normal Motion(Default)
    # 2 - Vibration
    # 3 - HeavyForce
    def getMotionStatus(self):
        stdDev = self.getStdDev()
        if(stdDev >= 0 and stdDev <= 2):
           return 0
        elif(stdDev >2 and stdDev <= 15):
           return 1
        elif(stdDev >15 and stdDev <=30):
           return 2
        else:
           return 3
