#!/usr/bin/env python

import baker
import json
import requests
import sys
import time
import websocket
import base64

from BaseHTTPServer import HTTPServer

HOST = "http://rancher.local:8080/v1"
USERNAME = "userid"
PASSWORD = "password"
kwargs = {}
images = {}

class ImageRecord:
    def __init__ (self):
        self.type = None
        self.registry = None
        self.path = None

def add_image(target_type,server,image_name):
  print "Registering " + server + ", " + image_name + "... for type = " + target_type
  if server not in images:
    images[server] = {}
  
  if image_name not in images[server]:
    images[server][image_name] = target_type
 
def get(url):
   r = requests.get(url, auth=(USERNAME, PASSWORD), **kwargs)
   r.raise_for_status()
   return r

def print_json(data):
   print json.dumps(data, sort_keys=True, indent=3, separators=(',', ': '))

@baker.command(default=True, params={"target_type": "rancher, kubernetes (optional)"})
def query(target_type=""):
  if target_type == "rancher":
    rancher_query()
  else:
    print "Incorrect or empty target provided. Exiting."

#
# Query for images
#
@baker.command()
def rancher_query():
   i = get(HOST + "/images").json()
   for x in i['data']:
     row = x['data']['dockerImage'] 
     add_image("rancher",row['server'],row['fullName'])

   for k,v in images.iteritems():
     print "Server: " + k
     for kk,vv in v.iteritems():
       print "Image: " + kk

#
# Script's entry point, starts Baker to execute the commands.
# Attempts to read environment variables to configure the program.
#
if __name__ == '__main__':
   import os

   if 'CATTLE_ACCESS_KEY' in os.environ:
      USERNAME = os.environ['CATTLE_ACCESS_KEY']

   if 'CATTLE_SECRET_KEY' in os.environ:
      PASSWORD = os.environ['CATTLE_SECRET_KEY']

   if 'CATTLE_URL' in os.environ:
      HOST = os.environ['CATTLE_URL']

   if 'RANCHER_ACCESS_KEY' in os.environ:
      USERNAME = os.environ['RANCHER_ACCESS_KEY']

   if 'RANCHER_SECRET_KEY' in os.environ:
      PASSWORD = os.environ['RANCHER_SECRET_KEY']

   if 'RANCHER_URL' in os.environ:
      HOST = os.environ['RANCHER_URL']

   if 'SSL_VERIFY' in os.environ:
      if os.environ['SSL_VERIFY'].lower() == "false":
        kwargs['verify'] = False
      else:
        kwargs['verify'] = os.environ['SSL_VERIFY']

   # make sure host ends with v1 if it is not contained in host
   if '/v1' not in HOST:
      HOST = HOST + '/v1'

   baker.run()
