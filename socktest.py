#! /usr/bin/python

from socketIO_client import SocketIO, BaseNamespace
import threading
import random
import time
import socket, os
import sys
import cProfile

#HOST = '37.153.97.105'	# Pilgrim's Joyent SmartMachine "PB1"
HOST = 'localhost'
PORT = 3000
HEARTBEAT_SECS = (1.0 / 500)
(MAX_X, MAX_Y) = (640,480)
SPACEQUANT = 24

g_socketIO = None
g_objects = {}	# A dict containing (x,y) tuples, indexed by _id
g_objects_lock = None	# Since we are multithreaded, protect access to g_objects. Otherwise we may e.g. choose a key to work with, then find it disappears under us
g_id = ""
g_start_time = 0
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

    g_objects_lock.acquire()
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

    g_objects_lock.release()


def heartbeat_thread():
    # Running at a defined QPS speed is complicated by the facts that:
    # 1) Doing the heartbeat takes time (which we need to subtract from any time we wait)
    # 2) sleep() may not delay at all if passed very small numbers
    # So we use an absolute measure of time, instead of a relative one
    # This does mean that if for some reason we get stalled, we will burst to catch up
    global g_updates, g_start_time
    while(1):
        heartbeat()
        elapsed = time.time() - g_start_time
        timetosleep = max(0, (g_updates+1)*HEARTBEAT_SECS - elapsed)
        g_updates += 1
        print g_updates,"updates,",int(elapsed),"secs (",int(g_updates/elapsed),"/sec) timetosleep=",timetosleep
        time.sleep(timetosleep)

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
            g_objects_lock.acquire()
            g_objects = {}
            for o in eventArguments[0]:
                g_objects[o["_id"]] = (o["x"],o["y"])
            g_objects_lock.release()

        if(eventName=="handle"):
            # print "HANDLE UPDATE:"
            (id,x,y) = eventArguments[0]["obj"]
            g_objects_lock.acquire()
            g_objects[id]=(x,y)	# Update local copy
            g_objects_lock.release()

    def on_message(self, id, message):
        print '[Message] %s: %s' % (id, message)

def main():
    global g_socketIO,g_start_time,g_objects_lock
    g_objects_lock = threading.Lock()

    print "Listening to "+HOST+":"+str(PORT)

    g_socketIO = SocketIO(HOST, PORT, Namespace)

    print "Emitting adduser"
    g_socketIO.emit("adduser",socket.getfqdn()+";"+str(os.getpid()))

    g_start_time = time.time()
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
