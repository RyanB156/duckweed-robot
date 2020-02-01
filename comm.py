from queue import Queue
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