from __future__ import division
import sys, serial, time, os
from threading import Thread
import datetime

class UART:

    def __init__(self, port, baudrate=115200, rx_cb=None, rx_buffered_cb=None):        
        # Setup serial port
        self._rx_cb = rx_cb
        self._rx_buffered_cb = rx_buffered_cb
        self._buffer = ""
        self._serial = serial.Serial(port=port, baudrate=baudrate, \
            parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, \
            bytesize=serial.EIGHTBITS, timeout=0)
        self.rts_clear()
        self.dtr_clear()
            
        # Create thread
        self._running = True
        self._thread = Thread(target=self._update)
        self._thread.start()
        
    def __del__(self):
        self._running = False
        self._serial.close()
        
    def _update(self):
        while self._running:
            c = self._serial.read(1)
            if c:
                if self._rx_buffered_cb:
                    self._buffer += c
                    if self._buffer.find("\r\n") > 1:
                        self._rx_buffered_cb(self._buffer)
                        self._buffer = ""
                elif self._rx_cb:
                    self._rx_cb(c)
            time.sleep(0.00001)
        return False
        
    def send(self, data):
        if self._running:
            if type(data) is list:
                data = bytearray(data)
            self._serial.write(data)
        
    def rts_set(self):
        self._serial.setRTS(True)
        self._rts = True
        
    def rts_clear(self):
        self._serial.setRTS(False)
        self._rts = False
        
    def rts_toggle(self):
        if self._rts:
            self.rts_clear()
        else:
            self.rts_set()
        
    def dtr_set(self):
        self._serial.setDTR(True)
        self._rts = True
        
    def dtr_clear(self):
        self._serial.setDTR(False)
        self._rts = False
        
    def dtr_toggle(self):
        if self._rts:
            self.dtr_clear()
        else:
            self.dtr_set()
    
    def quit(self):
        self.__del__()
