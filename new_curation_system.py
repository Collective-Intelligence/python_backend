from websocket import create_connection
from steem import Steem
import threading
import steem
import time
import random
import math
import socket

from memo_saving import interpret
from memo_saving import main
import json

class Main:
    def __init__(self, max_time,max_votes, sending_account, key, memo_account,nodes,posting_key, vote_threshold):
        self.vote_threshold = vote_threshold # min vote ratio for a vote
        self.average_post = interpret.get_vote_amount(86400)
        self.max_votes = max_votes
        print("VOTE AMOUNT")
        print(self.average_post)
        self.posting_key = posting_key
        self.user_actions = {}



        self.locks = {"return_list":threading.Lock(), "post-holder":threading.Lock(), "user_actions":threading.Lock()}
        # [average post, time period]
        # for average vote calculation, uses average of 10 full 100 % votes(1000) and devides it by average (voted on) posts
        # Max time is seconds
        self.max_time = max_time
        self.sending_account = sending_account
        self.key = key
        self.memo_account = memo_account
        self.votes_finished = False
        self.nodes = nodes
        self.account_info = {} # keeps list of recent account interactions, to help with abuse
        self.ratio_num = 0.75
        self.TCP_IP = '127.0.0.1'
        self.BUFFER_SIZE = 1024
        self.info_out = []
        self.TCP_PORT = 5006


        self.post_holders = {}



        print("DONE")
        thread = threading.Thread(target=self.communication_loop)
        thread.start()

    def user_action_loop(self):
        pass

    def communication_loop(self):
        # waits for internal socket connections (from celery in the flask_app sections)
        # takes the json sent, and then makes a new thread to process it
        # also processes jsons sent to get status data of tasks, which is blocking
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
                                if json.loads(data)["action"] == "return_json":
                                    with self.locks["return_list"]:
                                        for i in range(len(self.info_out)):

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
                                print(e)
                                conn.send(json.dumps({"success": False, "error": -1}).encode())

                        except Exception as e:
                            print(e)
                            pass

                        conn.close()


                        # creates thread to do stuff with inputs


            except Exception as e:
                print(e)
                pass

    def check_account_action(self, info):
        # checks if a user has made an action recently, if it is not in the system makes an entry
        # if the user has not made an action recently it is updated
        with self.locks["user_actions"]:
            print(self.account_info)
            try:
                self.account_info[info["steem-name"]]
            except:

                self.account_info[info["steem-name"]] = {"steem-name":info["steem-name"], "time":time.time()}
                return True

        try: # easy way to make it check through all of them every so often to stop it from getting too big
            1/random.randrange(100)
        except:
            for i in self.account_info:
                if self.account_info[i]["time"] - time.time() > 60 * 60:
                    self.account_info.pop(i, None)
        if self.account_info[info["steem-name"]]["time"] -time.time() > 2.5 * 60:
            self.account_info[info["steem-name"]]["time"] = time.time()
            return True
        else:

            return False

    def read_json(self,info,idnum):
        print("READ JSON", info)
        users_that_can_create = ["anarchyhasnogods","co-in"]
        info = json.loads(info)
        info["idnum"] = idnum

        if info["action"]["type"] == "add_post":
            try:
                if self.verify_key(info["steem-name"],info["key"]):
                    if self.check_account_action(info):



                        with self.locks["post-holder"]:

                            self.post_holders[info["action"]["tag"]].add_post(info["action"]["post-link"],info["steem-name"])

                        self.return_json({"success": True, "idnum": info["idnum"]}, idnum)
                    else:
                        self.return_json({"success": False, "error": 3, "idnum": info["idnum"]}, idnum)
                else:
                    self.return_json({"success": False, "error": 2, "idnum": info["idnum"]}, idnum)



            except:
                self.return_json({"success": False, "error": 1,"idnum":info["idnum"]},idnum)
        elif info["action"]["type"] == "create_session":


            try:
                print(-1)
                if not(info["steem-name"] in users_that_can_create and self.verify_key(info["steem-name"],info["key"])):

                    self.return_json({"success": False, "error": -20,"idnum":info["idnum"]},idnum)
                    print("HERE")

                print(0)
                with self.locks["post-holder"]:
                    print("HERE", info)
                    print(info["action"])
                    print(info["action"]["tag"])


                    self.post_holders[info["action"]["tag"]] = PostHolder(self)
                    self.return_json({"success": True,"action":info["action"]["type"], "idnum": info["idnum"]}, idnum)
            except Exception as e:
                print(e)
                print("here")
                self.return_json({"success": False, "error": 20, "idnum": info["idnum"]}, idnum)

        elif info["action"]["type"] == "session_list":
            try:
                print(self.post_holders)
                with self.locks["post-holder"]:
                    post_holder_list = []

                    for i in self.post_holders:
                        post_holder_list.append([i,len(self.post_holders[i].post_list)])
                    self.return_json({"post_holders":post_holder_list,"success":True,"idnum":idnum},idnum)
            except:
                self.return_json({"success": False, "error": 0, "idnum": info["idnum"]}, idnum)
        elif info["action"]["type"] == "get_post":
            try:
                with self.locks["post-holder"]:
                    post=self.post_holders[info["action"]["tag"]].get_random()[0]
                self.return_json({"success": True,"post":post, "idnum": info["idnum"]}, idnum)



            except:
                self.return_json({"success": False, "error": 10, "idnum": info["idnum"]}, idnum)

    def return_json(self,json,user_info):
        with self.locks["return_list"]:

            self.info_out.append([json, user_info,time.time()])









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


#----------------------------------------


class PostHolder:

    def __init__(self,main):
        print("THIS")
        self.main = main
        self.post_list = []
        self.lock = threading.Lock()

        self.vote_threshold = main.vote_threshold  # min vote ratio for a vote
        self.average_post = self.main.average_post
        self.max_votes = self.main.max_votes

        self.posting_key = self.main.posting_key

        # [average post, time period]
        # for average vote calculation, uses average of 10 full 100 % votes(1000) and devides it by average (voted on) posts
        # Max time is seconds
        self.max_time = main.max_time
        self.sending_account = main.sending_account
        self.key = main.key
        self.memo_account = main.memo_account
        self.nodes = main.nodes
        self.ratio_num = main.ratio_num
        self.TCP_IP = main.TCP_IP
        self.TCP_PORT = main.TCP_PORT
        self.BUFFER_SIZE = main.BUFFER_SIZE
        print("ENDTHING")



    def add_post(self, post_link, submission_author):
        print("ADDPOST")
        #https://steemit.com/politics/@anarchyhasnogods/a-communist-definition-of-property
        # example post link
        new_link = post_link.split("@")
        perm_link = new_link[1].split("/") # brings it to ["author","permlink"]

        # post_list = [[postname, submission author, vote list, advertisement_total]]
        print("ADDPOST1")

        # gets account info for reward calculation
        account_info_post = interpret.get_account_info(perm_link[1])
        print("ADDPOST2")
        if account_info_post != None:
            account_info_post = account_info_post[2]
            ad_tokens = int(account_info_post["ad-token-perm"])  # + int(account_info_post["ad-token-temp"])
        else:
            ad_tokens = 0
        # Gets info on post author
        print("ADDPOST3")

        print("ADDPOST4")
        # uses add tokens to calculate visibility within system, and save information needed for later.
        self.post_list.append([post_link, submission_author, [], 10 + int(math.sqrt(ad_tokens)), time.time(), perm_link])
        print("ADDPOST5 ")
        print(self.post_list)
        self.set_random()



    def set_random(self):
        # takes list of all posts produced earlier and shuffles them visibility is based on amount of post in list
        # the amount in the list is based on the number assigned earlier
        self.random_posts = []
        for i in self.post_list:
            for ii in range(i[3]):
                self.random_posts.append(i)
        random.shuffle(self.random_posts)

    def get_random(self):
        # finds the next post in the random order and removes it
        # when it runs out it just creates the list again
        # this forces the posts to be seen roughly the same amount of times as their chance
        try:
            if len(self.random_posts) == 0:
                self.set_random()
            return self.random_posts.pop(0)
        except AttributeError:
            self.set_random()
            return self.get_random()

    def add_vote(self, vote, post):
        # vote = [voter, vote]
        # vote is either -1, 0 or +1
        # -1 = plag, 0 = ignore, +1 = vote for
        # goes through every post and checks if it is the correct one, then every voter to see if it has been voted on already
        #print(vote,post)
        already_voted = False
        for i in self.post_list:
            if post[0] == i[0]:
                for ii in i[2]:
                    if ii[0] == vote[0]:
                        already_voted = True  # so that it changes it instead of adding a new vote onto the end
                        ii[1] = vote[1]
                        break
                if not already_voted:
                    i[2].append(vote)
                else:
                    break



    def make_vote(self, ratio, post_link):
        # takes ratio and post link and calculates the vote on the post, and returns it for use in the post memo
        if ratio < self.vote_threshold:
            return 0
        if self.account_info[post_link] != None:
            upvote_tokens = self.account_info[post_link]["token-upvote-perm"] #+ self.account_info[post_link]["token-upvote-temp"]
        else:
            upvote_tokens = 0
        print("UPVOTE TOKENS", upvote_tokens)

        equation = self.average_post[0] * (math.sqrt(upvote_tokens)/25 + 1) * (ratio/self.average_post[1])
        if equation > 100:
            equation = 100
        elif equation < 0.1:
            return 0
        for i in self.nodes:
            try:
                steem = Steem(node=i, keys=self.posting_key)
                print()
                steem.vote(post_link, equation, account=self.sending_account)
                return equation


            except Exception as e:
                print("exception")
                print(e)
                pass
        return 0
    def post_check_loop(self):
        pass

    def finish_post_set(self,post):

        already_vote = False
        for ii in self.nodes:

            s = Steem(node=ii)

            search_id =  i[0]
            print(search_id)
            search_id = search_id.split("/")
            print("HERE")
            print(search_id)
            search_id2 = search_id[0].split("@", 1)
            vote_list = s.get_active_votes(search_id2[1], search_id[1])

            for iii in vote_list:

                if iii["voter"] == self.sending_account:
                    already_vote = True
                    print("ALREADY VOTED")
                    break
        if not already_vote:

            votes = 0
            for vote in i[2]:
                if vote[1] == 1:
                    in_list = False
                    for ii in account_update_list:
                        if ii[0] == vote[0]:
                            in_list = True
                            ii[1].append(i[0])
                            break
                    votes += 1

            # Make post memo, this sits idle on chain until curation rewards are paid out.
            ratio = round(votes/len(i[2]),3)
            vote_size = round(self.make_vote(ratio,i[0]),2)
            interpret.vote_post(i[0], i[1], int(i[4]),i[2], votes / len(i[2]),  self.memo_account, self.sending_account, self.key,random.choice(self.nodes), vote_size)








thing = Main(100,1000000,"co-in","active_key","co-in-memo",["wss://rpc.buildteam.io"],"posting key", 0.5)
# ["post-link", "author","submitor acc]