#!/usr/bin/python3

import threading
import time
import socket
import Xbox.xbox as xbox
from snaptain_control import ControlMessage, Drone

DEADZONE = 256

class CommsThread(threading.Thread):
  def __init__(self, drone):
    super().__init__()
    self.drone = drone

  def run(self):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
      self.stop = False
      while not self.stop:
        m = drone.next_message()
        sock.sendto(m.to_proto(), ("172.16.10.1", 8080))
        #print(m)
        time.sleep(.02)

  def interrupt(self):
    self.stop = True
    self.join()

drone = Drone()
joy = xbox.Joystick()

comms = CommsThread(drone)
comms.start()

takeoff = False
stop = False
trim = False
speed = False
flip = False
try:
  while 1:
    (roll, pitch) = joy.rightStick(DEADZONE)
    (yaw, climb) = joy.leftStick(DEADZONE)
    if roll == 0 and yaw == 0:
      coordinated = joy.rightTrigger() - joy.leftTrigger()
      roll = coordinated
      yaw = 0.7*coordinated
    drone.set_pitch_roll_vec(pitch, roll)
    drone.set_yaw_climb_vec(yaw, climb)
    if joy.leftThumbstick() and joy.rightThumbstick():
      if not takeoff:
        drone.takeoff()
        takeoff = True
    else:
      takeoff = False
    if not trim:
      if joy.dpadUp():
        drone.trim_forward()
        trim = True
      elif joy.dpadDown():
        drone.trim_aft()
        trim = True
      elif joy.dpadLeft():
        drone.trim_left()
        trim = True
      elif joy.dpadRight():
        drone.trim_right()
        trim = True
    elif not joy.dpadUp() and not joy.dpadDown() and not joy.dpadLeft() and not joy.dpadRight():
      trim = False
    if joy.leftBumper():
      if not speed:
        drone.next_speed()
        speed = True
    else:
      speed = False
    if joy.A():
      if not flip:
        drone.flip()
        flip = True
    else:
      flip = False
    if joy.Start():
      if not stop:
        drone.stop()
        stop = True
    else:
      stop = False
    time.sleep(0.02)
except KeyboardInterrupt:
  pass

comms.interrupt()
joy.close()
