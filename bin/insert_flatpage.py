#!/usr/bin/env python3
# insert flatpages into django

import getopt
import os
import sys
import re

import psycopg2

SITE_NUM=1
DB_NAME='obi2026'
DB_HOST='localhost'
#DB_HOST='10.0.0.16'

def usage():
    print('usage:{} page.html'.format(sys.argv[0]), file=sys.stderr)
    sys.exit(-1)

def error(s):
    print('error: {}'.format(s), file=sys.stderr)
    sys.exit(-1)

def insert_pages(fname,connection,cursor):
    if not os.path.isdir(fname):
        print("error: -a needs a directory as argument")
        usage()
    # remove all pages if required
    if reset:
        comm = "delete from django_flatpage"
        cursor.execute(comm)
        comm = "delete from django_flatpage_sites"
        cursor.execute(comm)
        connection.commit()
    for root, dirs, files in os.walk(fname):
        for name in files:
            base,ext = os.path.splitext(name)
            if ext == ".html":
                insert_page(os.path.join(root,name),connection,cursor)

def insert_page(fname,connection,cursor):
    '''Inserts of updates a flatpage '''
    print('insert_page',fname,end='')
    with open(fname,"r",encoding='utf-8') as f:
        data = f.read()

    pattern = r'{%\s*comment\s*%}.*?{%\s*endcomment\s*%}'

    data = re.sub(pattern, ' ', data, flags=re.DOTALL)
    data = data.split("\n")

    # with open(fname,"r") as f:
    #     data = f.readlines()
    # try:
    #     with open(fname,"r",encoding='utf-8') as f:
    #         data = f.readlines()
    # except:
    #     usage()
    tmp_url = fname
    tmp_title = data[0].strip()
    tmp_template = data[1].strip()
    if tmp_title.find('title:') != 0:
        error('expected title at second line')
    if tmp_template.find('template:') != 0:
        error('expected template at third line')
    start = tmp_url.find('html/')
    if start < 0:
        error('path to filename must include html/')
    url = '/'+tmp_url[start+5:].replace('.html','/')
    title = tmp_title[6:]
    template = tmp_template[9:].strip()
    print(' as',url)

    content = " ".join(data[2:])

    #content = content.replace("'Oeste"," Oeste")
    
    comm = "select id from django_flatpage where url='{}'".format(url)
    cursor.execute(comm)
    try:
        # if there is already a page with same url, update it
        page_id = int(cursor.fetchone()[0])
        comm = "update django_flatpage set url=%s,title=%s,content=%s,enable_comments=%s,template_name=%s,registration_required=%s where id=%s"
        cursor.execute(comm,(url,title,"".join(content),False,template,False,page_id))
        connection.commit()
        print('updated')
    except:
        # new page, insert it
        comm = "insert into django_flatpage(url,title,content,enable_comments,template_name,registration_required) values ('{}','{}','{}',{},'{}',{}) returning id;".format(url,title,"".join(content),False,template,False)
        cursor.execute(comm)
        last_page_id = int(cursor.fetchone()[0])
        site = SITE_NUM
        #comm = 'insert into django_flatpage_sites(id, site_id) values ({},{})'.format(last_page_id,site)
        comm = 'insert into django_flatpage_sites(flatpage_id, site_id) values ({},{})'.format(last_page_id,site)
        cursor.execute(comm)
        connection.commit()
        print('inserted')

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
    reset = False
    for o, a in opts:
        if o in ("-r", "--reset"):
            reset = True
        else:
            assert False, "unhandled option"

    conn.set_client_encoding('UTF8')
    cur = conn.cursor()
    try:
        fname = args[0]
    except:
        print('error: need a filename or a dirname',file=sys.stderr)
        usage()
    if os.path.isdir(fname):
        insert_pages(fname,conn,cur)
    else:
        insert_page(fname,conn,cur)

if __name__ == "__main__":
    main()
