#!/usr/bin/python

import daemon
import time
import anchore_check
import psycopg2
from datetime import datetime # for getting timestamps when anchore is finished


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

def querey_db():
    
    conn = conn_to_postgres()
    curs = postgres_cursor(conn)
    
    
    # iterate over the rows of the database
    dbRow = curs.fetchone()
    while dbRow:
        
        name = dbRow[0]
        status = dbRow[1]
        repo = dbRow[2]
        imp_src = dbRow[3]
        
        if status == 'NEW':
            # add to anchore
            # QUESTION is the source="" in the anchore_add definition the same as the repository
            anchore_add(conn, name, imp_src, repository)
            
            # TODO add timestamp to the database entry for start time
            
        elif status == 'PENDING':
            # querey anchore to see if it's done yet
            # NOTE - need the sha256 digest
            anchore_check(conn, digest)
            
            # TODO - if anchore is finished, add entry for finish time to database
        
        print dbRow # NOTE debug print
        
        # fetch the next row of the database
        dbRow = curs.fetchone()
        
        
        
'''
Want to run the anchore_check as a background daemon since it should be
continually querying the anchore engine/database to check if the images are done
being scanned.
'''
def run():
    
    with daemon.DaemonContext():
        time.sleep(15) # sleep for 15 seconds between each iteration over the database
                        # NOTE - I need to think about the behavior of this a little more...
        query_db()
        # run anchore check here


# NOTE - I'm not sure if the way I have the daemon set up is super hacky


if __name__ == "__main__":
    
    run()
