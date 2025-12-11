#Irrelevant file. Just for me testing out zmq stuff. No main functionality. 

import time
import zmq
import simpleaudio as sa

context = zmq.Context()

print("connecting to server")
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5556")

socket.setsockopt_string(zmq.SUBSCRIBE, "")

msg = b"-1"
while (msg == b"-1"):
    msg = socket.recv()
    print(msg)
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
untilNext = (events[0][0] - time.time()) * 1000
print(events)
while (True):
    if (socket.poll(untilNext, zmq.POLLIN)):
        #have to change bpm
        msg = socket.recv()
        print(f"yes! {msg}")
    else:
        events.pop(0)[1].play()
        #UNFINISHED!!! needs quite a bit more work to...work.
        untilNext = (events[0][0] - time.time()) * 1000
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