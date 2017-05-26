#!/usr/bin/env python2

import time, traceback, sys
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, timeout
from threading import Thread

def hexchunks(data, n):
    chunks = [data[i:i+n] for i in range(0, len(data), n)]
    return [c.encode("hex") for c in chunks]

class DataListener(Thread):
    def run(self):
        self.s = socket(AF_INET, SOCK_DGRAM)
        self.s.bind(("0.0.0.0", 1337))
        self.s.settimeout(1)
        self._exit = False
        try:
            while not self._exit:
                try:
                    d = self.s.recvfrom(252)
                except timeout:
                    continue
                print("DataListener received:")
                print("\n".join(["    "+c for c in hexchunks("\xff"*4+d[0], 32)]))
        finally:
            self.s.close()

    def stop(self):
        self._exit = True

def drivetest(targetip):
    while 1:
        try:
            s = socket(AF_INET, SOCK_STREAM)
            s.connect((targetip, 2600))
            print("connected, starting data collection")
            s.send("adsb\n")
            time.sleep(30)
            s.send("exit\n")
            print("restarting payload")
        except Exception as e:
            traceback.print_exc()
        finally:
            s.close()
            print("starting again in 2 seconds...")
            time.sleep(2)

if __name__ == "__main__":
    targetip = sys.argv[1] if len(sys.argv)>1 else "10.101.10.11"
    t = DataListener()
    t.start()
    try:
        drivetest(targetip)
    finally:
        t.stop()
        t.join()
