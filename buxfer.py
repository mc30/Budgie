################################################################################
# Functions to interact with Buxfer
################################################################################

import urllib3
import sys
import json

from pandas.io.json import json_normalize


def check_error(result):
    response = result['response']
    if response['status'] != "OK":
        print("An error occurred: %s" % response['status'].replace('ERROR: ', ''))
        sys.exit(1)

    return response


def login(username, password):
    url = base + "/login?userid=" + username + "&password=" + password

    req = http.request('GET', url)
    response = json.loads(req.data.decode('utf-8'))
    print(response)
    check_error(response)

    rsp = response['response']
    token = rsp['token']

    return token


def get_budgets(token):
    url = base + "/budgets?token=" + token
    req = http.request('GET', url)
    response = json.loads(req.data.decode('utf-8'))
    check_error(response)

    print(response)

    rsp = response['response']

    for budget in rsp['budgets']:
        # print("%12s %8s %10.2f %10.2f" % (budget['name'],
        #                                   budget['currentPeriod'],
        #                                   budget['limit'],
        #                                   budget['remaining']))
        print("%12s %10.2f" % (budget['name'], budget['limit']))

    result = ""

    for budget in rsp['budgets']:
        result += "%12s %10.2f\n" % (budget['name'], budget['limit'])

    return result


def get_transactions(token):
    url = base + "/transactions?token=" + token
    req = http.request('GET', url)
    response = json.loads(req.data.decode('utf-8'))
    print(response)
    check_error(response)

    rsp = response['response']

    result = ""

    for transaction in rsp['transactions']:
        result += "%12s\t%10.2f\t%12s\n" % (transaction['description'],
                                            transaction['amount'], transaction['tags'])

    return result


def get_tags(token):
    url = base + "/tags?token=" + token
    req = http.request('GET', url)
    response = json.loads(req.data.decode('utf-8'))
    print(response)
    check_error(response)

    rsp = response['response']

    recs = rsp['tags']
    df = json_normalize(recs)

    print(df)

    return df


def get_accounts(token):
    url = base + "/accounts?token=" + token
    req = http.request('GET', url)
    response = json.loads(req.data.decode('utf-8'))
    print(response)
    check_error(response)

    rsp = response['response']

    recs = rsp['accounts']
    df = json_normalize(recs)

    print(df)

    return df


def add_transaction(token, description, amount,
                    account_id, date_str, tags='', type='expense',
                    status='cleared'):
    url = base + "/add_transaction?token=" + token + \
          "&description=" + description + \
          "&amount=" + amount + \
          "&accountId=" + account_id + \
          "&date=" + date_str + \
          "&tags=" + tags + \
          "&type=" + type + \
          "&status=" + status

    req = http.request('GET', url)
    response = json.loads(req.data.decode('utf-8'))
    print("Transaction added")
    print(response)


base = "https://www.buxfer.com/api"
http = urllib3.PoolManager()
