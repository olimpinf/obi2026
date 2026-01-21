#!/usr/bin/env python3
# show diffs for contenstants submissions

import getopt
import html
import os
import re
import sys


def usage():
    print('usage:{} file_input file_output'.format(sys.argv[0]), file=sys.stderr)
    sys.exit(-1)

def error(s):
    print('error:{}'.format(s), file=sys.stderr)
    usage()

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "a", ["all"])
    except getopt.GetoptError as err:
        print(err, file=sys.stderr) 
        usage()
    all = False
    for o, a in opts:
        if o in ("-a", "--all"):
            all = True
        else:
            assert False, "unhandled option"

    try:
        fname = args[0]
        fname_output = args[1]
    except:
        print('error: need two filenames',file=sys.stderr)
        usage()

    with open(fname, "r") as f:
        lines = f.readlines()

    cluster_links = []
    links = []
    cur_cluster = ''
    for line in lines:
        
        # cluster;task; compet_type; compet_id; compet_name; school; score; link
        try:
            cluster, task, compet_type, compet_id, compet_name, school, score, link = line.strip().split(';')
            links.append((link,school))
        except:
            cluster  = line.strip().split(';')[0]
            if cluster != cur_cluster:
                if len(links) > 0:
                    cluster_links.append((cur_cluster, links))
                cur_cluster = cluster
                links = []
                
    if len(links) > 0:
        cluster_links.append((cur_cluster, links))

    with open(file_output, "a") as fin:
    
        for cluster_link in cluster_links:
            links = cluster_link[1]
            for i in range(len(links)-1):
                first_link = links[i][0][31:]
                second_link = links[i+1][0][31:]
                fix_no_endline(first_link, "/tmp/file1")
                fix_no_endline(second_link, "/tmp/file2")
                first_school = links[i][1]
                second_school = links[i+1][1]
                os.system("clear")
                os.system(f"sdiff /tmp/file1 /tmp/file2")
                print("------------------------------------------")
                print(f"{first_school}   -----   {second_school}")
                print()
                s = input("y/n ?")
                if s == 'q':
                    return
                elif s == 'y':
                    print(",".join([compet_id_full,])

def fix_no_endline(oldfname, newfname):
    with open(oldfname, "r") as fin:
        with open(newfname, "w") as fout:
            fout.write(fin.read())
            fout.write("\n")
            
            
if __name__ == "__main__":
    main()
