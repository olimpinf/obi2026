#!/usr/bin/env python3
# insert flatpages into django

import getopt
import os
import sys

import psycopg2
from psycopg2.extras import DictCursor

DB_NAME='obi2021'
DB_HOST='localhost'
#DB_HOST='10.0.0.16'

def usage():
    print('usage:{} '.format(sys.argv[0]), file=sys.stderr)
    sys.exit(-1)

def error(s):
    print('error: {}'.format(s), file=sys.stderr)
    sys.exit(-1)


def main():
    global reset
    try:
        conn = psycopg2.connect("dbname='{}' user='obi' host={} password='guga.LC'".format(DB_NAME, DB_HOST))
    except:
        print("unable to connect to", DB_NAME, DB_HOST)
        sys.exit(-1)
    try:
        opts, args = getopt.getopt(sys.argv[1:], "r", ["reset"])
    except getopt.GetoptError as err:
        print(err, file=sys.stderr) 
        usage()

    # Abre conexao com BD
    conn.set_client_encoding('utf-8')
    curs = conn.cursor(cursor_factory=DictCursor)

    comm = "select school_id,school_inep_code,school_code,school_name,school_type,school_deleg_name,school_deleg_email,school_deleg_username,school_ok,school_is_known,school_state,school_city,school_zip,school_address,school_address_number,school_address_complement,school_address_district,school_phone,school_deleg_phone,school_deleg_login,school_ddd,school_prev,school_is_site_phase3,school_site_phase3_show,school_site_phase3_type,school_site_phase3,school_site_phase3_ini,school_site_phase3_prog,school_address_building,school_address_map,school_has_medal,school_hash,school_turn_phase1_prog,school_turn_phase1_ini from school where school_ok=false order by school_id"
    curs.execute(comm)
    data = curs.fetchall()
    
    for d in data:
        print("insert into school (school_inep_code,school_code,school_name,school_type,school_deleg_name,school_deleg_email,school_deleg_username,school_ok,school_is_known,school_state,school_city,school_zip,school_address,school_address_number,school_address_complement,school_address_district,school_phone,school_deleg_phone,school_deleg_login,school_ddd,school_prev,school_is_site_phase3,school_site_phase3_show,school_site_phase3_type,school_site_phase3,school_site_phase3_ini,school_site_phase3_prog,school_address_building,school_address_map,school_has_medal,school_hash,school_turn_phase1_prog,school_turn_phase1_ini) values ( '{}',  '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(d['school_inep_code'],d['school_code'],d['school_name'],d['school_type'],d['school_deleg_name'],d['school_deleg_email'],d['school_deleg_username'],d['school_ok'],d['school_is_known'],d['school_state'],d['school_city'],d['school_zip'],d['school_address'],d['school_address_number'],d['school_address_complement'],d['school_address_district'],d['school_phone'],d['school_deleg_phone'],d['school_deleg_login'],d['school_ddd'],d['school_prev'],d['school_is_site_phase3'],d['school_site_phase3_show'],d['school_site_phase3_type'],d['school_site_phase3'],d['school_site_phase3_ini'],d['school_site_phase3_prog'],d['school_address_building'],d['school_address_map'],d['school_has_medal'],'','',''))

if __name__ == "__main__":
    main()
