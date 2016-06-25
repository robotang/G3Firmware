from __future__ import division
import sys, serial, time, os
from threading import Thread
from time import gmtime, strftime
import datetime

class Tick:

    def __init__(self):        
        self._start_time = time.time()
        
    def uptime_ms(self):
        ms = int(round(1000*time.time() - 1000*self._start_time))
        return ms
