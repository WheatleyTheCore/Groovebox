##This is the main client file! It takes raw input from the piezos, 
##and passes them to the server as offsets. 

#adc stuff
import board
i2c = board.I2C()
from adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15
ads = ADS1115(i2c)
ads.data_rate = 860
#for waiting
import time
#for communication between programs
import zmq

#simple port of MovingAverageFilter from arduino to python, with some tweaks
#as of recent, unnecessary.
"""
class MovingAverageFilter:
    def __init__(self, dataPointsCount):
        self.dataPointsCount = dataPointsCount #num of data points averaged over
        self.k = 0 #position of data point to be replaced next
        self.values = [0] * dataPointsCount #array with data points in it
        self.average = 0
        
    def process(self, inp):
        self.values[self.k] = inp #replace oldest value with new value
        self.k = (self.k+1) % self.dataPointsCount #shift position of "oldest value" forward
        
        self.average = int(sum(self.values)/self.dataPointsCount)
        return self.average #average of all values
    
    def fill(self, inp):
        self.values = [inp for x in self.values]
        self.average = inp
"""

#easier to write, has error handling
def getPin(pin):
    try:
        if (pin == 0): return AnalogIn(ads, ads1x15.Pin.A1).value
        elif (pin == 1): return AnalogIn(ads, ads1x15.Pin.A2).value
        elif (pin == 2): return AnalogIn(ads, ads1x15.Pin.A3).value
    except Exception as e: #if an error occurs, just try again
        print(f"a little trouble with pin {pin}: {e}. retrying...")
        return getPin(pin)
            

#set up connection to zmq server
context = zmq.Context()
print("connecting to server")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")
print("connected :3")

#some variables that should only be initialized once
count = 0 #unnecessary
onsetFlag = -1 #-1 when no onset is happening, 0-3 when an onset is happening
prevEvent = 0
piezoInputs = [0]*3
#piezoInputsRaw = [0]*3
MIN_VAL_FOR_ONSET = 100
piezoActivatedThisOnset = [0]*3

while (True):
    #now = time.time_ns()
    
    #get all piezo values at this moment
    piezoInputs[0] = getPin(0)
    piezoInputs[1] = getPin(1)
    piezoInputs[2] = getPin(2)
    
    highestPiezoVal = max(piezoInputs)

    #if an onset is happening, update the running maxes of the piezos
    if (onsetFlag != -1):
        for i in range(3):
            piezoActivatedThisOnset[i] = max(piezoInputs[i], piezoActivatedThisOnset[i])
        if (onsetFlag != 3 and min(piezoActivatedThisOnset) > MIN_VAL_FOR_ONSET):
            socket.send_string("correction 3")
            print("3 correction")
            onsetFlag = 3
            socket.recv()

    #if there isn't an onset right now, continuously check for one:
    if ((onsetFlag == -1) and highestPiezoVal > MIN_VAL_FOR_ONSET and (time.time_ns() - prevEvent) > 15000000): #15 miliseconds?
        print(f"onset!!!{count}")
        #get another round of inputs, just in case the initial input was kinda weak
        piezoActivatedThisOnset[0] = max(piezoInputs[0], getPin(0))
        piezoActivatedThisOnset[1] = max(piezoInputs[1], getPin(1))
        piezoActivatedThisOnset[2] = max(piezoInputs[2], getPin(2))
        print(f"piezos: {piezoActivatedThisOnset}")

        if (min(piezoActivatedThisOnset) > MIN_VAL_FOR_ONSET):
            onsetFlag = 3 #all three are being pushed
        else:
            onsetFlag = piezoActivatedThisOnset.index(max(piezoActivatedThisOnset))
        socket.send_string(str(onsetFlag))

        prevEvent = time.time_ns()
        count += 1
        socket.recv()

    #if there is an onset happening right now, continually check whether or not it has ended:
    elif ((onsetFlag != -1) and highestPiezoVal < MIN_VAL_FOR_ONSET and (time.time_ns() - prevEvent) > 15000000):
        print(f"offset...{(time.time_ns() - prevEvent) / 1000000000}. piezos activated: {piezoActivatedThisOnset}")
        onsetFlag = -1
        piezoActivatedThisOnset = [0]*3
        prevEvent = time.time_ns()

