# IMD 20150420

# HISTORY - Started as a quick hack to do async Digital IO (ie not DSP
# controlled on DeepSIM in Oxford.  Simple interface to flip mirrrors
# in v1.0


import Pyro4
import socket
import threading

import DIO

pi = DIO.pi()

now = time.time()
nowtup = time.localtime(now)

#IMD 20150420 increase port number
def server():
    daemon = Pyro4.Daemon(port = 7768,
            host = socket.gethostbyname(socket.gethostname()))
    Pyro4.Daemon.serveSimple(
            {pi: 'pi',
             daemon = daemon, ns = False, verbose = True)
threading.Thread(target = server).start()

