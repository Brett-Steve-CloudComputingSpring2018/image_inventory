#!/usr/bin/python

import baker
import json
import requests
import sys
import time
import websocket
import base64
import anchore_check

from BaseHTTPServer import HTTPServer

#
## Thanks to https://github.com/etlweather/gaucho for introducing me to baker.
#

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

  image_record = ImageRecord()
  image_record.type = target_type
  image_record.server = server
  image_record.name = image_name

  if server not in images:
    #then it must be new, add it with an empty value
    images[server] = {}

  images[server][image_name] = image_record

def get(url):
   r = requests.get(url, auth=(USERNAME, PASSWORD), **kwargs)
   r.raise_for_status()
   return r

def print_json(data):
   print json.dumps(data, sort_keys=True, indent=3, separators=(',', ': '))

@baker.command(default=True, params={"target_type": "rancher, kubectl (optional)"})
def query(target_type=""):
  if target_type == "rancher":
    print "Rancher has been selected."
    rancher_query()
  else:
    print "Incorrect or empty target provided. Exiting."

@baker.command()
def rancher_query():
   print "Rancher query is running..."
   i = get(HOST + "/images").json()
   for x in i['data']:
     row = x['data']['dockerImage'] 
     add_image("rancher",row['server'],row['fullName'])

   print_images()

def print_servers():
   for k,v in images.iteritems():
     print "Server: " + k

def print_images():
   for k,v in images.iteritems():
     print "Server: " + k
     for image_name,image_record in v.iteritems():
       print "  Image: " + image_name + " (" + image_record.type + ")"

if __name__ == '__main__':
   import os

   if 'KUBECTL_ACCESS_KEY' in os.environ:
      USERNAME = os.environ['KUBECTL_ACCESS_KEY']

   if 'KUBECTL_SECRET_KEY' in os.environ:
      PASSWORD = os.environ['KUBECTL_SECRET_KEY']

   if 'KUBECTL_URL' in os.environ:
      HOST = os.environ['KUBECTL_URL']

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
        
   baker.run()
