#! /usr/bin/python

from socketIO_client import SocketIO, BaseNamespace
import threading
import random
import time
import socket, os
import sys
import cProfile

HOST = '37.153.97.105'
#HOST = 'localhost'
PORT = 3000
HEARTBEAT_SECS = (1.0 / 500)
(MAX_X, MAX_Y) = (640,480)
SPACEQUANT = 24

g_socketIO = None
g_objects = {}	# A dict containing (x,y) tuples, indexed by _id
g_id = ""
g_start_time = time.time()
g_updates = 0
g_targetcoord = (0,0)


def set_object(id,x,y):
# Update object, locally and remotely
    global g_objects
    g_objects[id]=(x,y)	# Update local copy
    g_socketIO.emit("handle",{"obj":[id,x,y]})	# Update remote copy

def sign(x):
    if(x > 0):
        return(1)
    elif(x < 0):
        return(-1)
    else:
        return(0)

def quant(x):
    return(int(x/SPACEQUANT)*SPACEQUANT)

def heartbeat():
    global g_objects,g_id,g_start_time,g_updates,g_targetcoord


    def retarget():
        global g_id, g_targetcoord
        g_id = g_objects.keys()[random.randrange(len(g_objects.keys()))]
        g_targetcoord=(quant(random.randrange(MAX_X)),quant(random.randrange(MAX_Y)))

    if g_objects<>{}:
        # Occasionally, pick a new key at random
        # if(random.randrange(50)==0) or (g_id==""):
        if(g_id==""):
            retarget()

	 
        # print "Moving object",g_id
        (x,y) = g_objects[g_id]
        # If we've got to destination, pick new target
        if (abs(x-g_targetcoord[0])<1) and (abs(y-g_targetcoord[1])<1):
            retarget()
            (x,y) = g_objects[g_id]

	(dx,dy) = (g_targetcoord[0] - x, g_targetcoord[1] - y)
        if(abs(dx) > abs(dy)):
            x = x + sign(dx)
        else:
            y = y + sign(dy)

        set_object(g_id,x,y)

        g_updates+=1
        t = time.time()-g_start_time
        print g_updates,"updates,",int(t),"secs (",int(g_updates/t),"/sec)"

def heartbeat_thread():
    while(1):
        heartbeat()
        time.sleep(HEARTBEAT_SECS)

class Namespace(BaseNamespace):

    def on_connect(self, socketIO):
        print '[Connected]'

    def on_disconnect(self):
        print '[Disconnected]'

    def on_error(self, name, message):
        print '[Error] %s: %s' % (name, message)

    def on_(self, eventName, *eventArguments):
        global g_objects
        # print '[Event] %s: %s' % (eventName, eventArguments)

        if(eventName=="objects"):
            # An update of all objects
            # Turn array into dict
            g_objects = {}
            for o in eventArguments[0]:
                g_objects[o["_id"]] = (o["x"],o["y"])

        if(eventName=="handle"):
            # print "HANDLE UPDATE:"
            (id,x,y) = eventArguments[0]["obj"]
            g_objects[id]=(x,y)	# Update local copy
            

    def on_message(self, id, message):
        print '[Message] %s: %s' % (id, message)

def main():
    global g_socketIO
    print "Listening to "+HOST+":"+str(PORT)

    g_socketIO = SocketIO(HOST, PORT, Namespace)

    print "Emitting adduser"
    g_socketIO.emit("adduser",socket.getfqdn()+";"+str(os.getpid()))

    if(len(sys.argv)<2):
        print "Usage:",sys.argv[0]," S or L or SL"
    if("S" in sys.argv[1]):
        print "Starting speaking"
        thread1 = threading.Thread(target=heartbeat_thread)
        thread1.start()
    if("L" in sys.argv[1]):
        print "Starting listening"
        g_socketIO.wait()
    else:
        time.sleep(60*60*24*365*100)

main()
