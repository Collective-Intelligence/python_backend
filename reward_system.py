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

# Make sure to add vests to steem equation
# for looking through all votes assumes same memo account


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
    print(post_list)


    for reward in reward_list:
        for post in post_list:

            try:
                post[2] = json.loads(post[2])
            except Exception as e:

                pass
            if post[2]["post_link"] == "@"+reward[1]["comment_author"] +"/" + reward[1]["comment_permlink"]:
                print(2)
                for vote in post[2]["vote-list"]:
                    print(1)
                    account = interpret.get_account_info(vote[0])
                    if account != None and account != []: # checks that its an actual account, for testing
                        # checks through all votes made by the account
                        # The vote is added to the account only after it is added to the reward total
                        already_voted = False


                        # goes through every vote made by the account to see if the saved position of the post-memo is the same as where it was found
                        # if no matching vote is found, a vote is added and rewards are adjusted
                        for account_vote in account[2]["vote"]:
                            if already_voted:
                                break

                            if post[0] == account_vote[0]:

                                already_voted = True
                            pass

                        for post_link in account[2]["vote-link"]:
                            if already_voted:
                                break
                            post_link = interpret.vote_link_find(post_link[0],post_link[1],sending_account,node)
                            print(post_link)
                            for post_vote in json.loads(post_link[0][2])["vote"]:
                                if already_voted:
                                    break
                                if post[0] == post_vote[0]:
                                    already_voted = True
                            print("end")

                        if not already_voted:
                            print("not already voted")
                            return
                            steem_value = steem.converter.Converter().vests_to_sp(float((reward[1]["reward"].split(" VESTS")[0])))/ len(post[2]["vote-list"]) # YOU CANT MAKE IT FucKING EASY CAN YOU
                            print(steem_value)
                            print(1111)
                            interpret.update_account(account[2]["account"], sending_account, memo_account,
                                                     [["vote",[post[0],memo_account]],["gp",account[2]["gp"] + steem_value * account[2]["steem-gp-ratio"]],
                                                      ["steem-owed",account[2]["steem-owed"] + steem_value * (1-account[2]["steem-gp-ratio"])]], active_key,node)
                        else:
                            print("already voted")

    return


    pass


def payout_rewards(sending_account,memo_account,active_key,node):
    pass



curation_rewards("anarchyhasnogods","space-pictures","active_key",24 * 60 * 60 * 2,"wss://steemd-int.steemit.com")
#for i in range(10):
 #   interpret.start_account(str(i),"","space-pictures","anarchyhasnogods")
