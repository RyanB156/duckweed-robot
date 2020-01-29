import socket
from signal import signal, SIGINT
from sys import exit
import time
import threading

s1 = socket.socket()
s2 = socket.socket()

rport = 12345
sport = 12346

s1.connect(('127.0.0.1', rport))
print("socket1 connected to {0}".format(rport))
s2.bind(('', sport))
print("socket1 bound to {0}".format(sport))
s2.listen(5)

def handler(signal_received, frame):
    print("CTRL-C detected")
    s1.close()
    s2.close()
    exit(0)

signal(SIGINT, handler)

def recv():
    while True:
        print(s1.recv(1024))
        
        
def send():
    while True:
        c, addr = s2.accept()
        print("got connection from {0}".format(addr))
        
        while True:
            userIn = input("Give command to robot: ")
            for cmd in userIn:
                move = "0"
                turn = "0"
                
                if cmd == 'w': move = "5"
                elif cmd == 's': move = "-5"
                elif cmd == 'd': turn = "-5"
                elif cmd == 'a': turn = "5"
                jsonOut = "{\"move\":\"" + move + "\", \"turn\":\"" + turn + "\"}"
                print(jsonOut)
                sendlength = c.send(jsonOut.encode()) # Client sends time to server
        c.close()
        
sender = threading.Thread(target=send, args=())
receiver = threading.Thread(target=recv, args=())
sender.start()
receiver.start()

