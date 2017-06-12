#!/usr/bin/env python2

# Command Radio Primary script

import math, sys, os, socket, time, struct, traceback, binascii, logging
from optparse import OptionParser
import threading
import datetime as dt
from main_thread import *

def main(options):
    main_thread = Main_Thread(options)
    main_thread.daemon = True
    main_thread.run()
    sys.exit()

if __name__ == "__main__":
    startup_ts = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    #--------START Command Line option parser------------------------------------------------------
    usage = "usage: %prog "
    parser = OptionParser(usage = usage)
    
    #Startup Timestamp
    ts_help = "Startup Timestamp: %default"
    callsign_help = "Callsign, [default=%default]"
    watchdog_help = "Watchdog Timeout, [default=%default]"
    delay_help = "Startup Delay [s], [default=%default]"
    parser.add_option("--ts" , dest = "startup_ts" , action = "store", type = "string", default=startup_ts , help = ts_help)
    parser.add_option("--cs" , dest = "callsign"   , action = "store", type = "string", default='KJ4WRQ'   , help = callsign_help)
    parser.add_option("--wd" , dest = "wd_timeout" , action = "store", type = "float" , default='30.0'     , help = watchdog_help)
    parser.add_option("--sd","--delay",dest="delay", action = "store", type = "float" , default=".1"       , help = delay_help)

    #HW TLM Serial Port
    h_ser_port = "HW TLM Serial Port, [default=%default]"
    h_ser_baud = "HW TLM Serial Baud, [default=%default]"
    parser.add_option("-d", dest = "ser_port", action = "store", type = "string", default='/dev/ttyACM0', help = h_ser_port)
    parser.add_option("-b", dest = "ser_baud", action = "store", type = "int"   , default='115200'      , help = h_ser_baud)

    #Payload Radio Interface, Command and Control Network Parameters
    h_pld_ip    = "Payload Radio IP Address, [default=%default]"
    h_cmd_port  = "Payload Radio TT&C Port Number, [default=%default]"
    h_adsb_port = "Command Radio ADSB Data RX Port Number, [default=%default]"
    h_ais_port  = "Command Radio AIS  Data RX Port Number, [default=%default]"
    parser.add_option("-a", dest = "pld_ip"   , action = "store", type = "string", default='192.168.20.41', help = h_pld_ip)
    parser.add_option("-p", dest = "cmd_port" , action = "store", type = "int"   , default='2600'         , help = h_cmd_port)
    parser.add_option("-q", dest = "adsb_port", action = "store", type = "int"   , default='1337'         , help = h_adsb_port)
    parser.add_option("-r", dest = "ais_port" , action = "store", type = "int"   , default='1338'         , help = h_ais_port)

    #Command Radio, GNU Radio Network Parameters
    h_gr_ip    = "GNU Radio Flowgraph IP Address, [default=%default]"
    h_gr_port  = "GNU Radio Flowgraph Port Number, [default=%default]"
    h_gr_path  = "GNU Radio Flowgraph Path, [default=%default]"
    h_gr_rate  = "Rate to Write to GNU Radio [s], [default=%default]"
    parser.add_option("-e", dest = "gr_ip"   , action = "store", type = "string", default='0.0.0.0', help = h_gr_ip)
    parser.add_option("-f", dest = "gr_port" , action = "store", type = "int"   , default='52001'  , help = h_gr_port)
    parser.add_option("-g", dest = "gr_path" , action = "store", type = "string", 
                            default='/home/zleffke/workspace/rocksat/2017/waveforms/command/v2/',  
                            help = h_gr_path)
    parser.add_option("-i", dest = "gr_rate", action = "store", type = "float", default='0.044', help = h_gr_rate)

    (options, args) = parser.parse_args()
    #--------END Command Line option parser------------------------------------------------------
    main(options)

