from websocket import create_connection
from steem import Steem
import steem
import time
import random
import math
from memo_saving import interpret
from memo_saving import main
import json
import reward_system
from flask import Flask
from multiprocessing import Process
import socket
import os
import threading
# This is the main class for the backend. This is the one that manages all of the systems
class Main():
    def __init__(self,max_ports,port_start,active_key,posting_key):
        self.steem_node = "wss://rpc.buildteam.io"
        self.active_key = active_key
        self.posting_key = posting_key
        self.TCP_IP = '127.0.0.1'
        self.BUFFER_SIZE = 1024
        self.info_out = []
        self.TCP_PORT = 5001
        self.sending_account = "co-in"
        self.memo_account = "co-in-memo"

        self.locks = {"curation_list":threading.Lock(),"user_session_list":threading.Lock()
            ,"open_ports":threading.Lock(), "return_list":threading.Lock(), "curation_info":threading.Lock()}
        self.user_sessions = [] #[{port:int,user_list[],last_activity:int,throughput:[time,actions]}
        self.curation_sessions = [] # [{port:int,tags:[],last_activity:int,held_posts:int} held posts may be overestimate at all times
        self.port_list = []
        self.curation_information_hold = []
        for i in range(max_ports):
            self.port_list.append(i + port_start)

        thread = threading.Thread(target=self.communication_loop)
        thread.start()

    def system_check(self):
        while True:
            open_ports = []
            new_curation_list = []
            time.sleep(60 * 10)
            with self.locks["curation_list"]:
                for i in self.curation_sessions:
                    for ii in i["tags"]:
                        if info["action"]["tag"] == ii:
                             if not json.loads(
                                self.send_communication(json.dumps(info), i["port"], self.TCP_IP, self.BUFFER_SIZE)):
                                open_ports.append(i["port"])
                             else:
                                 new_curation_list.append(i)
                self.curation_sessions = new_curation_list
            while self.locks["open_ports"]:
                for i in open_ports:
                    self.port_list.append(i)



    def communication_loop(self):
        TCP_IP = self.TCP_IP
        TCP_PORT = self.TCP_PORT
        BUFFER_SIZE = self.BUFFER_SIZE
        while True:
            try:
                num = 1
                # creates re-usable socket and listens until connection is made.

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print(TCP_PORT)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((TCP_IP, TCP_PORT))
                s.listen(0)
                while True:
                    num += 1
                    conn, addr = s.accept()
                    data = ""

                    if addr[0] == TCP_IP:
                        try:
                            # gives id for retrieval of status for tasks

                            id_num = random.randrange(1000000000000000000000000)

                            while True:
                                new_data = conn.recv(BUFFER_SIZE)
                                if not new_data: break
                                if not len(new_data) > 0: break
                                data += new_data.decode()
                                if not len(new_data) >= BUFFER_SIZE: break

                            try:
                                new_list = []
                                sent = False
                                #print(99)
                                #print(data)
                                if json.loads(data)["action"] == "return_json":
                                    with self.locks["return_list"]:
                                        #print(100)
                                        for i in range(len(self.info_out)):
                                         #   print(101)
                                            if self.info_out[i][0]["idnum"] == json.loads(data)["idnum"]:
                                                sent = True
                                                conn.send(json.dumps(self.info_out[i][0]).encode())
                                            elif not time.time() - self.info_out[i][2] > 600:
                                                new_list.append(self.info_out[i])
                                        self.info_out = new_list
                                        if not sent:
                                            conn.send("404".encode())

                                else:
                                    thread = threading.Thread(target=self.read_json, args=([data, id_num]))
                                    thread.start()
                                    conn.send(json.dumps({"idnum": id_num}).encode())

                            except Exception as e:
                                print("err 14")
                                print(e)
                                conn.send(json.dumps({"success": False, "error": -1}).encode())

                        except Exception as e:
                            print("err 13")
                            print(e)
                            pass

                        conn.close()


                        # creates thread to do stuff with inputs


            except Exception as e:
                print("err 12")
                print(e)
                pass

    def read_json(self,info,idnum):
        # self.return_json({"success": True, "idnum": info["idnum"]}, idnum)
        # TO ADD info["system"] = curation or user, info["forward"] true or false
        print("READ JSON", info)
        users_that_can_create = ["anarchyhasnogods","co-in"]
        info = json.loads(info)
        info["idnum"] = idnum

        if info["action"]["type"] == "get_curation_info":

            with self.locks["curation_info"]:
                if len(self.curation_information_hold) > 0:
                    self.return_json(
                        {"success": True, "idnum": info["idnum"], "info": self.curation_information_hold.pop()})
                else:
                    self.return_json(
                        {"success": False, "idnum": info["idnum"], "info": []})
        elif info["forward"] == "true":
            if info["system"] == "curation" and self.verify(info["steem-name"],info["key"]) and info["steem-name"] in users_that_can_create:
                with self.locks["curation_list"]:
                    for i in self.curation_sessions:
                        for ii in i["tags"]:
                            if info["action"]["tag"] == ii:
                                message = json.loads(self.send_communication(json.dumps(info),i["port"], self.TCP_IP,self.BUFFER_SIZE))
                                message["idnum"] = idnum
                                self.return_json(message)
            if info["system"] == "user":
                pass
        else:

            if info["action"]["type"] == "create_session_curation":
                with self.locks["open_ports"]:
                    port = self.port_list.pop()
                with self.locks["curation_info"]:
                    try:

                        p = Process(target=self.create_curation, args=())
                        p.start()
                        #self.create_curation_system(100, 1000000, "co-in", self.active_key, "co-in-memo", ["wss://rpc.buildteam.io"], self.posting_key, 0.5,port)
                        self.curation_information_hold.append(json.dumps([100, 1000000, "co-in", self.active_key, "co-in-memo", ["wss://rpc.buildteam.io"], self.posting_key, 0.5,port]))
                        time.sleep(30)


                        worked = True
                    except Exception as e:
                        print(e)
                        worked = False
                        self.return_json({"success": False,"error":10, "idnum": info["idnum"]})
                try_num = 0
                info["action"]["type"] = "create_session"
                while not self.send_communication(json.dumps(info), port, self.TCP_IP, self.BUFFER_SIZE):
                    if try_num > 5:
                        self.return_json({"success": False, "idnum": info["idnum"], "error":100})

                        break
                    try_num +=1
                    time.sleep(10)
                if not try_num > 5:
                    self.return_json({"success": True, "idnum": info["idnum"]})
                if worked:
                    with self.locks["curation_list"]:
                        self.curation_sessions.append({"port":port,"tags":[info["action"]["tag"]],"held_posts":0})
            elif info["action"]["type"] == "create_user_system":
                pass
            elif info["action"]["type"] == "session":
                tags = []
                with self.locks["curation_list"]:
                    for i in self.curation_sessions:
                        for ii in self.curation_sessions[i]["tags"]:
                            tags.append(ii)

                self.return_json({"success": True, "idnum": info["idnum"],"tag_list":tags})
    def create_curation(self):
        os.system("python3 new_curation_system.py")

        pass
    def verify(self,name,key):


        # Checks if the account exists, if the account does not exist in our system it checks if it really does exist
        # if the account does not exist on steem, ends, if it does exist it creates an account in our platform
        try:
            s = Steem(keys=key)
        except Exception as e:
            print("99")
            print(e)

            return False
        if not interpret.get_account_info(name, self.sending_account, self.memo_account,self.steem_node) is None:
            # account does exist on our platform. Next checks if the key for the account is correct
            if not self.verify_key(name,key):
                return False
            return True


        else:
            # checks if account exists on steem

            if not self.verify_key(name,key):
                return False
            interpret.start_account(name,self.active_key,self.memo_account,self.sending_account,self.steem_node)
        return True

        # verifies key

    def verify_key(self,name,key):
        s = Steem(keys=key)

        try:
            s.follow(self.sending_account, what=['blog'], account=name)
            return True
        except Exception as e:
            print(9)
            print(e)
            return False

    def send_communication(self, MESSAGE, TCP_PORT, TCP_IP, BUFFER_SIZE):
        time_out = 300

        return_object = False
        print("PORT NUMBER", TCP_PORT)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((TCP_IP, TCP_PORT ))
            s.send(MESSAGE.encode())
            data = ""
            while True:
                new_data = s.recv(BUFFER_SIZE)
                new_data = new_data.decode()
                data += new_data
                if not new_data: break
                if not len(new_data) > 0: break
                if not len(new_data) > BUFFER_SIZE: break
            id = json.loads(data)["idnum"]
            data = ""
            times = 0
            # waits until the task is done by the communication backend
            while not return_object or return_object == "404":
                data = ""
                times += 1
                if times > time_out:
                    return False
                time.sleep(1)
                MESSAGE = json.dumps({"action": "return_json", "idnum": id})
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((TCP_IP, TCP_PORT ))
                s.send(MESSAGE.encode())
                while True:
                    new_data = s.recv(BUFFER_SIZE)
                    new_data = new_data.decode()
                    data += new_data
                    if not new_data: break
                    if not len(new_data) > 0: break
                    if not len(new_data) > BUFFER_SIZE: break

                if data != "":
                    return_object = data


        except Exception as e:
            print("err 111")
            print(e)
            return False

            pass



        return return_object

    def return_json(self,json):
        with self.locks["return_list"]:

            self.info_out.append([json, None,time.time()])

    def update_loop(self):
        # Checks if systems need to be deleted
        pass

    def create_curation_system(self,max_time,max_votes, sending_account, key, memo_account,nodes,posting_key, vote_threshold,port):
        # This creates a curation session that can hold multiple tags
        #new_curation_system.create_system(max_time,max_votes, sending_account, key, memo_account,nodes,posting_key, vote_threshold,port)
        p = Process(target=new_curation_system.create_system, args=(max_time,max_votes, sending_account, key, memo_account,nodes,posting_key, vote_threshold,port))
        p.start()

    def delete_curation_session(self):
        # This deletes a curation session, based on activity, uses sys.exit()
        pass
    def create_user_system(self,node,active_key,port):
        # Creates a user system that can deal with multiple users at once
        pass

    def delete_user_session(self):
        # Deletes user systems based on activity, uses sys.exit()
        pass

    def get_all_curation_sessions(self):
        # Gets the tag and session of all curation sessions
        pass

    def get_all_user_sessions(self):
        # looks at all users logged in
        pass


thing = Main(1000,6000,"active_key","posting_key")