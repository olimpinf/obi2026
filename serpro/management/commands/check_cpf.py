import getopt
import os
import re
import sys
from datetime import datetime
import logging
from time import sleep

from django.utils.timezone import make_aware
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from accounts.models import Customer
from serpro.utils import generate_bearer_token, consulta_cpf, verifica_nome_cpf

def check_customer(customer):
    name = customer.user.first_name + ' ' + customer.user.last_name
    document = customer.document
    if verifica_nome_cpf(name, document):
        return 1
    else:
        return 0

def check_customers():
    customers = Customer.objects.filter(country='BRA').order_by('user_id')
    count_ok, count_fail = 0,0
    for customer in customers:
        print('------------')
        print("user_id:", customer.user_id)
        if check_customer(customer):
            print(f'OK {customer.user.first_name} {customer.user.last_name}')
            customer.action_required = False
            customer.save()
            count_ok += 1
        else:
            count_fail += 1
        sys.stdout.flush()
        sleep(1)
        
    return (count_ok, count_fail)

class Command(BaseCommand):
    help = 'Compute compets that are promoted to next phase'

    def add_arguments(self, parser):
        parser.add_argument('user_id', nargs='+', type=int)
        
    def handle(self, *args, **options):
        user_id = options['user_id'][0]
        if user_id == 0:
            count_ok, count_fail = check_customers()
        else:
            c = Customer.objects.get(user_id=user_id)
            if check_customer(c):
                count_ok = 1
                count_fail = 0
            else:
                count_ok = 0
                count_fail = 1

        print(f"\n\n{count_ok+count_fail} checked")
        print(f"{count_ok} ok")
        print(f"{count_fail} fail")
