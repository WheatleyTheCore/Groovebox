#This is the main server file!! It takes offsets from the client, 
#and fits them into 2-bar segments. It always assumes that the first
#four imputs are establishing tempo, and all inputs afterward are processed normally.

import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
#poller = zmq.Poller()
#poller.register(socket, zmq.POLLIN)

#get tempo from first 4 taps, average the ioi
tapTimes = [0]*4
for i in range(4):
    message = socket.recv()
    tapTimes[i] = time.time()
    socket.send(b"gotcha")

intervals = [(tapTimes[i+1] - tapTimes[i]) for i in range(3)]
averageIOI = sum(intervals) / 3
bpm = (1 / averageIOI) * 60
#print(f"bpm: {bpm}")
time.sleep(averageIOI - (time.time() - tapTimes[3]))
#print("tap")
#time.sleep(averageIOI)
#print("tic")
#time.sleep(averageIOI)
#print("tic")
#time.sleep(averageIOI)
#print("tic")

twoBarsStartTime = time.time()
twoBarsRemainingSecs = averageIOI * 8
prevEventTime = time.time()
notesThisTwoBars = []
while (True):
    if (socket.poll(twoBarsRemainingSecs * 1000, zmq.POLLIN)):
        message = socket.recv()
        socket.send(b"yessir")
        print(f"we got message: {message}")
        notesThisTwoBars.append((message, time.time() - twoBarsStartTime))
        now = time.time()
        twoBarsRemainingSecs -= (now - prevEventTime)
        prevEventTime = now
        print(f"remaining secs: {twoBarsRemainingSecs}")
        
    else:
        twoBarsRemainingSecs = averageIOI * 8
        prevEventTime = time.time()
        twoBarsStartTime = time.time()
        print(f"end of 2 bars. refresh time to be {twoBarsRemainingSecs}")
        print(notesThisTwoBars)
        notesThisTwoBars = []
    
    #wait for message
    #message = socket.recv()
    #print("we got a thing: %s" % message)

    #reply
    #socket.send(b"yessir")