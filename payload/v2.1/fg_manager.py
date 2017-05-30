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
from tb_thread import *

class FlowGraphManager():
    class Quit(IOError): pass # used to signal a shutdown requested by command

    def __init__(self, datatarget, logger):
        self.topblock = None
        self.logger = logger
        self.logger.info('Setup Flowgraph Manager')
        self.datatarget = datatarget
        self.r = UDPDataReporter((self.datatarget, 1337), logger)

    def processinput(self, cmd):
        cmd = cmd.strip().lower()
        self.r.checkfailure()
        if cmd in TopBlockThread.mode_handlers.keys():
            self.start(cmd)
        elif cmd == "stop":
            self.stop()
        elif cmd in ["quit", "exit"]:
            raise self.Quit(cmd)
        else:
            print("unrecognized command: '{}'".format(cmd))

    def start(self, mode="adsb"):
        self.stop()
        self.logger.info('Creating Top Block Thread: {}'.format(mode))
        if  mode == 'adsb':  self.r.update_target((self.datatarget, 1337))
        elif mode == 'ais':  self.r.update_target((self.datatarget, 1338))
        self.topblock = TopBlockThread(mode, self.r, self.logger)
        self.logger.info('Launching Top Block Thread: {}'.format(mode))
        self.topblock.start()

    def stop(self):
        if not self.topblock:
            return
        #self.logger.info('Stopping Top Block Thread')
        self.topblock.stop()
        self.topblock.join()
        #self.logger.info('Top Block Thread Stopped')
        self.topblock = None

    def destroy(self):
        self.stop()
        self.r.stop()


