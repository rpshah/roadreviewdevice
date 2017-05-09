import spidev
import time
import os
import math

MQ_PIN= 0                     # (0)     //define which analog input channel you are going to use
RL_VALUE= 5 #                     (5)     //define the load resistance on the board, in kilo ohms
RO_CLEAN_AIR_FACTOR = 9.83 #         (9.83)  //RO_CLEAR_AIR_FACTOR=(Sensor resistance in clean air)/RO,
                   #                                  //which is derived from the chart in datasheet

    #/***********************Software Related Macros************************************/
CALIBARAION_SAMPLE_TIMES = 50 #     (50)    //define how many samples you are going to take in the calibration phase
CALIBRATION_SAMPLE_INTERVAL =200 # (500)   //define the time interal(in milisecond) between each samples in the
    #               //cablibration phase
READ_SAMPLE_INTERVAL = 50 #         (50)    //define how many samples you are going to take in normal operation
READ_SAMPLE_TIMES = 5 #            (5)     //define the time interal(in milisecond) between each samples in 
                                         #                          //normal operation
GAS_LPG= 0
GAS_CO=1
GAS_SMOKE=2
#/*****************************Globals***********************************************/
LPGCurve =[2.3,0.21,-0.47] #  //two points are taken from the curve. 
COCurve=[2.3,0.72,-0.34] #    //two points are taken from the curve. 
SmokeCurve =[2.3,0.53,-0.44] #    //two points are taken from the curve. 
Ro =  10      #           //Ro is initialized to 10 kilo ohms

mq2 = 2

class Air:

    def MQResistanceCalculation(self,raw_adc):
        if raw_adc == 0 :
            return 0
        return ( (RL_VALUE*(1023-raw_adc)/raw_adc))
    
 
    def MQCalibration(self,mq_pin):
        val=0
        for i in range(0,CALIBARAION_SAMPLE_TIMES) : #           //take multiple samples
            val += self.MQResistanceCalculation(self.ReadChannel(mq2))
            time.sleep(CALIBRATION_SAMPLE_INTERVAL/1000)
        val = val/CALIBARAION_SAMPLE_TIMES                #   //calculate the average value
        val = val/RO_CLEAN_AIR_FACTOR #                        //divided by RO_CLEAN_AIR_FACTOR yields the Ro 
        return val

    def MQRead(self,mq_pin) :
        rs=0
        for i in range(0,READ_SAMPLE_TIMES) :
            rs += self.MQResistanceCalculation(self.ReadChannel(mq2))
            time.sleep(READ_SAMPLE_INTERVAL/1000)
        rs = rs/READ_SAMPLE_TIMES
        return rs  

    def MQGetGasPercentage(self,rs_ro_ratio,gas_id) :
        if ( gas_id == GAS_LPG ) :
            return self.MQGetPercentage(rs_ro_ratio,LPGCurve)
        elif ( gas_id == GAS_CO ) :
            return self.MQGetPercentage(rs_ro_ratio,COCurve)
        elif ( gas_id == GAS_SMOKE ) :
            return self.MQGetPercentage(rs_ro_ratio,SmokeCurve)
        return 0


    def MQGetPercentage(self,rs_ro_ratio,pcurve) :
        return (math.pow(10,( ((math.log(rs_ro_ratio)-pcurve[1])/pcurve[2]) + pcurve[0])))


    def __init__(self,bus):
        self.spi = bus
        self.mq2 = 2
        self.delay = 0.2
         
    def ReadChannel(self,channel):
        adc = self.spi.xfer2([1,(8+channel)<<4,0])
        data = ((adc[1]&3) << 8) + adc[2]
        return data
 
    def ConvertVolts(self,data,place,volt):
        volts = (data * volt) / float(1023)
        volts = round(volts,place)
        return volts

    def ConvertDecibles(self,data,maxreading,place):
        if data == 0 :
           data = 1 
        val = maxreading/float(data)
        db = 16.801 * (log(val)) + 9.875
        return round(db, place)
 
    def getData(self):
        mq2_value = self.ReadChannel(self.mq2)
        mq2_volts = self.ConvertVolts(mq2_value,2,5.0)
 
        #print "--------------------------------------"
        #print("MQ-2 : {} ({}V)".format(mq2_value,mq2_volts))
        #print("LPG : {:1f} ppm".format(MQGetGasPercentage(MQRead(MQ_PIN)/Ro,GAS_LPG) ))
        #print("CO : {:1f} ppm".format(MQGetGasPercentage(MQRead(MQ_PIN)/Ro,GAS_CO) ))
        #print("SMOKE : {:1f} ppm".format(MQGetGasPercentage(MQRead(MQ_PIN)/Ro,GAS_SMOKE) ))
        lpg = self.MQGetGasPercentage(self.MQRead(MQ_PIN)/Ro,GAS_LPG)
        co = self.MQGetGasPercentage(self.MQRead(MQ_PIN)/Ro,GAS_CO)
        smoke = self.MQGetGasPercentage(self.MQRead(MQ_PIN)/Ro,GAS_SMOKE)

        return lpg,co,smoke
    

