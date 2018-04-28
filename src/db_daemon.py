#!/usr/bin/python

import daemon
import time
import anchore_check
import psycopg2
from datetime import datetime


# NOTE - postgres stuff is hardcoded in temporarily
POSTGRES_NAME = 'csci5799'
POSTGRES_USERNAME = 'csciuser'
POSTGRES_PASSWORD = 'csci5799'
POSTGRES_HOST = 'csci5799-postgres.crzz7sianr5s.us-west-2.rds.amazonaws.com'
POSTGRES_PORT = '5432'


"""
Connects to the postgres database and return the connection() instance
"""
def conn_to_postgres():
    
    newConn = psycopg2.connect(dbname=POSTGRES_NAME, user=POSTGRES_USERNAME, password=POSTGRES_PASSWORD, host=POSTGRES_HOST, port=POSTGRES_PORT)
    return newConn

def postgres_cursor(connection):
    
    newCursor = connection.cursor()
    return newCursor

def query_db():
    
    conn = conn_to_postgres()
    conn.autocommit = True
    img_curs = postgres_cursor(conn)
    vuln_curs = postgres_cursor(conn)
    
    img_curs.execute("SELECT * FROM images_import")
    
    # iterate over the rows of the database
    img_row = img_curs.fetchone()
    while img_row:
        
        img_name = img_row[0]
        img_status = img_row[1]
        img_repo = img_row[2]
        imp_src = img_row[3]
        img_digest = img_row[4]
            
            
        # make sure the current image has been passed to anchore already
        if img_status == 'PENDING':
            
            # XXX - just a debug print
            print "Pending Record Found: " + img_digest
            
            # returns a json object
            anchore_data = anchore_check.anchore_check(conn, img_digest)
                        
            # if the function returns something other than 'none' we can insert
            # the vulterability info into the vulnerabilities database
            if anchore_data:

                # get a list of the vulnerabilities from the json object
                vuln_list = anchore_data['vulnerabilities']
                
                # extract each vulnerability for the current digest
                for vuln in vuln_list:
                    
                    cve = vuln["vuln"]
                    # fix = vuln["fix"]
                    package = vuln["package"]
                    severity = vuln["severity"]

                    vuln_curs.execute("INSERT INTO vulnerabilities (sha256_digest,cve,package,severity) VALUES (%s,%s,%s,%s)", (img_digest, cve, package, severity))
            
            
                # TODO add timestamp to the database entry for start time
                # TODO - if anchore is finished, update images_import db to show
                # the status as complete

        # fetch the next image row
        img_row = img_curs.fetchone()
        
        
        
'''
Want to run the anchore_check as a background daemon since it should be
continually querying the anchore engine/database to check if the images are done
being scanned.
'''
def run():
    
    # uncomment next line to run as daemon...
    # with daemon.DaemonContext():
    query_db()
    time.sleep(5) # sleep for 5 seconds between each iteration over the database
                        # NOTE - I need to think about the behavior of this a little more...



if __name__ == "__main__":
    
    run()
