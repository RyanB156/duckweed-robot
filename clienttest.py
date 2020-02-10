import json
import socket
from signal import signal, SIGINT
from sys import exit
import sys
import time
import threading

recv_socket = socket.socket()
send_socket = socket.socket()

rport = 12345
sport = 12346

display_map = False

def handler(signal_received, frame):
    print("CTRL-C detected")
    recv_socket.close()
    send_socket.close()
    exit(0)

signal(SIGINT, handler)

def recv():
    ctr = 0
    (rows, cols) = (11, 11)
    map = [[1 for i in range(cols)] for j in range(rows)]
    collecting = True
    
    if display_map:
        for a in range(rows):
            for b in range(cols):
                print(str(map[a][b]), end=" ")
            print()
    
    while True:
        i = recv_socket.recv(1024)
        print(i)
        data = i.decode('utf-8').strip('\x00')
        j = json.loads(data)
        if (int(j["weeds"]) >= 10000):
            collecting = False
            print("ALERT: Weed collector is full")
            
        if display_map:
            if collecting:
                x = int(float(j["position_x"]) / rows)
                y = int(float(j["position_y"]) / cols)
                print("x: {0}, y: {1}".format(x, y))
                map[x][y] = 0
            
            ctr += 1
            # Print map the robot has covered.
            if ctr >= 2:
                for a in range(rows):
                    for b in range(cols):
                        print(str(map[b][a]), end=" ")
                    print()
                ctr = 0
        
def send():
    while True:
        c, addr = send_socket.accept()
        print("got connection from {0}".format(addr))
        
        while True:
            userIn = input("Give command to robot: ")
            
            for cmd in userIn:
            
                if cmd == 'c' or cmd == 'm':
                    mode = "auto" if cmd == 'c' else "manual"
                    dict = {
                        "type": "mode_msg",
                        "mode": mode,
                    }
                else:
                    
                    move = "0"
                    turn = "0"
                    
                    if cmd == 'w': move = "5"
                    elif cmd == 's': move = "-5"
                    elif cmd == 'd': turn = "-5"
                    elif cmd == 'a': turn = "5"
                    
                    dict = { 
                    "type": "ctrl_msg",
                    "move": move,
                    "turn": turn,
                    }
                        
                s = "{"
                for key in dict:
                    s += "\"" + key + "\":\"" + str(dict[key]) + "\", "
                s = s[:-2]
                s += "}"
                
                print(s)
                sendlength = c.send(s.encode()) # Client sends time to server
                time.sleep(0.020)
        c.close()
        

if __name__ == "__main__":

    if len(sys.argv) == 2:
        recv_socket.connect((sys.argv[1], rport))
    else:
        print("Usage: python3 clienttest.py <IP address or \"localhost\">")
        sys.exit(1)
        
    print("socket1 connected to {0}".format(rport))
    send_socket.bind(('', sport))
    print("socket1 bound to {0}".format(sport))
    send_socket.listen(5)

    sender = threading.Thread(target=send, args=())
    receiver = threading.Thread(target=recv, args=())
    sender.start()
    receiver.start()
    

