# modified from https://myrobotlab.org/content/serial-terminal-loopbacks-linux

echo "unlinking the ttyUSBs..."
sudo unlink /dev/ttyUSB23
sudo unlink /dev/ttyUSB24
sudo killall socat
echo "done."