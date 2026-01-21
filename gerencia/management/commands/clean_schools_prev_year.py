import sys
import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from principal.models import School, Compet, Deleg, Colab


def do_it(this_year):

    # will build set with schools which have compet in at least one of last two years
    last_year = this_year - 1
    compets_last_year = Compet.objects.using(f'obi{last_year}').only('compet_school_id').distinct()
    schools_with_compets = set()
    for compet in compets_last_year:
        schools_with_compets.add(compet.compet_school_id)

    prev_year = this_year - 2
    compets_prev_year = Compet.objects.using(f'obi{prev_year}').only('compet_school_id').distinct()
    for compet in compets_prev_year:
        schools_with_compets.add(compet.compet_school_id)

    schools_with_no_compets_last_2years = School.objects.using(f'obi{last_year}').exclude(school_id__in=schools_with_compets)                                                                                    
    print(f'schools_with_no_compets_last_2years: {len(schools_with_no_compets_last_2years)}')

    schools_this_year = School.objects.using(f'obi{this_year}')

    failed,deleg_removed,colab_removed = 0,0,0
    for school in schools_this_year:
        if school.school_id in schools_with_compets:
            continue
        try:
            deleg = Deleg.objects.get(deleg_school_id=school.school_id)
        except:
            failed += 1

        deleg_user = User.objects.get(id=deleg.user_id)
        deleg_removed += 1
        
        colabs = Colab.objects.filter(colab_school_id=school.school_id)

        for colab in colabs:
            try:
                colab_user = User.objects.get(id=colab.user_id)
                colab_removed +=1
            except:
                pass

    print('deleg_removed', deleg_removed )
    print('colab_removed', colab_removed )
    print('failed', failed )
    return




class Command(BaseCommand):
    help = 'Send message'

    def add_arguments(self, parser):
        parser.add_argument('this_year', nargs='+', type=int)
        
    def handle(self, *args, **options):
        this_year= options['this_year'][0]
        do_it(this_year)
        self.stdout.write(self.style.SUCCESS('OK'))
