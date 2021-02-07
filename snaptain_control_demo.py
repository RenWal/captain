#!/usr/bin/python3

from snaptain_control import ControlMessage
from binascii import hexlify
import socket
import time

#print(hexlify(ControlMessage(pitch=0.01,yaw=-0.004,roll=-0.004,takeoff=True,rollTrim=-16).to_proto()))
#print(ControlMessage())
#print(ControlMessage.from_proto(bytearray(int(x, 16) for x in "ff 08 7e 3f 40 3f 90 10 10 00 0b".split())))

#print(ControlMessage.from_proto(bytearray(int(x, 16) for x in "ff 08 7e 3f 40 3f 90 10 00 40 print(hexlify(ControlMessage(sp))db".split())))

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
  # quick and dirty way to test if all axes are functional
  pt=-2
  rt=3
  # sending action flags for 1 second replicates what the app does,
  # however, sending it once is enough if you don't have packet loss
  messages = \
   [ControlMessage()]*200 \
   + [ControlMessage(calibrate=True)]*50 \
   + [ControlMessage()]*100 \
   + [ControlMessage(takeoff=True)]*50 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt)]*200 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt,roll=-0.5)]*20 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt)]*25 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt,roll=0.3)]*20 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt)]*100 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt,roll=0.5)]*20 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt)]*25 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt,roll=-0.3)]*20 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt)]*100 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt,pitch=-0.5)]*20 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt)]*25 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt,pitch=0.3)]*20 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt)]*100 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt,pitch=0.5)]*20 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt)]*25 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt,pitch=-0.3)]*20 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt)]*100 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt,climb=0.7)]*15 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt)]*200 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt,climb=-1)]*15 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt)]*200 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt,yaw=1)]*100 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt)]*200 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt,land=True)]*50 \
   + [ControlMessage(pitchTrim=pt,rollTrim=rt)]*500

  for m in messages:
    sock.sendto(m.to_proto(), ("172.16.10.1", 8080))
    # you can increase this a little, but the drone will go into comms-lost mode
    # if you increase this too much
    time.sleep(.02)
