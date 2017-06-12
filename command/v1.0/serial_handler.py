#!/usr/bin/env python
#############################################
#   Title: Serial Port Data Handler         #
# Project: Rocksat 2017                     #
# Version: 1.0                              #
#    Date: May 2017                         #
#  Author: Zach Leffke, KJ4QLP              #
# Comment:                                  #
#  -Sets up Serial Port to receive          #
#   data from the Teensy                    #
#  -Adds message type to data               #
#  -Places message in Queue to be read      #
#   by main thread
#############################################

import socket
import numpy
import binascii
import logging
import threading
import serial
import os
from Queue import Queue
from logger import *

class Serial_Handler(threading.Thread):
    def __init__ (self, options, logger):
        threading.Thread.__init__(self, name = 'SERIAL_handler')
        self._stop      = threading.Event()
        self.options = options
        self.logger = logger
        self.msg_type = numpy.uint8(2)
        print "Initializing Serial Data Handler"
        self.logger.info("Initializing Serial Data Handler")

        self.device = self.options.ser_port
        self.baud   = self.options.ser_baud
        self.startup_delay = 1
        self._ser_fault = False
        self.err_count = 0
        self.ser_data = ""
        self.port_flag = False

        self.q = Queue()
        
    def run(self):
        time.sleep(self.startup_delay)
        print "Serial Thread Running..."
        self.logger.info("Serial Thread Running...")
        try:
            self._find_serial_port()
            if self.device != None: 
                self._Open_Serial(self.device)
        except Exception as e:
            self._Handle_Exception(e)
        
        while (not self._stop.isSet()):
            if self._ser_fault == False:
                try: 
                    if self.ser.inWaiting() >= 245: 
                        self.ser_data = self.ser.readline()
                        self._update_queue()
                except Exception as e:
                    self._Handle_Exception(e)
            if self._ser_fault == True:
                try:
                    self._find_serial_port()
                    if self.device != None: 
                        self._Open_Serial(self.device)
                except Exception as e:
                    self._Handle_Exception(e)
                
                #if self._ser_fault == True: #Try other serial port
                #    time.sleep(1) #but wait a second first
                #    try:
                #        self._find_serial_port()
                #        self._Open_Serial(self.device)
                #        #self.ser_data = "$,RECONNECTED TO SERIAL PORT," + "/dev/ttyACM1,"
                #        self._update_queue()
                #    except Exception as e:
                #        self._Handle_Exception(e)
        self.ser.close()
        self.logger.info("Closing Serial Port.")
        self.logger.info("Serial Data Handler Terminated.")

    def _update_queue(self):
        #print len(self.ser_data)
        if len(self.ser_data) < 245:
            length = len(self.ser_data)
            pad_length = 245 - length
            for i in range(pad_length):
                self.ser_data = self.ser_data + "#"

        if len(self.ser_data) > 245:
            self.ser_data = self.ser_data[:245]

        msg = []
        msg.append(self.msg_type)
        msg.extend(self.ser_data)
        self.q.put(bytearray(msg))

    def _find_serial_port(self):
        fnames = self._Find_File_Names('/dev')
        for f in fnames:
            if 'ACM' in f:
                self.device = '/dev/'+f
                self.logger.info("Found Serial Port: {}".format(self.device))
            else:
                self.device = None
        #print self.device
            
    def _Find_File_Names(self, folder):
        #--return list of all filenames in 'folder'------------
        file_names = []
        #path =  os.getcwd() + '/' + folder + '/'
        #print path
        for (dirpath, dirnames, filenames) in os.walk(folder):
            file_names.extend(filenames)
            break
        file_names.sort()
        return file_names

            

    def _Open_Serial(self, dev):
        self.device = dev
        self.ser = serial.Serial(self.device, self.baud, dsrdtr=True, xonxoff=True, rtscts=True)
        self.logger.info("Opened Serial Port: {:s}".format(self.device))
        self.ser.flushInput()
        self._ser_fault = False
        self.ser_data = "$,SERIAL PORT CONNECTED,{}".format(self.device)
        self._update_queue()

    def _Handle_Exception(self, e):
        self.err_count += 1
        self.logger.info("Fault with Serial Port: {:s}".format(self.device))
        if type(e) == serial.serialutil.SerialException:
            self.ser_data = "$,SERIAL FAULT," + str(self.err_count) + "," + str(e) + ","
            self.logger.info("Serial Port Fault: {:s}".format(e))
        else:
            self.ser_data = "$,UNKNOWN FAULT," + str(self.err_count) + "," + str(e) + ","
            self.logger.info("Unknown Fault: {:s}".format(e))
        self._update_queue()
        self._ser_fault = True

    def stop(self):
        print "Serial Data Handler Terminating..."
        #self.q.put(self._StopReporter())
        self.logger.info("Serial Data Handler Terminating...")
        #self.data_logger.removeHandler(self.log_fh)
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

