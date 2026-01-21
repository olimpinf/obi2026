import getopt
import os
import re
import sys
from datetime import datetime
import logging

from django.utils.timezone import make_aware
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from accounts.models import Customer
from serpro.utils import generate_bearer_token, consulta_cpf, verifica_nome_cpf

class Command(BaseCommand):
    help = 'Compute compets that are promoted to next phase'

    def add_arguments(self, parser):
        parser.add_argument('nome', nargs='+', type=str)
        parser.add_argument('cpf', nargs='+', type=str)
        
    def handle(self, *args, **options):
        nome = options['nome'][0]
        cpf = options['cpf'][0]
        data = verifica_nome_cpf(nome, cpf)
        print(data)
