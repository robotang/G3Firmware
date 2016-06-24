from __future__ import division
import sys, time, msvcrt, os, argparse
from threading import Thread
from time import gmtime, strftime
import datetime

# Import library
import sys
sys.path.append("../")
import lib

def serial_rx(c):
    print "Hi"

DEFAULT_PORT = "COM13"
DEFAULT_BAUD = 38400

if __name__ == "__main__":
    next_update_ms = 0
    now_ms = 0

    # Parse arguments (e.g., to run with different port run "usb_test.py -p COMXX" where XX is the port number)
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=str, required=False)
    args = parser.parse_args()
    if args.port:
        port = args.port
    else:
        port = DEFAULT_PORT
        
    print "RS485 test\n"

    # Setup modules
    tick = lib.Tick()
    uart = lib.UART(port=port, baudrate=DEFAULT_BAUD, rx_cb=serial_rx)
    time.sleep(5)
    
    # Main loop
    while True:
        now_ms = tick.uptime_ms()
        
        # Request update
        if next_update_ms < now_ms:
            # Create payload
            payload = []
            payload.append(0x7F) # Device address
            payload.append(0x00) # Command
            crc = lib.crc_maxim(payload)
            
            # Create packet
            packet = []
            packet.append(0xD5) # Sync/start byte
            packet.append(len(payload)) # Length of payload (excludes CRC)
            packet += payload
            packet.append(crc)
            
            for x in packet:
                print hex(x)
            print "\n"
            
            # Send packet            
            uart.send(packet)
            next_update_ms += 1000
        
        # Handle keyboard press
        if msvcrt.kbhit():
            c = msvcrt.getch()
            if ord(c) == 27:
                print "Quitting"
                break
                
        # Delay
        time.sleep(0.1)
    
    uart.quit()