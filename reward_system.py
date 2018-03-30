from websocket import create_connection
from steem import Steem
import steem
import time
import random
import math

from memo_saving import interpret
from memo_saving import main
import json


# Update account with vote only after it was added to the reward total, which means removing it from the post holder
# this allows us to go through and check if it was already added, and if not add it
#                             interpret.update_account(ii[0], self.sending_account, self.memo_account, [["vote",[memo_pos,self.memo_account]]],self.key,iii)

def daily_reward_set(sending_account,memo_account,active_key, time_period,node):
    curation_rewards(sending_account,memo_account,active_key,time_period,node)
    payout_rewards(sending_account,memo_account,active_key,node)


def curation_rewards(sending_account,memo_account,active_key,time_period,node):

    reward_list = interpret.get_all_votes(time_period,sending_account,memo_account,node)
    print(reward_list)

    for i in reward_list:
        print(i)
    return

    for i in all_votes: # looks through all posts
        #print(json.loads(i[2])["vote-list"]) # gets list of votes from all posts
        print("999")
        curation_reward = interpret.check_if_curation_reward()

        if curation_reward:



            for ii in json.loads(i[2])["vote-list"]: # get individual votes
                if ii[1] == 1: # checks if the vote is positive
                    account = interpret.get_account_info(ii[0],sending_account,memo_account,node=node)
                    if account != None:
                        print(account)
                        vote_in = False
                        for vote in account["vote"]:
                            if vote_in:
                                break
                        # checks if vote is in this
                            if vote == ii:
                                vote_in = True

                        for vote_link in account["vote-link"]:
                            X = 1 # all votes in vote-link
                            if vote_in:
                                break
                        # get vote link
                            for vote_in_link in X:
                                if vote_in:
                                    break
                            # same thing as for vote in account[vote]
                                pass
                        if not vote_in:
                        # This updates account
                            pass

                #print(ii)
    pass


def payout_rewards(sending_account,memo_account,active_key,node):
    pass



curation_rewards("anarchyhasnogods","space-pictures","key",24 * 60 * 60 * 2,"wss://steemd-int.steemit.com")