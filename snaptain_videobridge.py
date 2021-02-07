#! /usr/bin/python3

import socket
import sys
import time

MAGIC_PACKET = bytes(range(10)) + bytes([0x28]*2)
MAGIC_INTERVAL = 1.0

out = sys.stdout.buffer

# you can try playing this with:
# ./snaptain-videobridge.py | cvlc --h264-fps 25 stream:///dev/stdin

# This will usually work fine for rough function checks, but the
# video delay is terrible and the decoder stumbles over all sorts of
# errors, especially when the wifi signal is weak and frames don't
# arrive in time. Sometimes VLC also just segfaults.
# You can try ffplay as well, this seems to be a little more stable,
# but the video delay is even worse.

with socket.socket() as s:
  s.connect(("172.16.10.1",8888))
  s.sendall(MAGIC_PACKET)
  t = time.monotonic()
  s.settimeout(10)
  out.write(bytes([0]))
  while 1:
    out.write(s.recv(1))
    if time.monotonic()-t > MAGIC_INTERVAL:
      # the app sends the magic packet about once per second
      # and the feed will freeze if you don't do that
      s.sendall(MAGIC_PACKET)
      t = time.monotonic()
