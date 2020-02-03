import socket
from signal import signal, SIGINT
from sys import exit
import time
import threading
import math
import json

s1 = socket.socket()
s2 = socket.socket()
print("Socket successfully created")

sport = 12345
rport = 12346

s1.bind(('', sport))
print("socket1 bound to {0}".format(sport))

s1.listen(5)
print("socket is listening")

# Object to hold the fake state of the robot. This will have other attributes in the real implementation.
# Turning by 90 degrees means turning left 90. + is ccw.
class State:
    def __init__(self, x, y, heading):
        self.x = x
        self.y = y
        self.heading = heading
    def move(self, amount):
        radHeading = self.heading * math.pi / 180
        self.x += amount * math.cos(radHeading)
        self.y += amount * math.sin(radHeading)
    def turn(self, amount):
        self.heading += amount
    def getStateString(self):
        dict = { 
            "timestamp": str(time.ctime()),
            "position_x": str(self.x),
            "position_y": str(self.y),
            "heading": str(self.heading),
        }
        s = "{"
        for key in dict:
            s += "\"" + key + "\":\"" + str(dict[key]) + "\", "
        s += "}"
        return s


def handler(signal_received, frame):
    print("CTRL-C detected")
    s1.close()
    s2.close()
    exit(0)

signal(SIGINT, handler)

def send():
    while True:
        c, addr = s1.accept()
        print("got connection from {0}".format(addr))
        
        # Wait for connection to be established with s1. Then the client has also opened a socket to connect to.
        #s2.connect(('127.0.0.1', rport))
        time.sleep(1)
        receiver.start()
        print("socket2 connected to {0}".format(rport))
        
        while True:
            sendlength = c.send(state.getStateString().encode())
            time.sleep(2)
        c.close()
        
def recv():
    while s2.connect_ex(('127.0.0.1', rport)) != 0:
        time.sleep(1)
    while True:
        i = s2.recv(1024)
        data = i.decode('utf-8').strip('\x00')
        j = json.loads(data)
        state.move(int(j["move"])) # Read move amount from json
        state.turn(int(j["turn"])) # Read turn amount from json
        print(data)
        
state = State(0, 0, 0) # Create a new state object at the origin facing East.

sender = threading.Thread(target=send, args=())
receiver = threading.Thread(target=recv, args=())
sender.start()

