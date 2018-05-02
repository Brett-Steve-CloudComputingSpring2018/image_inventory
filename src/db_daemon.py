#!/usr/bin/python

import daemon
import time
import anchore_check
import psycopg2


# NOTE - postgres credentials are hardcoded in temporarily
# I know I shouldn't be doing it like this, but right now I don't care
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

"""
query_db() connects to the postgres database and performs a number of functions:

1. It selects each image that is currently logged in the images_import table.
2. Using the sha256 hash it connects to the running anchore engine we have running
   to see if there is a result ready yet.
3. If there is a result, it takes the output json and logs that info into the
   vulnerabilities table in the database.
4. It updates the timestamp in the images_import table for the completion time
   of the vulnerability scan.

"""
def query_db():
    
    conn = conn_to_postgres()
    conn.autocommit = True # make sure any querys that change the database get pushed immediately
    img_curs = postgres_cursor(conn)
    t_stamp_curs = postgres_cursor(conn)
    vuln_curs = postgres_cursor(conn)
    
    
    # FIXME - I should probably break this giant block of code up but I don't
    # feel like it right now.
    
    while True:
        
        img_curs.execute("SELECT * FROM images_import")
        
        # iterate over each row of the table that img_curs points to
        for img_row in img_curs:
            
            img_name = img_row[0]
            img_status = img_row[1]
            img_repo = img_row[2]
            imp_src = img_row[3]
            img_digest = img_row[4]
                
            # make sure the current image has been passed to anchore already
            if img_status == 'PENDING':
                
                # XXX - just a debug print statement
                #print "Pending Record Found: " + img_digest
                
                # returns a json object and store in anchore_data
                anchore_data = anchore_check.anchore_check(conn, img_digest)
                        
                # if the function returns something other than 'none' we can insert
                # the vulterability info into the vulnerabilities database
                if anchore_data:
                    
                    # update the finished timestamp and show the status as complete in images_import database
                    t_stamp_curs.execute("UPDATE images_import SET status=%s, timestamp_done = now() WHERE name=%s", ('COMPLETE', img_name))

                    # get a list of the vulnerabilities from the json object
                    vuln_list = anchore_data['vulnerabilities']
                    
                    # extract each vulnerability for the current digest
                    for vuln in vuln_list:
                        
                        cve = vuln["vuln"]
                        # fix = vuln["fix"]
                        package = vuln["package"]
                        severity = vuln["severity"]

                        vuln_curs.execute("INSERT INTO vulnerabilities (sha256_digest,cve,package,severity) VALUES (%s,%s,%s,%s)", (img_digest, cve, package, severity))
    
        time.sleep(1) # sleep for 1 second between each iteration over the database
                        # NOTE - I need to think about the behavior of this a little more...
                        # It could just run continuously without bothering to sleep I guess...
            
        
'''
Want to run the anchore_check as a background daemon since it should be
continually querying the anchore engine/database to check if the images are done
being scanned.
'''
def run():
    
    # comment out/uncomment next line to run as daemon or not
    with daemon.DaemonContext():
        query_db()

if __name__ == "__main__":
    
    run()
