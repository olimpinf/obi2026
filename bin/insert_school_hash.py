#!/usr/bin/env python3
# insert hash into school DB

import getopt
import os
import sys
import hashlib
import psycopg2

SITE_NUM=1
DB_HOST='localhost'
#DB_HOST='10.0.0.16'

def usage():
    print('usage:{} dbname'.format(sys.argv[0]), file=sys.stderr)
    sys.exit(-1)

def error(s):
    print('error: {}'.format(s), file=sys.stderr)
    sys.exit(-1)

def insert_school_hash(connection,cursor,school_id):
    '''Inserts school hash in db '''
    print('school hash ',end='')

    #comm = "select distinct compet_school_id from compet"
    if school_id != 0:
        comm = f"select school_id,school_name,school_city from school where school_ok and school_id={school_id}"
    else:
        comm = "select school_id,school_name,school_city from school where school_ok"
    cursor.execute(comm)
    schools = cursor.fetchall()
    for school in schools:
        school_id = school[0]
        school_name = school[1]
        school_city = school[2]
        print(school_id,school_name,school_city)
        tmp = '{}{}{}'.format(school_id,school_name,school_city)
        hash = hashlib.sha224(tmp.encode('utf-8')).hexdigest()
        print(hash)
        comm = "update school set school_hash='{}' where school_id={}".format(hash,school_id)
        cursor.execute(comm)
        #print(comm)
        print('inserted hash for school_id={}'.format(school_id))
        connection.commit()

def main():
    global reset
    try:
        opts, args = getopt.getopt(sys.argv[1:], "r", ["reset"])
    except getopt.GetoptError as err:
        print(err, file=sys.stderr) 
        usage()
    reset = False
    for o, a in opts:
        if o in ("-r", "--reset"):
            reset = True
        else:
            assert False, "unhandled option"

    try:
        dbname = args[0]
        school_id = int(args[1])
    except:
        print('error: need a dbname and a school_id (zero for all schools)',file=sys.stderr)
        usage()

    try:
        conn = psycopg2.connect("dbname='{}' user='obi' host={} password='guga.LC'".format(dbname, DB_HOST))
    except:
        print("unable to connect")
        
    conn.set_client_encoding('UTF8')
    cur = conn.cursor()
    insert_school_hash(conn,cur,school_id)

if __name__ == "__main__":
    main()
