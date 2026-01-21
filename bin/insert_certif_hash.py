#!/usr/bin/env python3
# insert certif hash into school DB

import getopt
import os
import sys
import hashlib
import psycopg2

SITE_NUM=1
DB_HOST='localhost'

#DB_HOST='10.0.0.16'

def usage():
    print('usage:{} year compet_id'.format(sys.argv[0]), file=sys.stderr)
    sys.exit(-1)

def error(s):
    print('error: {}'.format(s), file=sys.stderr)
    sys.exit(-1)

def insert_certif_hash_compet(connection,cursor,compet_id,dbname):
    '''Inserts school hash in db '''

    #comm = "select distinct compet_school_id from compet"
    if compet_id != 0:
        comm = f"select compet_id,compet_name,compet_year from compet where compet_id={compet_id}"
    else:
        comm = f"select compet_id,compet_name,compet_year from compet"
    cursor.execute(comm)
    compets = cursor.fetchall()
    for compet in compets:
        compet_id = compet[0]
        compet_name = compet[1]
        compet_year = compet[2]
        #print(compet_id,compet_name,compet_year)
        tmp = '{}{}{}'.format(compet_id,compet_name,compet_year)
        hash = hashlib.sha224(tmp.encode('utf-8')).hexdigest()[:24]
        #print(hash)
        comm = f"insert into certif_hash (compet_id,hash) values('{compet_id}','{dbname}:{hash}')"
        cursor.execute(comm)
        #print(comm)
        #print('inserted hash for compet_id={}'.format(compet_id))
        connection.commit()

def insert_certif_hash_colab(connection,cursor,colab_id,dbname):
    '''Inserts school hash in db '''

    #comm = "select distinct colab_school_id from colab"
    if colab_id != 0:
        comm = f"select colab_id,colab_name,colab_email from colab where colab_id={colab_id}"
    else:
        comm = f"select colab_id,colab_name,colab_email from colab"
    cursor.execute(comm)
    colabs = cursor.fetchall()
    for colab in colabs:
        colab_id = colab[0]
        colab_name = colab[1]
        colab_email = colab[2]
        #print(colab_id,colab_name,colab_email)
        tmp = '{}{}{}'.format(colab_id,colab_name,colab_email)
        hash = hashlib.sha224(tmp.encode('utf-8')).hexdigest()[:24]
        #print(hash)
        comm = f"insert into certif_hash (colab_id,hash) values('{colab_id}','{dbname}:{hash}')"
        cursor.execute(comm)
        #print(comm)
        #print('inserted hash for colab_id={}'.format(colab_id))
        connection.commit()

def insert_certif_hash_coord(connection,cursor,school_id,dbname):
    '''Inserts school hash in db '''

    #comm = "select distinct deleg_school_id from deleg"
    if school_id != 0:
        comm = f"select school_id,school_deleg_name,school_deleg_email from school where school_id={school_id}"
    else:
        comm = f"select school_id,school_deleg_name,school_deleg_email from school where school_ok"

    cursor.execute(comm)
    schools = cursor.fetchall()
    for school in schools:
        school_id = school[0]
        deleg_name = school[1]
        deleg_email = school[2]
        #print(school_id,deleg_name,deleg_email)
        tmp = '{}{}{}'.format(school_id,deleg_name,deleg_email)
        hash = hashlib.sha224(tmp.encode('utf-8')).hexdigest()[:24]
        #print(hash)
        comm = f"insert into certif_hash (school_id,hash) values('{school_id}','{dbname}:{hash}')"
        cursor.execute(comm)
        #print(comm)
        #print('inserted hash for school_id={}'.format(school_id))
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
        year = args[0]
        compet_id = int(args[1])
    except:
        print('error: need a dbname and a compet_id (zero for all compets)',file=sys.stderr)
        usage()

    dbname = f'obi{year}'
    try:
        conn = psycopg2.connect("dbname='{}' user='obi' host={} password='guga.LC'".format(dbname, DB_HOST))
    except:
        print("unable to connect")
        
    conn.set_client_encoding('UTF8')
    cur = conn.cursor()
    insert_certif_hash_compet(conn,cur,compet_id,year)
    insert_certif_hash_colab(conn,cur,compet_id,year)
    insert_certif_hash_coord(conn,cur,compet_id,year)
    
    
if __name__ == "__main__":
    main()
