from websocket import create_connection
from steem import Steem
import steem
import time
import random
import math

from memo_saving import interpret
from memo_saving import main
import json

class Post_holder:
    def __init__(self, max_posts, max_time, sending_account, key, memo_account,nodes,posting_key, vote_threshold):
        self.vote_threshold = vote_threshold # min vote ratio for a vote
        self.average_post = interpret.get_vote_amount(86400)

        print("VOTE AMOUNT")
        print(self.average_post)
        self.posting_key = posting_key
        # [average post, time period]
        # for average vote calculation, uses average of 10 full 100 % votes(1000) and devides it by average (voted on) posts
        # Max time is seconds
        self.max_posts = max_posts
        self.max_time = max_time
        self.post_list = []
        self.post_draw_list = []
        self.sending_account = sending_account
        self.key = key
        self.memo_account = memo_account
        self.votes_finished = False
        self.nodes = nodes
        self.account_info = {}
        self.ratio_num = 0.75


    def add_post(self, post_link, submission_author, post_author):
        # post_list = [[postname, submission author, vote list, advertisement_total]]

        # gets account info for reward calculation
        account_info_post = interpret.get_account_info(post_author)
        if account_info_post != None:
            account_info_post = account_info_post[2]
            ad_tokens = int(account_info_post["ad-token-perm"])  # + int(account_info_post["ad-token-temp"])
        else:
            ad_tokens = 0
        # Gets info on post author


        self.account_info[post_link] = account_info_post
        # uses add tokens to calculate visibility within system, and save information needed for later.
        self.post_list.append([post_link, submission_author, [], 10 + int(math.sqrt(ad_tokens)), time.time(), post_author])



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
                        already_voted = True #so that it changes it instead of adding a new vote onto the end
                        ii[1] = vote[1]
                        break
                if not already_voted:
                    i[2].append(vote)
                else:
                    break



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


    def finish_post_set(self):
        account_update_list = [] # calculates the total votes of each post
        for i in self.post_list:
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
                ratio = votes/len(i[2])
                vote_size = self.make_vote(ratio,i[0])
                interpret.vote_post(i[0], i[1], i[4],i[2], votes / len(i[2]),  self.memo_account, self.sending_account, self.key,random.choice(self.nodes), vote_size)


                self.votes_finished = True


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
#----------------------------------------

post_holder = Post_holder(100,1000000,"anarchyhasnogods","active_key","space-pictures",["wss://rpc.buildteam.io"],"posting key", 0.5)
# ["post-link", "author","submitor acc]
post_list = [["@comedy-central/check-this","0","comedy-central"]]

for i in post_list:
    post_holder.add_post(i[0], i[1],i[2])

print(post_holder.post_list)

post_list = []

for i in range(10):

    post_list.append(post_holder.get_random())
    pass


# is [0]
for i in range(len(post_list)):
    #print(i)
    post_holder.add_vote([str(i % 10) ,1],post_list[i])





print(post_holder.post_list)

post_holder.finish_post_set()

