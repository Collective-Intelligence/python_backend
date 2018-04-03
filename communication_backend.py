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

# Will spawn threads for I/O with user
# Will use processes for blockchain related tasks



# The main class is the basis for the communication within the different areas of the backend.
# Multiple mains can run in different processes. Users can only see ongoing systems within their own main
# When a new system is requested by a user the main will hold it, when something is joined the session can be moved if needed

class Main():

    def __init__(self):
        self.user_sessions = {}
        self.curation_sessions = {}
        # {"Session":{"class":class,"new_input":[[user1/system1,input1],[user2/system2,input2]], "lock":lock}}
        
        self.locks = {"user_sessions":None,"curation_sessions":None}
        pass

    def session_loop(self):
        # This waits for json requests to start sessions
        pass

    def curation_loop(self):
        # This holds all the curation sessions and waits for requests to do something with them
        pass

    def create_session(self):
        # Creates session once users key has been verified.

        # Each session runs on a different thread.
        pass

    def verify(self):
        # Verifies that the user exists, and does not already have a session
        pass

    def curation_loop(self):
        # Serves as the base for each curation system

        pass


# Each session runs on their own thread (through main_loop), is able to communicate with everything within the main class
class Session:
    def __init__(self, user, locks):
        self.curation_session = None # Key for the curation session they are in

        pass

    def main_loop(self):
        # This is the hub of communication between the client and user, reads jsons as they come in

        pass

    def read_json(self):
        # Takes a json and determines if it is valid if it is what to do.
        # If it is valid it calls the correct function
        pass

    def return_json(self):
        # This takes information returned and creates a json to send back out of it.
        pass

    def make_purchase(self):
        # This takes GP the user has and buys a Token from it.
        pass

    def create_account(self):
        # If the user does not have an account they must be created
        pass

