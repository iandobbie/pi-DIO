#IMD 20150420

# Code to actually control the flip mirrors and save state
#

# Mirrors are:
# 1 - Flip between 10x and 60x up is 10x down is 60x
# 2 - Flip transmission illuminarion between the two objectives.
# 3 - WF entry mirror, up goes via the WF path, down to the SLM
# 4 - WF exit mirror, up gives the WF path, down aloows light from SLM to sample

#GPIO control
import RPi.GPIO as GPIO
#MCP98808 temperature sensors over I2C bus, loses 2 GPIO pins but gains 8
#temp sensors. 
import Adafruit_MCP9808.MCP9808 as MCP9808

GPIO_PINS = [2]

# Use BCM GPIO references (naming convention for GPIO pins from Broadcom)
# instead of physical pin numbers on the Raspberry Pi board
GPIO.setmode(GPIO.BCM)


class pi:
    def __init__(self):
        self.mirrors = 0    # state of all mirrors
        # init the GPIO lines as output
        for pin in GPIO_PINS:
            GPIO.setup(pin,GPIO.OUT, initial=GPIO.HIGH)
        #first temp sensor on default 0x18 address.
        self.sensor - MCP9808.MCP9808(address=0x18) 
        self.sensor.begin()


        
    def flipDownUp(self, mirror, position):
#        print "flip mirror = %d to position = %d" % (mirror,position)
        if(GPIO_PINS[mirror] != None):
            all = self.mirrors
            if position > 0:
                all = self.mirrors | (1 << mirror)
                GPIO.output(GPIO_PINS[mirror],GPIO.HIGH)
            else:
                #all = self.mirrors ^ (1 << mirror)
                all = self.mirrors & ~(1 << mirror)
                GPIO.output(GPIO_PINS[mirror],GPIO.LOW)
 #       print "flip mirror = %d " % (all)
        self.mirrors = all
        return all;

    def flipMirrors(self, positions):
        self.mirrors = positions
        #need code to step through list and set individual posiitons. 

    def get_temperature(self,sensors):
        return (self.sensor.readTempC())
