#!/usr/bin/env python
##################################################
# Title: E310 Serial to Ethernet Test
# Author: Zachary James Leffke
# Description: 
#   Test pyserial module on E310
# Generated: April 5, 2016
##################################################

import os
import sys
import time
import string
import serial
import socket
import threading
import random
import numpy
import struct
import ctypes
import binascii

from optparse import OptionParser
from datetime import datetime as date

CALLSIGN = "KJ4WRQ"
    
if __name__ == '__main__':
    #ts = (date.datetime.utcnow()).strftime("%Y%m%d")

    #--------START Command Line option parser------------------------------------------------------
    usage = "usage: %prog <options>"
    parser = OptionParser(usage = usage)

    #----Serial/socket options----
    ta_help = "Destination IP Address, [default=%default]"
    tp_help = "Destination Port, [default=%default]"
    ra_help = "Receive IP Address, [default=%default]"
    rp_help = "Receive Port, [default=%default]"
    r_help = "Socket Write Speed [sec], [default=%default]"
    f_help = "source data file, [default=%default]"
    rand_help = "Enable random sleep, [default=%default]"

    parser.add_option("--tx_addr"  ,dest="tx_addr"  ,action="store",type="string",default="0.0.0.0",help=ta_help)
    parser.add_option("--tx_port"  ,dest="tx_port"  ,action="store",type="int",default="52001",help=tp_help)
    parser.add_option("--rx_addr"  ,dest="rx_addr"  ,action="store",type="string",default="0.0.0.0",help=ra_help)
    parser.add_option("--rx_port"  ,dest="rx_port"  ,action="store",type="int",default="1337",help=rp_help)
    parser.add_option("-r","--rate"  ,dest="rate"  ,action="store",type="float" ,default="0.044",help=r_help)
    parser.add_option("-f","--file"  ,dest="file"  ,action="store",type="string",default="zeros.dat",help=f_help)
    parser.add_option("","--rand"  ,dest="rand"  ,action="store",type="int",default="0",help=rand_help)

    (options, args) = parser.parse_args()
    #--------END Command Line option parser------------------------------------------------------

    rx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rx_sock.setblocking(0)
    rx_sock.settimeout(options.rate)
    rx_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    rx_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #sock.sendto(data, (options.addr, options.port))
    rx_sock.bind((options.rx_addr, options.rx_port))

    tx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    tx_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    tx_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #sock.sendto(data, (options.addr, options.port))
    count = int(0)
    buff=ctypes.create_string_buffer(2)
    hdr = []

    for ch in CALLSIGN:
        hdr.append(ord(ch))

    
    #print list(data)
    #data.extend(numpy.random.randint(0, 256, size=248))
    #data = bytearray(data)
    #print binascii.hexlify(data)
    #sock.sendto(data, (options.addr, options.port))
    #if options.rand != 0:
    #    sleep_time = random.uniform(0, 2)
    #    print 'Sleeping for:', str(sleep_time)
    #    time.sleep(sleep_time)
    #else:
    #    time.sleep(options.rate)
    #count += 1
    msg = []
    count = numpy.uint16( numpy.int16(count) )
    
    msg.extend(hdr)
    msg.append((count >> 8) & 0xff)
    msg.append(count & 0xff)
    #need to add uplink packet count
    #need to add msg type
    msg.extend(numpy.random.randint(0, 1, size=248))
    msg = bytearray(msg)
    while 1:
        
        try:
            new_msg = []
            #increment counter
            count += 1
            count = numpy.uint16( numpy.int16(count) )
            #struct.pack_into(">H", buff, 0, count)
            #print buff
            #print count
            new_msg.extend(hdr)
            new_msg.append((count >> 8) & 0xff)
            new_msg.append(count & 0xff)
            rx_data, addr = rx_sock.recvfrom(4096) # block until data received on control port
            #new_msg.extend(hdr)
            new_msg.extend(rx_data)
            print count, addr
            new_msg = bytearray(new_msg)
            msg = new_msg
            #print binascii.hexlify(msg)
            tx_sock.sendto(msg, (options.tx_addr, options.tx_port))
            print binascii.hexlify(msg)
            print len(msg)
            #print addr
            
        except socket.timeout, e:
            print binascii.hexlify(msg)
            print len(msg)
            tx_sock.sendto(msg, (options.tx_addr, options.tx_port))
    
    sys.exit()
