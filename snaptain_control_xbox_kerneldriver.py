#!/usr/bin/python3

import threading
import time
import socket
from xbox360controller import Xbox360Controller
from snaptain_control import Drone

class CommsThread(threading.Thread):
  def __init__(self, drone):
    super().__init__()
    self.drone = drone

  def run(self):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
      self.stop = False
      self.send = False
      while not self.stop:
        m = drone.next_message()
        if self.send:
          sock.sendto(m.to_proto(), ("172.16.10.1", 8080))
        #print(m)
        time.sleep(.02)

  def interrupt(self):
    self.stop = True
    self.join()

  def set_connected(self, connected):
    self.send = connected
    if connected:
      print("connected")
    else:
      print("disconnected")
  
  def is_connected(self):
    return self.send

drone = Drone()
joy = Xbox360Controller()

comms = CommsThread(drone)
comms.start()

takeoff = False
stop = False
trim = False
speed = False
flip = False
connect = False
calibrate = False
try:
  while 1:
    (roll, pitch) = joy.axis_r.x, -joy.axis_r.y
    (yaw, climb) = joy.axis_l.x, -joy.axis_l.y
    if roll == 0 and yaw == 0:
      coordinated = joy.trigger_r.value - joy.trigger_l.value
      roll = coordinated
      yaw = 0.7*coordinated
    drone.set_pitch_roll_vec(pitch, roll)
    drone.set_yaw_climb_vec(yaw, climb)
    if joy.button_thumb_l.is_pressed and joy.button_thumb_r.is_pressed:
      if not takeoff:
        drone.takeoff()
        takeoff = True
    else:
      takeoff = False
    if not trim:
      if joy.hat.y == 1:
        drone.trim_forward()
        trim = True
      elif joy.hat.y == -1:
        drone.trim_aft()
        trim = True
      elif joy.hat.x == -1:
        drone.trim_left()
        trim = True
      elif joy.hat.x == 1:
        drone.trim_right()
        trim = True
    elif joy.hat.x == 0 and joy.hat.y == 0:
      trim = False
    if joy.button_trigger_l.is_pressed:
      if not speed:
        drone.next_speed()
        speed = True
    else:
      speed = False
    if joy.button_a.is_pressed:
      if not flip:
        drone.flip()
        flip = True
    else:
      flip = False
    if joy.button_start.is_pressed:
      if not stop:
        drone.stop()
        stop = True
    else:
      stop = False
    if joy.button_mode.is_pressed:
      if not connect:
        comms.set_connected(not comms.is_connected())
        connect = True
    else:
      connect = False
    if joy.button_select.is_pressed:
      if not calibrate:
        drone.calibrate()
        calibrate = True
    else:
      calibrate = False
    time.sleep(0.02)
except KeyboardInterrupt:
  pass

comms.interrupt()
joy.close()