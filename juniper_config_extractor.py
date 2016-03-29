#!/usr/bin/python
# collects xml over ncclient from various juniper devices
# and coverts it into a mongodb collection

import getpass
import os
import xmltodict
import pymongo
import argparse
import sys
from ncclient import manager

__author__ = ['shanecon']
__version__ = "Jan 2016"

# Have to easy_install ncclient, xmltodict, pymongo

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

# Login through netconf and download xml configuration
def retrieveConfig(host, user, password):
    with manager.connect(host=host, port=22, hostkey_verify=False,
    username=user, password=password) as m:
        c = m.get_config(source='running').data_xml
        with open("%s.xml" % host, 'w') as f:
            f.write(c)

def retrieve_individual_firewall():
    # Individual fw  
    db.drop_collection('fw')  
    retrieveConfig('fw', os.getenv("USER"),password)  
    xml_file = 'fw.xml'  
    with open(xml_file) as fd:
        mydict = xmltodict.parse(fd.read())
    os.remove('%s' %xml_file)
    db.fw.insert(mydict,check_keys=False) #  check_keys false otherwise  
    # Individual fw  
    db.drop_collection('fw')  
    retrieveConfig('fw1', os.getenv("USER"),password) 
    xml_file = 'fw1.xml' 
    with open(xml_file) as fd:
        mydict = xmltodict.parse(fd.read())
    os.remove('%s' %xml_file)
    db.fw1.insert(mydict,check_keys=False) #  check_keys false otherwise 
    # Individual fwxd
    db.drop_collection('fw1') 
    retrieveConfig('fw2', os.getenv("USER"),password) 
    xml_file = 'fw2.xml' 
    with open(xml_file) as fd:
        mydict = xmltodict.parse(fd.read())
    os.remove('%s' %xml_file)
    db.fw2.insert(mydict,check_keys=False) #  check_keys false otherwise

if __name__ == '__main__':

   # juniper edge routers
   edge = ('edge1','edge2')
   # juniper srx 
   fw = ('fw','fw1','fw2')
   # juniper edge switches
   switch = ('edge-sw1','edge-sw2',
             'edge-sw4','edge-sw3')
   # Gets users password
   password = get_user_info()
   # Login and collect xml information for each host
   try:
      # needs a mongodb instance running on your local host
      conn = pymongo.MongoClient('1.1.1.1', 27017)
   except pymongo.errors.ConnectionFailure, e:
      print "Could not connect to MongoDB: %s" % e
   # connecting to the database named neteng
   db = conn.neteng
   # reset collection fw
   credit_card_fw(args)
   db.drop_collection('fw')
   # loop through firewalls
   for f in fw:
      retrieveConfig(f, os.getenv("USER"),password)
      xml_file = f +'.xml'
      with open(xml_file) as fd:
         mydict = xmltodict.parse(fd.read())
      os.remove('%s' %xml_file)
      db.fw.insert(mydict,check_keys=False) #  check_keys false otherwise
      #  keys with '.' contained in them raise an error
   # Individual firewall to collection
   retrieve_individual_firewall()
   # reset collection edge
   db.drop_collection('edge')
   #loop through edge routers
   for e in edge:
      retrieveConfig(e, os.getenv("USER"),password)
      xml_file = e +'.xml'
      with open(xml_file) as fd:
         mydict = xmltodict.parse(fd.read())
      os.remove('%s' %xml_file)
      db.edge.insert(mydict,check_keys=False) #  check_keys false otherwise
      #  keys with '.' contained in them raise an error
   # reset collection switch
   db.drop_collection('switch')
   # loop through switches
   for s in switch:
      retrieveConfig(s, os.getenv("USER"),password)
      xml_file = s +'.xml'
      with open(xml_file) as fd:
         mydict = xmltodict.parse(fd.read())
      os.remove('%s' %xml_file)
      db.switch.insert(mydict,check_keys=False) #  check_keys false otherwise
      #   keys with '.' contained in them raise an error
   # reset collection vcs
   db.drop_collection('vcs')
   for v in vcs:
      retrieveConfig(v, os.getenv("USER"),password)
      xml_file = v +'.xml'
      with open(xml_file) as fd:
         mydict = xmltodict.parse(fd.read())
      os.remove('%s' %xml_file)
      db.vcs.insert(mydict,check_keys=False) #check_keys false otherwise
      #  keys with '.' contained in them raise an error
