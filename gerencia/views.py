import os
import logging
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from django.contrib import messages
from django.core import mail
#from django.core.mail import send_mass_mail, EmailMessage
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.text import slugify

from principal.models import Compet, School, Colab
from principal.utils.utils import obi_year
from .forms import EnviaConviteRecuperaForm, EnviaMensagemForm
from principal.utils.utils import remove_accents

EMAIL_FROM="Coordenação da OBI <olimpinf@ic.unicamp.br>"
logger = logging.getLogger(__name__)

def in_manager_group(user):
    """Use with a ``user_passes_test`` decorator to restrict access to 
    authenticated users who are not in the "Student" group."""
    return user.is_authenticated and (user.username=='olimpinf' or user.username=='fpisani')


@user_passes_test(in_manager_group, login_url='/restrito/')
def index(request):
    return render(request, 'gerencia/index.html', {})

@user_passes_test(in_manager_group, login_url='/restrito/')
def envia_convite_recupera(request):
    msg='''Prezado(a) Prof(a). {}

Estão abertas as inscrições para a OBI2020.

É necessário confirmar o cadastro da escola, mesmo tendo participado da OBI no ano passado. Se o(a) Sr(a) já confirmou o cadastro para a OBI2020 por favor desconsidere esta mensagem.

Confirmar o cadastro é simples. Caso o(a) Sr(a) ainda seja professor(a) da escola

{}

e possa continuar auxiliando na organização da OBI, atuando como Coordenador Local, basta seguir este link:

https://olimpiada.ic.unicamp.br/recupera_cadastro_auto/{}/

Sua escola será recadastrada automaticamente, utilizando as informações do cadastro no ano passado e o(a) Sr(a). receberá uma mensagem com a nova senha.

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
    connection.open()
    
    for s in schools_past_year:
        if not s.school_hash:
            continue
        if slugify(s.school_name) in schools_current_year:
            logger.info('school already registered: {}'.format(s.school_name))
            continue
        if s.school_deleg_email in emails_current_year:
            logger.info('email already registered: {}'.format(s.school_name))
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
        email.send()
        logger.info('{} - sent'.format(s.school_deleg_email))
        count += 1
        #if count % 5 == 0:
        #    sleep(1)
    connection.close()
    return render(request, 'gerencia/envia_mensagem_resp.html', {'count': count})


@user_passes_test(in_manager_group, login_url='/restrito/')
def envia_mensagem(request):
    if request.method == 'POST':
        form = EnviaMensagemForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            email_addresses = set(f['email_list']) # empty list if not given
            
            if 'compet_inic' in f['dest_groups'] and 'compet_prog' in f['dest_groups']:
                compets = Compet.objects.order_by('compet_id')
            elif 'compet_inic' in f['dest_groups']:
                compets = Compet.objects.filter(compet_type__in=[1,2,7]).order_by('compet_id')
            elif 'compet_prog' in f['dest_groups']:
                compets = Compet.objects.filter(compet_type__in=[3,4,5,6]).order_by('compet_id')
            else:
                compets = []
            if 'local_coord' in f['dest_groups']:
                schools = School.objects.filter(school_ok=True)
            else:
                schools = []
            if 'colab' in f['dest_groups']:
                colabs = Colab.objects.all()
            else:
                colabs = []

            for compet in compets:
                if compet.compet_email:
                    email_addresses.add(compet.compet_email)

            for school in schools:
                email_addresses.add(school.school_deleg_email)

            for colab in colabs:
                if colab.colab_email:
                    email_addresses.add(colab.colab_email)
                    
            #attachment_data = None
            #with open(os.path.join(settings.MEDIA_ROOT,'convite_unifei.png'), 'rb') as a:
            #    attachment_data = a.read()
                
            # send one by one, otherwise all go in the TO field of one message
            # count = 0
            # emails = []
            # for e in email_addresses:
            #     email = (
            #          f['subject'],
            #          f['message'],
            #          EMAIL_FROM,
            #          [e]
            #          )
            #     emails.append(email)
            #     #if attachment_data:
            #     #    email.attach('convite.png', attachment_data, 'image/png')
            # send_mass_mail is causing an error 
            #send_mass_mail((emails), fail_silently=False)

            # send explicitly
            connection = mail.get_connection()
            connection.open()
            count = 0
            for e in email_addresses:
                email = mail.EmailMessage(
                    f['subject'],
                    f['message'],
                    EMAIL_FROM,
                    [e],
                    connection=connection
                )
                #if attachment_data:
                #    email.attach('convite.png', attachment_data, 'image/png')
                email.send()
                print(e,'- sent')
                count += 1
                #if count % 5 == 0:
                #    sleep(1)
            connection.close()
            return render(request, 'gerencia/envia_mensagem_resp.html', {'count': count})
    else:
        form = EnviaMensagemForm()

    return render(request, 'gerencia/envia_mensagem.html', {'form': form})


def test(request):
    school = School.objects.get(school_id=1)
    return render(request, 'gerencia/mensagem_coord_sede_isolada_fase3.html', {'school': school, 'mod': 'ini', 'mod_name': 'Iniciação', 'mod_date': '15 de outubro'})
