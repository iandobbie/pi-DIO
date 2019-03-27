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
#library for TSYS01 sensor
import TSYS01.TSYS01 as TSYS01
#logging function to log the temp locally.
import logging
import time
import datetime
import os
import Pyro4
from logging.handlers import RotatingFileHandler
import threading
import readconfig
import re
#limit log files to about 1 MB. 
LOG_BYTES = 1000000 
CONFIG_NAME = 'rpi'

# Use BCM GPIO references (naming convention for GPIO pins from Broadcom)
# instead of physical pin numbers on the Raspberry Pi board
GPIO.setmode(GPIO.BCM)

@Pyro4.expose
class pi:
    def __init__(self):
        config = readconfig.config
        GPIO_linesString = config.get(CONFIG_NAME, 'GPIO_lines')
        self.GPIO_lines=[]
        for line in GPIO_linesString.split(','):
            self.GPIO_lines.append(int(line))
        temp_sensors_linesString = config.get(CONFIG_NAME, 'temp_sensors')
        self.sensors = []
        for line in temp_sensors_linesString.split(','):
            sensor_type,i2c_address =line.split(':')
            i2c_address=int(i2c_address,0) 
            print ("adding sensor: "+sensor_type +" Adress: %d " % i2c_address)
            if (sensor_type == 'MCP9808'):
                self.sensors.append(MCP9808.MCP9808(address=i2c_address))
                #starts the last one added
                self.sensors[-1].begin()
                print (self.sensors[-1].readTempC())
            elif (sensor_type == 'TSYS01'):
                self.sensors.append(TSYS01.TSYS01(address=i2c_address))
                print (self.sensors[-1].readTempC())

        self.mirrors = 0    # state of all mirrors
        # init the GPIO lines as output
        self.updatePeriod=10.0
        self.readsPerUpdate=10
        for pin in self.GPIO_lines:
            GPIO.setup(pin,GPIO.OUT, initial=GPIO.HIGH)
        #Open and start all temp sensors
        # A thread to record periodic temperature readings
        # This reads temperatures and logs them
        self.statusThread = threading.Thread(target=self.updateTemps)
        self.statusThread.Daemon = True
        self.statusThread.start()

    #what to do on device disable?
    def disable(self):
        pass

        
    def flipDownUp(self, mirror, position):
        self.logger.info("Flip =  %s - %s" % (mirror,position))        
        #        print "flip mirror = %d to position = %d" % (mirror,position)
        if(self.GPIO_lines[mirror] != None):
            all = self.mirrors
            if position > 0:
                all = self.mirrors | (1 << mirror)
                GPIO.output(self.GPIO_lines[mirror],GPIO.HIGH)
            else:
                #all = self.mirrors ^ (1 << mirror)
                all = self.mirrors & ~(1 << mirror)
                GPIO.output(self.GPIO_lines[mirror],GPIO.LOW)
 #       print "flip mirror = %d " % (all)
        self.mirrors = all
        return all;

    def flipMirrors(self, positions):
        self.mirrors = positions
        #need code to step through list and set individual posiitons. 

    #return the list of current temperatures.     
    def get_temperature(self):
        return (self.temperature)

    #create the log file
    def create_rotating_log(self):
        """
        Creates a rotating log
        """
        self.logger = logging.getLogger('TempratureLog')
        self.logger.setLevel(logging.INFO)
        # add a rotating handler
        self.handler = RotatingFileHandler(self.generateLogFilename(),
                                      maxBytes=LOG_BYTES, backupCount=5)
        self.handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)
 
    def generateLogFilename(self):
        timestr=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        filename="Temperature-"+timestr+".log"
        filename = os.path.join("/usr/local/pi-DIO/logs", filename)
        return filename

    #function to change updatePeriod
    def tempUpdatePeriod(self,period):
        self.updatePeriod=period

    #function to change readsPerUpdate
    def tempReadsPerUpdate(self,reads):
        self.readsPerUpdate=reads
    
    #function to read temperature at set update frequency.
    #runs in a separate thread.
    def updateTemps(self):
        """Runs in a separate thread publish status updates."""
        self.temperature = [None] * len(self.sensors)
        tempave = [None] * len(self.sensors)

        self.create_rotating_log()

        while True:
            #zero the new averages.
            for i in xrange(len(self.sensors)):
                tempave[i]=0.0
            #take readsPerUpdate measurements and average to reduce digitisation
            #errors and give better accuracy.
            for i in range(int(self.readsPerUpdate)):
                for i in xrange(len(self.sensors)):
                    try:
                        tempave[i]+=self.sensors[i].readTempC()
                    except:
                        localTemperature=None
                time.sleep(self.updatePeriod/self.readsPerUpdate)
            for i in xrange(len(self.sensors)):    
                self.temperature[i]=tempave[i]/self.readsPerUpdate
                self.logger.info("Temperature-%s =  %s" %(i,self.temperature[i]))
