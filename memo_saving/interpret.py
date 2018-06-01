# This file interprets the information gotten and stored to/from the memos for collective intellegence
# If you are not using our memo system exactly feel free to take a look at these functions but they won't be too useful

from memo_saving import main
import json
from steem import Steem


keywordlist = [["type","account"],["gp",0],["ad-token-perm",0],["token-upvote-perm",0],["ad-token-temp",0]
               ["token-post-review",0],["experience",0],["steem-owed",0],["vote",[]],["vote-link",[]]
               ["steem-gp-ratio",0.33],["groups",[["CI",1]]],["ratings",{"curation":0}]]
def start_account(account_name,active_key, our_memo_account="space-pictures", our_sending_account="anarchyhasnogods", node="wss://steemd-int.steemit.com"):
    keyword_dict = {}
    # creates account

    global keywordlist
    for i in keywordlist:
        keyword_dict[i[0]] = i[1]

    keyword_dict["account"] = account_name

    #info = list_to_full_string(real_list)
    #print("ddd", our_sending_account, our_memo_account)

    main.save_memo(keyword_dict, our_memo_account, our_sending_account, active_key)


def update_info_version(account_info, active_key, our_account,our_memo_account,node):
    changes = []
    keys = account_info.keys()
    for i in keywordlist:
        if not i[0] in keys:

            changes.append([i[0],i[1]])
            account_info[i[0]] = i[1]
    if changes != []:
        update_account(account_info["account"],our_account,our_memo_account,changes,active_key,node)
    return account_info





def get_account_info(account,active_key,our_account = "anarchyhasnogods", our_memo_account = "space-pictures",node ="wss://steemd-int.steemit.com"):
    # gets the useful account info for a specific account, goes through all accounts until it gets the correct account then returns info
    print("getting account info")
    return_info = main.retrieve([["account",account],["type","account"]], account=our_account, sent_to=our_memo_account,node=node)
    if return_info != []:


        return_info[0][2] = update_info_version(json.loads(return_info[0][2]),active_key,our_account,our_memo_account,node)

        return return_info[0]

    return None




def update_account(account, our_sending_account, our_memo_account, changes, active_key,node):
    # Changes is composed of a list of changes
    #Each seperate change is [keyword,new_information]
    info = get_account_info(account,our_sending_account, our_memo_account)
    #print("info",info)

    info_dict = info[2]
    #print("THISS")
    for i in changes:
        #print(i)
        if i[0] == "vote":
            info_dict[i[0]].append(i[1])
        elif i[1] == "DELETE":
            del info_dict[i[0]]

        else:
            info_dict[i[0]] = i[1]

    print("AT THING")
    thing = list_to_full_string(info_dict,our_memo_account,our_sending_account,active_key)
    print("THING MADE")
    print(our_memo_account, our_sending_account, active_key, node)
    return main.save_memo(thing, our_memo_account, our_sending_account, active_key,node=node)






def list_to_full_string(list_set,our_memo_account, our_sending_account, active_key):
    # turns objects into info that can be used as json
    # if its too long sends a static memo for votes
    print("THIS999")
    dump_list = json.dumps(list_set)
    dump_list = json.dumps(dump_list)
    total_len = len(dump_list)
    print(total_len)
    if total_len > 2000:
        print("TRY THIS")
        vote_list_post = main.save_memo({"account":list_set["account"],"type":"vote-link","vote":list_set["vote"]}, our_memo_account, our_sending_account, active_key)
        print(" PAST THIS")
        list_set["vote"] = []
        list_set["vote-link"].append([vote_list_post, our_memo_account])


    #print(list_set)
    return list_set






def vote_post(post_link, submission_author, submission_time,vote_list, ratio, our_memo_account, our_sending_account, active_key,node, vote_size):
    # creates basic account memo
    json_thing = {}
    json_thing["type"] = "post"
    json_thing["post_link"] = post_link
    json_thing["submission_author"] = submission_author
    json_thing["time"] = submission_time
    json_thing["ratio"] = ratio
    json_thing["vote-list"] = vote_list
    json_thing["vote_size"] = vote_size
    if len(vote_list) < 15:
        json_thing["message"] = "less than 15 votes, cannot vote"
    #print(json_thing)

    return main.save_memo(json_thing,our_memo_account, our_sending_account, active_key,node=node)


def get_account_list(sending_account,memo_account_list, node,days = 31):
    block = days * 24 * 60 * 20
    # checks up to 7 days ago by default
    memo_list = []
    temp_list = []
    accounts_in_list = {"accounts": []}

    for i in memo_account_list:
        temp_list.append(main.retrieve([["type", "account"]], sending_account, i, not_all_accounts = False, minblock=block,node=node))

        for ii in temp_list[0]:
            ii[2] = json.loads(ii[2])
            if ii[2]["account"] not in accounts_in_list["accounts"]:

                accounts_in_list["accounts"].append(ii[2]["account"])
                accounts_in_list[ii[2]["account"]] = ii

            elif accounts_in_list[ii[2]["account"]][3] > ii[3]:
                accounts_in_list[ii[2]["account"]] = ii

    # Account_in_list is a dictionary, "accounts" is a list of accounts. Each account has its full account memo info in the dict under its account name
    # to go through info in accounts iterate through the account list as dictionary keys
    return accounts_in_list



def get_all_accounts(sending_account,memo_account, node,days = 31):
    block = days * 24 * 60 * 20



    return_info = main.retrieve([["type", "account"]], sending_account, memo_account, not_all_accounts = False, minblock=block,node=node)
    account_list = []
    return_list = []
    for i in return_info:

        if not json.loads(i[2])["account"] in account_list:
            account_list.append(json.loads(i[2])["account"])
            return_list.append(i)
    return return_list

    pass
def vote_link_create(account_memo, our_memo_account, our_sending_account, active_key,node, create_link_anyway=False):
    # if the memo is too large it makes a static memo that is saved on its account
    print("this_thing")
    if len(json.dumps(account_memo)) > 2000 or create_link_anyway:
        #print(json.dumps(account_memo["vote"]))
        #print(account_memo["vote"])
        #print("this thing")
        index = main.save_memo(json.dumps(account_memo["vote"]), our_memo_account, our_sending_account, active_key, node=node)
        account_memo["vote"] = 0
        account_memo["vote-link"].append(index)
    return account_memo


def vote_link_find(position,our_memo_account,our_sending_account,node):
    return_info = main.retrieve(position=position,account=our_sending_account,sent_to = our_memo_account,node=node)

    return return_info


def get_vote_list(memo_account, sending_account, post_link, node):

    return_info = main.retrieve(keyword=[["vote-link",post_link]],account=sending_account, sent_to = memo_account, node=node)


    return return_info


def get_vote_amount(time_period,our_account = "anarchyhasnogods", our_memo_account = "space-pictures",node = "wss://steemd-int.steemit.com"):
    # time period is seconds
    # gets average vote size by our account on posts over the time period, using the post memos sent

    block = time_period / 3
    return_info = main.retrieve([["type","post"]], account=our_account, sent_to=our_memo_account,node=node,minblock = block,not_all_accounts = False)
    vote_power_in_period = (1000 / (24 * 60 * 60)) * time_period
    average_ratio = [0,0]

    for i in return_info:
        try:
            if float(json.loads(i[2])["vote_size"] != 0):
                average_ratio[0] += float(json.loads(i[2])["ratio"])
                average_ratio[1] +=1

        except KeyError:
            pass
    if average_ratio[1] !=0:


        average_ratio = average_ratio[0]/average_ratio[1]
    else:
        return [vote_power_in_period,1]
    print("RETURN INFO")
    print("RETURN INFO LENGTH: ", average_ratio, len(return_info))
    print(vote_power_in_period)
    if len(return_info) == 0:
        return [vote_power_in_period,1]


    return [vote_power_in_period / len(return_info), average_ratio]

def get_all_curation_rewards(time_period,our_account,our_memo_account,node):
    block = time_period / 3
    return_info = main.retrieve(account=our_account, sent_to=our_memo_account, node=node,
                                minblock=block, not_all_accounts=False,type_thing="curation_reward")
    return return_info
    pass

def get_all_votes(time_period,our_account,our_memo_account,node):
    block = time_period / 3
    return_info = main.retrieve([["type","post"]],account=our_account, sent_to=our_memo_account, node=node,
                                minblock=block, not_all_accounts=False)

    return return_info
    pass


def pay_account(size,our_account,our_memo_account,node,active_key,info):
    # Sends steem to account and then updates the account memo (even if not needed, keeps it near the top)
    try_num = 0
    print("here")
    while try_num < 5:
        try_num+= 1

        try:
            s = Steem(node=node,keys=active_key)
            print(2)
            s.transfer(info["account"],size, asset="STEEM", account=our_account, memo="payment of "+ str(size)+" Steem.")
            info["steem-owed"] -= size
            main.save_memo(info, our_memo_account, our_account, active_key, node=node)
            print("HERE")
            break
        except Exception as e:
            print(e)
            pass

