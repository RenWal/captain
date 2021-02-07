#!/usr/bin/python

import tkinter as tk
import threading
import time
import socket
from snaptain_control import ControlMessage, Drone

class ModeBox(tk.Message):
  def __init__(self, master, drone, title):
    super().__init__(master, text=title + "\n", borderwidth=1, relief="sunken", anchor="nw", width=100)
    self.title = title
    self.modes = set()

  def render(self):
    self['text'] = self.title + "\n" + "\n".join(sorted(self.modes))

  def clear_mode(self, mode):
    if mode in self.modes:
      self.modes.remove(mode)
      self.render()

  def add_mode(self, mode):
    self.modes.add(mode)
    self.render()

  def set_mode(self, mode):
    self.modes.clear()
    self.add_mode(mode)

class Application(tk.Frame):

  mode_labels = ["SPEED", "MODE", "", "CTRL"]

  def __init__(self, drone, master=None):
    super().__init__(master)
    self.drone = drone
    self.drone.register_callback(self.drone_callback)
    self.master = master
    self.pack()
    self.create_widgets()
    self.reset_modepanel()
    self.focus_set() # otherwise no key events
    self.bind("<KeyPress>", self.key_down)

  def create_widgets(self):
    self.center = tk.Frame(self)
    self.center.pack(side="right")
    self.maincontrol = tk.Canvas(self.center, bg="white", width=400, height=400, cursor="cross")
    self.maincontrol.create_line(200, 0, 200, 400)
    self.maincontrol.create_line(0, 200, 400, 200)
    self.maincontrol.pack(side="bottom")

    self.modepanel = tk.Frame(self.center, bg="red")
    self.modepanel.pack(side="top", fill="x", expand=1)
    self.mode_boxes = dict()
    for r in range(4):
      m = ModeBox(self.modepanel, self.drone, self.mode_labels[r])
      self.mode_boxes[self.mode_labels[r]] = m
      m.grid(row=0, column=r, sticky="new")
      self.modepanel.columnconfigure(r, weight=1, uniform="grp1")

    self.statuspanel = tk.Frame(self, relief='groove')
    self.statuspanel.pack(side="left")
    self.connect_btn = tk.Button(self.statuspanel, text="Connect")
    self.connect_btn.pack()
    self.speed_lbl = tk.Label(self.statuspanel, text="Speed: LOCK")
    self.speed_lbl.pack()

    self.maincontrol.bind("<B1-Motion>", self.mouse_move)
    self.maincontrol.bind("<ButtonPress-1>", self.mouse_move)
    self.maincontrol.bind("<ButtonRelease-1>", self.mouse_release)

  def reset_modepanel(self):
    self.mode_boxes["MODE"].set_mode("GROUND")
    self.mode_boxes["SPEED"].set_mode("LOCK")
    self.mode_boxes["CTRL"].set_mode("LOCK")

  def key_down(self, event):
    if event.char == 't':
      self.mode_boxes["MODE"].clear_mode("GROUND")
      self.mode_boxes["MODE"].add_mode("TAKEOFF")
      self.mode_boxes["SPEED"].set_mode(["30", "60", "MAX"][self.drone.speed])
      self.mode_boxes["CTRL"].set_mode("DIRECT")
      self.drone.takeoff()
    elif event.char == 'l':
      self.mode_boxes["MODE"].add_mode("LANDING")
      self.drone.land()
    elif event.char == 'w':
      if self.drone.climb < 0.9:
        self.drone.climb+=0.1
    elif event.char == 's':
      self.drone.climb = 0
    elif event.char == 'x':
      if self.drone.climb > -0.9:
        self.drone.climb-=0.1

  def mouse_move(self, event):
    self.drone.set_pitch_roll_vec((event.y-200)/200, (event.x-200)/200)

  def mouse_release(self, event):
    self.drone.attitude_hold()

  def drone_callback(self, event, data):
    self.after(0, self.drone_callback_uithread(event, data))

  def drone_callback_uithread(self, event, data):
    if event == 'action_end':
      if data == 'takeoff':
        self.mode_boxes["MODE"].clear_mode('TAKEOFF')
      elif data == 'land':
        self.reset_modepanel()

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

drone = Drone()

comms = CommsThread(drone)
root = tk.Tk()
app = Application(drone, master=root)

comms.start()
app.mainloop()

comms.interrupt()
comms.join()
