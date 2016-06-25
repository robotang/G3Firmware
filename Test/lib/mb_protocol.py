from __future__ import division
import sys, serial, time, os
from threading import Thread
import datetime

from crc import crc_1wire
import tick
import uart

MB_PROTOCOL_MAX_LENGTH = 32

MB_PROTOCOL_SYNC = 0xD5
MB_PROTOCOL_RESPONSE_SUCCESS = 0x81

MB_PROTOCOL_STATE_SYNC = 0
MB_PROTOCOL_STATE_LENGTH = 1
MB_PROTOCOL_STATE_DATA = 2
MB_PROTOCOL_STATE_CRC = 3

class MBProtocol:
    
    def __init__(self, port, baud, rx_func):
        self._rx = lambda:0
        self._rx.func = rx_func
        self._rx.state = MB_PROTOCOL_STATE_SYNC
        self._rx.length = 0
        self._rx.index = 0
        self._rx.data = [] 
        self._rx.crc = 0
        self._uart = uart.UART(port, baud, rx_cb=self._message_assemble)
        
    def __del__(self):
        self._uart.quit()
        
    def quit(self):
        self.__del__()
        
    def send(self, data):
        txdata = []
        length = len(data)
        if length > MB_PROTOCOL_MAX_LENGTH:
            return False        
        # Add sync, start, length
        txdata.append(MB_PROTOCOL_SYNC)
        txdata.append(length)
        # Add data
        for x in data:
            txdata.append(x)
        # Calculate checksum
        crc_calc = crc_1wire(data)
        # Add checksum
        txdata.append(crc_calc)
        
        # send data
        self._uart.send(txdata)
        
    def _message_assemble(self, c):
        c = ord(c)
        if self._rx.state == MB_PROTOCOL_STATE_SYNC and c == MB_PROTOCOL_SYNC:
            self._rx.state = MB_PROTOCOL_STATE_LENGTH
        elif self._rx.state == MB_PROTOCOL_STATE_LENGTH:
            self._rx.length = c
            if self._rx.length > MB_PROTOCOL_MAX_LENGTH:
                self._rx.data = MB_PROTOCOL_STATE_SYNC
            else:
                self._rx.state = MB_PROTOCOL_STATE_DATA    
        elif self._rx.state == MB_PROTOCOL_STATE_DATA:
            if self._rx.index <= MB_PROTOCOL_MAX_LENGTH:
                self._rx.data.append(c)
                self._rx.index += 1
            if self._rx.index == self._rx.length:
                self._rx.state = MB_PROTOCOL_STATE_CRC
        elif self._rx.state == MB_PROTOCOL_STATE_CRC:            
            self._rx.crc = c
            # Validate crc
            crc_calc = crc_1wire(self._rx.data)
            if self._rx.crc == crc_calc and self._rx.func:
                # Check response code
                if self._rx.data[0] == MB_PROTOCOL_RESPONSE_SUCCESS and self._rx.length > 1:
                    self._rx.data.pop(0)
                    self._rx.func(self._rx.data)
            # Reset state
            self._rx.state = MB_PROTOCOL_STATE_SYNC
            self._rx.index = 0
            self._rx.data = []
    
