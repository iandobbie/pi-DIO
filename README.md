# pi-DIO


A basic pyro server to allow digital IO tp be perfromed from cockpit
via a RaspberryPi. This uses the GPIO pins to flip 3.3V digital
signals from the Pi. Original desing is for the Oxford DeepSIM
instrument and this enables control of the light paths via Newport
flip mirrors.

Pinouts found from
http://raspberrypi.stackexchange.com/questions/12966/what-is-the-difference-between-board-and-bcm-for-gpio-pin-numbering
where the current system is using a model B revision 2.0 (second image
down on the page).

The cockpit side code is in devices/pi-DIO.py of
https://github.com/MicronOxford/cockpit.

Future plans include the ability to run temperature sensors over the
I2C connections so replacing all the functionality of the NI Digital
and Analouge board in the UCSF and earlier Oxford OMX's.

Basic calling conventions:

DIO.flipDownUp(mirror, position)

position=True flips up, position=False flips down, the relevant
mirror. Mirrors start at 0 (it is an index into GPIO_PINS array to say
which pin to flip for which logical mirror.


Instalation:

0) Install python and the raspberryPI GPIO python tools. We did this
by gettting a pretty standard raspbian install. I alos had to add
python_daemon using apt-get. This has a couple of extra dependencies
as well.

1) copy the DIO_server script into init.d, edit to reflect where the
code is on the system (currently /usr/local/pi_DIO)

2) edit the rpi.conf to reflect the port and IP address of the system.

3) Edit DIO.py to reflect what signals are on which pin of the system,
reference the diagram linked to above to work out which GPIO pin is
where on the connector. This should be moved into config file.

4) test to see it starts.

 
