#!/usr/bin/env python
#############################################
#   Title: Command Radio, Main Thread       #
# Project: ROCKSAT-X                        #
# Version: 1.0                              #
#    Date: April 2017                       #
#  Author: Zach Leffke, KJ4QLP              #
# Comment:                                  #
#   Main Control of comand radio,           #
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
from data_handler import *
from radio_thread import *
from watchdog_timer import *
from payload_cmd import *
from serial_handler import *


class Main_Thread(threading.Thread):
    def __init__ (self, options):
        threading.Thread.__init__(self, name = 'MainThread')
        self._stop      = threading.Event()
        self.options = options
        self.callsign = options.callsign

        self.log_fh = setup_logger('main')
        self.logger = logging.getLogger('main')
        
        self.dn_pkt_cnt = numpy.uint16(0)
        self.up_pkt_cnt = numpy.uint16(0)
        self.mode = 'BOOT'    #State of Main loop, should be BOOT, ADSB, or AIS

        self.timeout = self.options.wd_timeout
        #self.watchdog = threading.Timer(self.timeout, self.watchdog_event)
        #self.watchdog.daemon = True
        self.watchdog = Watchdog(self.options.wd_timeout, self.logger, self.watchdog_event)

        self.ADSB_CMD = bytearray(256)
        self.AIS_CMD = bytearray(256)
        for i, b in enumerate(self.AIS_CMD): self.AIS_CMD[i] = 0xFF
        print 'ADSB: ', binascii.hexlify(self.ADSB_CMD)
        print ' AIS: ', binascii.hexlify(self.AIS_CMD)
        
        self.ADSB_CMD = 'adsb_uplink_cmd'
        self.AIS_CMD = 'ais_uplink_cmd'

    def run(self):
        print "Main Thread Started..."
        self.logger.info('Launched main thread')
        try:
            if self.mode.upper() == 'BOOT':
                if self.init_threads():
                    self.logger.info('Successfully Launched Threads, Switching to ADSB Mode')
                    self.switch_mode('adsb')
                else:
                    self.logger.info('Failed to launch threads.....should probably do something smart here')
            while (not self._stop.isSet()):
                
                
                #Check uplink queue for msg
                # if msg -> parse -> extract uplink frame count -> increment local variable
                #                 -> if uplink command != mode: change modes
                #                 -> else: continue
                #        -> Reset Watchdog:  self.watchdog = threading.Timer(self.wd_timeout, self.watchdog_event)
                if (not self.radio_thread.rx_q.empty()): #Uplink Received!
                    rx_msg = self.radio_thread.rx_q.get()
                    print rx_msg
                    up_cmd = ''
                    if rx_msg.strip() == self.ADSB_CMD: #uplink command is for ADSB mode
                        up_cmd = 'ADSB'
                    elif rx_msg.strip() == self.AIS_CMD: #uplink command is for AIS MODE
                        up_cmd = 'AIS'
                    else:
                        up_cmd = self.mode #if unknown uplink command, stay in current mode
                    
                    if up_cmd != self.mode: #Switch Modes
                        self.logger.info('Received command to switch modes from uplink')
                        self.switch_mode(up_cmd)

                #1. check downlink queues
                msg = bytearray()
                #if self.mode == 'ADSB':
                if (not self.adsb_handler.q.empty()):
                    msg = self.adsb_handler.q.get()
                #elif self.mode == 'AIS':
                elif (not self.ais_handler.q.empty()):
                    msg = self.ais_handler.q.get()

                elif (not self.serial_handler.q.empty()):
                    msg = self.serial_handler.q.get()

                if len(msg) > 0: #should be 246 bytes
                    self.radio_thread.tx_q.put(msg)

                time.sleep(0.5)
        except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
            print "\nKilling Threads..."
            self.logger.warning('Terminating Threads...')
            self.pld_c2.stop()
            self.pld_c2.join()# wait for the thread to finish what it's doing
            self.adsb_handler.stop()
            self.adsb_handler.join() # wait for the thread to finish what it's doing
            self.ais_handler.stop()
            self.ais_handler.join() # wait for the thread to finish what it's doing
            self.serial_handler.stop()
            self.serial_handler.join() # wait for the thread to finish what it's doing
            self.radio_thread.stop()
            self.radio_thread.join() # wait for the thread to finish what it's doing
            self.watchdog.stop()
            self.logger.warning('Terminating Main Thread...')

            sys.exit()
        sys.exit()
    

    def switch_mode(self, new_mode):
        self.logger.info('Switching Mode from {} to {}'.format(self.mode, new_mode))
        self.mode = new_mode.upper()
        #self.pld_c2.q.put(self.mode)
        self.pld_c2.send(self.mode)        
        self.watchdog.reset()

    def watchdog_event(self):
        self.logger.info('Watchdog Timed Out...')
        if self.mode.upper() == 'ADSB':
            self.switch_mode('AIS')
        elif self.mode.upper() == 'AIS':
            self.switch_mode('ADSB')
        else:
            self.switch_mode('ADSB')

    def set_mode_ais(self):
        pass


    def init_threads(self):
        try:
            #Initialize Payload Radio Command and Control (C2) Thread
            self.logger.info('Setting up Payload Radio C2 Thread')
            self.pld_c2 = Payload_Control(self.options, self.logger) #Payload_Control
            self.pld_c2.daemon = True

            #Initialize ADSB Data_Handler Thread
            self.logger.info('Setting up ADSB Data Handler Thread')
            self.adsb_handler = Data_Handler(self.options, 'ADSB', self.logger) #ADSB Handler Thread
            self.adsb_handler.daemon = True

            #Initialize AIS Data_Handler Thread
            self.logger.info('Setting up AIS Data Handler Thread')
            self.ais_handler = Data_Handler(self.options, 'AIS', self.logger) #AIS Handler Thread
            self.ais_handler.daemon = True

            #Initialize Radio Thread
            self.logger.info('Setting up Serial Thread')
            self.serial_handler = Serial_Handler(self.options, self.logger) #Serial Thread
            self.serial_handler.daemon = True

            #Initialize Radio Thread
            self.logger.info('Setting up Radio Thread')
            self.radio_thread = Radio_Thread(self.options, self.logger) #Radio Thread
            self.radio_thread.daemon = True

            #Launch threads
            self.logger.info('Launching Payload Radio C2 Thread')
            self.pld_c2.start() #non-blocking
            
            self.logger.info('Launching ADSB Data Handler Thread')
            self.adsb_handler.start() #non-blocking

            self.logger.info('Launching AIS Data Handler Thread')
            self.ais_handler.start() #non-blocking

            self.logger.info('Launching Serial Handler thread')
            self.serial_handler.start() #non-blocking

            self.logger.info('Launching Radio thread')
            self.radio_thread.start() #non-blocking
            
            return True
        except Exception as e:
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



