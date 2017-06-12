#!/usr/bin/env python
#############################################
#   Title: Radio Interface Thread           #
# Project: Rocksat 2017                     #
# Version: 1.0                              #
#    Date: May 2017                         #
#  Author: Zach Leffke, KJ4QLP              #
# Comment:                                  #
# -Sends and Receives frames to/from        #
# -GNU Radio flowgraph                      #
#############################################

import socket
import numpy
import binascii
import logging 
import threading
import errno
from Queue import Queue
from logger import *

class Radio_Thread(threading.Thread):
    def __init__ (self, options, logger):
        threading.Thread.__init__(self, name = 'radio')
        self._stop      = threading.Event()
        self.options    = options
        self.tx_rate    = self.options.gr_rate
        self.callsign   = self.options.callsign
        self.target     = (self.options.gr_ip, self.options.gr_port)
        self.logger     = logger

        print "Initializing Radio Thread..."
        self.logger.info("Initializing Radio Thread...")

        self.up_log_fh = setup_logger('uplink')
        self.up_data_logger = logging.getLogger('uplink')
        self.dn_log_fh = setup_logger('downlink')
        self.dn_data_logger = logging.getLogger('downlink')

        self.connected = False
        self.rx_q = Queue()
        self.tx_q = Queue()
        self.tx_buf = bytearray(246) #This message holds the last downlink data field to be sent.

        #Need TX and RX Data loggers
        self.dn_pkt_cnt = numpy.uint16(0)
        self.up_pkt_cnt = numpy.uint16(0)

        print "Setting up GNU Radio Flowgraph..."
        self.logger.info("Setting up GNU Radio Flowgraph...")
        sys.path.insert(0, self.options.gr_path)
        from tx_scram_sock import *
        self.tb = tx_scram_sock()
        self.tb.start()
        print "GNU Radio Flowgraph Launched"
        self.logger.info("GNU Radio Flowgraph Launched")
 
    def run(self):
        time.sleep(4)
        print "Radio Thread Running..."
        self.logger.info("Radio Thread Running...")
        
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.setblocking(0)
            self.logger.info("Setup Socket, attempting to connect to GNU Radio....")
            self.sock.connect(self.target)
        except socket.error, v:
            errorcode=v[0]
            if errorcode==errno.EINPROGRESS:  #Expected, non blocking socket
                self.connected = True #sure lets assume this, connected but no data yet?
                self.logger.info("Connected to GNU Radio Flowgraph at: {0}:{1}".format(*self.target))
                print "Connected to GNU Radio Flowgraph at: {0}:{1}".format(*self.target)
                self.connected = True
        except:
            self.logger.info("Could not set up data socket on: {0}:{1}".format(*self.target))
            self.connected = False
        
        while (not self._stop.isSet()):
            if self.connected:
                try:
                    data = self.sock.recv(256)
                    if data:
                        self.up_data_logger.info(binascii.hexlify(data))
                        self.up_pkt_cnt += numpy.uint16(1) #increment uplink count
                        self.rx_q.put(data)
                        self._send_downlink_frame(self.tx_rate-0.001)
                except socket.error, v:
                    errorcode=v[0]
                    if errorcode==errno.EWOULDBLOCK:  #Expected, No data on uplink
                        self._send_downlink_frame(self.tx_rate)
               
                except Exception as e:
                    print 'Some other Exception occurred:', e
                    self.logger.info(e)

        self.sock.close()
        self.logger.info("Closed Socket Connection to GNU Radio...")
        self.tb.stop()
        self.logger.info("Shutdown GNU Radio Flowgraph...")
        self.logger.info("Radio Thread Terminated.")

    def _downlink_framer(self,msg):
        #Increment Downlink Frame Count
        self.dn_pkt_cnt += numpy.uint16(1)
        #insert two byte uplink packet count in big-endian format to message
        msg = struct.pack('>H', self.up_pkt_cnt) + msg
        #insert two byte downlink packet count in big-endian format to message
        msg = struct.pack('>H', self.dn_pkt_cnt) + msg                           
        msg = bytearray(self.callsign) + msg
        #print 'Radio:', len(msg), binascii.hexlify(msg)
        return msg

    def _send_downlink_frame(self, timeout):
        if (not self.tx_q.empty()): #new message in Queue for downlink
            tx_q = self.tx_q.get() #should be 246 byte messages
            if len(tx_q) > 0: self.tx_buf = tx_q #update downlink data buffer
        #Format the next downlink frame
        tx_msg = self._downlink_framer(self.tx_buf) #framer, returns full message ready for TX
        #Send to GNU Radio
        if len(tx_msg) == self.sock.send(tx_msg, len(tx_msg)):
            #Downlink Data Logger here
            #print 'Sent message successfully', binascii.hexlify(tx_msg)
            self.dn_data_logger.info(binascii.hexlify(tx_msg))
        time.sleep(timeout)

    def stop(self):
        print "Radio Thread Terminating..."
        #self.q.put(self._StopReporter())
        self.logger.info("Radio Thread Terminating...")
        #self.data_logger.removeHandler(self.log_fh)
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

