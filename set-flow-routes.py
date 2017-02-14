#!/usr/bin/python
# easy_install junos-eznc; juniper python interactive module
# A script that takes 3 arguments($DEVICE, $CONFIGURATION_METHOD $FILE) and
# uses that to change the configuration of a juniper device
# Reference
# http://www.juniper.net/techpubs/en_US/junos-pyez1.0/information-products/
# pathway-pages/junos-pyez-developer-guide.pdf
# yaml file neteng/etc/set-flow-route.yaml to set route variables

from jnpr.junos.utils.config import Config
from jnpr.junos import Device
from pprint import pprint
from jnpr.junos.factory import loadyaml
from jnpr.junos.op import *
from glob import glob
from jinja2 import Template
import os
import yaml
import sys
import getpass
import argparse
import socket
import argparse

__author__ = ['shane@']
__version__ = "Dec 2016"

# YAML file.
with open(glob('set-flow-route.yaml')[0]) as fh:
    data = yaml.load(fh.read())

# Jinja2 template file.
with open(glob('set-flow-route.junos')[0]) as t_fh:
    t_format = t_fh.read()

if len(data.keys()) > 1:
    for d in data.keys():
        routesnippet = Template(t_format)
        print (routesnippet.render(data[d]))
else:
    routesnippet = Template(t_format)                                       
    data_key = data.keys()[0]
    new_data = data.pop(data_key, None)
    print (routesnippet.render(new_data))

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

def process_response():
    """ Process the response of the user before committing.

    Args: None

    Return:
       System exit
    """
    answer = raw_input()
    if answer == 'yes':
        # Juniper check configuration method
        config.commit_check()
        # Juniper commit configuration
        config.commit(comment="Automated configuration of %s"
        %args.juniper_file)
        # unlock configuration
        config.unlock()
        # close the device
        juniper_device.close()
        sys.exit(0)
    elif answer == 'no':
        print "Rolling back configuration\n"
        # rollback candidate configuration
        config.rollback(0)
        # unlock configuration
        config.unlock()
        # close the device
        juniper_device.close()
        sys.exit(0)
    else:
        print "Need to answer yes or no\n"
        process_response()

# Open netconf connection with RR
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
    "Br1f flow configuration")
    parser.add_argument('juniper_device', help = """USAGE ./set-flow-routes.py
    $DEVICE""")
    args = parser.parse_args()
    # convert device name to ip address
    ip_addr_juniper_device = socket.gethostbyname(args.juniper_device)
    # grab password
    password = get_user_info()
    # Create object with ip_address, user and password
    juniper_device = Device(host=ip_addr_juniper_device, user=os.getenv("USER"),
    password=password)
    # open the device defined instance
    juniper_device.open()
    # open configuration method
    config = Config(juniper_device)
    try:
        config.lock()
    except LockError:
        print "Error: Unable to lock configuration"
        juniper_device.close()
        sys.exit(0)

    # rollback any configuration that might be in candidate configuration
    config.rollback(0)
    try:
        if len(data.keys()) > 1:                                                        
            for d in data.keys(): 
                config.load(template_path='set-flow-route.junos',
                template_vars=data[d], format='text', merge=True)
        else:
            config.load(template_path='set-flow-route.junos',
            template_vars=new_data, format='text', merge=True) 
    except ValueError as err:
        print err.message
    print config.diff()
    print "Proceed with commit?:(yes or no)"
    # Commit and unlock
    process_response()
