#This is the main server file!! It takes offsets from the client, 
#and fits them into 2-bar segments. It always assumes that the first
#four imputs are establishing tempo, and all inputs afterward are processed normally.

import zmq
import time
from midiutil.MidiFile import MIDIFile
import simpleaudio as sa

MIDI_INP0 = 60
MIDI_INP1 = 61
MIDI_INP2 = 62
MIDI_OUTFILE = "output.mid"

def makeMidiFile(notesThisTwoBars):
    #largely taken from stackoverflow.com/questions/11059801/how-can-i-write-a-midi-file-with-python
    mf = MIDIFile(1)
    track = 0
    time = 0
    mf.addTrackName(track, time, "gwuh")
    mf.addTempo(track, time, bpm)
    channel = 0
    volume = 100

    for note in notesThisTwoBars:
        pitch = 60 + int(note[0])
        time = note[1] * bpm / 60
        duration = 0.5
        mf.addNote(track, channel, pitch, time, duration, volume)

    with open(MIDI_OUTFILE, 'wb') as outf:
        mf.writeFile(outf)

lastThree = 0
prevThreeDiffs = [0]
k = 0
bpm = 0
averageIOI = 0
#"three" referring to when all three piezos receive input. a hit in the middle. 
#used to set bpm
def handleThree(hitTime):
    global lastThree, prevThreeDiffs, k
    #play ding TODO
    ioi = hitTime - lastThree
    if (ioi < 2): #only seriously handle stuff if there's been a recent other hit, less than 2 seconds ago
        #if the list isn't long enough to have an index of [k], add it
        if (len(prevThreeDiffs) <= k):
            prevThreeDiffs.append(ioi)
        else:
            prevThreeDiffs[k] = ioi
        k = (k + 1) % 8 #increase k, cycling at 8

        if (len(prevThreeDiffs) >= 3): #we have 3 intervals at minimum
            global averageIOI, bpm
            averageIOI = sum(prevThreeDiffs) / len(prevThreeDiffs)
            bpm = (1 / averageIOI) * 60
    else:
        prevThreeDiffs = [0] #reset the IOI tracker to be re-used soon
        k = 0

    lastThree = hitTime

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

socket2 = context.socket(zmq.PUB)
socket2.bind("tcp://*:5556")

#for some godforsaken reason, something like these three lines is needed. 
#it will never recieve the first. it won't recieve the second if the sleep is absent.
#wizardry, i tell you. it's fine, just a half second delay at startup. annoying.
socket2.send_string("-1")
time.sleep(0.5)
socket2.send_string("-1")
#poller = zmq.Poller()
#poller.register(socket, zmq.POLLIN)

#while (True):
#    print("sending 30 bwabwa")
#    socket2.send_string("30 40")
#    time.sleep(1)


#get tempo from first 4 taps, average the ioi
tapTimes = [0]*4
while (averageIOI == 0):
    message = socket.recv()
    if (message != b"correction 3"): #ignore 3 corrections
        #tapTimes[i] = time.time()
        handleThree(time.time())
        socket.send(b"gotcha")
        print("bom")
    else:
        socket.send(b"don't talk to me with those correction messages right now")

#intervals = [(tapTimes[i+1] - tapTimes[i]) for i in range(3)]
#averageIOI = sum(intervals) / 3
#bpm = (1 / averageIOI) * 60
#print(f"bpm: {bpm}")
print(f"ioi {averageIOI}, time {time.time()}, last three {lastThree}")
time.sleep(averageIOI - (time.time() - lastThree))
#if anything came in during that sleep, silence it
if (socket.poll(1, zmq.POLLIN)):
    socket.recv()
    socket.send(b"shut up")

socket2.send_string(str(bpm))
#print("tap")
#time.sleep(averageIOI)
#print("tic")
#time.sleep(averageIOI)
#print("tic")
#time.sleep(averageIOI)
#print("tic")

wavKick = sa.WaveObject.from_wave_file("rock-kit/Rock-Kit-Kick-ff-1.wav")
wavHiHat = sa.WaveObject.from_wave_file("rock-kit/Rock-Kit-HiHat-Open.wav")
wavSnare = sa.WaveObject.from_wave_file("rock-kit/Rock-Snare-ff-1.wav")
wavCenter = sa.WaveObject.from_wave_file("rock-kit/Rock-Rack-1.wav")
drumkitList = [wavKick, wavHiHat, wavSnare]

twoBarsStartTime = time.time()
twoBarsRemainingSecs = averageIOI * 8
prevEventTime = time.time()
notesThisTwoBars = []
while (True):
    if (twoBarsRemainingSecs > 0 and socket.poll(twoBarsRemainingSecs * 1000, zmq.POLLIN)):
        message = socket.recv()
        now = time.time()
        socket.send(b"yessir")
        print(f"we got message: {message}")
        
        if (message == b"3"):
            playingWav = wavCenter.play()
            handleThree(now)
        elif (message == b"correction 3"):
            playingWav.stop()
            playingWav = wavCenter.play()
            #remove last note (if it exists) because actually that was a 3
            #stop current sound TODO
            if (len(notesThisTwoBars) != 0):
                handleThree(notesThisTwoBars.pop()[1] + twoBarsStartTime)
        else:
            playingWav = drumkitList[int(message)].play()
            #add to list of notes
            notesThisTwoBars.append((message, time.time() - twoBarsStartTime))
            
        
        now = time.time()
        twoBarsRemainingSecs -= (now - prevEventTime)
        prevEventTime = now
        print(f"remaining secs: {twoBarsRemainingSecs}")
        
    else:
        twoBarsRemainingSecs = averageIOI * 8
        prevEventTime = time.time()
        twoBarsStartTime = time.time()
        print(f"end of 2 bars. notes were {notesThisTwoBars}")
        makeMidiFile(notesThisTwoBars)
        notesThisTwoBars = []
        socket2.send_string(str(bpm))
        #CALL MODEL FOR output.mid
