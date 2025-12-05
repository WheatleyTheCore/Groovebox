##This is the main client file! It takes raw input from the piezos, 
##and passes them to the server as offsets. 

#adc stuff
import board
i2c = board.I2C()
from adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15
ads = ADS1115(i2c)
#for waiting
import time
#import os
#for communication between programs
import zmq

#simple port of MovingAverageFilter from arduino to python, with some tweaks
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

#some moving average filters

#some constants
#OFFSET_ENERGY_DELTA_THRESH = 0.8
#OFFSET_SETTLE_TIME = 20 #milliseconds

#set up connection to zmq server
context = zmq.Context()
print("connecting to server")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")
print("connected :3")

#some variables that should only be initialized once
count = 0 #unnecessary
onsetFlag = False
prevEvent = 0
piezoInputs = [0]*3
#piezoInputsRaw = [0]*3
MIN_VAL_FOR_ONSET = 100
piezoActivatedThisOnset = [0]*3

#calibrate
"""
piezoOffsets = [MovingAverageFilter(5), MovingAverageFilter(5), MovingAverageFilter(5)]
piezoOffsets[0].fill(AnalogIn(ads, ads1x15.Pin.A1).value)
piezoOffsets[1].fill(AnalogIn(ads, ads1x15.Pin.A2).value)
piezoOffsets[2].fill(AnalogIn(ads, ads1x15.Pin.A3).value)
"""
while (True):
    #now = time.time_ns()
    
    #get a;; piezo values at this moment
    piezoInputs[0] = AnalogIn(ads, ads1x15.Pin.A1).value# - piezoOffsets[0].average
    piezoInputs[1] = AnalogIn(ads, ads1x15.Pin.A2).value# - piezoOffsets[1].average
    piezoInputs[2] = AnalogIn(ads, ads1x15.Pin.A3).value# - piezoOffsets[2].average

    #for i in range(3):
    #    piezoInputsRaw[i] = piezoInputs[i] + piezoOffsets[i].average
    
    highestPiezoVal = max(piezoInputs)

    #if there isn't an onset right now, continuously check for one:
    if ((not onsetFlag) and highestPiezoVal > MIN_VAL_FOR_ONSET and (time.time_ns() - prevEvent) > 15000000): #15 miliseconds?
        print(f"onset!!!{count}")
        #piezoInputs[0] = AnalogIn(ads, ads1x15.Pin.A1).value 
        #piezoInputs[1] = AnalogIn(ads, ads1x15.Pin.A2).value 
        #piezoInputs[2] = AnalogIn(ads, ads1x15.Pin.A3).value 
        onsetFlag = True
        prevEvent = time.time_ns()
        count += 1

    #if there is an onset happening right now, continually check whether or not it has ended:
    elif (onsetFlag and highestPiezoVal < MIN_VAL_FOR_ONSET and (time.time_ns() - prevEvent) > 15000000):
        elapsed = time.time_ns() - prevEvent #irrelevant, will delete later
        
        if (min(piezoActivatedThisOnset) != 0):
            packet = 3 #all three
        else:
            packet = piezoActivatedThisOnset.index(max(piezoActivatedThisOnset))
        socket.send_string(str(packet))

        print(f"offset...{elapsed / 1000000000}. piezos activated: {piezoActivatedThisOnset}")
        onsetFlag = False
        for i in range(3):
            piezoActivatedThisOnset[i] = 0
        socket.recv()
        prevEvent = time.time_ns()

    #if there's an onset right now, mark all piezos that are detecting pressure
    if (onsetFlag):
        for i in range(3):
            if (piezoInputs[i] > MIN_VAL_FOR_ONSET):
                piezoActivatedThisOnset[i] = max(piezoInputs[i], piezoActivatedThisOnset[i])
    
    #if (not onsetFlag):
    #    for i in range(3):
    #        piezoOffsets[i].process(piezoInputsRaw[i])
    #print(f"filter: {piezoInputs}")
    #print(f"filter at 1: {piezoOffsets[0].values} and average is {piezoOffsets[0].average}")
    #print(f"raw: {piezoInputsRaw}")
    """
    raw_avg_pressure = (AnalogIn(ads, ads1x15.Pin.A1).value +
                        AnalogIn(ads, ads1x15.Pin.A2).value +
                        AnalogIn(ads, ads1x15.Pin.A3).value) /3
    filtered_avg_pressure = pressureFilter.process(raw_avg_pressure) - 440
    ema_s = (EMA_A * rawPiezoInput) + ((1-EMA_A)*ema_s)
    highpassValue = min(100, max(0, rawPiezoInput - ema_s)) #constrains between 0 and 100
    filteredPiezoInput = piezoFilter.process(highpassValue)
    
    #onset stuff!
    detectedOnset = (filteredPiezoInput - previousPiezoInput > OFFSET_ENERGY_DELTA_THRESH)
    if (detectedOnset and (not onsetFlag) and (filtered_avg_pressure < 100)):
        onsetFlag = True
        onsetTime = round(time.time() * 1000) #time in miliseconds
        #print("onset!!!")
    
    if ((not detectedOnset) and onsetFlag):
        if (round(time.time() * 1000) - onsetTime > OFFSET_SETTLE_TIME):
            onsetFlag = False
    """
    
    #os.system('clear')
    #print(f"""onstFlg: {onsetFlag}
    #      detOnst: {detectedOnset}
    #      filt-prev: {filteredPiezoInput - previousPiezoInput}
    #      rawInp: {rawPiezoInput}
    #      filt inp: {filteredPiezoInput}
    #      prev inp: {previousPiezoInput}
    #      time since las: {(time.time_ns() - now) / 1000000}""")
    #previousPiezoInput = filteredPiezoInput
    