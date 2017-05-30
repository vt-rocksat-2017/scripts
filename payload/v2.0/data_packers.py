#!/usr/bin/env python2

# this manages the currently running flow graph
# future: receive commands from network

# ./payload_2.py
# ./mockcommand.py 127.0.0.1

import math, sys, os, socket, time, struct, traceback, binascii, logging

class ADSBPacker(object):
    class PacketFullError(ValueError): pass

    def __init__(self):
        self.len = 0
        self.msgs = []

    # refer to icd, ADSB section
    def __str__(self):
        count = len(self.msgs)
        if count > 32: # 6 bits
            return "\0ERROR packet too large"
        lengths = 0
        bit = 1
        for i in range(count):
            l = len(self.msgs[i])*8
            if l == 56:
                # 0, do nothing
                pass
            elif l == 112:
                # 1, add to bitmask
                lengths += bit
            else:
                raise ValueError("bad packet length {} (data {})".format(l, repr(self.msgs[i])))
            bit *= 2
        #print count
        #print bin(lengths)
        ret = struct.pack("!BI", count, lengths) + "".join(self.msgs)
        return ret

    def add(self, msg):
        if (1 + 4 + self.len + len(msg)) > 245:
            raise self.PacketFullError("packet is full!")
        #print("queueing ADSB message: {}".format(repr(msg)))
        print("queueing ADSB message: {}".format(binascii.hexlify(msg)))
        self.msgs.append(msg)
        self.len += len(msg)

class AISPacker(object):
    class PacketFullError(ValueError): pass

    def __init__(self):
        self.len = 0
        self.msgs = []

    def __str__(self):
        ret = ""
        for msg in self.msgs:
            ret += msg
        return ret

    def add(self, msg):
        if (self.len + len(msg)) > 245:
            raise self.PacketFullError("packet is full!")
        print("queueing AIS message {:3d}: {}".format(len(msg), repr(msg)))
        self.msgs.append(msg)
        self.len += len(msg)

