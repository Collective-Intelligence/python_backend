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
messages = [json.dumps({"action":{"type":"create_session_curation","tag":"general"},"key":"mykey","steem-name":"anarchyhasnogods", "forward":"false"})
            ,   json.dumps({"action":{"type":"create_session_curation","tag":"LGBT"},"key":"mykey","steem-name":"anarchyhasnogods", "forward":"false"})]


def connect_func(MESSAGE):
    print("here")
    while True:
        try:

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

for i in messages:

    connect_func(i)

#os.system("")
#os.system("")
#os.system("")





