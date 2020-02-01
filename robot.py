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
        self.manual_control = True
        self.auto_turn_chance = 0.1
        self.auto_turn_amount = 15
        self.auto_move_amount = 10
        self.auto_col_turn_max = 90
        self.communicator = Comm(12345, 12346)
        self.start()
        
    def start(self):
        while True:
            while self.communicator.has_read_data():
                data = self.communicator.read() # cmd will be a JSON object from the controller.
                cmd = json.loads(data)
                self.process(cmd)
                
            if not self.manual_control:
                self.auto()
                
            self.communicator.send(self.get_state_string())
            time.sleep(1)
            
    # cmd is a JSON string.
    def process(self, cmd):
        print("Processing {0}".format(cmd))
        self.move(int(cmd["move"])) # Read move amount from json
        self.turn(int(cmd["turn"])) # Read turn amount from json
        self.manual_control = cmd["ctrl"] == "manual"
        if cmd["ctrl"] == "auto": print("Setting autonomous control")
    
    # Move the robot around autonomously
    def auto(self):
        if random.random() < self.auto_turn_chance:
            dir = 1 if random.randrange(2) == 1 else -1 # + left, - right
            self.turn(self.auto_turn_amount * dir)
        self.move(self.auto_move_amount)
        # Keep reversing and turning until the robot is free
        while self.detect_collision():
            self.move(-self.auto_move_amount)
            self.turn(random.randrange(self.auto_col_turn_max))
            
    def detect_collision(self):
        b = self.x < 0 or self.x > 100 or self.y < 0 or self.y > 100
        if b:
            print("Collision Detected!")
            print("Collision Detected!")
            print("Collision Detected!")
        return b
    
    def move(self, amount):
        radHeading = self.heading * math.pi / 180
        self.x += amount * math.cos(radHeading)
        self.y += amount * math.sin(radHeading)
        
        weeds = random.randrange(5)
        self.weed_volume += weeds
        print("Robot collected {0}".format(weeds))
        
    def turn(self, amount):
        self.heading += amount
        self.heading %= 360
        
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

robot = Robot(50, 50, 0)
        
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
