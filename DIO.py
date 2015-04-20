#IMD 20150420

# Code to actually control the flip mirrors and save state
#

# Mirrors are:
# 1 - Flip between 10x and 60x up is 10x down is 60x
# 2 - Flip transmission illuminarion between the two objectives.
# 3 - WF entry mirror, up goes via the WF path, down to the SLM
# 4 - WF exit mirror, up gives the WF path, down aloows light from SLM to sample

# 1 & 2 shiuld be flipped together and 3 & 4 other staes dont
# generally make much sense.

# # cmd line test, works on Raspberry Pi B v2.0 with patch cable I made.
# GPIO.setmmode(GPIO.BCM)
# GPIO.setup(2,GPIO.OUT, initial=GPIO.HIGH)
# #set line 2 low
# GPIO.output(2,GPIO.LOW)
# #set line 2 high
# GPIO.output(2,GPIO.HIGH)


# GPIO pins for the raspberry pi

import RPi.GPIO as GPIO

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
            
        


        
    def flipDownUp(self, mirror, position):
        print "flip mirror = %d to position = %d" % (mirror,position)
        if(GPIO_PINS[mirror] != None):
            all = self.mirrors
            if position > 0:
                all = self.mirrors | (1 << mirror)
                GPIO.output(GPIO_PINS[mirror],GPIO.HIGH)
            else:
                #all = self.mirrors ^ (1 << mirror)
                all = self.mirrors & ~(1 << mirror)
                GPIO.output(GPIO_PINS[mirror],GPIO.LOW)
        print "flip mirror = %d " % (all)
        self.mirrors = all
        return all;

    def flipMirrors(self, positions):
        self.mirrors = positions
        #need code to step through list and set individual posiitons. 
