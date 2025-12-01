import asyncio
import websockets
import serial 
import os

async def handle_client(websocket):
    try:
        serial_port = serial.serial_for_url('/dev/ttyUSB23')
        serial_port.baudrate = 115200
        async for message in websocket:
            print(f"Received: {message}")
            serial_port.write(message.encode('utf-8'))
            
            
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")

async def main():
    # make sure the serial ports are open (only one is needed, we have two so I can test write to one manually)
    os.system('/home/violet/projects/wpi/research/MPRL/PureData_mobile_controller/serialLoopback/unlinkSerialPorts.sh') # ideally should dynamically get it, hard coded for safety for now
    os.system('/home/violet/projects/wpi/research/MPRL/PureData_mobile_controller/serialLoopback/setupLoopback.sh')
    
    async with websockets.serve(handle_client, "0.0.0.0", 9999):
        print("WebSocket server started on ws://localhost:9999")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())