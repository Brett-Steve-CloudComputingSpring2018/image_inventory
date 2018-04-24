#!/usr/bin/python

import baker
import json
import subprocess

results = {}
def anchore_check(image_name, server=""):

  if server:
    full_image_name = server + "/" + image_name
  else:
    full_image_name = image_name
  print "Checking " + full_image_name

  response = subprocess.check_output("anchore-cli --json image add " + full_image_name, shell=True)
  json_out = json.loads(response)
  #pick out the digest
  digest = json_out[0]['imageDigest']

  response = subprocess.check_output("anchore-cli --json image vuln " + digest + " os", shell=True)
  json_out = json.loads(response)
  print type(json_out)
  for row in json_out['vulnerabilities']:
    print row['vuln'] + ", " + row['severity']
