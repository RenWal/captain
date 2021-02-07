This is a work-in-progress project for an API to control the Snaptain SP650 and
SP650Pro drones (and other models that share some portion of the protocol).

To use the tools in this repo, simply connect your device to the drone's wifi
hotspot.

## What are these files?

`snaptain_videobridge.py` is a tool to grab the video feed from the drone's FPV
camera. It returns a (currently very buggy) h264 stream on stdout that you can
pipe in some sort of ffmpeg-capable video player.

`snaptain_control.py` implements the UDP remote control protocol
(`ControlMessage`) used to directly control the drone. The protocol is rather
simple: Each data packet contains the same fields, the most important ones being
the pitch, roll, yaw, climb axes and their trim values. These packets need to be
sent at a semi-constant interval. The vendor's app does it 50 times per second.
*If you want to set any of the special control bits, such as the one for auto
takeoff, set them on 50 consecutive packets (i.e. one second).*<br>
To save you the pain of generating all messages by hand, there's the `Drone`
class, which keeps some state information, makes trimming easier, and handles
the packet counting for the control bits. The 2.4GHz non-WiFi controller needs
to be disconnected for this to work, just like the vendor's app won't work while
the controller is connected.

If you want to understand how the remote control protocol works on a bit level,
look at the `ControlMessage` class. It shows quite clearly how to generate the
packet byte sequence. Just send that sequence in an UDP packet to the drone.

`snaptain_control_demo.py` contains a crude definition for a sequence of remote
inputs that you can use to check out if all of the control axes work as
expected, especially if you want to try this on other models. It will just let
the drone take off, fly some short maneuvers, and land automatically.

`snaptain_control_xbox.py` is the fun stuff. It uses the Linux `xboxdrv` package
that allows you to receive data from xbox controllers, and some Python bindings.
(Note that you need to install xboxdrv before running this!) You can then use
any Xbox controller to fly the drone. The controls are mapped roughly the same
as on the official remote, however it's not yet feature-complete.
The important mappings are:
* yaw, climb: left stick
* roll, pitch: right stick
* trim: dpad
* 360 flip: A key
* takeoff: press on both thumbsticks simultaneously
* change speed: left bumper
* emergency stop: start key

Remember to clone the `Xbox` submodule if you want to use this! See the
[section on cloning with submodules in the git book](https://git-scm.com/book/en/v2/Git-Tools-Submodules#_cloning_submodules)
if you don't know how this works.

`snaptain_control_gui.py` is a very crude, very experimental Tkinter GUI that
lets you control the drone with your mouse. Unless you like pain, or lost
drones, or both, you should probably not use it and stick with using the xbox
controller.


## What's still missing?

**Telemetry** is not supported in any of the `snaptain_control_*.py`. There is
some telemetry experiment in `snaptain_tcproto.py` if you want to work on this.
Be advised that **you will not get battery warnings**! The drone's lights will
start flashing when the batteries are low, but there's no aural alert. When the
drone runs out of battery, it will autoland at its present position.

**Video Capture** and taking photos on the SD card is not supported yet. Those
commands seem to go through the telemetry protocol, rather than through the
control protocol.

**Return to Home** is not supported. It's unclear how the drone gets this
command, for the SP650 this seems to be outside of the control protocol. Anyway,
RTH never properly worked even with the vendor's remote. This shouldn't be too
much of a surprise since the drone doesn't have GPS.

Also, some fields from the control message protocol can't be set using the
`Drone` class yet. Feel free to add them.

## Tips

If you're daring enough to take this code and go flying, then here are some
pointers:

* When the drone senses loss of signal (WiFi lost or no valid UDP control
message during about 3 seconds), it will go into position hold mode, then land
after some more seconds. If the connection is re-established, you can take
control again which will cancel the autoland.
* You can prepare for a crash of this code by also having your phone with the
vendor's app  connected (but the app must be closed). If the Python code
crashes, you can quickly start the app and take control. Yes, the drone allows
having multiple WiFi remotes connected at the same time. Yes, you can connect a
new remote in flight. (And yes, this would theoretically allow someone to hijack
your drone.)
* When the non-WiFi remote is connected, WiFi control commands are ignored.
That means that you must turn that remote off. The drone will *not* allow you to
connect the non-WiFi remote in flight, unless the drone is in loss-of-signal
mode. In that case, you can turn the remote on, perform the pairing sequence and
take control.
* If you're using the Xbox controller, keep in mind that (usually) the
connection between controller and laptop has way less range than the connection
from laptop to drone. Should the drone stop responding, unless you're carrying
the laptop, don't make my mistake of running towards the drone and away from the
laptop. Most likely, you're just standing too far away from the laptop.
* Sometimes after a hard crash, you need to power cycle the drone before it
starts reacting to control commands via WiFi again.

## Known Bugs

* If you trim to the limits (which you probably shouldn't do anyway), then the
drone starts oscillating a bit and becomes generally hard to control. It tends
to react strangely to control inputs. If you find out why, please do let me
know.
* As previously stated, the video tools are very unstable. If you know how to
fix this, pull requests are welcome!

## Disclaimer

You can use this library for free. However, I take no responsibility for lost,
crashed, damaged or even bricked drones. This API isn't thoroughly tested and
it's not meant to be used for anything than hacking around with hardware you can
afford to lose.
