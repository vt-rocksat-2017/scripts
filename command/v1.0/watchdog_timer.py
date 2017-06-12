#!/usr/bin/env python2

# Watchdog Timer
# Based on: https://stackoverflow.com/questions/16148735/how-to-implement-a-watchdog-timer-in-python
# Modified by Zach Leffke for Rocksat X 2017

#from threading import Timer
import threading
import logging

class Watchdog():
    def __init__(self, timeout, logger, userHandler=None):  # timeout in seconds
        #threading.Timer.__init__(self, name = 'Watchdog')
        self.timeout = timeout
        self.logger = logging.getLogger('main')
        self.handler = userHandler if userHandler is not None else self.defaultHandler
        self.timer = threading.Timer(self.timeout, self.handler)
        self.timer.name = 'Watchdog'

    def reset(self):
        #self.logger.info('Watchdog Reset')
        self.timer.cancel()
        self.timer = threading.Timer(self.timeout, self.handler)
        self.timer.name = 'Watchdog'
        self.timer.start()

    def stop(self):
        self.timer.cancel()

    def defaultHandler(self):
        raise self
