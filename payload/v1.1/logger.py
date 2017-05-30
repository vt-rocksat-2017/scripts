#!/usr/bin/env python2

# Logger utilities

import math, sys, os, socket, time, struct, traceback, binascii, logging
import datetime as dt

class MyFormatter(logging.Formatter):
    #Overriding formatter for datetime
    converter=dt.datetime.utcfromtimestamp
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s

def setup_logger(mode, uptime_seconds):
    #Setup Main Logger    
    log_file = "{:s}_{:s}.log".format(mode, str(uptime_seconds))
    log_path = '/mnt/log/' + log_file
    logger = logging.getLogger(__name__)
    #self.logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)
    hdlr  = logging.FileHandler(log_path)
    logger.addHandler(hdlr)
    formatter = MyFormatter(fmt='%(asctime)s UTC - %(threadName)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S.%f')
    hdlr.setFormatter(formatter)
    logger.info('Logger Initialized')
    return logger

def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        print uptime_seconds
        return uptime_seconds
        #uptime_string = str(timedelta(seconds = uptime_seconds))
