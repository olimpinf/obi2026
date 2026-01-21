import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.models import Q

from week.models import Week
from principal.models import LEVEL, Compet

class Command(BaseCommand):
    help = 'Add compet to Week'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        all_compets = Compet.objects.filter(compet_rank_final__lte=200,compet_type__in=(1,2,3,4,5))
        compets_i1 = all_compets.filter(compet_type=1,compet_medal='o').order_by('compet_name')
        # 18399 | Samuel Caleb Nunes Camara (já veio)
        compets_i2 = all_compets.filter(compet_type=2,compet_medal='o').exclude(compet_id=18399).order_by('compet_name')

        # PJ
        # 30596 | Amanda Sarmento da Silva (CF)
        # 55102 | João Paulo de Menezes Soares (já veio)
        # 41641 | Irina Zhou Ye (convidada P1 pelo CF)
        # 52060 | Manuela Farias dos Santos (CF)
        compets_pj = all_compets.filter(Q(compet_type=5,compet_medal__in=('o','p')) | Q(compet_id__in=(30596,52060))).exclude(compet_id__in=(41641,55102)).order_by('compet_name')

        # P1
        # 41641 | Irina Zhou Ye (convidada P1 pelo CF)
        # 33972 | Malu Araujo Azevedo
        compets_p1 = all_compets.filter(Q(compet_type=3,compet_medal__in=('o','p')) | Q(compet_id__in=(33972,41641))).order_by('compet_name')

        # P2
        compets_p2 = all_compets.filter(compet_type=4)
        compets_p2 = compets_p2.filter(Q(compet_rank_final__lte=15) | ((Q(compet_sex='F') | Q(compet_year__in=('M1','M2'))) & Q(compet_points_fase3__gte=250))).order_by('compet_name')

        invited = []
        invited.append((1,compets_i1))
        invited.append((2,compets_i2))
        invited.append((5,compets_pj))
        invited.append((3,compets_p1))
        invited.append((4,compets_p2))
        
        num = 0
        for level, compets in invited:
            for c in compets:
                print(c.compet_rank_final,c.compet_points_fase3,c.compet_year, c.compet_name, level)

                if Week.objects.filter(compet_id=c.compet_id).exists():
                    self.stdout.write(self.style.ERROR('Compet already invited'))
                    self.stdout.write(self.style.ERROR('No change'))
                    continue

                week = Week(compet_id=c.compet_id,partic_level=level,school_id=c.compet_school_id)
                week.save()
                num += 1
        self.stdout.write(self.style.SUCCESS(f'Inserted {num} compets'))
