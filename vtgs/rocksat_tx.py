#!/usr/bin/env python
#########################################
#   Title: Rocksat Telemetry Dashboard  #
# Project: Rocksat-X Competition        #
# Version: 1.1                          #
#    Date: Jul 06, 2016                 #
#  Author: Zach Leffke, KJ4QLP          #
# Comment: This is the initial version  # 
#########################################

import math
import string
import time
import sys
import os
import socket
import threading
import datetime as dt
from optparse import OptionParser
from uplink_thread import *

def main():
    start_ts = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S.%f")
    #--------START Command Line option parser------------------------------------------------------
    usage  = "usage: %prog "
    parser = OptionParser(usage = usage)
    #Main Parameters
    h_ts    = "Startup Timestamp: [default=%default]"
    h_ip    = "Set Rocksat Transmitter Modem IP [default=%default]"
    h_port  = "Set Rocksat Transmitter Modem Port [default=%default]"
    h_loc   = "Set Rocksat Transmitter ID [default=%default]"
    h_call  = "Set Rocksat Transmitter Callsign [default=%default]"
    h_rate  = "Set Rocksat Transmitter TX Rate [default=%default sec]"
    h_mode  = "Set Rocksat Transmitter Mode Switch Rate [default=%default sec]"
    parser.add_option("-t", "--ts"  , dest="ts"   , type="string", default=start_ts  , help=h_ts)    
    parser.add_option("-a", "--ip"  , dest="ip"   , type="string", default="0.0.0.0" , help=h_ip)
    parser.add_option("-p", "--port", dest="port" , type="int"   , default="52002"   , help=h_port)
    parser.add_option("-i", "--id"  , dest="id"   , type="string", default="VTGS"    , help=h_loc)
    parser.add_option("-c", "--call", dest="call" , type="string", default="KJ4QLP"  , help=h_call)
    parser.add_option("-r", "--rate", dest="rate" , type="float" , default="1.0"     , help=h_rate)
    parser.add_option("-m", "--mode", dest="mode" , type="float" , default="60.0"     , help=h_rate)

    (options, args) = parser.parse_args()
    #--------END Command Line option parser------------------------------------------------------    

    os.system('reset')

    up_thread = Uplink_Thread(options)
    up_thread.daemon = True
    up_thread.run() #blocking
    #server_thread.start() #Non-blocking



    sys.exit()


if __name__ == '__main__':
    main()

    
