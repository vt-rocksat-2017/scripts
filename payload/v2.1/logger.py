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


def setup_logger(log_name, level=logging.INFO):
    l = logging.getLogger(log_name)
    log_file = "{:s}_{:s}.log".format(log_name, str(get_uptime()))
    log_path = '/mnt/log/' + log_file
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

def setup_logger_old(mode, uptime_seconds):
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

def setup_logger_ref(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler) 

def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        #print uptime_seconds
        return uptime_seconds
        #uptime_string = str(timedelta(seconds = uptime_seconds))
