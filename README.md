# pi-DIO

Copyright, Ian Dobbie - ian.dobbie@bioch.ox.ac.uk and David Pinto - carandraug@gmail.com 2015


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


This code now runs the Adafruit MCP9808 temperature sensor over i2c but this requires some config.

1.Install smb and i2c tools on Pi,
sudo apt-get install -y python-smbus i2c-tools
2.Install the adafruit MC9808 library, this required the python-dev packages as well.
enable i2c using the raspi-config tool (in adavnced options)
3.add i2c-bcm2708 and i2c-dev to the /etc/modules file
4.reboot


#Instalation:

0) Install python and the raspberryPI GPIO python tools. We did this
by gettting a pretty standard raspbian install. I alos had to add
python_daemon using apt-get. This has a couple of extra dependencies
as well.

1) copy the DIO_server script into init.d, edit to reflect where the
code is on the system (currently /usr/local/pi_DIO)

2) edit the RPi.conf to reflect the port and IP address of the system.

2b) Check permissions the init.d file and the DIO_server.py must have execute permissions. 

3) Edit DIO.py to reflect what signals are on which pin of the system,
reference the diagram linked to above to work out which GPIO pin is
where on the connector. This should be moved into config file.

4) test to see it starts.



#Basic calling conventions:

DIO.flipDownUp(mirror, position)

position=True flips up, position=False flips down, the relevant
mirror. Mirrors start at 0 (it is an index into GPIO_PINS array to say
which pin to flip for which logical mirror.

DIO.get_temperature() returns an averaged temperature reading
Averages are based on two variables readsPerUpdate and updatePeriod

Temperature is logged to a rotating log file.

#Brief summary of the config file format

As is the cockpit convention it has a section heading in this case it is "[rpi]"

ipAddress: is the current host ip address, needed as the system may have
	   several IPs and we need to know what to listen on.

port: Port to list on. Current standard is 7768.

GPIO lines: list of lines to use, currently in order
     	    [17,27,22,10,9,11,5]

TEMP_SENSORS = list of the i2c temp sensors addresses default first on
	       is [0x18]
 
