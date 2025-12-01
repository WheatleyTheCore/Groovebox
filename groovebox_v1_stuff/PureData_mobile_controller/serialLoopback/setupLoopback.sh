# modified from https://myrobotlab.org/content/serial-terminal-loopbacks-linux

# terminalEmulation.sh
#Terminal emulation script by Adam Harris

#create the two linked pseudoterminals
socat -d -d pty,raw,echo=0 pty,raw,echo=0 &

#now create symbolic links to these terminals
sudo ln -s /dev/pts/2 /dev/ttyUSB23
sudo ln -s /dev/pts/3 /dev/ttyUSB24