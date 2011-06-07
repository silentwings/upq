#!/usr/bin/env python

import socket
import sys
import ConfigParser



def send_cmd(txts, socket_path):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)
    print >>sys.stderr, "Connected to '%s'."%socket_path
    #for txt in txts:
    txt = reduce(lambda x, y: x+" "+y, txts)
    sock.send(txt+"\n")
    print >>sys.stderr, "Sent    : '%s'"%txt
    res=""
    while True:
        sock.settimeout(10)
        res += sock.recv(1)
        if res.endswith("\n"):
            print >>sys.stderr, res,
            break
    sock.close()

def main(argv=None):
    config = ConfigParser.RawConfigParser()
    config.read('upq.cfg')
    socket_path=config.get("paths","socket")
    if argv is None:
        argv = sys.argv
    send_cmd(argv[1:],socket_path)

if __name__ == "__main__":
    sys.exit(main())
