# this manages the currently running flow graph
# future: receive commands from network

# source ~/prefix/setup_env.sh && cd ~/rocksat/ && python2 manager.py
# while true; do nc -lp 1337; done

from threading import Thread, Semaphore
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from Queue import Queue
import binascii, logging
from logger import *

class DataHandler(Thread):
    max_msg_len = 245
    class _StopHandler(): pass # reporter shutdown token class

    def __init__(self, mode, logger):
        super(DataHandler, self).__init__(name = mode+'_handler')
        self.failure = False
        self.logger = logger
        self.mode = mode
        self.msg_type = None #0 = adsb, 1 = ais, 2 = hw_tlm
        print "setting up {} Data Handler".format(self.mode)
        self.logger.info("setting up {} Data Handler".format(self.mode))

        #self.log_fh = setup_logger('data_reporter')
        #self.data_logger = logging.getLogger('data_reporter')
        
        self.q = Queue()
        
        
        if self.failure:
            raise IOError("couldn't initialize DataReporter")

    def run(self):
        try:
            
            self.s = socket(AF_INET, SOCK_DGRAM)
            self.logger.info("UDPDataReporter ready to send to {0}:{1}".format(*self.target))
            print("UDPDataReporter ready to send to {0}:{1}".format(*self.target))
        finally:
            self.loaded.release()

        while 1:
            msg = self.q.get()
            if self.failure or isinstance(msg, self._StopReporter):
                self.logger.info("UDPDataReporter Socket Closing...")
                self.s.close()
                break
            self._checkmsg(msg)
            try:
                self.s.sendto(msg, self.target)
                self.data_logger.info('Sending {}'.format(binascii.hexlify(msg)))
            except:
                self.failure = True
                raise
        self.logger.info("UDPDataReporter Terminated")

    def stop(self):
        print "UDPDataReporter Terminating..."
        self.q.put(self._StopReporter())
        self.logger.info("UDPDataReporter Terminating...")
        self.data_logger.removeHandler(self.log_fh)

    def send(self, msg):
        self.checkfailure()
        self._checkmsg(msg)
        self.q.put(msg)

    def update_target(self,target):
        self.target = target
        self.logger.info("Updating UDPDataReporter Target:  {0}:{1}".format(*self.target))

    def checkfailure(self):
        if self.failure:
            raise IOError("DataReporter failure has occurred")

    def _checkmsg(self, msg):
        pass
        #if not isinstance(msg, str):
        #    raise ValueError("only send strings")
        #if len(msg) != self.max_msg_len:
        #    raise ValueError("messages was {} instead of {} bytes"
        #            "".format(len(msg), self.max_msg_len))

