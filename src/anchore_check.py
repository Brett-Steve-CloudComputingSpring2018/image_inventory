#!/usr/bin/python

import baker
import json
import subprocess
import time

results = {}
def anchore_check(image_name, server=""):

  if server:
    full_image_name = server + "/" + image_name
  else:
    full_image_name = image_name
  print "Checking " + full_image_name

  try:
    response = subprocess.check_output("anchore-cli --json image add " + full_image_name, shell=True)
  except subprocess.CalledProcessError, e:
    print "add output:\n", e.output
    return
  json_out = json.loads(response)
  #pick out the digest
  digest = json_out[0]['imageDigest']

  #give it time to work... cheesy but effective
  time.sleep(15)

  try:
    response = subprocess.check_output("anchore-cli --json image vuln " + digest + " os", shell=True)
  except subprocess.CalledProcessError, e:
    print "vuln output:\n", e.output
    return
  json_out = json.loads(response)
  print type(json_out)
  for row in json_out['vulnerabilities']:
    print row['vuln'] + ", " + row['severity']
