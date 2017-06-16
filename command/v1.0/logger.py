#!/usr/bin/env python2

# Logger utilities

import math, sys, os, time, struct, traceback, binascii, logging
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


def setup_logger(log_name, level=logging.INFO, ts = None):
    l = logging.getLogger(log_name)
    if ts == None: ts = str(get_uptime())
    log_file = "{:s}_{:s}.log".format(log_name, ts)
    log_path = '/mnt/log/' + log_file
    print log_path
    formatter = MyFormatter(fmt='%(asctime)s UTC - %(threadName)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S.%f')
    #fileHandler = logging.FileHandler(log_path, mode='w')
    fileHandler = logging.FileHandler(log_path)
    fileHandler.setFormatter(formatter)
    #streamHandler = logging.StreamHandler()
    #streamHandler.setFormatter(formatter)
    l.setLevel(level)
    l.addHandler(fileHandler)
    l.info('Logger Initialized')
    #l.addHandler(streamHandler) 
    return fileHandler

def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        #print uptime_seconds
        return uptime_seconds
        #uptime_string = str(timedelta(seconds = uptime_seconds))
