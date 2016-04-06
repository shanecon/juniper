#!/usr/bin/python
# Juniper pexpect script that logins in and gathers ae status data 
import pexpect
import datetime
import getpass
import re

__author__ = ['shane']
__version__ = "April 2016"

# function to grab password from user for later use
def get_user_info():
    """Get password of the user to login with.

    Args: None

    Return:
      Tuple: (password)
    """
    password = getpass.getpass('LDAP Password: ')
    if len(password) > 8:
        return (password)
    else:
        print('Password entered is less than 8 characters long')
        get_user_info()

# Define switch and ae interfaces
switch_ae = {
'router1-mx':['ae3','ae4'],                                               
'router2-mx':['ae3','ae4'],                                               
'switch1-ex':['ae1','ae3','ae5','ae10','ae11'],
'switch2-ex':['ae1','ae3','ae5','ae10','ae11'],
}

if __name__ == '__main__':

    # grab password for use in pexpect
    password = get_user_info()
    # grap today's data and print it out
    today = datetime.date.today()
    print today

    for switch, ae in sorted(switch_ae.items()):
        juniper_ae = pexpect.spawn \
        ('ssh -p 22 -o "StrictHostKeyChecking=no" %s' %switch)
        juniper_ae.maxread = 5000
        juniper_ae.expect('[pP]assword:')
        juniper_ae.sendline('%s' %password)
        juniper_ae.expect('>')
        # loop through ae interfaces
        for a in ae:
            juniper_ae.sendline ('show interfaces %s | match Speed' % a)
            juniper_ae.expect(' ')
            juniper_ae.expect('{master.*}')
            juniper_ae_speed =  juniper_ae.before
            # different output from ex and mx's screen scraping
            if re.match('switch.*',switch):
                print "%s, %s speed" %(switch,a), juniper_ae_speed.split(' ')\
                [-4].rstrip() 
            else:
                print "%s, %s speed" %(switch,a), juniper_ae_speed.split(' ')\
                [-1].rstrip()
        juniper_ae.expect('>')
        juniper_ae.sendline('exit')
