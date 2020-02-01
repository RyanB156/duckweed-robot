import json
import math
from queue import Queue
import random
from signal import signal, SIGINT
import socket
from sys import exit
import time
import threading

class Comm:
    def __init__(self, send_port, recv_port):
        self.send_socket = socket.socket()
        self.recv_socket = socket.socket()
        self.conn = socket.socket()
        self.send_port = send_port
        self.recv_port = recv_port
        self.recv_thread = threading.Thread(target=self.receive, args=())
        self.read_queue = Queue()
        
        self.start_sender()
        
    def start_sender(self):
        self.send_socket.bind(('', self.send_port))
        print("socket1 bound to {0}".format(self.send_port))
        self.send_socket.listen(5)
        print("socket is listening")
        
        self.conn, addr = self.send_socket.accept() # Need a way to retry the connection if self.conn closes.
        print("got connection from {0}".format(addr))
        time.sleep(1)
        self.recv_thread.start()
        
    def send(self, data):
        self.conn.send(data.encode())
        
    # Threaded method to listen to data on recv_socket. Read any data to read_queue.
    def receive(self):
        while self.recv_socket.connect_ex(('127.0.0.1', self.recv_port)) != 0: # Try to connect until a connection is established.
            time.sleep(1)
        while True:
            i = self.recv_socket.recv(1024)
            if i:
                data = i.decode('utf-8').strip('\x00')
                self.read_queue.put(data)
                print("Adding {0} to read_queue".format(data))
            else:
                print("Connection closed in Comm.receive")
                break
                
    def has_read_data(self):
        return not self.read_queue.empty()
        
    def read(self):
        if not self.read_queue.empty():
            data = self.read_queue.get()
        else:
            data = ""
        print("Reading {0} from read_queue".format(data))
        return data
        
    def close(self):
        self.send_socket.close()
        self.recv_socket.close()
        self.conn.close()
        
#j = json.loads(data)
#state.move(int(j["move"])) # Read move amount from json
#state.turn(int(j["turn"])) # Read turn amount from json

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
