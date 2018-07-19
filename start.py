import os
from multiprocessing import Process
import json



def flask_run():
    os.system("python3 -m venv venv")
    os.system("source venv/bin/activate")
    os.system("export FLASK_APP=testing.py")
    os.system("sudo flask run")

#p = Process(target=flask_run, args=())
#p.start()

def main_run():
    os.system("python3 main.py")

p = Process(target=main_run, args=())
p.start()


import socket
import threading
import time
TCP_IP = '127.0.0.1'
TCP_PORT = 5001
BUFFER_SIZE = 1024

def connect_func():
    print("here")
    while True:
        try:
            MESSAGE = json.dumps({"action":{"type":"create_session_curation","tag":"TAG"},"key":"","steem-name":"anarchyhasnogods", "forward":"false"})

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((TCP_IP, TCP_PORT))
            s.send(MESSAGE.encode())
            data =""
            while True:
                new_data= s.recv(BUFFER_SIZE)
                new_data = new_data.decode()
                data += new_data
                if not data: break
                if not len(data) >0: break
                if not len(data) > BUFFER_SIZE: break
                #print(data)

            s.close()
            break
            time.sleep(1)
        except Exception as e:
            print(e)
            time.sleep(1)
connect_func()

#os.system("")
#os.system("")
#os.system("")





