#!/usr/bin/env python
#############################################
#   Title: AIS/ADSB Data Handler            #
# Project: Rocksat 2017                     #
# Version: 1.0                              #
#    Date: May 2017                         #
#  Author: Zach Leffke, KJ4QLP              #
# Comment:                                  #
#  -Sets up UDP Server Socket to receive    #
#   data from the Payload E310              #
#  -Adds message type to data               #
#  -Places message in Queue to be read      #
#   by main thread
#############################################

import socket, numpy, binascii, logging, threading
from Queue import Queue
from logger import *

class Data_Handler(threading.Thread):
    def __init__ (self, options, mode, logger):
        threading.Thread.__init__(self, name = mode+'_handler')
        self._stop      = threading.Event()
        self.options = options
        self.mode = mode
        self.logger = logger
        print "setting up {} Data Handler".format(self.mode)
        self.logger.info("setting up {} Data Handler".format(self.mode))

        self.q = Queue()

        self.ip = '0.0.0.0' 
        self.mode = mode.upper()
        if self.mode == 'ADSB':
            self.port = self.options.adsb_port
            self.msg_type = numpy.uint8(0)
        elif self.mode == 'AIS':
            self.port = self.options.ais_port
            self.msg_type = numpy.uint8(1)

    def run(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.ip, self.port))
            self.logger.info("Ready to send receive {} data on: {0}:{1}".format(self.mode, self.ip, self.port))
            print "Ready to send receive {} data on: {0}:{1}".format(self.mode, self.ip, self.port)
        except:
            self.logger.info("Could not set up {} data on: {0}:{1}".format(self.mode, self.ip, self.port))

        while (not self._stop.isSet()):
            data, addr = self.sock.recvfrom(1024) # block until data received on control port
            #should check message lengh here and add error handling (exceptions)
            print len(data), binascii.hexlify(data)
            msg = []
            msg.append(self.msg_type)
            msg.extend(data)
            self.q.put(msg)
        self.sock.close()
        self.logger.info("{} Data Handler Terminated".format(self.mode))

    def stop(self):
        print "{} Data Handler Terminating...".format(self.mode)
        #self.q.put(self._StopReporter())
        self.logger.info("{} Data Handler Terminating...".format(self.mode))
        #self.data_logger.removeHandler(self.log_fh)
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

