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
URL_SERVICE = "/services/"
URL_ENVIRONMENT = "/projects/"
USERNAME = "userid"
PASSWORD = "password"
kwargs = {}

# HTTP
def get(url):
   r = requests.get(url, auth=(USERNAME, PASSWORD), **kwargs)
   r.raise_for_status()
   return r

def post(url, data=""):
   if data:
      r = requests.post(url, data=json.dumps(data), auth=(USERNAME, PASSWORD), **kwargs)
   else:
      r = requests.post(url, data="", auth=(USERNAME, PASSWORD), **kwargs)
   r.raise_for_status()
   return r.json()

def delete(url, data=""):
   if data:
      r = requests.delete(url, data=json.dumps(data), auth=(USERNAME, PASSWORD), **kwargs)
   else:
      r = requests.delete(url, data="", auth=(USERNAME, PASSWORD), **kwargs)
   r.raise_for_status()
   return r.json()

# Websocket
def ws(url):
  webS = websocket.create_connection(url)
  resp = base64.b64decode( webS.recv() )
  webS.close()
  return resp

# Helper
def print_json(data):
   print json.dumps(data, sort_keys=True, indent=3, separators=(',', ': '))


#
# Query the service configuration.
#
@baker.command(default=True, params={"service_id": "The ID of the service to read (optional)"})
def query(service_id=""):
   """Retrieves the service information.

   If you don't specify an ID, data for all services
   will be retrieved.
   """

   r = get(HOST + URL_SERVICE + service_id)
   print_json(r.json())

#
# Converts a service name into an ID
#
@baker.command(params={
                        "name": "The name of the service to lookup.",
                        "newest": "From list of IDs, return newest (optional)"})
def id_of (name="", newest=False):
   """Retrieves the ID of a service, given its name.
   """
   if newest:
    index = -1
   else:
    index = 0

   service = get(HOST + "/services?name=" + name).json()
   return service['data'][index]['id']

#
# Converts a environment name into an ID
#
@baker.command(params={"name": "The name of the environment to lookup."})
def id_of_env (name=""):
   """Retrieves the ID of a project, given its name.
   """

   environment = get(HOST + "/project?name=" + name).json()
   return environment['data'][0]['id']

#
# Start containers within a service (e.g. for Start Once containers).
#
@baker.command(params={"service_id": "The ID of the service to start the containers of."})
def start_containers (service_id):
   """Starts the containers of a given service, typically a Start Once service.
   """
   start_service (service_id)

#
# Start containers within a service (e.g. for Start Once containers).
#
@baker.command(params={"service_id": "The ID of the service to start the containers of."})
def start_service (service_id):
   """Starts the containers of a given service, typically a Start Once service.
   """

   # Get the array of containers
   containers = get(HOST + URL_SERVICE + service_id + "/instances").json()['data']
   for container in containers:
      start_url = container['actions']['start']
      print "Starting container %s with url %s" % (container['name'], start_url)
      post(start_url, "")


#
# Stop containers within a service.
#
@baker.command(params={"service_id": "The ID of the service to stop the containers of."})
def stop_service (service_id):
   """Stop the containers of a given service.
   """

   # Get the array of containers
   containers = get(HOST + URL_SERVICE + service_id + "/instances").json()['data']
   for container in containers:
      stop_url = container['actions']['stop']
      print "Stopping container %s with url %s" % (container['name'], stop_url)
      post(stop_url, "")

#
# Get a service state
#
@baker.command(default=True, params={"service_id": "The ID of the service to read"})
def state(service_id=""):
   """Retrieves the service state information.
   """

   r = get(HOST + URL_SERVICE + service_id)
   print(r.json()["state"])


#
# Script's entry point, starts Baker to execute the commands.
# Attempts to read environment variables to configure the program.
#
if __name__ == '__main__':
   import os

   # support for new Rancher agent services
   # http://docs.rancher.com/rancher/latest/en/rancher-services/service-accounts/
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
