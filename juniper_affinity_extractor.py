#!/usr/bin/python

# A script that logs into juniper routers running mpls
# and creates either json or csv output of the affinity
# groups

import argparse
import getpass
import os
import xmltodict
import json
import argparse
import pymongo
from ncclient import manager

__author__ = ['shanecon']
__version__ = "May 2015"

# Have to easy_install ncclient, xmltodict

class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value
r = AutoVivification()

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

def lsp_name_converter(lsp_name):
   """Transform lsp name 

   Args: lsp name 

   Return: 
        Transformed lsp name   
   """
   lsp_name_list = lsp_name.split('-')
   new_lsp_name = lsp_name_list[2]+"-"+lsp_name_list[3]
   return new_lsp_name

def retrieveConfig(host, user, password):
    with manager.connect(host=host, port=22, hostkey_verify=False, username=user, password=password,ssh_config='~/.ssh/config') as m:
        c = m.get_config(source='running').data_xml
        with open("%s.xml" % host, 'w') as f:
            f.write(c)

def convert_xml_to_list(bbr,mydict):
   """Convert xml to csv list 

   Args: router, dictionary  

   Return: 
        string:(csv list object) 
   """
   mpls_list = []
   for l in range(len(mydict['data']['configuration']['protocols']['mpls']['label-switched-path'])):
      primary_name = mydict['data']['configuration']['protocols']['mpls']['label-switched-path'][l]['primary']['name']
      secondary_name = mydict['data']['configuration']['protocols']['mpls']['label-switched-path'][l]['secondary'][0]['name']
      secondary_host = lsp_name_converter(primary_name)
      primary_admin = mydict['data']['configuration']['protocols']['mpls']['label-switched-path'][l]['primary']['admin-group-extended'].values()
      secondary_admin = mydict['data']['configuration']['protocols']['mpls']['label-switched-path'][l]['secondary'][0]['admin-group-extended'].values()
      for p in primary_admin:
         if p == 'POP':
            string_primary_admin = p
            continue
         string_primary_admin = ' '.join(p)
      for s in secondary_admin:
         if s == 'POP':
            string_secondary_admin = p
            continue
         string_secondary_admin = ' '.join(s)
      mpls_list.append(bbr.upper()+","+secondary_host+","+primary_name+","+string_primary_admin)
      mpls_list.append(bbr.upper()+","+secondary_host+","+secondary_name+","+string_secondary_admin)
   return mpls_list

def convert_xml_to_json(bbr,mydict):
   """Convert xml to json

   Args: router, dictionary 

   Return:
        string:(dictionary object) 
   """
   for l in range(len(mydict['data']['configuration']['protocols']['mpls']['label-switched-path'])):
      primary_name = mydict['data']['configuration']['protocols']['mpls']['label-switched-path'][l]['primary']['name']
      secondary_name = mydict['data']['configuration']['protocols']['mpls']['label-switched-path'][l]['secondary'][0]['name']
      secondary_host = lsp_name_converter(primary_name)
      r[bbr.upper()][secondary_host][primary_name] = mydict['data']['configuration']['protocols']['mpls']['label-switched-path'][l]['primary']['admin-group-extended'].values() 
      r[bbr.upper()][secondary_host][secondary_name] = mydict['data']['configuration']['protocols']['mpls']['label-switched-path'][l]['secondary'][0]['admin-group-extended'].values()
   return r 

if __name__ == '__main__':
   affinity_dict = {}
   big_list = []
   bbr = ('router1','router2','router3')
   # argparser configuration
   parser = argparse.ArgumentParser(description="JSON output or CSV output")
   parser.add_argument('output',choices=['json','csv'],help='USAGE juniper_affinity_extractor.py [json|csv]')
   args = parser.parse_args()
   password = get_user_info()
   #json output
   if args.output == 'json':
      try:
         conn = pymongo.MongoClient('1.1.1.1', 27017)
      except pymongo.errors.ConnectionFailure, e:
         print "Could not connect to MongoDB: %s" % e
      db = conn.neteng
      for bb in bbr:  
         retrieveConfig(bb, os.getenv("USER"),password)
         xml_file = bb +'.xml'
         with open(xml_file) as fd:
            mydict = xmltodict.parse(fd.read())
         affinity_dict.update(convert_xml_to_json(bb[:-3], mydict))
         os.remove('%s' %xml_file)
      #print affinity_dict
      db.drop_collection('affinity_script_generated')
      db.affinity_script_generated.insert(affinity_dict) 
      #json_affinity = json.dumps(affinity_dict)
      #print json_affinity  
   #csv output
   elif args.output == 'csv':
      for bb in bbr:
         retrieveConfig(bb, os.getenv("USER"),password)
         xml_file = bb +'.xml'
         with open(xml_file) as fd:
            mydict = xmltodict.parse(fd.read())
         big_list.append(convert_xml_to_list(bb.strip('.nw'), mydict))
         os.remove('%s' %xml_file)
      for big in big_list:
         print "\n"
         for b in big:
            print b 
