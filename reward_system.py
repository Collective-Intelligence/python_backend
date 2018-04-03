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
    post_list = interpret.get_all_votes(time_period * 5,sending_account,memo_account,node)
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


def payout_rewards(sending_account,memo_account,active_key,node, account_reward= 0.45, del_reward = 0.44, owners = 0.3):
    # only pays out accounts active in the last 30 days.

    total_steem_owed = 0.01
    group_level_total = 0
    steem_levels = [0,0,0] # accounts with more than 1 steem owed, 0.1 steem and 0.01 steem
    # This is used to determine how much is paid out, if there isnt enough to pay everyone 0.01 they may not be paid in that session
    account_list = interpret.get_all_accounts(sending_account,memo_account,node)
    total_del = 0
    # pulls all accounts and calculates the total amount of steem owed to them
    for account in account_list:
        try:
            account[2] = json.loads(account[2])
            steem_owed = account[2]["steem-owed"]

            total_steem_owed += steem_owed
            if steem_owed > 1:
                steem_levels = [steem_levels[0] + 1, steem_levels[1] + 1, steem_levels[2] + 1]
            elif steem_owed > 0.1:
                steem_levels = [steem_levels[0], steem_levels[1] + 1, steem_levels[2] + 1]
            elif steem_owed > 0.01:
                steem_levels = [steem_levels[0], steem_levels[1], steem_levels[2] + 1]

            s = Steem(node=node)

            #account_del = float(s.get_vesting_delegations(account[2]["account"],sending_account,10000)["vesting_shares"].split(" VESTS")[0])
            thing = s.get_vesting_delegations(account[2]["account"],sending_account,1000)
            account_del = 0
            for i in thing:
                if i["delegatee"] == sending_account:
                    account_del += float(i["vesting_shares"].split(" VESTS")[0])
                    print(i)

            owner_total = 0
            for i in account[2]["groups"]:
                print(i)
                if i[0] == "CI" and i[1] == 5:
                    owner_total += 1


            #print(account_del)
            account.append(account_del)
            account.append(owner_total)
            print(account_del)
            group_level_total += owner_total
            total_del += account_del
        except Exception as e:
            print(e)
            pass




    # DO vesting delegation before payout to accounts, send new memo so it stays current and can be found.
    # If they have delegation and curation it will send newer memo which is updated (this one just keeps current, no actual change)
    print("here")
    s = Steem(node=node)
    total_steem = float(s.get_account(sending_account)["balance"].split(" STEEM")[0])
    print(total_steem)


    # Measures if we are able to get every user at least 0.01 of their reward
    # if not no rewards are paid out, to save enough levels to pay everyone
    if total_steem * account_reward /0.05 < steem_levels[2]:
        print("RETURN", total_steem, account_reward, steem_levels[2])
        return
    reward_per_steem_owed = (total_steem * account_reward) / total_steem_owed
    for account in account_list:
        print("This")

        amount = reward_per_steem_owed * account[2]["steem-owed"]
        if amount > account[2]["steem-owed"]:
            amount = account[2]["steem-owed"]
        amount += + del_reward * total_steem * account_del / total_del + account[5] * total_steem * owners/ group_level_total
        print(reward_per_steem_owed,account[2]["steem-owed"], del_reward * total_steem * account[4] / total_del)

        amount = round(amount,2)
        print("here",amount)
        if amount > 0.01:
            interpret.pay_account(amount,sending_account,memo_account,node,active_key,account[2])



#curation_rewards("anarchyhasnogods","space-pictures","active_key",24 * 60 * 60 * 2,"wss://steemd-int.steemit.com")


#for i in range(10):
 #   interpret.start_account(str(i),"","space-pictures","anarchyhasnogods")
