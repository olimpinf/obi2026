import logging
import magic
import hashlib
import os

from datetime import datetime

from django.db.models.functions import Collate
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import make_aware, timezone
from django.http import HttpResponse, HttpResponseRedirect

from .models import Week, Parent, Payment
from .forms import ConfirmParticWeekForm, InformPaymentForm, ConfirmPaymentForm, SBCprocessPaymentForm

from principal.utils.get_certif import (get_week_certif_compet, get_week_certif_monitor, get_week_certif_monitor_lab, get_week_certif_professor)

from principal.utils.get_receipt import get_receipt

from principal.models import Compet, School, LEVEL_NAME
from principal.utils.get_letter import get_letter_teacher
from principal.utils.utils import (obi_year,
                                   capitalize_name,
                                   write_uploaded_file,
                                   write_school_uploaded_file,
                                   calculate_page_size, format_currency)

from obi.settings import BASE_DIR,MEDIA_ROOT,YEAR
from compet.views import in_compet_group
from restrito.views import in_compet_coord_colab_group, in_sbc_group
from week.models import STATUS

logger = logging.getLogger('obi')
TAX_VALUE = 2300

##########
# monitores
##########
#monitor_2022s1 = {
#1:('Ana Laura Chioca Vieira','F',4),
#2:('André Gomes Regino','M',12),
#3:('Beatriz Cardoso de Oliveira','F',22),
#4:('Beatriz Lomes da Silva','M',24),
#5:('Carlos Alexandre Pinheiro de Souza','M',14),
#6:('Daniel Yuji Hosomi','M',18),
#7:('Diego da Silva Parra','M',26),
#8:('Eduardo Ribeiro Silva de Oliveira','M',6),
#9:('Guilherme Paixão','M',4),
#10:('Gustavo de Souza dos Reis','M',18),
#11:('Helder Betiol','M',18),
#12:('Ilan Francisco da Silva','M',18),
#13:('Isabella Silva de Faria','F',2),
#14:('João Pedro Carolino Morais','M',12),
#15:('Jonas Cardoso Gonçalves','M',28),
#16:('JOSE VICTOR MACHUCA','M',22),
#17:('Lethycia Maia de Souza','F',8),
#18:('Leticia Mara Berto','F',16),
#20:('Luã Marcelo Muriana','M',24),
#22:('Luiz Gustavo Silva Aguiar','M',16),
#25:('Mateus Ferreira Gomes','M',4),
#26:('Matheus Diógenes Andrade','M',18),
#27:('Milena Heidecher de Oliveira','F',12),
#28:('Natan Henrique Sanches','M',8),
#29:('Paulo Henrique Marçal Martins Souza','M',10),
#31:('Pedro Oliveira Torrente','M',24),
#32:('Rafael de Queiroz Souza','M',28),
#33:('Raphael Augusto Silva Giannattasio','M',6),
#34:('Rian Radeck Santos Costa','M',18),
#36:('Thaís Steinmuller Farias','F',14),
#37:('Tomás Silva','M',18),
#38:('Wellington Tavares Alexandre da Silva','M',8),
#39:('Wesley Soares Ferreira','M',18),
#40:('Willian Miura Mori','M',18)
#}

# monitor_2022 = {
#     1:('Árathi Zanvettor Guedes',          'M', 40),
#     2:('Aline Hesley Silva Sousa',         'F', 40),
#     3:('Caio Vinicius Castro dos Santos',  'M', 40),
#     4:('Jarol Butron Soria',               'M', 40),
#     5:('Leandro Ponsano Corimbaba',        'M', 40),
#     6:('Lethycia Maia de Souza',           'F', 40),
#     7:('Leticia da Silva Bomfim',          'F', 40),
#     8:('Luis Gustavo da Soledade Gonzaga', 'M', 40),
#     9:('Paulo Bassani',                    'M', 40),
#     10:('Vítor Gomes Chagas',              'M', 40),
#     11:('Luã Marcelo Muriana',             'M', 40)
# }

# 2023
# monitor = {
#     1:('Luã Marcelo Muriana',              'M', 60),
#     2:('Aline Hesley Silva Sousa',         'F', 60),
#     3:('Letícia Berto',                    'F', 60),
#     4:('Leticia da Silva Bomfim',          'F', 60),
#     5:('Jovanio José Galvão Júnior',       'M', 60),
#     6:('Maria Clara da Costa Oliveira',    'F', 60),
#     7:('Nicolas dos Santos França',        'M', 60),
#     8:('Paulo Bassani',                    'M', 60),
#     9:('Pedro Machado Leão',               'M', 60),
#     10:('Rafael Queiroz',                  'M', 60),
#     11:('Vinicius Leme Soares',            'M', 60),
#     12:('Vítor Gomes Chagas',              'M', 60),
# }

# monitor_lab = {
#     1:('Felipe Carvalho Pereira',          'M', 20),
#     2:('Gustavo Sacramento Santos',        'M', 20),
#     3:('Leonardo Rezende Costa',           'M', 20),
#     4:('Luana Amorim',                     'F', 20),
#     5:('Lucas Francisco Silva Paiva',      'M', 20),
# }

# monitor2024 = {
#     1:('Luã Marcelo Muriana',             'M', 60),
#     2:('Athyrson Machado Ribeiro',        'M', 60),
#     3:('Evelyn Roberta de Lima Silva',    'F', 60),
#     4:('Guilherme de Godoi Monteiro',     'M', 60),
#     5:('Gustavo Sousa',                   'M', 60),
#     6:('Jarol Vijay Butron Soria',        'M', 60),
#     7:('Maria Clara da Costa Oliveira',   'F', 60),
#     8:('Paulo Bassani',                   'M', 60),
#     9:('Santiago Rodrigues da Silva',     'M', 60),
#     10:('Thais Steinmüller Farias',       'F', 60),
#     11:('Victoria Alchangelo dos Santos', 'F', 60),
#     12:('Wladimir Arturo Garces Carrillo','M', 60),
# }

# monitor_lab_2024 = {
#     1:('Caio Emanuel Rhoden',             'M', 20),
#     2:('Karen Cristina Baliero Lima',     'F', 20),
#     3:('Viviane da Silva Pimentel',       'M', 20),
#     4:('Leonardo Rezende Costa',          'M', 20),
# }

monitor = {
    1:('Wladimir Arturo Garces Carrillo', 'M', 48),
    2:('Amanda Scherr Caldeira Coelho',   'F', 48),
    3:('Athyrson Machado Ribeiro',        'M', 48),
    4:('Caio Maia Moreira Santos',        'M', 48),
    5:('Evelyn Roberta de Lima Silva',    'F', 48),
    6:('Guilherme de Godoi Monteiro',     'M', 48),
    7:('Gustavo de Oliveira Sousa',       'M', 48),
    8:('Jarol Vijay Butron Soria',        'M', 48),
    9:('Juliana Costa Dantas',            'F', 48),
   10:('Maria Clara da Costa Oliveira',   'F', 48),
   11:('Mariana Fonsechi Mandarino',      'F', 48),
   12:('Paulo Bassani',                   'M', 48),
   13:('Vinicius Leme Soares',            'M', 48),
   14:('Thais Steinmüller Farias',       'F', 48),
   15:('Victoria Alchangelo dos Santos', 'F', 48),
   16:('Viviane da Silva Pimentel',      'M', 48),
}

monitor_lab = {
    1:('Ana Luiza Mota Gomes',            'M', 20),
    2:('Ana Margarida Borges',            'F', 20),
    3:('Gabriela Taniguchi',              'F', 20),
    4:('Leonardo Ferreira',               'M', 20),
    5:('Lucas Cabral Senno',              'M', 20),
    6:('Lucas Henrique Bertanha',         'M', 20),
}

##########
# professores
##########
#professor_2021 = {
#    1:('Flávia Pisani','F','Introdução à Programação de Computadores em C/C++'),
#    2:('Fábio Mallaco Moreira','M','Introdução à Programação de Computadores em C/C++'),
#    3:('Bernardo Amorim','M','Técnicas de Programação, Estruturas de Dados e Algoritmos'),
#    4:('Bernardo Panka Archegas','M','Introdução a Técnicas de Programação, Estruturas de Dados e Algoritmos'),
#    5:('Bruno Monteiro','M','Técnicas de Programação, Estruturas de Dados e Algoritmos'),
#    6:('Emmanuel Silva','M','Técnicas de Programação, Estruturas de Dados e Algoritmos'),
#    7:('Yan Matheus Tavares e Silva','M','Introdução a Técnicas de Programação, Estruturas de Dados e Algoritmos'),
#}

#professor_2022s1 = {
#    1:('André Amaral de Sousa','M','Seletiva Competições Internacionais'),
#    2:('Arthur Ferreira do Nascimento','M','Seletiva Competições Internacionais'),
#    3:('Bernardo Panka Archegas','M','Seletiva Competições Internacionais'),
#    4:('Bruno Maletta Monteiro','M','Seletiva Competições Internacionais'),
#    5:('Emanuel Juliano Morais Silva','M','Seletiva Competições Internacionais'),
#    6:('Felipe Mota dos Santos','M','Seletiva Competições Internacionais'),
#    7:('Frederico Bulhões de Sousa Ribeiro','M','Seletiva Competições Internacionais'),
#    8:('Luiz Fernando Batista Morato','M','Seletiva Competições Internacionais'),
#    9:('Luiz Henrique Yuji Delgado Oda','M','Seletiva Competições Internacionais'),
#    10:('Matheus Leal Viana','M','Seletiva Competições Internacionais'),
#    11:('Naim Shaikhzadeh Santos','M','Seletiva Competições Internacionais'),
#    12:('Tiago Domingos Almeida Souza','M','Seletiva Competições Internacionais'),
#    13:('Yan Matheus Tavares e Silva','M','Seletiva Competições Internacionais'),
#}

# professor_2023 = {
#     1:('André Amaral de Sousa', 'M', '``Seletiva Competições Internacionais\'\''),
#     2:('Arthur Ferreira do Nascimento', 'M', '``Seletiva Competições Internacionais\'\''),
#     3:('Eduardo, Quirino de Oliveira', 'M', '``Seletiva Competições Internacionais\'\''),
#     4:('Emanuel, Juliano Morais Silva', 'M', '``Seletiva Competições Internacionais\'\''),
#     5:('Frederico Bulhões de Sousa Ribeiro', 'M', '``Seletiva Competições Internacionais\'\''),
#     6:('Gabriel, Lucas Costa Martins', 'M', '``Seletiva Competições Internacionais\'\''),
#     7:('Heitor, Gonçalves Leite', 'M', '``Seletiva Competições Internacionais\'\''),
#     8:('Leonardo Valente Nascimento', 'M', '``Seletiva Competições Internacionais\'\''),
#     9:('Letícia Freire Carvalho de Sousa', 'F', '``Seletiva Competições Internacionais\'\''),
#     10:('Luca, Dantas de Britto Monte Araújo', 'M', '``Seletiva Competições Internacionais\'\''),
#     11:('Mateus, Bezrutchka', 'M', '``Seletiva Competições Internacionais\'\''),
#     12:('Naim, Shaikhzadeh Santos', 'M', '``Seletiva Competições Internacionais\'\''),
#     13:('Rafael, Nascimento Soares', 'M', '``Seletiva Competições Internacionais\'\''),
#     14:('Santiago Valdés Ravelo', 'M', '``Introdução à Programação de Computadores\'\''),
#     15:('Thiago Mota Martins', 'M', '``Seletiva Competições Internacionais\'\''),
#     16:('Yan Matheus Tavares e Silva', 'M', '``Seletiva Competições Internacionais\'\''),
# }

# professor2024 = {
#     1: ('Crishna Irion', 'F', 'Introdução à Programação de Computadores'),
#     2: ('Juliana Freitag Borin', 'F', 'Introdução à Programação de Computadores'),
#     3: ('Pedro César Mesquita Ferreira', 'M','Introdução a Técnicas de Programação, Estruturas de Dados e Algoritmos'), 
#     4: ('Enzo Dantas de Britto Monte Araújo', 'M','Introdução a Técnicas de Programação, Estruturas de Dados e Algoritmos'), 
#     5: ('Daniel Yuji Hosomi', 'M','Técnicas de Programação, Estruturas de Dados e Algoritmos'), 
#     6: ('Thiago Mota Martins', 'M','Técnicas de Programação, Estruturas de Dados e Algoritmos'), 
#     7: ('André Amaral de Sousa', 'M', 'Seletiva Competições Internacionais'),
#     8: ('Arthur Lobo Leite Lopes', 'M', 'Seletiva Competições Internacionais'),
#     9: ('Arthur Ferreira do Nascimento', 'M', 'Seletiva Competições Internacionais'),
#     10:('Eduardo Quirino de Oliveira', 'M', 'Seletiva Competições Internacionais'),
#     11:('Filipe de Souza Lalic', 'M', 'Seletiva Competições Internacionais'),
#     12:('Leonardo Valente Nascimento', 'M', 'Seletiva Competições Internacionais'),
#     13:('Luana Amorim Lima', 'M', 'Seletiva Competições Internacionais'),
#     14:('Mateus Bezrutchka', 'M', 'Seletiva Competições Internacionais'),
#     15:('Naim Shaikhzadeh Santos', 'M', 'Seletiva Competições Internacionais'),
# }

professor = {
    1: ('Arthur Lobo Leite Lopes', 'M', 'Introdução à Programação de Computadores'),
    2: ('Juliana Freitag Borin', 'F', 'Introdução à Programação de Computadores'),
    3: ('Pedro César Mesquita Ferreira', 'M','Introdução a Técnicas de Programação, Estruturas de Dados e Algoritmos'), 
    4: ('Enzo Dantas de Britto Monte Araújo', 'M','Introdução a Técnicas de Programação, Estruturas de Dados e Algoritmos'), 
    5: ('Daniel Yuji Hosomi', 'M','Técnicas de Programação, Estruturas de Dados e Algoritmos'), 
    6: ('Fernando Graminholi Gonçalves', 'M','Técnicas de Programação, Estruturas de Dados e Algoritmos'), 
    7: ('André Amaral de Sousa', 'M', 'Seletiva Competições Internacionais'),
    9: ('Arthur Ferreira do Nascimento', 'M', 'Seletiva Competições Internacionais'),
    10:('Caique Paiva', 'M', 'Seletiva Competições Internacionais'),
    11:('Filipe de Souza Lalic', 'M', 'Seletiva Competições Internacionais'),
    12:('Leonardo Valente Nascimento', 'M', 'Seletiva Competições Internacionais'),
    13:('Luana Amorim Lima', 'M', 'Seletiva Competições Internacionais'),
    14:('Mateus Bezrutchka', 'M', 'Seletiva Competições Internacionais'),
    15:('Naim Shaikhzadeh Santos', 'M', 'Seletiva Competições Internacionais'),
    16:('Pedro Henrique Assunção', 'M', 'Seletiva Competições Internacionais'),
}

def gen_hash(edition_year, partic_name):
    tmp = '{}{}'.format(partic_name,edition_year)
    hash = hashlib.sha224(tmp.encode('utf-8')).hexdigest()
    #print(hash[:20])
    return hash

def index(request):
    return render(request, 'week/index.html', {})

def palestras(request):
    return render(request, 'week/palestras_acompanhantes.html', {})

def cerimonia(request):
    return render(request, 'week/cerimonia.html', {})

def emite_carta_professor(request, id):
    print("in emite_carta_professor");
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="carta.pdf"'
    file_data = get_letter_teacher(professor[id][0],professor[id][1],YEAR)
    response.write(file_data)
    return response

def emite_certificado(request,type,id):
    id = int(id)
    print("in emite_certificado, views.py")
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="certificado.pdf"'
    if type=='compet':
        file_data = get_week_certif_compet(id,3,YEAR)
    elif type=='monitor':
        file_data = get_week_certif_monitor(monitor[id][0],monitor[id][1],monitor[id][2],YEAR)
    elif type=='monitor_lab':
        file_data = get_week_certif_monitor_lab(monitor_lab[id][0],monitor_lab[id][1],monitor_lab[id][2],YEAR)
    elif type=='professor':
        file_data = get_week_certif_professor(professor[id][0],professor[id][1],professor[id][2],YEAR)
    elif type=='setter':
        file_data = get_week_certif_professor(professor[id][0],professor[id][1],professor[id][2],YEAR)
    response.write(file_data)
    return response


@user_passes_test(in_compet_group, login_url='/contas/login/')
def confirm(request):
    compet = Compet.objects.get(user_id=request.user.pk)
    school = School.objects.get(school_id=compet.compet_school_id)
    level_name = LEVEL_NAME[compet.compet_type].lower()

    if request.method == 'POST':
        form = ConfirmParticWeekForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data

            w = Week.objects.get(compet=compet)
            w.allergies = f['partic_allergies']
            w.document = f['partic_document']
            w.shirt_size = f['partic_shirt_size']
            w.phone = f['partic_phone']
            w.status = STATUS['confirm']
            w.form_info = True
            w.save()

            try:
                p = Parent.objects.get(parent_compet=compet)
            except:
                p = Parent()
            p.parent_compet = compet
            p.parent_name = f['parent_name']
            p.parent_type = f['parent_type']
            p.parent_phone = f['parent_phone']
            p.parent_email = f['parent_email']
            p.save()

            logger.info(f"Confirmação de participação na semana olimpíca: {compet}")
            messages.success(request, 'Confirmação de participação recebida')
            return redirect('/compet/')
    else:
        form = ConfirmParticWeekForm(initial={'partic_name': compet.compet_name, 'pagetitle': 'Confirmação de participação na Semana Olímpica'})

    return render(request, 'week/confirm_partic_week.html', {'form': form})

@user_passes_test(in_compet_group, login_url='/contas/login/')
def deny(request):
    compet = Compet.objects.get(user_id=request.user.pk)
    school = School.objects.get(school_id=compet.compet_school_id)
    # level_name = LEVEL_NAME[compet.compet_type].lower()
    # if request.method == 'POST':
    #     form = CheckDenyWeekForm(request.POST)
    #     if form.is_valid():
    #         f = form.cleaned_data
    # else:
    #     form = CheckDenyWeekForm(initial={'partic_name': compet.compet_name})
    return render(request, 'week/check_deny.html', {'pagetitle': "Confirmação de NÃO participação"})



@user_passes_test(in_compet_group, login_url='/contas/login/')
def do_deny(request):
    compet = Compet.objects.get(user_id=request.user.pk)
    school = School.objects.get(school_id=compet.compet_school_id)
    level_name = LEVEL_NAME[compet.compet_type].lower()

    w = Week.objects.get(compet=compet)
    w.status = STATUS['deny']
    w.save()

    logger.info(f"Confirmação de NÃO participação na semana olimpíca: {compet}")

    return render(request, 'week/deny_partic_week.html')

def classes(request):
    return render(request, 'week/agenda_aulas.html', {})

def ini1(request):
    return render(request, 'week/ini1.html', {})

def progj(request):
    return render(request, 'week/progj.html', {})

def prog1(request):
    return render(request, 'week/prog1.html', {})

def prog2(request):
    return render(request, 'week/ini1.html', {})

def invited(request):
    return render(request, 'week/convidados.html', {})

def monitors(request):
    return render(request, 'week/monitores.html', {})

def instructors(request):
    return render(request, 'week/professores.html', {})

def documentos(request):
    return render(request, 'week/documentos.html', {})

def certificados(request):
    return render(request, 'week/certificados.html', {})

def agenda(request):
    return render(request, 'week/agenda.html', {})

def ecos(request):
    return render(request, 'week/ecos_instrucoes.html', {})

def ecos_instituicoes(request):
    return render(request, 'week/ecos_instituicoes.html', {})

def programa(request):
    return render(request, 'week/programa.html', {})

def info_seletiva(request):
    return render(request, 'week/info_seletiva.html', {})

def conteudo(request):
    return render(request, 'week/conteudo.html', {})

def participants_seletiva(request):
    return

    #qs_p2 = Week.objects.filter(partic_level=4).order_by('compet__compet_name')
    #context = {
    #    'invited': (
    #        {'level':'Programação 2','participants':qs_p2},
    #    ),
    #}
    ##for i in qs_p2:
    ##    print(i.compet.compet_name)
    #return render(request, 'week/participantes_seletiva.html', context)

    partic_ioi = ['Arthur Lobo Leite Lopes', 'Brunno Rezende dos Santos', 'Carlos Cabral de Menezes Filho', \
                  'Carolina Moura Valle Costa', 'Erick Cassiano da Silva Passos', 'Erik Cruz Morbach', \
                  'Felipe Kai Hu', 'Gabriel Lucas Costa Martins', 'Guilherme Cabral de Menezes', \
                  'Guilherme Gobo dos Santos', 'Heitor Gonçalves Leite', 'Leonardo de Andrade Paes', \
                  'Leonardo Valente Nascimento', 'Luana Amorim Lima', \
                  'Luca Dantas de Britto Monte Araujo', 'Lucio Cardoso Dias Figueiredo Filho', \
                  'Luiz Felipe Funaki Bigarelli', 'Marcos Paulo Evers Cordeiro', \
                  'Pedro Bignotto Racchetti', 'Pedro Shinzato Chen', 'Pedro Suyama Leston Rey', \
                  'Rafael Nascimento Soares', 'Rafael Setton Alencar de Carvalho']

    partic_egoi = ['Camila Maeda Shida', 'Carolina Moura Valle Costa', 'Endy Lumy Okamura Miyashita', \
                   'Estela Baron Nakamura', \
                   'Luana Amorim Lima', 'Maria Eduarda Bertole Matos', 'Pietra Gullo Salgado Chaves', \
                   'Sara Miyuka Abe', 'Sofia Torres de Paula Cintra', 'Sophia Damm Zogaib Mardones']

    qs_ioi = Week.objects.filter(compet__compet_name__in=partic_ioi).order_by('compet__compet_name')
    qs_egoi = Week.objects.filter(compet__compet_name__in=partic_egoi).order_by('compet__compet_name')

    context = {
        'invited': (
            {'level':'Seletiva IOI','participants':qs_ioi},
            {'level':'Seletiva EGOI','participants':qs_egoi}
        ),
    }

    return render(request, 'week/participantes_seletivas_2022.html', context)

def participants(request):
    ONLY_CONFIRMED = False

    if ONLY_CONFIRMED:
        qs_i1 = Week.objects.filter(partic_level=1,form_info=True).exclude(status=STATUS['no_reply']).exclude(status=STATUS['deny']).order_by('compet__compet_name')
        qs_i2 = Week.objects.filter(partic_level=2,form_info=True).exclude(status=STATUS['no_reply']).exclude(status=STATUS['deny']).order_by('compet__compet_name')
        qs_pj = Week.objects.filter(partic_level=5,form_info=True).exclude(status=STATUS['no_reply']).exclude(status=STATUS['deny']).order_by('compet__compet_name')
        qs_p1 = Week.objects.filter(partic_level=3,form_info=True).exclude(status=STATUS['no_reply']).exclude(status=STATUS['deny']).order_by('compet__compet_name')
        qs_p2 = Week.objects.filter(partic_level=4,form_info=True).exclude(status=STATUS['no_reply']).exclude(status=STATUS['deny']).order_by('compet__compet_name')
    else:
        qs_i1 = Week.objects.filter(partic_level=1).exclude(status=STATUS['no_reply']).exclude(status=STATUS['deny']).order_by('compet__compet_name')
        qs_i2 = Week.objects.filter(partic_level=2).exclude(status=STATUS['no_reply']).exclude(status=STATUS['deny']).order_by('compet__compet_name')
        qs_pj = Week.objects.filter(partic_level=5).exclude(status=STATUS['no_reply']).exclude(status=STATUS['deny']).order_by('compet__compet_name')
        qs_p1 = Week.objects.filter(partic_level=3).exclude(status=STATUS['no_reply']).exclude(status=STATUS['deny']).order_by('compet__compet_name')
        qs_p2 = Week.objects.filter(partic_level=4).exclude(status=STATUS['no_reply']).exclude(status=STATUS['deny']).order_by('compet__compet_name')

    qs_ap = Week.objects.filter(colab__colab_id__gt=0,paying=True).order_by('colab__colab_name') | \
        Week.objects.filter(chaperone__chaperone_id__gt=0,paying=True).order_by('chaperone__chaperone_name')

    qs_an = Week.objects.filter(colab__colab_id__gt=0,paying=False).order_by('colab__colab_name') | \
        Week.objects.filter(chaperone__chaperone_id__gt=0,paying=False).order_by('chaperone__chaperone_name')

    context = {
        'invited': (
            {'level':'Iniciação 1','participants':qs_i1},
            {'level':'Iniciação 2','participants':qs_i2},
            {'level':'Programação Júnior','participants':qs_pj},
            {'level':'Programação 1','participants':qs_p1},
            {'level':'Programação 2','participants':qs_p2},
            {'level':'Acompanhantes Pagantes','participants':qs_ap},
            {'level':'Acompanhantes Não Pagantes','participants':qs_an},
            ),
        }

    return render(request, 'week/participantes.html', context)

def camisetas(request):
    qs_i1 = Week.objects.filter(partic_level=1).exclude(status=STATUS['no_reply']).exclude(status=STATUS['deny']).order_by('compet__compet_name')
    qs_i2 = Week.objects.filter(partic_level=2).exclude(status=STATUS['no_reply']).exclude(status=STATUS['deny']).order_by('compet__compet_name')
    qs_pj = Week.objects.filter(partic_level=5).exclude(status=STATUS['no_reply']).exclude(status=STATUS['deny']).order_by('compet__compet_name')
    qs_p1 = Week.objects.filter(partic_level=3).exclude(status=STATUS['no_reply']).exclude(status=STATUS['deny']).order_by('compet__compet_name')
    qs_p2 = Week.objects.filter(partic_level=4).exclude(status=STATUS['no_reply']).exclude(status=STATUS['deny']).order_by('compet__compet_name')
    qs_ap = Week.objects.filter(colab__colab_id__gt=0,paying=True).order_by('colab__colab_name') | \
        Week.objects.filter(chaperone__chaperone_id__gt=0,paying=True).order_by('chaperone__chaperone_name')

    #    print(i.form)
    #qs_ap = Week.objects.filter(colab__colab_id__gt=0,paid=True).order_by('colab__colab_name') | \
    #    Week.objects.filter(chaperone__chaperone_id__gt=0,paid=True).order_by('chaperone__chaperone_name')
    #qs_an = Week.objects.filter(colab__colab_id__gt=0,paid=False).order_by('colab__colab_name') | \
    #    Week.objects.filter(chaperone__chaperone_id__gt=0,paid=False).order_by('chaperone__chaperone_name')
    context = {
        'invited': (
            {'level':'Iniciação 1','participants':qs_i1},
            {'level':'Iniciação 2','participants':qs_i2},
            {'level':'Programação Júnior','participants':qs_pj},
            {'level':'Programação 1','participants':qs_p1},
            {'level':'Programação 2','participants':qs_p2},
            {'level':'Acompanhantes Pagantes','participants':qs_ap},
            #{'level':'Acompanhantes não Pagantes','participants':qs_an},
            ),
        }

    return render(request, 'week/camisetas.html', context)


def arrivals(request):
    qs_airport = Week.objects.filter(arrival_place='Aeroporto').order_by('arrival_time')
    qs_bus_station = Week.objects.filter(arrival_place='Rodoviária').order_by('arrival_time')
    qs_hotel = Week.objects.filter(arrival_place='Hotel').order_by('arrival_time')
    #qs_no_info = Week.objects.filter(arrival_place=None).order_by(Collate('compet__compet_name','C.UTF-8'))
    qs_no_info = Week.objects.filter(arrival_place=None).order_by('compet__compet_name')
    context = {
        'airport': (
            {'participants':qs_airport},
            ),
        'bus_station': (
            {'participants':qs_bus_station},
            ),
        'hotel': (
            {'participants':qs_hotel},
            ),
        'no_info': (
            {'participants':qs_no_info},
            ),
        }
    return render(request, 'week/arrivals.html', context)

def arrivals2(request):
    qs_airport = Week.objects.filter(arrival_place='Aeroporto').order_by('arrival_time')
    qs_bus_station = Week.objects.filter(arrival_place='Rodoviária').order_by('arrival_time')
    qs_hotel = Week.objects.filter(arrival_place='Hotel').order_by('arrival_time')
    #qs_no_info = Week.objects.filter(arrival_place=None).order_by(Collate('compet__compet_name','C.UTF-8'))
    qs_no_info = Week.objects.filter(arrival_place=None).order_by('compet__compet_name')
    context = {
        'airport': (
            {'participants':qs_airport},
            ),
        'bus_station': (
            {'participants':qs_bus_station},
            ),
        'hotel': (
            {'participants':qs_hotel},
            ),
        'no_info': (
            {'participants':qs_no_info},
            ),
        }
    return render(request, 'week/arrivals2.html', context)


def departures(request):
    qs_airport = Week.objects.filter(departure_place='Aeroporto').exclude(week_id__in=(120,122)).order_by('departure_time')
    qs_bus_station = Week.objects.filter(departure_place='Rodoviária').order_by('departure_time')
    qs_hotel = Week.objects.filter(departure_place='Hotel').order_by('compet__compet_name')
    qs_no_info = Week.objects.filter(departure_place=None).order_by('compet__compet_name')
    context = {
        'airport': (
            {'participants':qs_airport},
            ),
        'bus_station': (
            {'participants':qs_bus_station},
            ),
        'hotel': (
            {'participants':qs_hotel},
            ),
        'no_info': (
            {'participants':qs_no_info},
            ),
        }
    return render(request, 'week/departures.html', context)

def departures2(request):
    qs_airport = Week.objects.filter(departure_place='Aeroporto').order_by('departure_time')
    qs_bus_station = Week.objects.filter(departure_place='Rodoviária').order_by('departure_time')
    qs_hotel = Week.objects.filter(departure_place='Hotel').order_by('compet__compet_name')
    qs_no_info = Week.objects.filter(departure_place=None).order_by('compet__compet_name')
    context = {
        'airport': (
            {'participants':qs_airport},
            ),
        'bus_station': (
            {'participants':qs_bus_station},
            ),
        'hotel': (
            {'participants':qs_hotel},
            ),
        'no_info': (
            {'participants':qs_no_info},
            ),
        }
    return render(request, 'week/departures2.html', context)

@user_passes_test(in_compet_coord_colab_group, login_url='/contas/login/')
def emit_receipt(request,id):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="recibo.pdf"'
    file_data = get_receipt(id=int(id),year=int(YEAR))
    response.write(file_data)
    return response

@user_passes_test(in_compet_coord_colab_group, login_url='/contas/login/')
def inform_payment(request):
    if request.user.groups.filter(name__in=['compet']).exists():
        payer = 'compet'
        school = request.user.compet.compet_school
    elif request.user.groups.filter(name__in=['colab', 'colab_full']).exists():
        payer = 'school'
        school = request.user.colab.colab_school
    else:
        payer = 'school'
        school = request.user.deleg.deleg_school

    if request.method == 'POST':
        form = InformPaymentForm(request.POST, request.FILES)
        if form.is_valid():

            # write file
            file_path, resultfile = write_school_uploaded_file(school_id=school.school_id,
                                                               modality='semana',phase_name='semana',fwhy='pagam_taxa',
                                                               f=request.FILES['receipt_file'],fname='taxa')

            # and process it
            guess = magic.from_file(file_path,mime=True)

            if guess == 'application/pdf':
                print('is pdf')
                os.system(f'convert {file_path} {file_path}.png')
                if os.path.exists(f'{file_path}-0.png'):
                    os.system(f'cp {file_path}-0.png {file_path}.png')
                imgpath = file_path + '.png'
            elif guess == 'image/png':
                os.system(f'cp {file_path} {file_path}.png')
                imgpath = file_path + '.png'
            elif guess == 'image/jpeg':
                os.system(f'cp {file_path} {file_path}.jpg')
                imgpath = file_path + '.jpg'

            try:
                os.system(f'chgrp www-data {imgpath}')
            except:
                pass

            file_number = os.path.basename(file_path).split('_')

            name_hash = gen_hash(school.school_id, school.school_name) + ('_' + file_number[1] if len(file_number) > 1 else '')

            static_imgpath = os.path.join(f'extras/obi{YEAR}/semana/pagamentos', name_hash)

            local_static_imgpath = os.path.join('static', static_imgpath)
            os.system(f'cp {imgpath} {local_static_imgpath}')

            f = form.cleaned_data
            print('value',f['value'])

            w = Week.objects.all()
            data = f['participants']
            doc_notice = f['doc_notice']
            lines = data.split('\n')
            participants = []

            for l in lines:
                tks = l.split(',')
                id,check = tks[0].split('-')
                id = int(id)
                p = w.get(compet_id=id)
                participants.append((",".join((p.compet.compet_id_full,p.compet.compet_name))))

            form = ConfirmPaymentForm(initial={'participants':'\n'.join(participants), 'receipt_file': static_imgpath,
                                               'doc_name': f['doc_name'], 'doc_email': f['doc_email'], 'value':f['value'],
                                               'doc_number': f['doc_number'], 'doc_address':f['doc_address'],
                                               'doc_notice':f['doc_notice'], 'doc_fiscal':f['doc_fiscal'],
                                               })

            return render(request, 'week/confirm_payment_tax.html', {'form': form, 'pagetitle': 'Informa pagamento', 'participants': participants, 'imgpath': static_imgpath})
    else:
        partic = Week.objects.filter(school=school)
        participants = []
        for p in partic:
            participants.append((",".join((p.compet.compet_id_full,p.compet.compet_name))))
        value = format_currency(TAX_VALUE*len(participants))
        doc_email = school.school_deleg_email
        doc_name = school.school_name

        doc_address = school.school_name + '\n' + 'Setor Financeiro\n' + school.school_address + ', ' + school.school_address_number

        if school.school_address_complement is not None:
            doc_address += ', ' + school.school_address_complement

        doc_address += '. ' + school.school_address_district + '\n' + school.school_zip + ' ' + school.school_city + ' ' + school.school_state

        form = InformPaymentForm(initial={'participants':'\n'.join(participants), 'doc_email': doc_email,
                                          'doc_name': doc_name, 'doc_address': doc_address, 'value': value})

    return render(request, 'week/confirm_partic_week.html', {'form': form, 'pagetitle': 'Informa pagamento'})

@user_passes_test(in_compet_coord_colab_group, login_url='/contas/login/')
def process_payment(request):
    if request.user.groups.filter(name__in=['compet']).exists():
        payer = 'compet'
        school = request.user.compet.compet_school
    elif request.user.groups.filter(name__in=['colab', 'colab_full']).exists():
        payer = 'school'
        school = request.user.colab.colab_school
    else:
        payer = 'school'
        school = request.user.deleg.deleg_school

    if request.method == 'POST':
        form = ConfirmPaymentForm(request.POST)

        if form.is_valid():
            f = form.cleaned_data
            w = Week.objects.all()
            data = f['participants']
            receipt_file = f['receipt_file']
            lines = data.split('\n')
            participants = []
            for l in lines:
                tks = l.split(',')
                id,check = tks[0].split('-')
                id = int(id)
                p = w.get(compet_id=id)
                p.tax_paid = True
                p.save()

            week_dir = os.path.join(MEDIA_ROOT, 'semana')
            if not os.path.exists(week_dir):
                os.mkdir(week_dir, 0o755)
            pag_dir =  os.path.join(week_dir, 'pagamentos')
            if not os.path.exists(pag_dir):
                os.mkdir(pag_dir, 0o755)

            payment = Payment()
            payment.value = float(f['value'].replace(',','.'))
            payment.doc_name = f['doc_name']
            payment.doc_number = f['doc_number']
            payment.doc_email = f['doc_email']
            payment.doc_address = f['doc_address']

            payment.data = data
            payment.save()
            source_receipt_file = os.path.join(BASE_DIR, 'static', receipt_file)
            file_extension = os.path.splitext(source_receipt_file)[1]
            dest_receipt_file = os.path.join(pag_dir, str(payment.id) + file_extension)

            print(f'cp {source_receipt_file} {os.path.join(MEDIA_ROOT,dest_receipt_file)}')
            os.system(f'cp {source_receipt_file} {os.path.join(MEDIA_ROOT,dest_receipt_file)}')
            pos = dest_receipt_file.find('media')
            payment.receipt_file = dest_receipt_file[pos-1:]
            payment.save()

            msg = 'O pagamento foi processado corretamente. Por favor aguarde o Setor Financeiro da SBC confirmar o recebimento (pode demorar um ou dois dias).'
            messages.success(request, msg)
            if payer == 'compet':
                return redirect('/compet/')
            else:
                return redirect('/restrito/')

    else:
        partic = Week.objects.filter(school=school)
        participants = []
        for p in partic:
            participants.append((",".join((p.compet.compet_id_full,p.compet.compet_name))))
        doc_email = school.school_deleg_email
        doc_name = school.school_name
        doc_address = f'''{school.school_name}
Setor Financeiro
{school.school_address}, {school.school_address_number}. {school.school_address_complement} {school.school_address_district}
{school.school_zip} {school.school_city} {school.school_state}'''
        form = InformPaymentForm(initial={'participants':'\n'.join(participants), 'doc_email': doc_email,
                                          'doc_name': doc_name, 'doc_address': doc_address, 'value': value})

    #return render(request, 'week/confirm_partic_week.html', {'form': form, 'pagetitle': 'Informa pagamento'})
    return render(request, 'week/sbc_show_payment.html', {'form': form, 'pagetitle': 'Informa pagamento'})

@user_passes_test(in_sbc_group, login_url='/contas/login/')
def sbc_list_payment(request):
    todo = Payment.objects.filter(confirmed_sbc=False, ignored=False).order_by('time_informed')
    done = Payment.objects.filter(confirmed_sbc=True).order_by('time_informed')
    ignored = Payment.objects.filter(ignored=True).order_by('time_ignored')
    return render(request, 'week/sbc_list_payment.html', {'pagetitle': 'Confirma pagamento', 'todo': todo, 'done': done, 'ignored':ignored})
        
@user_passes_test(in_sbc_group, login_url='/contas/login/')
def sbc_process_payment(request):
    # not used

    if request.method == 'POST':
        form = ConfirmPaymentForm(request.POST)
        if form.is_valid():
            print("form is valid")
            f = form.cleaned_data
            w = Week.objects.all()
            data = f['participants']
            receipt_file = f['receipt_file']
            lines = data.split('\n')
            participants = []
            print(lines)
            for l in lines:
                print(l)
                tks = l.split(',')
                id,check = tks[0].split('-')
                id = int(id)
                p = w.get(compet_id=id)
                p.tax_paid = True
                p.save()
                print("saving participant",p)
                participants.append(p)

            week_dir = os.path.join(MEDIA_ROOT, 'semana')
            if not os.path.exists(week_dir):
                os.mkdir(week_dir, 0o755)
            pag_dir =  os.path.join(week_dir, 'pagamentos')
            if not os.path.exists(pag_dir):
                os.mkdir(pag_dir, 0o755)

            payment = Payment()
            payment.doc_name = f['doc_name']
            payment.doc_email = f['doc_email']
            payment.doc_address = f['doc_address']

            payment.data = data
            payment.save()
            source_receipt_file = os.path.join(BASE_DIR, receipt_file)
            file_extension = os.path.splitext(source_receipt_file)[1]
            payment.receipt_file = os.path.join(pag_dir, str(payment.id) + file_extension)

            print(payment.receipt_file)
            os.system(f'cp {source_receipt_file} {os.path.join(MEDIA_ROOT,payment.receipt_file)}')
            payment.save()
            # now we have payment id, set it so that we can build the receipt
            print("participants",participants)
            for p in participants:
                p.payment_id = payment.id
                p.save()
                print("saving payment_id",payment.id)

            msg = 'O pagamento foi processado corretamente.'
            messages.success(request, msg)
            return redirect('/sbc/')

    else:
        partic = Week.objects.filter(school=school)
        participants = []
        for p in partic:
            participants.append((",".join((p.compet.compet_id_full,p.compet.compet_name))))
        doc_email = school.school_deleg_email
        doc_name = school.school_name
        #TODO: Check for None
        doc_address = f'''{school.school_name}
Setor Financeiro
{school.school_address}, {school.school_address_number}. {school.school_address_complement} {school.school_address_district}
{school.school_zip} {school.school_city} {school.school_state}'''
        form = InformPaymentForm(initial={'participants':'\n'.join(participants), 'doc_email': doc_email,
                                          'doc_name': doc_name, 'doc_address': doc_address})

    return render(request, 'week/confirm_partic_week.html', {'form': form, 'pagetitle': 'Informa pagamento'})

@user_passes_test(in_sbc_group, login_url='/contas/login/')
def sbc_show_payment(request,id):
    p = Payment.objects.get(pk=id)
    print(p.receipt_file)
    if request.method == 'POST':
        form = SBCprocessPaymentForm(request.POST)
        if 'ignore' in request.POST:
            p.ignored = True
            p.time_ignored = make_aware(datetime.now())
            p.save()
            messages.success(request, 'Pagamento ignorado')
            return redirect('/semana/sbc_lista_pagamento')
        elif 'cancel' in request.POST:
            return redirect('/semana/sbc_lista_pagamento')

        #print(p.receipt_file)
        p.confirmed_sbc = True
        p.time_confirmed = make_aware(datetime.now())
        p.save()
        messages.success(request, 'Pagamento confirmado')
        w = Week.objects.all()
        data = p.data
        lines = data.split('\n')
        for l in lines:
            tks = l.split(',')
            id,check = tks[0].split('-')
            id = int(id)
            partic = w.get(compet_id=id)
            partic.tax_confirmed = True
            partic.payment = p
            partic.save()

        return redirect('/semana/sbc_lista_pagamento')


    else:
        form = SBCprocessPaymentForm(initial={'payment_id': id})
    return render(request, 'week/sbc_show_payment.html', {'form': form, 'p': p, 'pagetitle': 'Confirma pagamento'})
