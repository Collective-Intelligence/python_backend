from websocket import create_connection
from steem import Steem
import steem
import time
import random
import math

from memo_saving import interpret
from memo_saving import main
import json

# Make sure to add vests to steem equation



# Update account with vote only after it was added to the reward total, which means removing it from the post holder
# this allows us to go through and check if it was already added, and if not add it
#                             interpret.update_account(ii[0], self.sending_account, self.memo_account, [["vote",[memo_pos,self.memo_account]]],self.key,iii)

def daily_reward_set(sending_account,memo_account,active_key, time_period,node):
    curation_rewards(sending_account,memo_account,active_key,time_period,node)
    payout_rewards(sending_account,memo_account,active_key,node)


def curation_rewards(sending_account,memo_account,active_key,time_period,node):
    # gets full list of curation rewards, then full list of posts through our system
    # looks to see if post is in the post_list, if it is it adds some of the reward to every account involved
    reward_list = interpret.get_all_curation_rewards(time_period,sending_account,memo_account,node)
    print(reward_list)
    post_list = interpret.get_all_votes(time_period * 4,sending_account,memo_account,node)


    for reward in reward_list:
        for post in post_list:
            if post[1]["post-link"] == reward[1]["comment_author"] +"@" + reward[1]["comment_permlink"]:
                for vote in post["vote-list"]:
                    account = interpret.get_account_info(vote[0])
                    if account != None and account != []: # checks that its an actual account, for testing
                        # checks through all votes made by the account
                        # The vote is added to the account only after it is added to the reward total
                        already_voted = False
                        for account_vote in account[1]["votes"]:
                            if already_voted:
                                break
                            pass

                        for post_link in account[1]["post-link"]:
                            if already_voted:
                                break
                            pass
                        if not already_voted:
                            steem_value = None
                            interpret.update_account(account["account"], sending_account, memo_account,
                                                     [["vote",[post[0],memo_account]],["gp",account[1]["gp"] + steem_value * account[1]["steem-gp-ratio"]],
                                                      ["steem-owed",account[1]["steem-owed"] + steem_value * (1-account[1]["steem-gp-ratio"])]], active_key,node)

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