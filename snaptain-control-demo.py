#!/usr/bin/python3

from binascii import hexlify
import socket
import time

class ControlMessage:
  def __init__(self, climb = 0, roll = 0, pitch = 0, yaw = 0, pitchTrim = 0, rollTrim = 0, yawTrim = 0, speed = 0, noHead = False, propLock = False, flip = False, takeoff = False, land = False, calibrate = False):
    # up-down vector, -1..1
    self.climb = climb
    # roll vector, -1..1 (negative is left)
    self.roll = roll
    # pitch vector, -1..1 (negative is down, resulting in forward movement)
    self.pitch = pitch
    # yaw vector, -1..1 (negative is anticlockwise)
    self.yaw = yaw
    # up-down trim, -16..15 (negative is aft)
    self.pitchTrim = pitchTrim
    # roll trim, -16..15 (negative is left)
    self.rollTrim = rollTrim
    # yaw trim, -16..15 (negative is left)
    # (yaw trim is quite gentle on the SP650, if you want to see it, go to the limits)
    self.yawTrim = yawTrim
    # speed mode, 0..2 (0 = 30%, 1 = 60%, 2 = 100%)
    # this governs the responsiveness of the control inputs
    self.speed = speed
    # headless mode
    # decouples the pitch and roll axis from the yaw axis, i.e. when the
    # drone is rotated those axes do not rotate with it
    # (this is nice when you want to rotate for camera angle but keep going straight)
    self.noHead = noHead
    # prop lock
    # stops the rotors (the drone WILL fall out of the sky if you set this flag
    # while in the air; it's supposed to be used when landing and as a last-resort
    # emergency stop)
    self.propLock = propLock
    # "360degree flip" action
    # loops the drone (ensure ground clearance!)
    self.flip = flip
    # auto-takeoff action
    # brings the drone up and enters attitude hold
    self.takeoff = takeoff
    # auto-land action
    # sets slight negative thrust bias and stops rotors once the drone collides
    # with the ground
    self.land = land
    # calibrate action
    # calibrates the gyro (do NOT do this except when on the ground with prop lock engaged)
    self.calibrate = calibrate

  @staticmethod
  def pack_bigvec(f):
    return round((f/2+0.5)*255)

  @staticmethod
  def unpack_bigvec(b):
    return (b/255-0.5)*2

  @staticmethod
  def pack_smallvec(f):
    return round((f/4+0.25)*255)

  @staticmethod
  def unpack_smallvec(b):
    return (b/255-0.25)*4

  @staticmethod
  def pack_trim(t):
    return t+16

  @staticmethod
  def unpack_trim(b):
    return b-16

  def to_proto(self):
    # packs the values into the bit field expected by the drone
    field = bytearray([0]*11)
    field[0] = 0xFF
    field[1] = 0x08
    field[2] = self.pack_bigvec(self.climb)
    field[3] = self.pack_smallvec(self.yaw)
    field[4] = self.pack_smallvec(self.pitch)
    field[5] = self.pack_smallvec(self.roll)
    field[6] = self.pack_trim(self.yawTrim) | (int(self.calibrate) << 6) | (1<<7)
    field[7] = self.pack_trim(self.pitchTrim)
    field[8] = self.pack_trim(self.rollTrim)
    field[9] = self.speed | (self.flip<<2) | (self.noHead<<4) | (self.propLock<<5) | (self.takeoff<<6) | (self.land<<7)
    field[10] = 255 - (sum(field[1:10]) % 256)
    return field

  @classmethod
  def from_proto(clazz, field, ignoreChecksum = False):
    assert ignoreChecksum or field[10] == 255 - (sum(field[1:10]) % 256), "checksum fail"
    m = ControlMessage()
    m.climb = -m.unpack_bigvec(field[2])
    m.yaw = m.unpack_smallvec(field[3])
    m.pitch = m.unpack_smallvec(field[4])
    m.roll = m.unpack_smallvec(field[5])
    m.yawTrim = m.unpack_trim(field[6] & 0b00011111)
    m.calibrate = (field[6] & 1<<6) != 0
    m.pitchTrim = m.unpack_trim(field[7])
    m.rollTrim = m.unpack_trim(field[8])
    m.speed = field[9] & 0b11
    m.flip = (field[9] & 1<<2) != 0
    m.noHead = (field[9] & 1<<4) != 0
    m.propLock = (field[9] & 1<<5) != 0
    m.takeoff = (field[9] & 1<<6) != 0
    m.land = (field[9] & 1<<7) != 0
    return m

  def __str__(self):
    return "climb: {}\npitch: {}\nroll: {}\nyaw: {}\npitch trim: {}\nroll trim: {}\nyaw trim: {}\nspeed: {}\ncalibrate: {}\nflip: {}\nno head: {}\nprop lock: {}\ntakeoff: {}\nland: {}".format(
      self.climb, self.pitch, self.roll, self.yaw,
      self.pitchTrim, self.rollTrim, self.yawTrim,
      self.speed, self.calibrate, self.flip, self.noHead, self.propLock, self.takeoff, self.land
    )

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
