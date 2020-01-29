import socket
from signal import signal, SIGINT
from sys import exit
import time
import threading

s1 = socket.socket()
s2 = socket.socket()
print("Socket successfully created")

sport = 12345
rport = 12346

s1.bind(('', sport))
print("socket1 bound to {0}".format(sport))

s1.listen(5)
print("socket is listening")

def handler(signal_received, frame):
    print("CTRL-C detected")
    s1.close()
    s2.close()
    exit(0)

signal(SIGINT, handler)

def send():
    while True:
        ctr = 0
        c, addr = s1.accept()
        print("got connection from {0}".format(addr))
        
        # Wait for connection to be established with s1. Then the client has also opened a socket to connect to.
        #s2.connect(('127.0.0.1', rport))
        receiver.start()
        print("socket2 connected to {0}".format(rport))
        
        while True:
            sendlength = c.send(str(ctr).encode())
            time.sleep(1)
            ctr += 1
        c.close()
        
def recv():
    s2.connect(('127.0.0.1', rport))
    while True:
        print(s2.recv(1024))
    
sender = threading.Thread(target=send, args=())
receiver = threading.Thread(target=recv, args=())
sender.start()
#receiver.start()
    
    
    