#!/usr/bin/python
import datetime
import argparse
import getpass
import os
import socket
import sys
import logging
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import LockError
# Provides the same device looping functionality for juniper as
# arista_api_config.py

__author__ = ['shane@']
__version__ = "Oct 2016"

def resolve_host(hostname):
   """Resolve dns name to ip address

    Args: hostname

    Return:
      ip or false
    """
   try:
      ip = socket.gethostbyname(hostname)
      return "%s" % ip
   except:
      return False

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
    #log("User Response:%s" %answer)
    if answer == 'yes':
        # Juniper check configuration method
        config.commit_check()
        # Juniper commit configuration
        config.commit(comment="Automated configuration")
        # unlock configuration
        config.unlock()
        # close the device
        juniper_device.close()
    elif answer == 'no':
        print "Rolling back configuration\n"
        # rollback candidate configuration
        config.rollback(0)
        # unlock configuration
        config.unlock()
        # close the device
        juniper_device.close()
    else:
        print "Need to answer yes or no\n"
        process_response()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Configure with jnpr.junos')
    parser.add_argument('-file',help='Enter the file with hostname list')
    parser.add_argument('-commands',help='Enter the file with commands')
    parser.add_argument('configuration_choice', choices=['set','text','xml'],
    help="""USAGE ./juniper_automation_configuration.py $DEVICE
    $CONFIGURATION_METHOD $FILE; EXAMPLE ./juniper_automation_configuration.py
    fwxd [set|text|xml] juniper_config""")
    args = parser.parse_args()
    if args.file:
        if os.path.exists(args.file):
            print 'file:', args.file
            filename = args.file
        else:
            exit('Given file doesnt exist.Please provide the correct file')
    else:
        exit('No input.Please enter the file')
    if args.commands:
        if os.path.exists(args.commands):
            print 'commands:', args.commands
            commands_file = args.commands
        else:
            exit('Given commands file doesnt exist.Please provide the correct file')
    else:
        exit('No input.Please enter the commands file')

    username = getpass.getuser()
    password = get_user_info()
    # Create object with ip_address, user and password
    lines = open(filename).readlines()
    for line in lines:
        hostname = line.strip()
        log("Juniper Device name:%s,configuration file:%s" %(hostname,args.commands))
        ip = resolve_host(hostname)
        if ip:
            juniper_device = Device(host=ip,user=os.getenv("USER"),password=password,port='22')
            # open the device defined instance
            juniper_device.open()
            # open configuration method
            config = Config(juniper_device)
            # open configuration lock method allowing only one configuration
            try:
                config.lock()
            except LockError:
                print "Error: Unable to lock configuration"
                juniper_device.close()
                sys.exit(0)
            # rollback any configuration that might be in candidate configuration
            config.rollback(0)
            try:
                config.load(path=args.commands, format=args.configuration_choice,
                merge="True")
                # Merge = "False" would implies a replace action. A
                # replace action, however, requires that the configuration file have a
                # 'replace:' statement in it print configuration diff from devices
                # perspective. To load a jinja template:
                # cu.load(template_path=conf_file, template_vars=config, merge=True)
            except ValueError as err:
                print err.message
            print config.diff()
            print hostname
            print "Proceed with commit?:(yes or no)"
            process_response()

