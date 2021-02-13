import socket
import sys
import errno
import threading
from threading import Thread
from .player import PlayerThread
from .master import MasterThread

class ReceptionThread(Thread):
    def __init__(self, port, master_):
        Thread.__init__(self)
        self.setDaemon(True)
        self.port = port
        self.master: MasterThread = master_
        self.print_header = "[*] reception.py:"
    

    def server_socket(self, portnum):
        try:
            for res in socket.getaddrinfo(None, portnum, socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, socket.AI_PASSIVE):
                af, socktype, proto, canonname, sa = res
                break
        except socket.gaieor as e:
            print(self.print_header, "getaddrinfo():{}".format(e))
            sys.exit(1)

        try:
            nbuf, sbuf = socket.getnameinfo(sa, socket.AI_PASSIVE)
        except socket.gaieor as e:
            print(self.print_header, "getnameinfo():{}".format(e))
            sys.exit(1)

        print(self.print_header, "port={}".format(sbuf))

        try:
            soc = socket.socket(af, socktype, proto)
        except OSError as e:
            print(self.print_header, "socket:{}".format(e))
            sys.exit(1)

        try:
            soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except OSError as e:
            print(self.print_header, "setsockopt:{}".format(e))
            sys.exit(1)

        try:
            soc.bind(sa)
        except OSError as e:
            print(self.print_header, "bind:{}".format(e))
            soc.close()
            sys.exit(1)

        try:
            soc.listen(socket.SOMAXCONN)
        except OSError as e:
            print(self.print_header, "listen:{}".format(e))
            soc.close()
            sys.exit(1)

        return soc

    def accept_loop(self, soc):
        while True:
            try:
                acc, addr = soc.accept()
                hbuf, sbuf = socket.getnameinfo(addr, socket.NI_NUMERICHOST | socket.NI_NUMERICSERV)
                print(self.print_header, "accept:{}:{}".format(hbuf, sbuf))
                t = PlayerThread(acc, master_=self.master)
                t.start()

            except InterruptedError as e:
                if e.errno != errno.EINTR:
                    print(self.print_header, "accept:{}".format(e))
            except RuntimeError as e:
                print(self.print_header, "thread:{}".format(e))


    def run(self):
        # if (len(sys.argv) != 2):
        #     print("Usage: {} <server port>".format(sys.argv[0]))
        #     sys.exit(1)

        soc = self.server_socket(self.port)

        print(self.print_header, "ready for accept")

        try:
            self.accept_loop(soc)
            soc.close()
        except KeyboardInterrupt:
            soc.close()
            sys.exit(1)

    