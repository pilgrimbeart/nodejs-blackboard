#! /usr/bin/python

from socketIO_client import SocketIO, BaseNamespace
import threading
import random
import time
import socket, os
import cProfile

HOST = '37.153.97.105'
#HOST = 'localhost'
PORT = 3000
HEARTBEAT_SECS = 0.002
(MAX_X, MAX_Y) = (640,480)

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

def heartbeat():
    global g_objects,g_id,g_start_time,g_updates,g_targetcoord

    def sign(x):
        if(x > 0):
            return(1)
        elif(x < 0):
            return(-1)
        else:
            return(0)

    if g_objects<>{}:
        # Occasionally, pick a new key at random
        if(random.randrange(50)==0) or (g_id==""):
            g_id = g_objects.keys()[random.randrange(len(g_objects.keys()))]
            g_targetcoord=(random.randrange(MAX_X),random.randrange(MAX_Y))

	 
        # print "Moving object",g_id
        (x,y) = g_objects[g_id]
        #x = (x-200)*0.9+200
        #y = (y-200)*0.9+200
        #if(y > 0):
        #    y = y - 1
	(dx,dy) = (g_targetcoord[0] - x, g_targetcoord[1] - y)
        if(abs(dx) > abs(dy)):
            x = x + sign(dx)
        else:
            y = y + sign(dy)
        set_object(g_id,x,y)
        g_updates+=1
        t = time.time()-g_start_time
        print g_updates,"updates,",int(t),"secs (",int(g_updates/t),"/sec)"
    threading.Timer(HEARTBEAT_SECS, heartbeat).start()

class Namespace(BaseNamespace):

    def on_connect(self, socketIO):
        print '[Connected]'

    def on_disconnect(self):
        print '[Disconnected]'

    def on_error(self, name, message):
        print '[Error] %s: %s' % (name, message)

    def on_(self, eventName, *eventArguments):
        global g_objects
        print '[Event] %s: %s' % (eventName, eventArguments)

        if(eventName=="objects"):
            # An update of all objects
            # Turn array into dict
            g_objects = {}
            for o in eventArguments[0]:
                g_objects[o["_id"]] = (o["x"],o["y"])

        if(eventName=="handle"):
            print "HANDLE UPDATE:"
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

    print "Starting timer"
    threading.Timer(HEARTBEAT_SECS, heartbeat).start()

    g_socketIO.wait()


cProfile.run("main()")
