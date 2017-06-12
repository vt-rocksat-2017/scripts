#!/usr/bin/env python
#############################################
#   Title: Payload Radio Interface          #
# Project: Rocksat 2017                     #
# Version: 1.0                              #
#    Date: May 2017                         #
#  Author: Zach Leffke, KJ4QLP              #
# Comment:                                  #
#  -Sets up TCP Client Socket to receive    #
#############################################

import socket, numpy, binascii, logging, threading
from Queue import Queue
from logger import *

class Payload_Control(threading.Thread):
    def __init__ (self, options, logger):
        threading.Thread.__init__(self, name = "pld_c2")
        self._stop      = threading.Event()
        self.options = options
        self.logger = logger
        print "Initializing Payload Radio C2 Thread..."
        self.logger.info("Initializing Payload Radio C2 Thread...")

        self.q = Queue()
        self.connected = False
        self.target = (self.options.pld_ip, self.options.cmd_port) 
 
    def run(self):
        print "Payload Radio C2 Thread Running..."
        self.logger.info("Payload Radio C2 Thread Running...")
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            con_status = self.sock.connect_ex(self.target)
            if con_status == 0:  
                self.connected = True
                print "Connected To Payload Radio on: {0}:{1}".format(*self.target)
                self.logger.info("Connected To Payload Radio on: {0}:{1}".format(*self.target))
                #msg = "adsb"
                #if len(msg) == self.sock.send(msg, len(msg)):
                #    print "Successfully Sent Message to {}:{}: {}".format(self.target[0],self.target[1], msg)
                #    self.logger.info("Successfully Sent Message to {}:{}: {}".format(self.target[0],self.target[1], msg))
            else:
                self.logger.warning("Failed To Connect to Payload Radio on: {0}:{1}".format(*self.target))
                self.logger.warning("Socket Error Number: {}".format(con_status))
        except Exception as e:
            self.logger.warning("Failed To Connect to Payload Radio on: {0}:{1}".format(*self.target))
            self.logger.warning(e)

        while (not self._stop.isSet()):
            try:
                if self.connected:
                    if (not self.q.empty()):
                        msg = self.q.get() + '\n'
                        if len(msg) == self.sock.send(msg, len(msg)):
                            print "Successfully Sent Message to {}:{}: {}".format(self.target[0],self.target[1], msg)
                            self.logger.info("Successfully Sent Message to {}:{}: {}".format(self.target[0],self.target[1], msg))
            except Exception as e:
                print "Some other Exception occurred:", e
                self.logger.warning(e)

        self.sock.close()
        self.logger.info("Closed Socket Connection to Payload Radio...")
        self.logger.info("Payload Radio C2 Thread Terminated.")

    def send(self, msg):
        self.q.put(msg)

    def stop(self):
        print "Payload Radio C2 Thread Terminating..."
        #self.q.put(self._StopReporter())
        self.logger.info("Payload Radio C2 Thread Terminating...")
        #self.data_logger.removeHandler(self.log_fh)
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

