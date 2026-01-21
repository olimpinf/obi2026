from time import sleep

from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from principal.utils.utils import obi_year
from principal.models import School

EMAIL_FROM="Coordenação da OBI <olimpinf@ic.unicamp.br>"

def send_invitations(dbname):
    msg='''Prezado(a) Prof(a). {}

Estão abertas as inscrições para a OBI2020.

É necessário confirmar o cadastro da escola, mesmo tendo participado da OBI no ano passado.

Confirmar o cadastro é simples. Caso o(a) Sr(a) ainda seja professor(a) da escola

{}

e possa continuar auxiliando na organização da OBI, atuando como Coordenador Local, basta seguir este link:

https://olimpiada.ic.unicamp.br/recupera_cadastro_auto/{}/

Sua escola será recadastrada automaticamente, utilizando as informações
do cadastro no ano passado e o(a) Sr(a). receberá uma mensagem com a
nova senha.

Caso o(a) Sr(a) lecione agora em outra escola, mas deseje continuar atuando como Coordenador Local da nova escola, basta preencher o formulário de cadastro (é simples e rápido): 

https://olimpiada.ic.unicamp.br/cadastra_escola

Devido à pandemia de Covid-19, as provas da Fase Local (Fase 1) poderão ser realizadas online (com o competidor na sua casa) ou presencialmente na escola, à escolha da escola. A OBI disponibiliza um ambiente de provas online, que já está disponível para que os competidores possam praticar antes da prova.

Agradecemos a colaboração com a OBI2020.

---
Coordenação da OBI2020

'''
    subject = "OBI2020 - inscrições abertas"
    tmp = School.objects.only('school_name','school_deleg_email')
    schools_current_year = set()
    emails_current_year = set()
    for s in tmp:
        schools_current_year.add(slugify(s.school_name.strip()))
        emails_current_year.add(s.school_deleg_email.strip())
    schools_past_year = School.objects.using('obi{}'.format(obi_year(as_int=True)-1)).order_by('school_id')
    count = 0

    # send explicitly
    connection = mail.get_connection()
    # when testing, the connection is not the debug port, fix this here
    #connection.localhost = 'localhost'
    #connection.port = 1025
    connection.open()
    
    for s in schools_past_year:
        if s.school_deleg_email in ('joaospindola@cursosantosdumont.org.br','olimpiadas@notredamecampinas.net.br','laffernandes@ic.uff.br','luiz.freitas@ifms.edu.br','joao.emiliano@sesisp.org.br','rlem.rehael@gmail.com','dannluciano@ifpi.edu.br','danilo@fatecitapetininga.edu.br'):
            print('already sent: {}'.format(s.school_name))
            continue
        if not s.school_hash:
            print('no hash: {}'.format(s.school_name))
            continue
        if slugify(s.school_name) in schools_current_year:
            print('school already registered: {}'.format(s.school_name))
            continue
        if s.school_deleg_email in emails_current_year:
            print('email already registered: {}'.format(s.school_name))
            continue

        email = mail.EmailMessage(
            subject,
            msg.format(s.school_deleg_name,s.school_name,s.school_hash.strip()),
            EMAIL_FROM,
            [s.school_deleg_email],
            connection=connection
        )
        #if attachment_data:
        #    email.attach('convite.png', attachment_data, 'image/png')
        try:
            email.send()
            print('{} - sent'.format(s.school_deleg_email))
        except:
            print('{} - FAILED'.format(s.school_deleg_email))
            
        count += 1
        if count % 5 == 0:
            sleep(1)
    connection.close()
    return count


class Command(BaseCommand):
    help = 'Send invitation messages to last year schools'

    def add_arguments(self, parser):
        parser.add_argument('dbname', nargs='+', type=str)

    def handle(self, *args, **options):
        for dbname in options['dbname']:
            count = send_invitations(dbname)
        self.stdout.write(self.style.SUCCESS('Sent {} messages.'.format(count)))
