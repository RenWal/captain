#! /usr/bin/python3

import socket
import sys
import time
from binascii import hexlify

MAGIC_PACKET = bytes(range(10)) + bytes([0x25]*2)
NOTHING = bytes("noact\r\n", "ASCII")

with socket.socket() as s:
  s.connect(("172.16.10.1",8888))
  while 1:
    s.sendall(MAGIC_PACKET)
    line = bytearray()
    while not line or line[-1] != 0x0a:
      line += s.recv(1)
    if line != NOTHING:
      print(hexlify(line).decode('ASCII'))
    time.sleep(1)
