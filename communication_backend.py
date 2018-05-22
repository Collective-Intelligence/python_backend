from websocket import create_connection
from steem import Steem
import steem
import time
import random
import math
import socket
from memo_saving import interpret
from memo_saving import main
import json
import steem
import requests
import json
import time
import datetime
from websocket import create_connection
from steem import Steem
import json
import os
from smtplib import SMTP as SMTP
import random
from multiprocessing import Process
import threading

# Will spawn threads for I/O with user
# Will use processes for blockchain related tasks



# The main class is the basis for the communication within the different areas of the backend.
# Multiple mains can run in different processes. Users can only see ongoing systems within their own main
# When a new system is requested by a user the main will hold it, when something is joined the session can be moved if needed

class Main():

    def __init__(self,node,active_key):

        self.sending_account = "co-in"
        self.memo_account = "co-in-memo"
        self.user_sessions = {}
        self.curation_sessions = {}
        #{tag:{"TCP_IP":ip,"TPC_PORT":port,"BUFFER_SIZE":buffer_size}}
        #uses ports from 37000-38000

        self.steem_node = node
        self.active_key = active_key
        self.info_out = []
        self.json_return_list = []

        self.locks = {"user-sessions":threading.Lock(),"curation_sessions":threading.Lock(),"input-info":threading.Lock(),"return_list":threading.Lock()}

        self.TCP_IP = '127.0.0.1'
        self.TCP_PORT = 5005
        print(self.TCP_PORT)
        self.BUFFER_SIZE = 1024


        # this brings it to about 20 posts per curation system, when it is full
        # Force user to spend at least 3-5 min per post to keep votes lower
        self.posts_per_user_ratio = 1/5.0
        self.users_per_curation_system = 100


        thread = threading.Thread(target=self.communication_loop)
        thread.start()



        # {"Session":{"class":class,"new_input":[[user1/system1,input1],[user2/system2,input2]], "lock":lock}}
    def communication_loop(self):
        # waits for internal socket connections (from celery in the flask_app sections)
        # takes the json sent, and then makes a new thread to process it
        # also processes jsons sent to get status data of tasks, which is blocking
        TCP_IP = self.TCP_IP
        TCP_PORT = 5005
        BUFFER_SIZE = self.BUFFER_SIZE
        while True:
            try:
                num = 1
                # creates re-usable socket and listens until connection is made.

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print(TCP_PORT)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)
                s.bind((TCP_IP, TCP_PORT))
                s.listen(0)
                while True:
                    num+= 1
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
                                if json.loads(data)["action"] == "return_json":
                                    with self.locks["return_list"]:
                                        for i in range(len(self.info_out)):

                                            if self.info_out[i][0]["idnum"] == json.loads(data)["idnum"]:
                                                sent = True
                                                conn.send(json.dumps(self.info_out[i][0]).encode())
                                            elif not time.time()-self.info_out[i][2] > 600:
                                                new_list.append(self.info_out[i])
                                        self.info_out = new_list
                                        if not sent:
                                            conn.send("404".encode())

                                else:
                                    thread = threading.Thread(target=self.read_json, args=([data, id_num]))
                                    thread.start()
                                    conn.send(json.dumps({"idnum":id_num}).encode())

                            except Exception as e:
                                print(e)
                                conn.send(json.dumps({"success":False, "error":-1}).encode())

                        except Exception as e:
                            print(e)
                            pass

                        conn.close()


                        # creates thread to do stuff with inputs


            except Exception as e:
                print(e)
                pass






    def read_json(self,json_object,idnum):
        print(json_object)
        # takes the json and id num and does actions based on what it contains
        # then creates a status memo based on the id and how the task went.

        json_object = json.loads(json_object)
        user_info = {"steem-account":json_object["steem-name"]}
        json_object["idnum"] = idnum

        if json_object["action"] == "create_session":
            if self.verify(json_object["steem-name"],json_object["key"]):
                self.create_session(user_info)
                self.return_json({"success":True,"action":"session created", "idnum":json_object["idnum"]},user_info)

            else:
                self.return_json({"success":False,"error":1,"idnum":json_object["idnum"]},user_info) # Session could not be created

        elif json_object["action"]["type"] == "account":
            with self.locks["user-sessions"]:
                # Checks if session exists and key is correct. If not, it returns an error
                try:

                    self.user_sessions[json_object["steem-name"]]
                    if self.verify_key(json_object["steem-name"],json_object["key"]):
                        json_object["action"]["idnum"] = json_object["idnum"]
                        self.user_sessions[json_object["steem-name"]]["inputs"].append(json_object["action"])
                        print("xxxxxxxxxx",self.user_sessions)
                    else:
                        self.return_json({"success": False, "error":3,"idnum":json_object["idnum"]},user_info) # The key is incorrect
                except Exception as e:
                    print(e)
                    print(100)

                    self.return_json({"success": False, "error":2,"idnum":json_object["idnum"]},user_info) # Session does not exist












    def create_session(self,user_info):
        # Creates session once users key has been verified.

        # Each session runs on a different thread.
        with self.locks["user-sessions"]:
            self.user_sessions[user_info["steem-account"]] = \
                {"user-info":user_info,"session":Session(user_info, self.locks,self, self.steem_node),"inputs":[]}

        print(self.user_sessions)

    def verify(self,name,key):

        # Verifies that the user exists, and does not already have a session

        # This checks if the session exists, if it does not it continues
        with self.locks["user-sessions"]:
            try:
                self.user_sessions[name]
                return False
            except Exception as e:
                print(e)
                pass
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


    def return_json(self,json,user_info):
        with self.locks["return_list"]:

            self.info_out.append([json, user_info,time.time()])

        pass

# Each session runs on their own thread (through main_loop), is able to communicate with everything within the main class
class Session:
    def __init__(self, user_info, locks, main,steem_node):
        self.main = main
        self.user_info = user_info # {"steem-account":str}
        self.steem_node = steem_node
        self.locks = locks
        self.vote_lock = threading.Lock()
        self.time_of_last_vote = 0

        self.token_prices = {"token-upvote-perm":0.5,"ad-token-perm":0.75}
        thread = threading.Thread(target=self.main_loop)
        thread.start()



    def main_loop(self):
        time_since_last_communication = 0
        sleep_time = 2
        print(8)
        while True:
            with self.locks["user-sessions"]:
                input_thing = self.main.user_sessions[self.user_info["steem-account"]]["inputs"]
            while len(input_thing) > 0:
                self.read_json(input_thing.pop())
                time_since_last_communication = 0
            time.sleep(sleep_time)
            time_since_last_communication += sleep_time

            if time_since_last_communication > 1000:
                pass
                # END COMMUNICATION, REMOVE CLASS OBJECT

        # This is the hub of communication between the client and user, reads jsons as they come in

        pass

    def read_json(self,info):
        # Takes a json and determines if it is valid if it is what to do.
        # If it is valid it calls the correct function
        print(24)
        if info["action_type"] == "make_purchase":
            print(25)
            try:
                print(12)
                if info["amount"] > 0:
                    self.make_purchase(info["token_type"],info["amount"])
                    self.return_json({"success": True, "action":"purchase_tokens","idnum":info["idnum"]})
                    print(26)
                else:

                    self.return_json({"success": False, "error": -20,"idnum":info["idnum"]})  # can only buy tokens

            except :
                self.return_json({"success": False, "error":10,"idnum":info["idnum"]}) # function doesnt work




        pass

    def return_json(self,json):
        # This takes information returned and creates a json to send back out of it.
        self.main.return_json(json,self.user_info)
        pass


    def make_purchase(self,token,amount):
        # This takes GP the user has and buys a Token from it.
        try:
            account = interpret.get_account_info(self.user_info["steem-account"], self.main.sending_account, self.main.memo_account,self.steem_node)
            print(27)
            # Checks if the account has enough GP to buy the tokens, if it does update the account with the new amount
            if account[2]["gp"] > self.token_prices[token] * amount:
                print(28)
                interpret.update_account(self.user_info["steem-account"],self.main.sending_account,self.main.memo_account,
                                         [["gp", account[2]["gp"] - self.token_prices[token] * amount], [token, account[2][token] + amount]],self.main.active_key,self.main.steem_node)

            else:
                print(29)
            #elif account[2]["gp"] + account[2]["steem-owed"] > self.token_prices[token] * amount:
             #   interpret.update_account(self.user_info["steem-account"])
            print(account)
            return account
        except Exception as e:
            print(e)
            return False





main = Main("wss://steemd-int.steemit.com","active_key")
user = {"steem-account":"anarchyhasnogods"}
#main.create_session({"steem-account":"anarchyhasnogods"})
#main.user_sessions["anarchyhasnogods"]["session"].make_purchase("ad-token-perm",2)


print("end")
