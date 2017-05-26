# this manages the currently running flow graph
# future: receive commands from network

# source ~/prefix/setup_env.sh && cd ~/rocksat/ && python2 manager.py
# while true; do nc -lp 1337; done

from threading import Thread, Semaphore
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from Queue import Queue

class DataReporter(Thread):
    max_msg_len = 252
    class _StopReporter(): pass # reporter shutdown token class

    def __init__(self, target):
        super(DataReporter, self).__init__()
        self.target = target
        self.failure = False
        self.q = Queue()
        self.loaded = Semaphore(0)
        self.start()
        self.loaded.acquire()
        if self.failure:
            raise IOError("couldn't initialize DataReporter")

    def stop(self):
        self.q.put(self._StopReporter())

    def send(self, msg):
        self.checkfailure()
        self._checkmsg(msg)
        self.q.put(msg)

    def checkfailure(self):
        if self.failure:
            raise IOError("DataReporter failure has occurred")

    def _checkmsg(self, msg):
        if not isinstance(msg, str):
            raise ValueError("only send strings")
        if len(msg) != self.max_msg_len:
            raise ValueError("messages was {} instead of {} bytes"
                    "".format(len(msg), self.max_msg_len))

class UDPDataReporter(DataReporter):
    def run(self):
        try:
            self.s = socket(AF_INET, SOCK_DGRAM)
            print("UDPDataReporter ready to send to {0}:{1}".format(*self.target))
        finally:
            self.loaded.release()

        while 1:
            msg = self.q.get()
            if self.failure or isinstance(msg, self._StopReporter):
                self.s.close()
                break
            self._checkmsg(msg)
            try:
                self.s.sendto(msg, self.target)
            except:
                self.failure = True
                raise

class TCPDataReporter(DataReporter):
    def run(self):
        try:
            self.s = socket(AF_INET, SOCK_STREAM)
            self.s.connect(self.target)
            print("TCPDataReporter connected to {0}:{1}".format(*self.target))
        except:
            print("TCPDataReporter failed connecting to {0}:{1}\n"
                    "HELPFUL HINT: try nc -lp {1}".format(*self.target))
            self.failure = True
            raise
        finally:
            self.loaded.release()

        while 1:
            msg = self.q.get()
            if self.failure or isinstance(msg, self._StopReporter):
                self.s.close()
                break
            self._checkmsg(msg)
            try:
                self.s.send(msg + "\n")
            except:
                self.failure = True
                raise

    def _checkmsg(self, msg):
        super(TCPDataReporter, self)._checkmsg(msg)
        if "\n" in msg:
            raise NotImplementedError("TCPDataReporter does not support newlines")


