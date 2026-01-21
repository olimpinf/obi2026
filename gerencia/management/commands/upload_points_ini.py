import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from principal.models import LEVEL, LEVEL_NAME, Compet, School
#from fase2.utils.check_solutions_file import Error, check_solutions_file
from principal.utils.check_compet_points_batch import check_compet_points_batch
from principal.utils.utils import format_compet_id

class Command(BaseCommand):
    help = 'Upload points, init compets'

    def add_arguments(self, parser):
        parser.add_argument('archive', nargs='+', type=str)
        parser.add_argument('school_id', nargs='+', type=int)
        parser.add_argument('phase', nargs='+', type=int)
        parser.add_argument('max_points', nargs='+', type=int)

    def handle(self, *args, **options):
        archive = options['archive'][0]
        phase = options['phase'][0]
        school_id = options['school_id'][0]
        max_points = options['max_points'][0]
        msg,errors,validated_compet_points = check_compet_points_batch(archive,school_id,max_points,phase=phase,is_superuser=True)
        if msg:
            print(msg)
            for e in errors:
                print(e)
            return
        
        valid = []
        if len(errors)==0 and len(msg)==0:
            for c,p in validated_compet_points:
                c = Compet.objects.get(pk=c)
                #if c.compet_type != level_num:
                #    print("ERROR, wrong compet type",c.compet_type, level_num)
                #    continue
                if (phase==1):
                    if c.compet_points_fase1 == None:
                        print(c.compet_id_full, 'none', '-->', p)
                    elif c.compet_points_fase1 < p:
                        print(c.compet_id_full, c.compet_points_fase1, '-->', p)
                    c.compet_points_fase1 = p
                elif (phase==2):
                    if c.compet_classif_fase1:
                        if not c.compet_points_fase2:
                            print(c.compet_id_full, 'none', '-->', p)
                        elif c.compet_points_fase2 < p:
                            print(c.compet_id_full, c.compet_points_fase2, '-->', p)

                        c.compet_points_fase2 = p
                    else:
                        print("ERROR, compet not classif",c.compet_id_full)
                elif (phase==3):
                    if c.compet_classif_fase2:
                        if not c.compet_points_fase2:
                            print(c.compet_id_full, 'none', '-->', p)
                        elif c.compet_points_fase3 < p:
                            print(c.compet_id_full, c.compet_points_fase3, '-->', p)
                        else:
                            print(c.compet_id_full, 'DIMINISHING POINTS?', c.compet_points_fase3, '-->', p)
                            continue
                        c.compet_points_fase3 = p
                    else:
                        print("ERROR, compet not classif",c.compet_id_full)
                else:
                    print("ERROR")
                    return
                c.save()
                #valid.append({'id':format_compet_id(c.compet_id),'name':c.compet_name,'points':c.compet_points_fase2,'level':LEVEL_NAME[c.compet_type]})

        #for v in valid:
        #    print(v)
        if errors:
            print("num linha, erro, linha")
        for error in errors:
            print(error.linenum, error.msg, error.line)
        self.stdout.write(self.style.SUCCESS('OK'))
