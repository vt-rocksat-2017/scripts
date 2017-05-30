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

class Payload_Cmd(threading.Thread):
    def __init__ (self, options, logger):
        threading.Thread.__init__(self, name = 'pld_cmd')
        self._stop      = threading.Event()
        self.options = options
        self.logger = logger
        print "setting up Payload Command Thread..."
        self.logger.info("setting up Payload Command Thread...")

        self.q = Queue()
        self.q_timeout = 1

        self.target = (self.options.pld_ip, self.options.cmd_port) 
 
    def run(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.connect((self.ip, self.port))
            self.logger.info("Ready to send command data on: {0}:{1}".format(self.target))
            print "Ready to send command data on: {0}:{1}".format(self.target)
        except:
            self.logger.info("Could not set up command data on: {0}:{1}".format(self.target))

        while (not self._stop.isSet()):
            try:
                msg = self.q.get(True, self.q_timeout) #should block until a message is placed in the Queue, problem for terminating thread?
                #---Should probably add error checks here------
                self.sock.send(msg) #send message to payload radio
                self.logger.info('Sent Message to {0}:{1}: {}'.format(self.target, self.msg))
            except Queue.Empty: #this plus the q timeout should properly terminate thread
                continue
            except Exception as e:
                print 'Some other Exception occurred:', e
                self.logger.info(e)

        self.sock.close()
        self.logger.info("Payload Command Thread Terminated".format(self.mode))

    def send(self, msg):
        self.q.put(msg)

    def stop(self):
        print "{} Data Handler Terminating...".format(self.mode)
        #self.q.put(self._StopReporter())
        self.logger.info("{} Data Handler Terminating...".format(self.mode))
        #self.data_logger.removeHandler(self.log_fh)
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

