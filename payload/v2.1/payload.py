#!/usr/bin/env python2

# this manages the currently running flow graph
# future: receive commands from network

# ./payload_2.py
# ./mockcommand.py 127.0.0.1

import math, sys, os, socket, time, struct, traceback, binascii, logging
#from threading import Thread
import threading
from subprocess import Popen, PIPE
from logger import *
from data_packers import *
from tb_thread import *
from fg_manager import *


def main():
    start = time.time()
    t = lambda: time.time()-start
    #print t

    setup_logger('main')
    logger = logging.getLogger('main')
    while 1: # this loop repeats for every new connection
        try:
            logger.info('Started Main Loop...')
            # we completely tear down and recreate the socket every time in case of weirdness
            logger.info('Listening for new command connection...')
            print("listening for new command connection...")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("0.0.0.0", 2600))
            # we only handle a single connection at a time, so this isn't in its own thread
            s.listen(1)
            c, info = s.accept()
            print("command connection received from {}".format(info))
            logger.info('Connection received from {}'.format(info))
            f = FlowGraphManager(info[0], logger)
            while 1:
                cmd = c.recv(1024).strip()
                logger.info('Received Command: {}'.format(cmd))
                if not cmd:
                    logger.info('command protocol error: empty command')
                    raise IOError("command protocol error: empty command")
                f.processinput(cmd)

        except f.Quit:
            print("payload processor restarted by command")

        except Exception as e:
            traceback.print_exc()

        finally:
            if 'f' in locals().keys():
                f.destroy()
            if 'c' in locals().keys():
                c.close()
            s.close()
            time.sleep(1) # limit cpu usage in case of repeated errors setting up connection

if __name__ == "__main__":
    main()

