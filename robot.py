import json
import math
import random
from signal import signal, SIGINT
import socket
from sys import exit
import time
import threading
from comm import Comm


class Robot:
    def __init__(self, x, y, heading):
        self.x = x
        self.y = y
        self.heading = heading
        self.weed_volume = 0
        self.communicator = Comm(12345, 12346)
        self.start()
        
    def start(self):
        while True:
            while self.communicator.has_read_data():
                data = self.communicator.read() # cmd will be a JSON object from the controller.
                cmd = json.loads(data)
                self.process(cmd)
                
            weeds = random.randrange(5)
            self.weed_volume += weeds
            print("Robot collected {0}".format(weeds))
                
            self.communicator.send(self.get_state_string())
            time.sleep(2)
            
    # cmd is a JSON string.
    def process(self, cmd):
        print("Processing {0}".format(cmd))
        self.move(int(cmd["move"])) # Read move amount from json
        self.turn(int(cmd["turn"])) # Read turn amount from json
            
    def move(self, amount):
        radHeading = self.heading * math.pi / 180
        self.x += amount * math.cos(radHeading)
        self.y += amount * math.sin(radHeading)
        
    def turn(self, amount):
        self.heading += amount
        
    def get_state_string(self):
        dict = { 
            "timestamp": str(time.ctime()),
            "position_x": str(self.x),
            "position_y": str(self.y),
            "heading": str(self.heading),
            "weeds": str(self.weed_volume),
        }
        s = "{"
        for key in dict:
            s += "\"" + key + "\":\"" + str(dict[key]) + "\", "
        s = s[:-2]
        s += "}"
        return s
        
    def shutdown(self):
        self.communicator.close()

robot = Robot(0, 0, 0)
        
# Cleanup the program before shutdown.
def handler(signal_received, frame):
    print("CTRL-C detected")
    robot.shutdown()
    exit(0)
    
signal(SIGINT, handler)

# Issues
# Client sometimes sends two JSON objects lumped together somehow
#
# Next Steps
# Add features to Robot class to simulate sensors and movement -> new data
#
