This is a work-in-progress project for an API to control the Snaptain SP650 and
SP650Pro drones (and other models that share some portion of the protocol).

To use the tools in this repo, simply connect your device to the drone's wifi.

`snaptain-videobridge` is a tool to grab the video feed from the drone's FPV camera.
It returns a (currently very buggy) h264 stream on stdout that you can pipe in some
sort of ffmpeg-capable video player.

`snaptain-control-demo` implements the UDP remote control protocol used to directly
control the drone. The controller needs to be disconnected for this to work, just
like the app won't work while the controller is connected.

If you want to understand how the remote control protocol works, look at the
ControlMessage class in the demo. It allows you to specify what you want the drone
to do and build the binary packet. Just send this via UDP to the drone.

The demo contains a crude definition for a sequence of remote inputs that you can
use to check out if all of the control axes work as expected, especially if you
want to try this on other models.

## Disclaimer

You can use this library for free. However, I take no responsibility for lost,
crashed, damaged or even bricked drones. This API isn't tested and it's not meant
to be used for anything than hacking around with hardware you can afford to lose.
