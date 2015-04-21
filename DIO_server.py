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

import serial
import socket
import threading
import time
import Pyro4

CONFIG_NAME = 'RPi'
Pyro4.config.SERIALIZER = 'pickle'
Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')

class Server(object):
    def __init__(self):
        self.run_flag = True
        self.devices = {}
        self.daemon_thread = None


    def run(self):
        import readconfig
        config = readconfig.config
        port = config.get(CONFIG_NAME, 'port')
        host = config.get(CONFIG_NAME, 'ipAddress')
        import DIO
        pi = DIO.pi()
        self.devices={pi: pi}
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
            device.connection.close()


    def stop(self):
        self.run_flag = False

if __name__ == "__main__":
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
