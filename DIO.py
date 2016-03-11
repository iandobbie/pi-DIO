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
#logging function to log the temp locally.
import logging
import time
from logging.handlers import RotatingFileHandler
#limit log files to about 1 MB. 
LOG_BYTES = 1000000 

#define the GPIO pins we are using. 
GPIO_PINS = [17,27,22,10,9,11,5]

# Use BCM GPIO references (naming convention for GPIO pins from Broadcom)
# instead of physical pin numbers on the Raspberry Pi board
GPIO.setmode(GPIO.BCM)


class pi:
    def __init__(self):
        self.mirrors = 0    # state of all mirrors
        # init the GPIO lines as output
        self.updatePeriod=60.0
        self.readsPerUpdate=10
        for pin in GPIO_PINS:
            GPIO.setup(pin,GPIO.OUT, initial=GPIO.HIGH)
        #first temp sensor on default 0x18 address.
        self.sensor =MCP9808.MCP9808(address=0x18) 
        self.sensor.begin()

        # A thread to publish status updates.
        # This reads temperatures and logs them
        self.statusThread = threading.Thread(target=self.updateTemps)
        self.statusThread.Daemon = True
        self.statusThread.start()
         


        
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

    def get_temperature(self):
        return (self.temperature)

    #create the log file
    def create_rotating_log(path):
        """
        Creates a rotating log
        """
        self.logger = logging.getLogger("TempratureLog")
        self.logger.setLevel(logging.INFO)
        # add a rotating handler
        handler = RotatingFileHandler(self.generateLogFilename(),
                                      maxBytes=LOG_BYTES, backupCount=5)
        formatter = logging.Formatter('%(asctime)s - %(message)s')

        self.logger.addHandler(handler)
 
        for i in range(10):
            self.logger.info("This is test log line %s" % i)
            time.sleep(1.5)
            
    def generateLogFilename(self):
        timestr=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        filename="ValueLog"+timestr+".log"
        filename = os.path.join("logs", filename)
        return filename

    #function to read temperature at set update frequency.
    #runs in a separate thread.
    def updateStatus(self):
        """Runs in a separate thread publish status updates."""
        self.temperature = None

        while True:
            #take readsPerUpdate measurements and average to reduce digitisation
            #errors and give better accuracy.
            for i in range(int(self.readPerUpdate)):
                try:
                    localTemperature = self.sensor.readTempC()
                    tempave+=localTemperature
                except:
                    localTemperature=None

                time.sleep(self.updatePeriod/self.readsPerUpdate)
            self.temperature=tempave/self.readsPerUpdate
