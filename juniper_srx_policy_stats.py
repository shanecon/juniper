#!/usr/bin/python

import getpass
import xmltodict
import pymongo
import threading
import switch_list
import os
from ncclient import manager

__author__ = ['shane@']
__version__ = "Sept 2016"

def get_user_info():
    """Get password of the user to login with.

    Args: None

    Return:
     Tuple: (password)
    """
    password = getpass.getpass('Password: ')
    if len(password) > 6:
        return (password)
    else:
        print('Password entered is less than 8 characters long')
        get_user_info()

def connect(host, user, password,port=22):
    conn = manager.connect(host=host,
           username=user,
           port = port,
           password=password,
           timeout=10,
           device_params = {'name':'junos'},
           hostkey_verify=False,)

    policy_stats = conn.command(command='show security policies hit-count',
    format='xml')
    policy_stats = str(policy_stats)
    policy_stats = xmltodict.parse(policy_stats)
    # append host name 
    host = {'host-name':host}
    policy_stats.update(host)
    db.fw_policy_stats.insert(policy_stats, check_keys=False)

if __name__ == '__main__':
    password = get_user_info()
    try:
        # needs a mongodb instance running
        conn = pymongo.MongoClient('10.0.0.0', 27017)
    except pymongo.errors.ConnectionFailure, e:
        print "Could not connect to MongoDB: %s" % e
    # connecting to the database named neteng
    db = conn.neteng
    # list of firewalls imported from switch_list
    fw = switch_list.fw
    # define threads
    threads = []
    db.drop_collection('fw_policy_stats')
    for f in fw:
        t = threading.Thread(target=connect, args=(f,os.getenv("USER"),password,))
        threads.append(t)
        t.start()
