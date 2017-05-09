import Adafruit_DHT as dht

class Temperature:

    def getData(self):
        h,t = dht.read_retry(dht.AM2302, 5, 5)
        if(h is not None and t is not None):
            print 'Temp={0:0.1f}*C Humidity={1:0.1f}%'.format(h,t)
            return h,t
        else:
            print "No input found Temp"
            return 0,0

def main():
    temp = Temperature()
    print temp.getData()
    
if __name__ == "__main__": main()    
