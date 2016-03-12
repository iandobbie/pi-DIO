#!/usr/bin/env python
"""A modular server for Laser classes.

Copyright 2014-2015 Mick Phillips (mick.phillips at gmail dot com)
and 2015 Ian Dobbie (ian.dobbie at gmail dot com)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import threading
import time

import Pyro4

import readconfig
import DIO

CONFIG_NAME = 'rpi'
Pyro4.config.SERIALIZER = 'pickle'
Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')

class Server(object):
    def __init__(self):
        self.run_flag = True
        self.devices = {}
        self.daemon_thread = None


    def run(self):
        config = readconfig.config
        port = config.get(CONFIG_NAME, 'port')
        host = config.get(CONFIG_NAME, 'ipAddress')
        self.pi = DIO.pi()
        print self.pi
        self.devices={self.pi: 'pi'}
        self.daemon = Pyro4.Daemon(port=int(port), host=host)
        # Start the daemon in a new thread.
        self.daemon_thread = threading.Thread(
            target=Pyro4.Daemon.serveSimple,
            args = (self.devices, ), # our mapping of class instances to names
            kwargs = {'daemon': self.daemon, 'ns': False}
            )
        self.daemon_thread.start()

        # Wait until run_flag is set to False.
        while self.run_flag:
            time.sleep(1)

        # Do any cleanup.
        self.daemon.shutdown()
        self.daemon_thread.join()

        # For each laser ...
        for (device, name) in self.devices.iteritems():
            # ... make sure emission is switched off
            device.disable()
            # ... relase the COM port.
#            device.connection.close()


    def stop(self):
        self.run_flag = False

def start_server():		
    ## Only run when called as a script --- do not run on include.
    #  This way, we can use an interactive shell to test out the class.
    server = Server()
    server_thread = threading.Thread(target = server.run)
    server_thread.start()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        server.stop()
        server_thread.join()
		
def main():
    ##FIXME This is wrong. We should instead be checking with
    ##      DIO if we have enough permissions instead.
    if os.getuid() != 0:
        raise EnvironmentError("We need root permissions")
    ## Ideally we would create a nice daemon, create a pidfile, and
    ## it would be possible check our status and stop from an init.d
    ## script.  Unfortunately, our version of daemon does not have
    ## that class, and lockfile does not write the PID.  So we don't
    ## fork, we don't count on daemon, and rely start-stop-daemon
    ## to do all of this for us.
    start_server()
		
		
if __name__ == "__main__":
    main()
