#!/usr/bin/python
# A script that takes a dns host name and prints out from an SRX configuration
# address book, adrress set, global address set, policy

import pymongo
import argparse
import socket
import sys

__author__ = ['shane']
__version__ = "Mar 2016"

def parser_user_input():
    """Get user host input

    Args: None

    Return:
        string: (ip address))
    """
    parser = argparse.ArgumentParser(description="Juniper Device Name and Configuration Method")
    parser.add_argument('host_name', help="""USAGE ./acl_grep.py $HOST; EXAMPLE ./acl_grep.py
    host1""")
    args = parser.parse_args()
    try:
        ip_addr = socket.gethostbyname(args.host_name)
    except:
        print "***Invalid Dns***"
        sys.exit(0)
    return ip_addr

def grab_address_book(ip_address,firewall):
    addr_name = 'false'
    """Get address book

    Args: ip address

    Return:
        string: (address book name)
    """
    for fw in firewall:
        try:
            for f in fw['data']['configuration']['security']['address-book']['address']:
                if ip_addr+'/32' in f.values():
                    addr_name = f['name']
                    print "***Firewall***", fw['data']['configuration']['groups'][0]['system']['host-name']
                    print "***Address book entry***", f['name']
                    print "***Ip Prefix***", f['ip-prefix']
        except KeyError:
            continue 
    return addr_name

def grab_addr_set(addr_name,firewall):
    addr_set = 'false'
    """Get address set

    Args: address book name

    Return:
        string: (address set)
    """
    count = 0
    for fw in firewall:
        try:
            for f in fw['data']['configuration']['security']['address-book']['address-set']:
                for e in f.values():
                    if type(e) == list:
                        for d in e:
                            if addr_name in d['name']:
                                if count < 1:
                                    addr_set = f.values()[0]
                                    print "***Address set entry***",  f.values()[0]
                                    count +=1
        except KeyError:
            continue 
    return addr_set

def grab_addr_set_top_level(addr_set,firewall):
    addr_set_top_level = 'false'
    """Get address set global

    Args: address book name

    Return:
        string: (address set)
    """
    count = 0
    for fw in firewall:
        try:
            for f in fw['data']['configuration']['security']['address-book']['address-set']:
                for e in f.values():
                    if type(e) == list:
                        for d in e:
                            if addr_set == d['name']:
                                if count < 1:
                                    addr_set_top_level = f.values()[1]
                                    print "***Top Level Address Set***", f.values()[1]
                                    count += 1
        except KeyError:
            continue 
    return addr_set_top_level

def grab_policy(addr_set_top_level,firewall):
    """Get Acl Policy

    Args: address set top level

    Return:
        None
    """
    for fw in firewall:
        try:
            for f in fw['data']['configuration']['security']['policies']['global']['policy']:
                for e in f.values():
                    if type(e) == dict:
                        for d in e.values():
                            if type(d) == list:
                                if addr_set_top_level in d:
                                    source_address = f['match']['source-address']
                                    destination_address = f['match']['destination-address']
                                    application = f['match']['application']
                                    print "***Policy Name***", f['name']
                                    if type(source_address) == list:
                                         print "***Policy Match source***", " ".join([str(x) for x in source_address])
                                    else:
                                        print "***Policy Match source***", source_address
                                    if type(destination_address) == list:
                                        print "***Policy Match destination***", " ".join([str(x) for x in destination_address])
                                    else:
                                        print "***Policy Match destination***", destination_address
                                    if type(application) == list:
                                        print "***Policy Match application***", " ".join([str(x) for x in application])
                                    else:
                                        print "***Policy Match application***", application
                                    print "***Policy Action***", f['then'].keys()[0]
        except KeyError:
            continue 

def fw1_search(ip_addr):
    """Fw1 Policy search"

    Args: user provided ip address

    Return:
        None
    """
    print '***Firewall***\n'
    # Converting ip address into address book
    firewall = db.fw1.find()
    addr_name = grab_address_book(ip_addr,firewall)
    # Converting address book into address et
    firewall = db.fw1.find()
    addr_set = grab_addr_set(addr_name,firewall)
    # Converting address set to top level address set
    firewall = db.fw1.find()
    addr_set_top_level = grab_addr_set_top_level(addr_set,firewall)
    # Converting top level addres set into policy
    firewall = db.fw1.find()
    grab_policy(addr_set_top_level,firewall)

def fw2_search(ip_addr):
    """Fw2 Policy search"

    Args: user provided ip address

    Return:
        None
    """
    print '\n***Firewall***\n'
    # Converting ip address into address book
    firewall = db.fw2.find()
    addr_name = grab_address_book(ip_addr,firewall)
    # Converting address book into address et
    firewall = db.fw2.find()
    addr_set = grab_addr_set(addr_name,firewall)
    # Converting address set to top level address set
    firewall = db.fw2.find()
    addr_set_top_level = grab_addr_set_top_level(addr_set,firewall)
    # Converting top level addres set into policy
    firewall = db.fw2.find()
    grab_policy(addr_set_top_level,firewall)

def fw3_search(ip_addr):
    """Fw3 Policy search"

    Args: user provided ip address

    Return:
        None
    """
    print '\n***Firewall***\n'
    # Converting ip address into address book
    firewall = db.fw3.find()
    addr_name = grab_address_book(ip_addr,firewall)
    # Converting address book into address et
    firewall = db.fw3.find()
    addr_set = grab_addr_set(addr_name,firewall)
    # Converting address set to top level address set
    firewall = db.fw3.find()
    addr_set_top_level = grab_addr_set_top_level(addr_set,firewall)
    # Converting top level addres set into policy
    firewall = db.fw3.find()
    grab_policy(addr_set_top_level,firewall)

def fw4_search(ip_addr):
    """Fw4 Policy search"

    Args: user provided ip address

    Return:
        None
    """
    print '\n***Firewall***\n'
    # Converting ip address into address book
    firewall = db.fw4.find()
    addr_name = grab_address_book(ip_addr,firewall)
    # Converting address book into address et
    firewall = db.fw4.find()
    addr_set = grab_addr_set(addr_name,firewall)
    # Converting address set to top level address set
    firewall = db.fw4.find()
    addr_set_top_level = grab_addr_set_top_level(addr_set,firewall)
    # Converting top level addres set into policy
    firewall = db.fw4.find()
    grab_policy(addr_set_top_level,firewall)

if __name__ == '__main__':
    try:
       # needs a mongodb instance on dev8d
        conn = pymongo.MongoClient('1.1.1.1', 27017)
    except pymongo.errors.ConnectionFailure, e:
        print "Could not connect to MongoDB: %s" % e
    # connecting to the database named neteng
    db = conn.neteng
    # Converting user provided hostname to ip address
    ip_addr = parser_user_input()
    # fw1 firewall search
    fw1_search(ip_addr)
    # fw2 firewall search
    fw2_search(ip_addr)
    # fw3 fireswall search
    fw3_search(ip_addr)
    # fw4 
    fw4_search(ip_addr)
