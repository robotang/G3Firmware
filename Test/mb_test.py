#!/usr/bin/python

from __future__ import division
import sys, time, os, argparse
from threading import Thread
from time import gmtime, strftime
import datetime

# Import library
import sys
sys.path.append("../")
import lib

DEFAULT_PORT = "/dev/ttyUSB0"
DEFAULT_BAUD = 38400

def mb_cb(data):
    print data

if __name__ == "__main__":
    next_update_ms = 0
    now_ms = 0

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=str, required=False)
    args = parser.parse_args()
    if args.port:
        port = args.port
    else:
        port = DEFAULT_PORT
        
    print "RS485 test\n"

    # Setup modules
    kb = lib.KBHit()
    tick = lib.Tick()
    mb = lib.MBProtocol(port=port, baud=DEFAULT_BAUD, rx_func=mb_cb)
    
    # Main loop
    while True:
        now_ms = tick.uptime_ms()
        
        # Request update
        if next_update_ms < now_ms:
            # Get toolhead temperature
            mb.send([0, 32])
            
            next_update_ms += 1000
        
        # Handle keyboard press
        if kb.kbhit():
            c = kb.getch()
            if ord(c) == 27:
                print "Quitting"
                break
                
        # Delay
        time.sleep(0.1)
    
    mb.quit()
    kb.set_normal_term()
