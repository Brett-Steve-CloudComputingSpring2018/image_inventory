#!/usr/bin/python

import baker
import json
import subprocess
import time
import psycopg2

results = {}
def anchore_add(conn,image_name,import_source,server=""):

  print "Adding to anchore " + image_name
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
  print "Anchore returns " + digest
  try:
    cursor = conn.cursor()
    cursor.execute("UPDATE images_import SET status=%s,sha256_digest=%s WHERE repository=%s and name=%s and import_source=%s", ("PENDING",digest,server,image_name,import_source))
  except:
    print "Unexpected error.", sys.exc_info()

#This will require the sha256 digest to look up
def anchore_check(conn,digest):
  try:
    response = subprocess.check_output("anchore-cli --json image vuln " + digest + " os", shell=True)
  except subprocess.CalledProcessError, e:
    print "vuln output:\n", e.output
    return
  json_out = json.loads(response)
  
  #TODO output vulns to database
  print type(json_out)
  for row in json_out['vulnerabilities']:
    print row['vuln'] + ", " + row['severity']
