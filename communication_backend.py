from websocket import create_connection
from steem import Steem
import steem
import time
import random
import math

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
        self.steem_node = node
        self.active_key = active_key
        self.input_info = []
        self.json_return_list = []

        # {"Session":{"class":class,"new_input":[[user1/system1,input1],[user2/system2,input2]], "lock":lock}}

        self.locks = {"user-sessions":threading.Lock(),"curation_sessions":threading.Lock(),"input-info":threading.Lock(),"return_list":threading.Lock()}
        pass

    def communication_loop(self):

        json_list = []
        while True:

            json_list = input()
            try:
                print(json_list, type(json_list), len([json_list]))
                # creates thread to do stuff with inputs
                thread = threading.Thread(target=self.read_json, args=([json_list]))
                thread.start()
                print(1)
            except:
                #---------------------------------
                # UNDER CONSTRUCTION, create system for return JSON
                #---------------------------------
                with self.locks["return_list"]:
                    self.json_return_list.append()
                pass
            # Send return jsons


        pass

    def read_json(self,json_object):
        print(2)
        return_json = None
        json_object = json.loads(json_object)
        if json_object["action"] == "create_session":
            if self.verify(json_object["steem-name"],json_object["key"]):
                self.create_session({"steem-account":json_object["steem-name"]})
            else:
                return json.dumps({"success":False,"error":1}) # Session could not be created

        elif json_object["action"]["type"] == "account":
            print(9)
            with self.locks["user-sessions"]:
                print(20)
                # Checks if session exists and key is correct. If not, it returns an error
                try:
                    print(21)
                    self.user_sessions[json_object["steem-name"]]
                    if self.verify_key(json_object["steem-name"],json_object["key"]):
                        print(24)
                        self.user_sessions[json_object["steem-name"]]["inputs"].append(json_object["action"])
                        print("xxxxxxxxxx",self.user_sessions)
                    else:
                        return json.dumps({"success": False, "error":3}) # The key is incorrect
                except Exception as e:
                    print(e)
                    print(22)
                    print(self.user_sessions)
                    return json.dumps({"success": False, "error":2}) # Session does not exist

        print(21)
        print(json_object["action"])
    def curation_loop(self):
        # This holds all the curation sessions and waits for requests to do something with them
        pass

    def create_session(self,user_info):
        # Creates session once users key has been verified.

        # Each session runs on a different thread.
        print(7)
        with self.locks["user-sessions"]:
            self.user_sessions[user_info["steem-account"]] = \
                {"user-info":user_info,"session":Session(user_info, self.locks,self, self.steem_node),"inputs":[]}

        print(self.user_sessions)
        pass

    def verify(self,name,key):

        # Verifies that the user exists, and does not already have a session

        print(3)
        # This checks if the session exists, if it does not it continues
        with self.locks["user-sessions"]:
            try:
                self.user_sessions[name]
                print(6)
                return False
            except Exception as e:
                print(e)
                pass
        # Checks if the account exists, if the account does not exist in our system it checks if it really does exist
        # if the account does not exist on steem, ends, if it does exist it creates an account in our platform
        print(4)
        s = Steem(keys=key)
        if not interpret.get_account_info(name, self.sending_account, self.memo_account,self.steem_node) is None:
            # account does exist on our platform. Next checks if the key for the account is correct
            if not self.verify_key(name,key):
                print(6)
                return False
            print(5)
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

    def curation_loop(self):
        # Serves as the base for each curation system

        pass


# Each session runs on their own thread (through main_loop), is able to communicate with everything within the main class
class Session:
    def __init__(self, user_info, locks, main,steem_node):
        self.main = main
        self.user_info = user_info # {"steem-account":acc}
        self.steem_node = steem_node
        self.locks = locks
        self.curation_session = None # Key for the curation session they are in

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

    def read_json(self,json):
        # Takes a json and determines if it is valid if it is what to do.
        # If it is valid it calls the correct function
        print(24)
        if json["action_type"] == "make_purchase":
            print(25)
            try:
                print(12)
                if json["amount"] > 0:
                    self.make_purchase(json["token_type"],json["amount"])
                    print(26)
                else:

                    self.return_json({"success": False, "error": 20})  # can only buy tokens

            except:
                self.return_json({"success": False, "error":10}) # function doesnt work

        elif json["action_type"] == "get_curation_sessions":
            self.return_json(self.get_curation_sessions())
        pass

    def return_json(self):
        # This takes information returned and creates a json to send back out of it.
        pass
    def get_curation_sessions(self):
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

main.communication_loop()

print("end")
