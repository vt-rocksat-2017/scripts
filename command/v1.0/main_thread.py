#!/usr/bin/env python
#############################################
#   Title: Gimbal Control Code, Main Thread #
# Project: TRIPPWIRE                        #
# Version: 1.0                              #
#    Date: April 2017                       #
#  Author: Zach Leffke, KJ4QLP              #
# Comment:                                  #
#   Main Control of gimbal,                 #
#   launches other threads                  #
#############################################

import threading
import os
import math
import sys
import string
import time
import logging
import numpy
import ctypes
import binascii

from optparse import OptionParser
from datetime import datetime as date
import datetime as dt
from Queue import Queue
from logger import *




class Main_Thread(threading.Thread):
    def __init__ (self, options):
        threading.Thread.__init__(self, name = 'MainThread')
        self._stop      = threading.Event()
        self.options = options
        self.callsign = options.callsign

        self.log_fh = setup_logger('main')
        self.logger = logging.getLogger('main')
        
        self.down_pkt_count = numpy.uint16(numpy.int16(0))
        self.up_pkt_count = numpy.uint16(0)
        self.mode = 'BOOT'    #State of Main loop, should be BOOT, ADSB, or AIS

        self.timeout = self.options.wd_timeout
        self.watchdog = threading.Timer(self.timeout, self.watchdog_event)
        self.watchdog.daemon = True

    def run(self):
        print "Main Thread Started..."
        self.logger.info('Launched main thread')
        try:
            if mode.upper() == 'BOOT':
                if self.init_threads():
                    self.logger.info('Successfully Launched Threads, Switching to ADSB Mode')
                    self.switch_mode('adsb')
                else:
                    self.logger.info('Failed to launch threads.....should probably do something smart here')
            while (not self._stop.isSet()):
                print self.mode
                msg = []
                #Check uplink queue for msg
                # if msg -> parse -> extract uplink frame count -> increment local variable
                #                 -> if uplink command != mode: change modes
                #                 -> else: continue
                #        -> Reset Watchdog:  self.watchdog = threading.Timer(self.wd_timeout, self.watchdog_event)
                #1. check queue
                if self.mode == 'adsb':
                    # check adsb queue for data
                    if (not self.data_handler.q.Empty()):
                        msg = self.data_handler.q.get()
                elif self.mode == 'ais':
                    #check ais queue for msg data
                    pass
                #if no data from payload radio queue
                #  get HW TLM Frame 
                #Increment Downlink Frame Count
                #2.  Add header data
                
                #send data
                time.sleep(0.5)
        except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
            print "\nKilling Threads..."
            self.logger.warning('Terminating Threads...')
            #self.gps_thread.stop(self.name)
            #self.gps_thread.join() # wait for the thread to finish what it's doing
            #self.ttc_thread.stop(self.name)
            #self.ttc_thread.join() # wait for the thread to finish what it's doing
            #self.md01_thread.stop(self.name)
            #self.md01_thread.join()
            #self.imu_thread.stop(self.name)
            #self.imu_thread.join() # wait for the thread to finish what it's doing
            #self.pwm_thread.stop(self.name)
            #self.pwm_thread.join() # wait for the thread to finish what it's doing
            self.logger.warning('Terminating Main Thread...')

            sys.exit()
        sys.exit()
    

    def switch_mode(new_mode):
        self.logger.info('Switching Mode from {} to {}'.format(self.mode, new_mode))
        self.mode = new_mode
        self.cmd_thread.send(self.mode)        
        self.reset_watchdog()

    def self.watchdog_event(self):
        if mode.upper() == 'ADSB':
            self.switch_mode('AIS')
        elif mode.upper() == 'AIS':
            self.switch_mode('ADSB')
        else:
            self.switch_mode('ADSB')

    def self.reset_watchdog(self):
        self.watchdog = threading.Timer(self.timeout, self.watchdog_event)
        self.watchdog.daemon = True
        self.watchdog.start()

    def set_mode_adsb(self):
        self.mode = 'ADSB'
        self.cmd_thread.set_adsb()
        self.logger.info('Switching Mode to ADSB')

    def set_mode_ais(self):
        pass


    def init_threads(self):
        try:
            #Initialize TTC Thread
            #self.logger.info('Setting up TTC thread')
            #self.ttc_thread = TTC_Thread(self.options, self.logger, self) #TTTC Thread
            #self.ttc_thread.daemon = True

            #Initialize Data_Handler Thread
            self.logger.info('Setting up Data Handler Thread, mode: {}')
            self.imu_thread = IMU_Thread(self.options, self.logger, self) #IMU Thread
            self.imu_thread.daemon = True

            #Initialize MD01 Thread
            #self.logger.info('Setting up MD01 thread')
            #self.md01_thread = MD01_Thread(self.options, self.logger, self)#MD01 Thread
            #self.md01_thread.daemon = True

            #Launch threads
            #self.logger.info('Launching TTC thread')
            #self.ttc_thread.start() #non-blocking
            
            #self.logger.info('Launching IMU thread')
            #self.imu_thread.start() #non-blocking

            #self.logger.info('Launching MD01 thread')
            #self.md01_thread.start() #non-blocking

            return True
        except e:
            self.logger.warning('Error Launching Threads:')
            self.logger.warning(str(e))
            self.logger.warning('Setting STATE --> FAULT')
            self.state = 'FAULT'
            return False


    

    #---- END ANTENNA CONTROL SET FUNCTIONS -----

    def utc_ts(self):
        return str(date.utcnow()) + " UTC | "

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()



