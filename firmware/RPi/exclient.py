#Plays audio

import time
import zmq
import simpleaudio as sa
from mido import MidiFile

INPUT_FILENAME = "output.mid"

midiToWav = {60: sa.WaveObject.from_wave_file("rock-kit/Rock-Kit-Kick-ff-1.wav"), 
             61: sa.WaveObject.from_wave_file("rock-kit/Rock-Kit-HiHat-Open.wav"), 
             62: sa.WaveObject.from_wave_file("rock-kit/Rock-Snare-ff-1.wav")}

bpm = -1
ioi = -1
events = []
untilNext = 0
def bpmToMetronome(newBpm):
    global bpm, ioi, events, untilNext
    startOf2Measures = time.time()
    #play first things first
    sa.WaveObject.from_wave_file("rock-kit/Rock-Kit-Floor-2.wav").play()
    #now, msg will have the initial bpm in it
    bpm = float(msg)
    ioi = 1 / (bpm / 60)
    events = []
    for i in range(7):
        if (i == 3): wavFile = sa.WaveObject.from_wave_file("rock-kit/Rock-Kit-Floor-2.wav")
        else: wavFile = sa.WaveObject.from_wave_file("rock-kit/Rock-Kit-HiHat-Tip-1.wav")
        soundTime = startOf2Measures + (ioi * (i + 1))
        events.append((soundTime, wavFile))
    
    mid = MidiFile(INPUT_FILENAME, clip=True)
    prevMesgTime = 0
    for mesg in mid:
        if mesg.type == "note_on":
            events.append((mesg.time + startOf2Measures + prevMesgTime, midiToWav[mesg.note]))
            prevMesgTime += mesg.time
    
    events.sort(key=lambda event : event[0])
    
    for event in events:
        print(f"time: {event[0] - startOf2Measures}")

    untilNext = (events[0][0] - time.time()) * 1000


context = zmq.Context()

print("connecting to server")
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5556")

socket.setsockopt_string(zmq.SUBSCRIBE, "")

msg = b"-1"
while (msg == b"-1"):
    msg = socket.recv()
    print(msg)

bpmToMetronome(float(msg))

print(events)
while (True):
    if (untilNext > 0 and socket.poll(untilNext, zmq.POLLIN)):
        #have to change bpm
        msg = socket.recv()
        print(f"yes! {msg}")
        bpmToMetronome(float(msg))
    elif (len(events) != 0):
        events.pop(0)[1].play()
        #UNFINISHED!!! needs quite a bit more work to...work.
        if (len(events) != 0):
            untilNext = (events[0][0] - time.time()) * 1000
        else:
            untilNext = 99999999
    else:
        untilNext = 99999999 #wait until next input from server



"""
    msg = socket.recv()
    startTime = time.time()
    print(msg)
    bpm = float(msg)
    if (bpm != -1):
        tick = sa.WaveObject.from_wave_file("rock-kit/Rock-Kit-Floor-2.wav")
        tick.play()
        tock = sa.WaveObject.from_wave_file("rock-kit/Rock-Kit-HiHat-Tip-1.wav")
        ioi = 1 / (bpm / 60)
        time.sleep(startTime + ioi*1 - time.time())
        tock.play()
        time.sleep(startTime + ioi*2 - time.time())
        tock.play()
        time.sleep(startTime + ioi*3 - time.time())
        tock.play()
        time.sleep(startTime + ioi*4 - time.time())
        tick.play()
        time.sleep(startTime + ioi*5 - time.time())
        tock.play()
        time.sleep(startTime + ioi*6 - time.time())
        tock.play()
        time.sleep(startTime + ioi*7 - time.time())
        tock.play()
    """