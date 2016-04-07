#!/usr/bin/python
# easy_install junos-eznc; juniper python interactive module
# A script that takes 3 arguments($DEVICE, $CONFIGURATION_METHOD $FILE) and
# uses that to change the configuration of a juniper device
import argparse
import getpass
import os
import socket
import sys
import logging
import datetime
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import LockError

__author__ = ['shanecon']
__version__ = "Mar 2016"

def log(msg):
    """Log message to stdout and logging file
    Args:
        msg: string to print
    Returns: None
    """
    logging.basicConfig(filename='/tmp/JuniperConfig.log', level=logging.INFO)
    logging.info(msg)

def get_user_info():
    """Get password of the user to login with.

    Args: None

    Return:
      Tuple: (password)
    """
    password = getpass.getpass('Password: ')
    if len(password) > 8:
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
    log("User Response:%s" %answer)
    if answer == 'yes':
        # Juniper check configuration method
        config.commit_check()
        # Juniper commit configuration
        config.commit(comment="Automated configuration of %s"
        %args.juniper_file)
        # unlock configuration
        config.unlock()
        sys.exit(0)
    elif answer == 'no':
        print "Rolling back configuration\n"
        # rollback candidate configuration
        config.rollback(0)
        # unlock configuration
        config.unlock()
        sys.exit(0)
    else:
        print "Need to answer yes or no\n"
        process_response()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
    "Juniper Device Name and Configuration Method")
    parser.add_argument('juniper_device', help=
    """USAGE ./juniper_automation_configuration.py $DEVICE
    $CONFIGURATION_METHOD $FILE; EXAMPLE ./juniper_automation_configuration.py
    $DEVICE [set|text|xml] juniper_config""")
    parser.add_argument('configuration_choice', choices=['set','text','xml'],
    help="""USAGE ./juniper_automation_configuration.py $DEVICE
    $CONFIGURATION_METHOD $FILE; EXAMPLE ./juniper_automation_configuration.py
    $DEVICE [set|text|xml] juniper_config""")
    parser.add_argument('juniper_file', help="""USAGE
    ./juniper_automation_configuration.py $DEVICE $CONFIGURATION_METHOD $FILE;
    EXAMPLE ./juniper_automation_configuration.py $DEVICE [set|text|xml]
    juniper_config""")
    args = parser.parse_args()
    # date for log purposes
    today = datetime.date.today()
    # log date
    log("Todays date is:%s" %today)
    # log arguments
    log("""Juniper Device name:%s, Configuration Choice:%s, Configuration file
    :%s""" %(args.juniper_device, args.configuration_choice,
    args.juniper_file))
    # convert device name to ip address
    ip_addr_juniper_device = socket.gethostbyname(args.juniper_device)
    # log device ip address
    log("IP address:%s" %ip_addr_juniper_device)
    # grab password
    password = get_user_info()
    # Create object with ip_address, user and password
    juniper_device = Device(host=ip_addr_juniper_device,
    user=os.getenv("USER"),password=password,port='22')
    # open the device defined instance
    juniper_device.open()
    # open configuration method
    config = Config(juniper_device)
    # open configuration lock method allowing only one configuration
    config.lock()
    # rollback any configuration that might be in candidate configuration
    config.rollback(0)
    # load file juniper_config
    config.load(path=args.juniper_file, format=args.configuration_choice,
    merge="True") #  Merge = "False" would implies a replace action. A replace
    # action, however, requires that the configuration file have a 'replace:'
    # statement in it print configuration diff from devices perspective
    print config.diff()
    # log configuration diff
    log("Configuration Diff:%s" %config.diff())
    print "Proceed with commit?:(yes or no)"
    # Process the user respsone
    process_response()
