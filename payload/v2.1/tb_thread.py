#!/usr/bin/env python2

# this manages the currently running flow graph
# future: receive commands from network

# ./payload_2.py
# ./mockcommand.py 127.0.0.1

import math, sys, os, socket, time, struct, traceback, binascii, logging
#from threading import Thread
import threading
from datareporter import TCPDataReporter, UDPDataReporter
from subprocess import Popen, PIPE
from logger import *
from data_packers import *

class TopBlockThread(threading.Thread):
    def __init__(self, mode, r, logger):
        #super(TopBlockThread, self).__init__(self, name = 'TopBlockThread')
        threading.Thread.__init__(self, name = mode + '_thread')
        self._stop      = threading.Event()
        self.mode = mode
        self.r = r
        self.p = None
        self.adsb_part = ADSBPacker()
        self.ais_part = AISPacker()
        #uptime_seconds = get_uptime()
        self.logger = logger
        self.log_fh = setup_logger(mode)
        self.data_logger = logging.getLogger(mode)
        if self.mode not in self.mode_handlers.keys():
            raise ValueError("TopBlockThread mode {} not supported, try {}".format(
                    self.mode, self.mode_handlers))

    def _process_adsb(self, data):
        msg = data.strip().split()[0].decode("hex")
        try:
            self.adsb_part.add(msg)
        except self.adsb_part.PacketFullError:
            # packetize the queued messages
            ret = str(self.adsb_part)
            # add the next message to the next packet
            self.adsb_part = ADSBPacker()
            self.adsb_part.add(msg)
            return ret

    def _process_ais(self, data):
        msg = data.strip('\n')
        try:
            self.ais_part.add(msg)
        except self.ais_part.PacketFullError:
            # packetize the queued messages
            ret = str(self.ais_part)
            # add the next message to the next packet
            self.ais_part = AISPacker()
            self.ais_part.add(msg)
            return ret

    def _process_test(self, data):
        return data.strip()

    mode_binaries = {
            #I used the full path for adsb because we modified the stock modes_rx
            "adsb":     os.path.join(os.path.dirname(__file__), "modes_rx"),
            "ais":      "/home/root/waveforms/ais_rx.py --rx-gain 10",
            "testmode": "testmode/top_block.py",
    }
    mode_handlers = {
            "adsb":     _process_adsb,
            "ais":      _process_ais,
            "testmode": _process_adsb, # use testing data to exercise adsb packer
    }

    def run(self):
        print 'Starting {} Radio: {}'.format(self.mode, self.mode_binaries[self.mode])
        self.logger.info('Starting {} Radio: {}'.format(self.mode, self.mode_binaries[self.mode]))
        self.p = Popen(self.mode_binaries[self.mode], stdout=PIPE, stdin=PIPE, shell=True)
        print 'Launching subprocess: {}'.format(str(self.p.pid))
        self.logger.info('Launching subprocess: {}'.format(str(self.p.pid)))
        try:
            self._wait_for_load()
            while 1: 
                line = self.p.stdout.readline()
                if not line: # process finished
                    break
                self.data_logger.info(line.strip())
                msg = self.mode_handlers[self.mode](self, line)
                if msg:
                    self.r.send(self._pad_msg(msg))
        finally:
            #self.stop()
            print '{} radio terminated'.format(self.mode)
            self.logger.info('{} radio terminated'.format(self.mode))

    def _pad_msg(self, data):
        ret = ''
        if self.mode == 'adsb':
            ret = data.ljust(self.r.max_msg_len, "\0")
        elif self.mode == 'ais':
            #pad with special character
            ret = data.ljust(self.r.max_msg_len, "!")
        print("sending {:3d}: {}".format(len(ret), binascii.hexlify(ret)))
        return ret

    def _wait_for_load(self):
        if self.mode == "adsb":
            trace = ""
            while 1:
                line = self.p.stdout.readline()
                if not line:
                    raise IOError("failed to load {}, output so far:\n{}".format(self.mode, trace))
                if line.startswith("Using Volk machine: "):
                    #next line will be actual data
                    return
                trace += line
        elif self.mode == "ais":
            trace = ""
            cnt = 0
            while 1:
                line = self.p.stdout.readline()
                if not line:
                    raise IOError("failed to load {}, output so far:\n{}".format(self.mode, trace))
                if line.startswith("-- Performing timer loopback test... pass"):
                    if cnt == 0:
                        cnt += 1
                    elif cnt == 1:
                        #next line will be actual data
                        return
                trace += line

    def stop(self):
        print 'Stopping {} Radio: {}'.format(self.mode, self.mode_binaries[self.mode])
        self.logger.info('Stopping {} Radio: {}'.format(self.mode, self.mode_binaries[self.mode]))
        if self.p:
            if self.mode == 'ais':
                print 'Sending Character to terminate AIS Flowgraph'
                self.logger.info('Sending Character to termiante AIS Flowgraph')
                self.p.stdin.write('\n')
                
            print 'Terminating subprocess: {}'.format(str(self.p.pid))
            self.logger.info('Terminating subprocess: {}'.format(str(self.p.pid)))
            self.p.kill()
            #os.kill(self.p.pid, 0)
            self.p = None
        self._stop.set()
        print 'Terminating Logger'
        self.logger.info('Terminating Logger: {}'.format(self.mode))
        self.data_logger.removeHandler(self.log_fh)

    def stopped(self):
        return self._stop.isSet()
