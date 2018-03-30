# This will be a function-based helper for storing information in transactions on the steem blockchain
# This will not try to interperet the data
from websocket import create_connection
from steem import Steem
import time
import json

def retrieve(keyword=[], account="anarchyhasnogods",sent_to="randowhale", position=-1, recent = 1, step = 10000, minblock = -1, node="wss://steemd.privex.io", not_all_accounts = True, type_thing="transfer"):
    # minblock is blocks before current block
    # account is the account that sent the memo
    # sent-to is account that it was sent to
    # keyword is what it looks for in the json ["type","account"] would bring back memos with the type account
    # -1 position means the latest, anything else means a specific memo where the position is known
    # step means how many actions it grabs at once
    # notallaccounts is wether or not it looks at every account


    node_connection = create_connection(node)
    s = Steem(node=node_connection)
    memo_list = []
    if position > -1:
        # This returns the memo based on a saved position
        return get_memo(s.get_account_history(sent_to, position, 1),type_thing)


    else:
        # If the first is 0, it checks the first one with the keyword or account
        #(or and depending on keyword and account)
        found = True
        memo_list = []
        # This gets the total amount of items in the accounts history
        # This it to prevent errors related to going before the creation of the account
        if type_thing == "transfer":
            memo_thing = s.get_account_history(sent_to,-1,0)
        elif type_thing == "curation_reward":
            memo_thing = s.get_account_history(account,-1,0)
        size = memo_thing[0][0]
        if minblock > 0:
            print(minblock, memo_thing[0][1]["block"], minblock)

            minblock = memo_thing[0][1]["block"] - minblock
            print(minblock)
        position = size
        if position < 0:
            position = step +1
        if step > position:
            step = position - 1
        while found:
            # Checks if the

            if (recent > 0 and len(memo_list) > 0) and not_all_accounts:
                if len(memo_list) >= recent:

                    break
            if type_thing =="transfer":
                history = s.get_account_history(sent_to, position, step)
                memos = get_memo(history, type_thing)
            elif type_thing=="curation_reward":
                history = s.get_account_history(account,position,step)
                memos = get_memo(history, type_thing)
            has_min_block = False
            #print(len(memos),keyword)
            for i in range(len(memos)-1, -1, -1):
                # goes through memos one at a time, starting with latest
                if len(memo_list) >= recent and not_all_accounts:
                    # ends if there are enough memos
                    print("here")
                    break
                has_keyword = False
                if type_thing == "transfer":
                    if memos[i][3] < minblock:
                        has_min_block = True
                    has_account = False

                    if memos[i][1] == account:
                        has_account = True
                if type_thing == "curation_reward":

                    if memos[i][2] < minblock:
                        has_min_block = True
                    has_account = True
                if keyword != []:
                    # checks if keyword is in the memo

                    #print("HERE")
                    try:
                        new_memo = json.loads(str(memos[i][2]))
                     #   print(new_memo)
                        for ii in keyword:
                      #      print(i)

                            has_keyword = False

                            if new_memo[ii[0]] == ii[1]:
                                has_keyword = True
                            if not has_keyword:
                                break

                    except Exception as e:
                        pass

                else:
                    # not having a keyword is not advisible for transfer memos
                    has_keyword = True
                if has_keyword and has_account or type_thing == "curation_reward":


                    memo_list.append(memos[i])



                if has_min_block:
                    break
            if position == step+1 or has_min_block or (recent <= len(memo_list) and not_all_accounts):
                # ends if it has gone through all the memos, reached the min block, or has too many memos
             #   print("break")
                break

            elif position-step <= step:
                position = step+1

            else:

                position -=step
        return memo_list
    # This checks if it has the keyword or is by the account


def save_memo(information, to, account_from, active_key, transaction_size=0.001, asset="SBD", node="wss://steemd-int.steemit.com",try_thing = [0,0]):
    # print statements are because im testing rn
    # This should send a memo and return the position

    print("AAAAAAAAaa",information)
    try:
        if information["account"] != to:
            while True:
                print("THIS")
                try:

                    print("here1")
                    s = Steem(node=node)
                    thing = s.get_account(information["account"])
                    print(thing)
                    print("here2")
                    break
                    save_memo(information,information["account"],account_from,active_key,node=node)
                    break
                except:
                    try_num += 1
                    if try_num >3:
                        break

    except KeyError:
        pass
    print("HERE")
    index = None
    try:
        print(0)
        node_connection = create_connection(node)
        print(1)
        s = Steem(node=node_connection, keys=active_key)

        memo = json.dumps(information)
        print("MEMO THINF MADE")
        print(to, transaction_size, asset, account_from, memo)
        s.transfer(to,transaction_size,asset=asset,account=account_from, memo=memo)
        print(2)
        try_thing[0] = 0
    except Exception as e:
        print(to, transaction_size, asset, account_from, memo)
        print(6)
        print(e)
        print(try_thing)
        if try_thing[0] > 5:
            try_thing[0] = 0
            return False
        print(1222)
        return save_memo(information, to, account_from,active_key,transaction_size,asset,node, [try_thing[0] +1,try_thing[1]])
    time.sleep(3)
    while index == None or index == []:
        try:

            if information["type"] == "account":
                index = retrieve(account=account_from, sent_to=to, recent=1, step=50, keyword=[["account",str(information["account"])], ["type","account"]])
            elif information["type"] == "post":
                index = retrieve(account=account_from, sent_to=to, recent=1, step=50, keyword=[["type","post"],["post_link",information["post_link"]]])
                print("index")
            elif information["type"] == "vote-link":



                index = retrieve(account=account_from, sent_to=to, recent=1, step=50, keyword=[["type","vote-link"],["account",information["account"]]])



        except Exception as e:
            print("EXCEPTTT")
            print(e)
        try_thing[1] += 1
        if try_thing[1] > 5:
            try_thing[1] = 0
            print("FALSE1")
            return False




    return index[0][0]



def get_memo(history_list,type_thing):
    # this goes through every account action and sees if it is a transfer
    # it then adds it to the list for the functions above to check
    memos = []
    for i in history_list:# full list of account actions
        memo = []
        for ii in i: # goes through every action until it gets what i actually need

            if type(ii) == dict: # what i need is the only dict
                try:
                    if ii['op'][0] ==type_thing and type_thing =="transfer" :
                        # Example:

                        memo.append(ii['op'][1]['from'])
                        memo.append(ii['op'][1]['memo'])
                        memo.append(ii['block'])
                        memos.append(memo)
                    if ii['op'][0] == type_thing and type_thing =="curation_reward":
                        # ii, example:{'trx_id': '0000000000000000000000000000000000000000', 'block': 21097520, 'trx_in_block': 55, 'op_in_trx': 1, 'virtual_op': 0, 'timestamp': '2018-03-29T11:16:12', 'op': ['curation_reward', {'curator': 'anarchyhasnogods',
                        # 'reward': '4.079991 VESTS', 'comment_author': 'valth', 'comment_permlink': 'today-is-the-world-water-day'}]}
                        memo.append(ii['op'][1])

                        memo.append(ii['block'])
                        memos.append(memo)
                    else:
                        memo = []
                except:

                    pass
            if type(ii) == int:

                memo.append(ii)

    return memos






def get_curation(history_list):

    pass







