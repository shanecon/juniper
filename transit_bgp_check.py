#!/usr/bin/python

import pexpect
import sys
import re
import getpass
from collections import deque

__author__ = ['shane@']
__version__ = "May 2016"

def get_user_info():
  """Get password of the user to login with.

  Args: None

  Return:
    Tuple: (password)
  """
  password = getpass.getpass('LDAP Password: ')
  if len(password) > 6:
    return (password)
  else:
    print('Password entered is less than 6 characters long')
    get_user_info()

if __name__ == '__main__':

    # variable definitions
    switches_backbone = (
    'router1',
    'router2',
    'router3',
    'router4'
    )
    as_name = {
    '174':'Cogent',
    '209':'CenturyLink',
    '3356':'Level3',
    '2914':'NTT',
    '6461':'Zayo',
    '7922':'Comcast'
    }
    password = get_user_info()
    # formatting template for bgp output
    template = "{0:30}|{1:15}|{2:15}|{3:15}|{4:16}|{5:15}|{6:15}"

    for switch_bb in switches_backbone:
        juniper_switch = pexpect.spawn\
        ('ssh -p 22 -o "StrictHostKeyChecking=no" %s' %switch_bb)
        juniper_switch.maxread = 5000
        juniper_switch.expect('[pP]assword:')
        juniper_switch.sendline('%s' %password)
        juniper_switch.expect('>')
        juniper_switch.sendline('show bgp summary | no-more')
        juniper_switch.expect('.*')
        juniper_switch.expect('{master}')
        juniper_switch_count =  juniper_switch.before
        juniper_switch_count.rstrip()
        juniper_switch.expect('>')
        juniper_switch.sendline('exit')
        bgp_split = juniper_switch_count.split('\r')
        print '\n*** %s ***' %switch_bb
        print template.format("Peer IP", "Peer AS", "As Name", "Flaps",\
        "Time since flap", "State","Routes")
        routes = []
        for bgp in bgp_split:
            new_bgp = bgp.split(' ')
            bgp_list_remove = [x for x in new_bgp if x]
            bgp_list_remove_new = map(lambda s: s.strip(), bgp_list_remove)
            if re.match('\d+.\d+.\d+', bgp_list_remove_new[-1]) and\
            bgp_list_remove_new[1] != 'inetflow.0:':
                routes.append(bgp_list_remove_new[-1])
        route_queue = deque(routes)
        for bgp in bgp_split:
            new_bgp = bgp.split(' ')
            bgp_list_remove = [x for x in new_bgp if x]
            bgp_list_remove_new = map(lambda s: s.strip(), bgp_list_remove)
            if bgp_list_remove_new[0]:
                if re.match('\d+', bgp_list_remove_new[0]):
                    print template.format(bgp_list_remove_new[0],
                    bgp_list_remove_new[1], as_name[bgp_list_remove_new[1]],
                    bgp_list_remove_new[5], bgp_list_remove_new[6],
                    bgp_list_remove_new[7], route_queue.popleft())
