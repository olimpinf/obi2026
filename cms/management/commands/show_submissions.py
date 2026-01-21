import base64
import logging
import os
import re
import shutil
import sys
from time import sleep

from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group, UserManager

from principal.models import School, Compet, CompetCfObi, LEVEL, PJ, P1, P2, PS, CF
#from cfobi.models import CompetCfObi
from principal.utils.utils import (obi_year,
                                   verify_compet_id,
                                   format_compet_id,)
from obi.settings import BASE_DIR

logger = logging.getLogger(__name__)


COMPET_LEVEL = {3:"P1", 4:"P2", 5:"PJ", 6:"PS", 8:"CF"}

def fix_no_endline(oldfname, newfname):
    with open(oldfname, "r") as fin:
        with open(newfname, "w") as fout:
            fout.write(fin.read())
            fout.write("\n")
            
def show_submissions(input_file, output_file):
    with open(input_file, "r") as f:
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

    compet_seen = set()
    for cluster_link in cluster_links:
        links = cluster_link[1]
        for i in range(len(links)-1):
            first_link = links[i][0][31:]
            second_link = links[i+1][0][31:]
            fix_no_endline(first_link, "/tmp/file1")
            fix_no_endline(second_link, "/tmp/file2")

            # static/dupl-fase1/submissions_all/py/dieta/72106-dieta-sub133230_py.txt
            pattern = re.compile(fr"(\d+)-(\w+)-sub(\d+)_(\w+).txt")
            match = re.search(pattern, first_link)
            compet_id = match.groups()[0]
            compet1 = Compet.objects.get(compet_id=compet_id)
            school1 = School.objects.get(school_id=compet1.compet_school_id)

            match = re.search(pattern, second_link)
            compet_id = match.groups()[0]
            compet2 = Compet.objects.get(compet_id=compet_id)
            school2 = School.objects.get(school_id=compet2.compet_school_id)
            
            os.system("clear")
            os.system(f"sdiff /tmp/file1 /tmp/file2")
            print("------------------------------------------")
            print(f"{school1.school_name} ({school1.school_city}, {school1.school_state})   -----   {school2.school_name} ({school2.school_city}, {school2.school_state})")
            print()
            
            s = input("y/n ?")
            if s == 'q':
                return
            elif s == 'y':
                # static/dupl-fase1/submissions_all/py/dieta/72106-dieta-sub133230_py.txt
                if compet1.compet_id not in compet_seen:
                    compet_seen.add(compet1.compet_id)
                    with open(output_file, 'a') as fout:
                        print(",".join([compet1.compet_id_full, f"{compet1.compet_school_id}", "cópia", "1"]), file=fout)
                if compet2.compet_id not in compet_seen:
                    compet_seen.add(compet2.compet_id)
                    with open(output_file, 'a') as fout:
                        print(",".join([compet2.compet_id_full, f"{compet2.compet_school_id}", "cópia", "1"]), file=fout)
                else:
                    continue
                
                
class Command(BaseCommand):
    help = 'Show submissions side by side, for checking copies'

    def add_arguments(self, parser):
        parser.add_argument('input_file', nargs='+', type=str)
        parser.add_argument('output_file', nargs='+', type=str)

    def handle(self, *args, **options):
        input_file = options['input_file'][0]
        output_file = options['output_file'][0]

        show_submissions(input_file, output_file)
        print("finished")
