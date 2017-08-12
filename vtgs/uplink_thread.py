#!/usr/bin/env python
#########################################
#   Title: Rocksat Data Server Class    #
# Project: Rocksat                      #
# Version: 1.0                          #
#    Date: August, 2017                 #
#  Author: Zach Leffke, KJ4QLP          #
# Comment: Initial Version              # 
#########################################

import socket
import threading
import sys
import os
import errno
import time
import binascii
import numpy

import datetime as dt
from logger import *
from watchdog_timer import *

class Uplink_Thread(threading.Thread):
    def __init__ (self, options):
        threading.Thread.__init__(self,name = 'UplinkThread')
        self._stop          = threading.Event()
        self.ip             = options.ip
        self.port           = options.port
        self.id             = options.id
        self.ts             = options.ts
        self.callsign       = options.call
        self.tx_rate        = options.rate
        self.mode_rate      = options.mode

        self.sock           = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #TCP Socket
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connected      = False

        self.log_fh = setup_logger(self.id, 'uplink', self.ts)
        self.logger = logging.getLogger('uplink')

        #self.timer = threading.Timer(self.timeout, self.tx_handler)
        self.tx_frame_count = 0
        self.mode           = 'ADSB'
        

    def run(self):
        print "Uplink Thread Running..."
        
        while (not self._stop.isSet()):
            self.tx_frame_count += 1
            self.tx_ts = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S.%f")
            msg = '{:s}_{:s}_{:04d}_{:s}'.format(   self.callsign,
                                                    self.mode,
                                                    self.tx_frame_count,
                                                    self.tx_ts) 
            print 'Sending:',msg
            self.logger.info(msg)
            self.sock.sendto(msg,(self.ip, self.port))

            if self.tx_frame_count % (self.mode_rate/self.tx_rate) == 0:
                if   self.mode == 'ADSB': self.mode = 'AIS'
                elif self.mode == 'AIS' : self.mode = 'ADSB'
            time.sleep(self.tx_rate)
            
        sys.exit()

    def Format_Uplink_Frame(self):
        #KJ4QLP_ADSB_0001_YYYYMMDD_HHMMSS.SSSSSS
        
        pass

    def tx_handler(self):
        print 'timer working'
        self.timer.reset()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def utc_ts(self):
        return str(dt.datetime.utcnow()) + " UTC | "

