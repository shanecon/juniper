#!/usr/bin/python
from pprint import pprint as pp
from lxml import etree
from jnpr.junos import Device as Junos
from jnpr.junos.op.phyport import *
import switch_list
import getpass
import os
import json
import itertools
import threading

__author__ = ['shane']
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
        print('Password entered is less than 6 characters long')
        get_user_info()

def juniper_error(switch):
    """ Get Juniper switch interface errors
  
    Args: switch

    Return:
      Switch interface errors
    """ 
    login = dict(user=os.getenv("USER"), host=switch, password=password)
    rtr = Junos(**login)
    rtr.open()
    ports = PhyPortTable(rtr).get()
    stats = PhyPortErrorTable(rtr).get()
    print "host: " + rtr.hostname
    print "Interface\tError"

    for port,stat in map(None,ports,stats):
        for attr in stat.FIELDS:
            if 'err' in attr:
                if getattr(stat,attr) != 0:
                    print port.name.ljust(12), attr.ljust(12), getattr(stat, 
                    attr)
    rtr.close()

if __name__ == '__main__':
    switch = switch_list.switch
    edge = switch_list.edge
    password = get_user_info()
    threads = []
    for s in switch:
        t = threading.Thread(target=juniper_error, args=(s,))
        threads.append(t)
        t.start()
    for e in edge:
        t = threading.Thread(target=juniper_error, args=(e,))                   
        threads.append(t)                                                       
        t.start()
