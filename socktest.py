#! /usr/bin/python

from socketIO_client import SocketIO, BaseNamespace

HOST = '37.153.97.105'
PORT = 3000

class Namespace(BaseNamespace):

    def on_(self, eventname, eventargs):
        print "FOO:"+str(eventname)+":"+str(eventargs)

    def on_connect(self, socketIO):
        print '[Connected]'

    def on_disconnect(self):
        print '[Disconnected]'

    def on_error(self, name, message):
        print '[Error] %s: %s' % (name, message)

    def on_message(self, id, message):
        print '[Message] %s: %s' % (id, message)

print "Listening to "+HOST+":"+str(PORT)

socketIO = SocketIO(HOST, PORT, Namespace)

socketIO.emit("adduser","fred")
socketIO.wait()


