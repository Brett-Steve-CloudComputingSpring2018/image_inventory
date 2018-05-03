#!/usr/bin/python

import baker
import json
import subprocess
import time
import psycopg2
import os
import sys

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
  image_size_bytes = json_out[0]['image_content']['metadata']['image_size']
  image_layer_count = json_out[0]['image_content']['metadata']['layer_count']
  image_updated_date = json_out[0]['image_detail'][0]['last_updated']
  print "Anchore returns " + digest
  try:
    cursor = conn.cursor()
    cursor.execute("UPDATE images_import SET status=%s,sha256_digest=%s,image_layer_count=%s,image_size_bytes=%s,image_updated_date=%s WHERE repository=%s and name=%s and import_source=%s", ("PENDING",digest,image_layer_count,image_size_bytes,image_updated_date,server,image_name,import_source))
  except:
    print "Unexpected error.", sys.exc_info()

#This will require the sha256 digest to look up
def anchore_check(conn,digest):
  try:
    response = subprocess.check_output("anchore-cli --json image vuln " + digest + " os", shell=True)
    json_out = json.loads(response)
    return json_out
  except subprocess.CalledProcessError, e:
    print "vuln output:\n", e.output
    try:
      output_failed_cursor = conn.cursor()
      output_failed_cursor.execute("UPDATE images_import SET status=%s, timestamp_done = now(), notes = %s WHERE sha256_digest=%s", ('FAILED', e.output, digest))
    except:
      print "Unexpected error.", sys.exc_info()

@baker.command()
def anchore_delete_all():
  anchore_disable_subscription_all()
  try:
    response = subprocess.check_output("anchore-cli --json image list", shell=True)
  except subprocess.CalledProcessError, e:
    print "Error listing output:\n", e.output
    return
  json_out = json.loads(response)
  for row in json_out:
    anchore_delete(row['imageDigest'])
 
def anchore_delete(digest):
  print "Removing " + digest
  try:
    response = subprocess.check_output("anchore-cli --json image del " + digest, shell=True)
  except subprocess.CalledProcessError, e:
    print "Error deleting output:\n", e.output
    return
  except:
    print "Unexpected error.", sys.exc_info()

def anchore_disable_subscription(fulltag,subtype="vuln_update"):
  print "Disabling " + fulltag + " for type = " + subtype
  try:
    response = subprocess.check_output("anchore-cli --json subscription deactivate " + subtype + " " + fulltag, shell=True)
  except subprocess.CalledProcessError, e:
    print "Error disablig output:\n", e.output
    return
  except:
    print "Unexpected error.", sys.exc_info()

@baker.command()
def anchore_disable_subscription_all():
  try:
    response = subprocess.check_output("anchore-cli --json subscription list", shell=True)
  except subprocess.CalledProcessError, e:
    print "Error disablig output:\n", e.output
    return
  except:
    print "Unexpected error.", sys.exc_info()
  json_out = json.loads(response)
  for row in json_out:
    if row["active"]:
      anchore_disable_subscription(row["subscription_key"],row["subscription_type"])

if __name__ == '__main__':
  import os
  baker.run()
  
