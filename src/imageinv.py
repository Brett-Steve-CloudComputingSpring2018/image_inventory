#!/usr/bin/python

import baker
import json
import requests
import sys
import time
import websocket
import base64
import psycopg2
import psycopg2.extras
from psycopg2 import IntegrityError
from anchore_check import *

from BaseHTTPServer import HTTPServer

#
## Thanks to https://github.com/etlweather/gaucho for introducing me to baker.
#

HOST = "http://rancher.local:8080/v1"
USERNAME = "userid"
PASSWORD = "password"
kwargs = {}
images = {}
   
class ConnectRecord:
    def __init__ (self):
        self.endpoint = "default.endpoint"
        self.username = "default"
        self.password = "bogus"
        self.database = "default"
connect_record = ConnectRecord()
        
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

@baker.command(default=True, params={"target_type": "rancher, kubectl, flatfile (optional)", "filepath":""})
def query(target_type, filepath=None):
  if target_type == "rancher":
    print "Rancher has been selected."
    rancher_query()
  elif target_type == "flatfile":
    if filepath:
      flatfile_query(filepath)
    else:
      raise ValueError("filepath must be true is target_type is flatfile.")    
  else:
    print "Incorrect or empty target provided. Exiting."

  print_images()
  check_images()
    
@baker.command
def rancher_query():
   print "Rancher query is running..."
   i = get(HOST + "/images").json()
   for x in i['data']:
     row = x['data']['dockerImage'] 
     add_image("rancher",row['server'],row['fullName'])

@baker.command
def flatfile_query(filepath):
  print "Working " + filepath
  f = open(filepath,"r")
  line = f.readline()
  while line:
    insert_new_image(line.strip(),"NEW","flatfile")
    line = f.readline()
  f.close()

def insert_new_image(image_name,status,import_source,repository=""):
  print "Inserting " + image_name
  try:
    conn = psycopg2.connect( host=connect_record.endpoint, user=connect_record.username, password=connect_record.password, dbname=connect_record.database, connect_timeout=4 )
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute("INSERT INTO images_import (name,status,repository,import_source) VALUES (%s,%s,%s,%s)", (image_name,"NEW",repository,import_source))

    #call the anchore 'add' (includes database call which adds the sha256_digest)
    anchore_add(conn,image_name,import_source,repository)
   
    conn.close()
  except IntegrityError as err:
    print err
    conn.close()
  except:
    print "Unexpected error.", sys.exc_info()

@baker.command
def reset_db(anchore=False,clair=False):
  print "Resetting database and optionally anchore"
  try:
    conn = psycopg2.connect( host=connect_record.endpoint, user=connect_record.username, password=connect_record.password, dbname=connect_record.database, connect_timeout=4 )
    conn.autocommit = True
    select_cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    delete_cursor = conn.cursor()
    select_cursor.execute("SELECT * FROM images_import")
    delete_cursor.execute("DELETE FROM images_import WHERE sha256_digest is null")

    row = select_cursor.fetchone()
    while row:
      digest = row["sha256_digest"]

      print row["name"] + ", " + digest
      try:
        delete_cursor.execute("DELETE FROM images_import WHERE sha256_digest=%s", (digest,) )
      except:
        print "Unexpected error.", sys.exc_info()

      if anchore:
        #call the anchore 'delete' 
        anchore_delete(digest)

      row = select_cursor.fetchone()

    conn.close()
    return
  except:
    print "Unexpected error.", sys.exc_info()

def print_servers():
   for k,v in images.iteritems():
     print "Server: " + k

def print_images():
   for k,v in images.iteritems():
     print "Server: " + k
     for image_name,image_record in v.iteritems():
       print "  Image: " + image_name + " (" + image_record.type + ")"

def check_images():
   for k,v in images.iteritems():
     for image_name,image_record in v.iteritems():
       anchore_check(image_name,k)
              
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

   if 'POSTGRES_USERNAME' in os.environ:
      connect_record.username = os.environ['POSTGRES_USERNAME']

   if 'POSTGRES_PASSWORD' in os.environ:
      connect_record.password = os.environ['POSTGRES_PASSWORD']

   if 'POSTGRES_ENDPOINT' in os.environ:
      connect_record.endpoint = os.environ['POSTGRES_ENDPOINT']

   if 'POSTGRES_DATABASE' in os.environ:
      connect_record.database = os.environ['POSTGRES_DATABASE']

   if 'SSL_VERIFY' in os.environ:
      if os.environ['SSL_VERIFY'].lower() == "false":
        kwargs['verify'] = False
      else:
        kwargs['verify'] = os.environ['SSL_VERIFY']
        
   baker.run()
