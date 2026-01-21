import os
import sys
from itertools import chain
import copy

from time import sleep
from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.template import loader
from django.db.models import F

from obi.settings import BASE_DIR, DEFAULT_FROM_EMAIL
from principal.utils.utils import obi_year
from principal.models import School, SchoolExtra, SchoolPhase3, Colab, Compet, IJ, I1, I2, PJ, P1, P2, PS, LEVEL_NAME_FULL, QueuedMail, States, Cities
from week.models import Week


DO_SEND = True

def send_messages(msg_subject,msg_template,msg_to_addresses):

    school_ini = None
    school_prog = None
    
    template_txt = loader.get_template(os.path.join(BASE_DIR,"gerencia","templates","gerencia",msg_template+"_txt.html"))
    try:
        template_htm = loader.get_template(os.path.join(BASE_DIR,"gerencia","templates","gerencia",msg_template+"_htm.html"))
    except:
        template_htm = ""
        
    if msg_to_addresses == 'all':
        coords = School.objects.filter(school_ok=True).distinct('school_deleg_email').order_by('school_deleg_email').only('school_deleg_email','school_deleg_name','school_deleg_username')
        colabs = Colab.objects.distinct('colab_email').order_by('colab_email').only('colab_email','colab_name')
        coords = list(chain(coords,colabs))
    elif msg_to_addresses == 'nocompet':
        # schools with not compets registered
        compet_schools = Compet.objects.distinct('compet_school_id').only('compet_school_id')
        schools_with_compets = [c.compet_school_id for c in compet_schools]
        coords = School.objects.filter(school_ok=True).distinct('school_deleg_email').order_by('school_deleg_email').only('school_deleg_email','school_deleg_name','school_deleg_username')
        colabs = Colab.objects.distinct('colab_email').order_by('colab_email').only('colab_email','colab_name')
        print("all coords", len(coords))
        print("all colabs", len(colabs))
        coords = coords.exclude(school_id__in=schools_with_compets)
        colabs = colabs.exclude(colab_school_id__in=schools_with_compets)
        print("coords", len(coords))
        print("colabs", len(colabs))
        coords = list(chain(coords,colabs))
        print("coords final", len(coords))
    elif msg_to_addresses == 'coord':
        coords = School.objects.filter(school_ok=True).only('school_deleg_email','school_deleg_name','school_deleg_username').distinct()
    elif msg_to_addresses == 'ini':
        schools_with_compet = Compet.objects.filter(compet_type__in=(IJ,I1,I2)).only('compet_school_id').distinct('compet_school_id').order_by('compet_school_id')
        print('schools_with_compet',len(schools_with_compet))
        school_ini_set = set()
        for s in schools_with_compet:
            school_ini_set.add(s.compet_school_id)
        coords = School.objects.filter(school_id__in=school_ini_set).only('school_deleg_email','school_deleg_name','school_deleg_username').distinct()
        print('coords',len(coords))
    elif msg_to_addresses == 'correcao-fase1':
        schools_with_compet = Compet.objects.all().only('compet_school_id').distinct('compet_school_id').order_by('compet_school_id')
        print('schools_with_compet',len(schools_with_compet))
        school_set = set()
        for s in schools_with_compet:
            school_set.add(s.compet_school_id)
        coords = School.objects.filter(school_id__in=school_set).only('school_deleg_email','school_deleg_name','school_deleg_username').distinct()
        print(len(coords))
    elif msg_to_addresses == 'ini-fase2':
        schools_with_compet = Compet.objects.filter(compet_type__in=(IJ,I1,I2), compet_classif_fase1=True).only('compet_school_id').distinct('compet_school_id').order_by('compet_school_id')
        print('schools_with_compet',len(schools_with_compet))
        school_ini_set = set()
        for s in schools_with_compet:
            school_ini_set.add(s.compet_school_id)
        coords = School.objects.filter(school_id__in=school_ini_set).only('school_deleg_email','school_deleg_name','school_deleg_username').distinct()
        print(len(coords))
        colabs = Colab.objects.filter(colab_school_id__in=school_ini_set).only('colab_email','colab_name').distinct()
        print(len(colabs))
        coords = list(chain(coords,colabs))
        print(len(coords))
        # for coord in coords:
        #     try:
        #         print(coord.school_deleg_email, coord.school_deleg_name)
        #     except:
        #         print(coord.colab_email, coord.colab_name)
        # sys.exit(0)
    elif msg_to_addresses == 'prog-fase2':
        schools_with_compet = Compet.objects.filter(compet_type__in=(PJ,P1,P2,PS),compet_classif_fase1=True).only('compet_school_id').distinct('compet_school_id').order_by('compet_school_id')
        print('schools_with_compet',len(schools_with_compet))
        school_prog_set = set()
        for s in schools_with_compet:
            school_prog_set.add(s.compet_school_id)
        # wrong coords = School.objects.filter(school_id__in=school_ini_set).only('school_deleg_email','school_deleg_name','school_deleg_username').distinct()
        coords = School.objects.filter(school_id__in=school_prog_set).only('school_deleg_email','school_deleg_name','school_deleg_username').distinct()
        colabs = Colab.objects.filter(colab_school_id__in=school_prog_set).only('colab_email','colab_name').distinct()
        coords = list(chain(coords,colabs))
        print(len(coords))
    elif msg_to_addresses == 'prog-fase3':
        schools_with_compet = Compet.objects.filter(compet_type__in=(PJ,P1,P2,PS),compet_classif_fase2=True).only('compet_school_id').distinct('compet_school_id').order_by('compet_school_id')
        print('schools_with_compet',len(schools_with_compet))
        school_prog_set = set()
        for s in schools_with_compet:
            school_prog_set.add(s.compet_school_id)
        coords = School.objects.filter(school_id__in=school_prog_set).only('school_deleg_email','school_deleg_name','school_deleg_username').distinct()
        colabs = Colab.objects.filter(colab_school_id__in=school_prog_set).only('colab_email','colab_name').distinct()
        coords = list(chain(coords,colabs))
        print(len(coords))
    elif msg_to_addresses == 'ini-fase3':
        schools_with_compet = Compet.objects.filter(compet_type__in=(IJ,I1,I2),compet_classif_fase2=True).only('compet_school_id').distinct('compet_school_id').order_by('compet_school_id')
        print('schools_with_compet',len(schools_with_compet))
        school_prog_set = set()
        for s in schools_with_compet:
            school_prog_set.add(s.compet_school_id)
        coords = School.objects.filter(school_id__in=school_prog_set).only('school_deleg_email','school_deleg_name','school_deleg_username').distinct()
        colabs = Colab.objects.filter(colab_school_id__in=school_prog_set).only('colab_email','colab_name').distinct()
        coords = list(chain(coords,colabs))
        print(len(coords))
    elif msg_to_addresses == 'site-ini-fase3':
        modality = 'ini'
        school_ini_set = set()
        for s in School.objects.filter(school_id__exact=F('school_site_phase3_ini')):
            school_ini_set.add(s.school_id)
        coords = School.objects.filter(school_id__in=school_ini_set).only('school_deleg_email','school_deleg_name','school_deleg_username').distinct()
        colabs = Colab.objects.filter(colab_school_id__in=school_ini_set).only('colab_email','colab_name').distinct()
        coords = list(chain(coords,colabs))
        print('coords:',len(coords))
        print('schools:',len(school_ini_set))
        # to test, send only to school_id=1
        #school_ini_set = set()
        #school_ini_set.add(1)
        #coords = School.objects.filter(school_id__in=school_ini_set).only('school_deleg_email','school_deleg_name','school_deleg_username').distinct()
        #coords = list(chain(coords,))
        #print('coords:',len(coords))
        
    elif msg_to_addresses == 'site-prog-fase3':
        modality = 'prog'
        school_prog_set = set()
        for s in School.objects.filter(school_id__exact=F('school_site_phase3_prog')):
            school_prog_set.add(s.school_id)
        coords = School.objects.filter(school_id__in=school_prog_set).only('school_deleg_email','school_deleg_name','school_deleg_username').distinct()
        colabs = Colab.objects.filter(colab_school_id__in=school_prog_set).only('colab_email','colab_name').distinct()
        print('schools:',len(school_prog_set))
        print('coords:',len(coords))
        print('colabs:',len(colabs))
        coords = list(chain(coords,colabs))
        print('all:',len(coords))
        
    elif msg_to_addresses == 'no-site-prog-fase3':
        tmp = Compet.objects.filter(compet_classif_fase2=True, compet_type__in=(3,4,5,6)).only('compet_school_id').distinct('compet_school_id')
        schools_with_compet = []
        for c in tmp:
            schools_with_compet.append(c.compet_school_id)
        school_prog_set = set()

        for s in School.objects.all():
            if s.school_id != s.school_site_phase3_prog and s.school_id in schools_with_compet:
                school_prog_set.add(s.school_id)
        coords = School.objects.filter(school_id__in=school_prog_set).only('school_deleg_email','school_deleg_name','school_deleg_username').distinct()
        colabs = Colab.objects.filter(colab_school_id__in=school_prog_set).only('colab_email','colab_name').distinct()
        coords = list(chain(coords,colabs))
        print('coords:',len(coords))
        print('schools:',len(school_prog_set))
    elif msg_to_addresses == 'all-fase3':
        schools_with_compet = Compet.objects.filter(compet_classif_fase2=True).only('compet_school_id').distinct('compet_school_id').order_by('compet_school_id')
        print('schools_with_compet',len(schools_with_compet))
        school_prog_set = set()
        for s in schools_with_compet:
            school_prog_set.add(s.compet_school_id)
        coords = School.objects.filter(school_id__in=school_prog_set).only('school_deleg_email','school_deleg_name','school_deleg_username').distinct()
        colabs = Colab.objects.filter(colab_school_id__in=school_prog_set).only('colab_email','colab_name').distinct()
        coords = list(chain(coords,colabs))
        print(len(coords))
    elif msg_to_addresses == 'week':
        modality = 'a'
        tmp = Week.objects.filter(partic_type='compet')
        compets = []
        for t in tmp:
            c = t.compet
            compets.append(c)

        school_week_set = set()
        for c in compets:
            school_week_set.add(c.compet_school_id)
        coords = School.objects.filter(school_id__in=school_week_set).only('school_deleg_email','school_deleg_name','school_deleg_username').distinct()
        colabs = Colab.objects.filter(colab_school_id__in=school_week_set).only('colab_email','colab_name').distinct()
        coords = list(chain(coords,colabs))
    elif msg_to_addresses == 'week2':
        tmp = Week.objects.filter(compet__compet_type__in=(1,2,3,4,5,8),form_info=None)
        print("len(tmp)",len(tmp),file=sys.stderr)
        compets = []
        for t in tmp:
            c = t.compet
            compets.append(c)

        school_week_set = set()
        for c in compets:
            school_week_set.add(c.compet_school_id)
        coords = School.objects.filter(school_id__in=school_week_set).only('school_deleg_email','school_deleg_name','school_deleg_username').distinct()
        colabs = Colab.objects.filter(colab_school_id__in=school_week_set).only('colab_email','colab_name').distinct()
        coords = list(chain(coords,colabs))
    elif msg_to_addresses == 'medalha':
        schools_with_compet = Compet.objects.filter(compet_medal__in=['o','p','b']).only('compet_school_id').distinct('compet_school_id').order_by('compet_school_id')
        print('schools_with_compet',len(schools_with_compet))
        school_prog_set = set()
        for s in schools_with_compet:
            school_prog_set.add(s.compet_school_id)
        coords = School.objects.filter(school_id__in=school_prog_set).only('school_deleg_email','school_deleg_name','school_deleg_username').distinct()
        colabs = Colab.objects.filter(colab_school_id__in=school_prog_set).only('colab_email','colab_name').distinct()
        coords = list(chain(coords,colabs))

    elif msg_to_addresses == 'sede_isolada_ini':
        #school_ids = (220, 197, 391, 719, 905, 412, 193, 447, 603, 988, 902, 567, 1071, 849, 493, 310, 617, 439, 184, 109, 745, 281, 1074, 147, 188, 152, 802, 541, 556, 961, 283, 1024, 829, 276, 166, 351, 1101, 148, 477, 595, 489, 940, 1008, 696, 1032, 890, 376, 810, 31, 1080, 854, 873, 323, 349, 839, 352, 465, 328, 983, 859, 989, 850, 479, 633, 927, 630, 702, 817, 650, 416, 356, 350, 511, 864, 301, 690)
        school_ids = (283,349,376,412,595,603,702,719,829,854,902,983,1074,1080,1101,690) # LEMBRETE
        #school_ids = (690,)
        coords = School.objects.filter(school_id__in=school_ids).distinct()
    elif msg_to_addresses == 'sede_isolada_prog':
        #school_ids = (1048, 752, 1136, 389, 798, 449, 1035, 1015, 175, 1112, 202, 375, 1016, 519, 594, 826, 473, 670, 494, 239, 586, 1078, 414, 1088, 168, 676, 638, 747, 649, 1044, 987, 365, 457, 198, 504, 196, 225, 921, 717, 268, 1120, 488, 785, 744, 1097, 808, 1108, 1198, 977, 341, 967, 300, 314, 673, 951, 601, 442, 306, 789, 1163, 1177, 236, 535, 1220, 832, 265, 508, 159, 1125, 929, 909, 320, 621, 671, 1178, 1207, 682, 835, 1174, 162, 299, 1139, 465, 222, 35, 382, 474, 170, 1119, 876, 433, 689, 1010, 503, 865, 227, 356, 533, 651, 1060, 1159, 542, 1214, 377, 697, 886, 949, 1029, 283, 1103, 690)
        #school_ids = (690,)
        #school_ids = (162, 283, 377, 457, 649, 651, 697, 876, 949, 967, 987, 1016, 1112, 1125, 1207, 1198, 1159, 690) # LEMBRETE
        school_ids = (554, 690)
        coords = School.objects.filter(school_id__in=school_ids).distinct()
    elif msg_to_addresses == 'sede_cidade_ini':
        sites = {544: [['Brasília','DF']]}
        #sites = {1: [['Campinas','SP'],['Valinhos','SP'],['Vinhedo','SP'],['Jundiaí','SP']],
        #        26: [['Aracaju','SE']],
        #        34: [['Porto Alegre','RS']],
        #        194: [['Recife','PE']],
        #        224: [['Mogi Mirim','SP']],
        #        227: [['Ipatinga','MG']],
        #        293: [['Goiânia','GO']],
        #        302: [['Brasília','DF']],
        #        325: [['Belo Horizonte','MG']],
        #        345: [['Crato','CE'],['Juazeiro do Norte','CE'],['Barbalha','CE']],
        #        355: [['Londrina','PR'],['Rolândia','PR']],
        #        378: [['Teodoro Sampaio','SP']],
        #        380: [['Vitória da Conquista','BA']],
        #        422: [['Niterói','RJ'],['Rio de Janeiro','RJ'],['São Gonçalo','RJ']],
        #        425: [['Natal','RN'],['Parnamirim','RN']],
        #        445: [['Videira','SC']],
        #        #471: [['São Bernardo do Campo','SP'],['São Paulo','SP']],
        #        472: [['Porto Velho','RO']],
        #        558: [['Muzambinho','MG']],
        #        576: [['Belém','PA']],
        #        586: [['Ribeirão Preto','SP']],
        #        614: [['Marituba','PA']],
        #        711: [['Campina Grande','PB']],
        #        737: [['Araxá','MG']],
        #        744: [['Salto','SP']],
        #        749: [['Limeira','SP']],
        #        757: [['João Pessoa','PB']],
        #        799: [['Ponta Grossa','PR']],
        #        825: [['Amontada','CE']],
        #        896: [['Maceió','AL']],
        #        903: [['Jacareí','SP'],['São José dos Campos','SP'],['Guararema','SP']],
        #        922: [['Jijoca de Jericoacoara','CE']],
        #        933: [['Vitória','ES']],
        #        959: [['São João del Rei','MG']],
        #        976: [['Água Branca','PI']],
        #        997: [['Santa Isabel','SP']],
        #        1043: [['Sobral','CE']],
        #        1057: [['Manaus','AM']],
        #        1107: [['Bauru','SP']],
        #        1168: [['Salvador','BA']],
        #        1253: [['Fortaleza','CE']]}

        # ====================== BEGIN TESTS =================================
        #sites = {690: [['Campinas','SP'],['Jundiaí','SP'],['Valinhos','SP'],['Vinhedo','SP']],
        #        1248: [['Aracaju','SE']],
        #        1249: [['Porto Alegre','RS']],
        #        1250: [['Recife','PE']],
        #        1251: [['Fortaleza','CE']],
        #        1252: [['Mogi Mirim','SP']]}
        #sites = {690: [['Campinas','SP'],['Jundiaí','SP'],['Valinhos','SP'],['Vinhedo','SP']], 1252: [['Barbalha','CE'],['Crato','CE'],['Juazeiro do Norte','CE']]}
        # ========================= END TESTS ====================================
        coords = School.objects.filter(school_id__in=sites.keys()).distinct()
        compets = {}
        for site_id, cities in sites.items():
            compets[site_id] = []
            for city in cities:
                compets[site_id] += list(Compet.objects.filter(compet_type__in=(IJ,I1,I2),compet_classif_fase2=True,
                                                               compet_school__in=School.objects.filter(school_city=city[0],school_state=city[1]).distinct()))

    elif msg_to_addresses == 'sede_cidade_prog':
        sites = {455: [['Curitiba','PR'],['Pinhais','PR']],
                 690: [['Campinas','SP']],
        }
        #sites = {344: [['Recife','PE'],['Cabo de Santo Agostinho','PE']],
        #         690: [['Campinas','SP']],
        #}
        #sites = {1221: [['Curitiba','PR'],['Pinhais','PR']],
        #         690: [['Campinas','SP']],
        #}
        #sites = {228: [['Curitiba','PR'],['Pinhais','PR']],
        #         690: [['Campinas','SP']],
        #}
        #sites = {264: [['Recife','PE'],['Cabo de Santo Agostinho','PE']],
        #         639: [['São Luís','MA']],
        #         690: [['Campinas','SP']],
        #}
        #sites = {1168: [['Salvador','BA']],
        #         690: [['Campinas','SP']],
        #}
        #sites = {194: [['Recife','PE']],
        #         592: [['Teresina','PI']],
        #         691: [['Salvador','BA']],
        #         845: [['Campina Grande','PB']],
        #         690: [['Campinas','SP']],
        #}
        #sites = {138: [['João Pessoa','PB']],
        #         690: [['Campinas','SP']],
        #}
        #sites = {208: [['Campina Grande','PB']],
        #         275: [['Teresina','PI']],
        #         872: [['Recife','PE']],
        #         958: [['São Luís','MA']],
        #         690: [['Campinas','SP']],
        #}
        #sites = {1: [['Campinas','SP'],['Paulínia','SP']],
        #        26: [['Aracaju','SE']],
        #        34: [['Porto Alegre','RS']],
        #        83: [['Uberlândia','MG']],
        #        195: [['Cascavel','CE']],
        #        229: [['Maceió','AL']],
        #        267: [['Campo Grande','MS']],
        #        293: [['Goiânia','GO'],['Anápolis','GO']],
        #        296: [['Belo Horizonte','MG']],
        #        302: [['Brasília','DF']],
        #        374: [['Guarulhos','SP']],
        #        422: [['Niterói','RJ'],['Rio de Janeiro','RJ']],
        #        425: [['Natal','RN'],['Ceará-Mirim','RN']],
        #        462: [['Caucaia','CE']],
        #        512: [['São Paulo','SP'],['Santo André','SP']],
        #        648: [['São José do Rio Preto','SP']],
        #        678: [['Teresina','PI']],
        #        681: [['Recife','PE']],
        #        710: [['São Luís','MA']],
        #        711: [['Campina Grande','PB']],
        #        757: [['João Pessoa','PB']],
        #        903: [['São José dos Campos','SP']],
        #        946: [['Taubaté','SP']],
        #        993: [['Salvador','BA']],
        #        1057: [['Manaus','AM']],
        #        1148: [['São Carlos','SP']],
        #        1253: [['Fortaleza','CE']]}

        # ====================== BEGIN TESTS =================================
        #sites = {690: [['Campinas','SP'],['Paulínia','SP']],
        #        1248: [['Aracaju','SE']],
        #        1249: [['Porto Alegre','RS']],
        #        1250: [['Uberlândia','MG']],
        #        1251: [['Cascavel','CE']],
        #        1252: [['Maceió','AL']]}
        #sites = {690: [['Campinas','SP'], ['Paulínia','SP']], 1252: [['Aracaju','SE']]}
        # ========================= END TESTS ====================================
        coords = School.objects.filter(school_id__in=sites.keys()).distinct()
        compets = {}
        for site_id, cities in sites.items():
            compets[site_id] = []
            for city in cities:
                compets[site_id] += list(Compet.objects.filter(compet_type__in=(PJ,P1,P2,PS),compet_classif_fase2=True,
                                                               compet_school__in=School.objects.filter(school_city=city[0],school_state=city[1]).distinct()))
    elif msg_to_addresses == 'sede_premiada_cfobi':
        school_ids = (390,926,1149,810,690)
        coords = School.objects.filter(school_id__in=school_ids).distinct()

    elif msg_to_addresses == 'sede_cidade_fase3_novos_alunos_prog':
        #sites = (265,296,594,673,747,1078,690)
        #sites = (503,690)
        sites = (442,690)
        coords = School.objects.filter(school_id__in=sites).distinct()
        compets = {}
        for s in sites:
            compets[s] = SchoolPhase3.objects.get(school_id=s).get_compets_prog_in_this_site()

    elif msg_to_addresses == 'sede_cidade_fase3_novos_alunos_ini':
        #sites = (817,1071)
        #sites = (961,)
        #sites = (690,)
        #sites = (690,184)
        #sites = (438,)
        #sites = (903,)
        sites = (849,)

        coords = School.objects.filter(school_id__in=sites).distinct()
        compets = {}
        for s in sites:
            compets[s] = SchoolPhase3.objects.get(school_id=s).get_compets_ini_in_this_site()

    elif msg_to_addresses == 'cfobi':
        schools_with_compet = Compet.objects.filter(compet_type__in=(3,5),compet_sex='F').only('compet_school_id').distinct('compet_school_id').order_by('compet_school_id')
        print('schools_with_compet',len(schools_with_compet))
        school_prog_set = set()
        for s in schools_with_compet:
            school_prog_set.add(s.compet_school_id)
        coords = School.objects.filter(school_id__in=school_prog_set).only('school_deleg_email','school_deleg_name','school_deleg_username').distinct()
        colabs = Colab.objects.filter(colab_school_id__in=school_prog_set).only('colab_email','colab_name').distinct()
        coords = list(chain(coords,colabs))

    elif msg_to_addresses == 'bic':
        schools_with_compet = Compet.objects.filter(compet_type__in=(1,2,3,4,5,7),compet_rank_final__lte=500).only('compet_school_id').distinct('compet_school_id').order_by('compet_school_id')
        print('schools_with_compet',len(schools_with_compet))
        school_prog_set = set()
        for s in schools_with_compet:
            school_prog_set.add(s.compet_school_id)
        coords = School.objects.filter(school_id__in=school_prog_set).only('school_deleg_email','school_deleg_name','school_deleg_username').distinct()
        colabs = Colab.objects.filter(colab_school_id__in=school_prog_set).only('colab_email','colab_name').distinct()
        coords = list(chain(coords,colabs))

    elif msg_to_addresses == 'consulta-site-fase3-ini':
        modality = 'ini'
        # only compets in ini; schools with compet in both ini and prog will be sent another message
        schools_with_compet_prog = Compet.objects.filter(compet_classif_fase2=True, compet_type__in=(3,4,5,6)).only('compet_school_id').distinct('compet_school_id').order_by('compet_school_id')
        schools_with_compet_ini = Compet.objects.filter(compet_classif_fase2=True, compet_type__in=(1,2,7)).only('compet_school_id').distinct('compet_school_id').order_by('compet_school_id')

        school_ini_set = set()
        for s in schools_with_compet_ini:
            school_ini_set.add(s.compet_school_id)
        school_prog_set = set()
        for s in schools_with_compet_prog:
            school_prog_set.add(s.compet_school_id)

        schools = School.objects.filter(school_id__in=school_ini_set).exclude(school_id__in=school_prog_set).order_by("school_id")

        schools = schools.exclude(school_city='Rio de Janeiro', school_state='RJ')
        schools = schools.exclude(school_city='Salvador', school_state='BA')
        schools = schools.exclude(school_city='Fortaleza', school_state='CE')
        schools = schools.exclude(school_city='Campinas', school_state='SP')
        schools = schools.exclude(school_city='Indaiatuba', school_state='SP')
        schools = schools.exclude(school_city='São Paulo', school_state='SP')
        schools = schools.exclude(school_city='São José dos Campos', school_state='SP')
        schools = schools.exclude(school_city='Valinhos', school_state='SP')

        
        # to test:
        # schools = School.objects.filter(school_id=1)
        
              
        compets_in_city = {}
        states = States.objects.all()
        comps = Compet.objects.filter(
            compet_type__in=[1, 2, 7],
            compet_classif_fase2=True
        ).select_related("compet_school")

        # group counts
        city_school_counts = {}
        for c in comps:
            school = c.compet_school
            key = (school.school_city, school.school_state)
            city_school_counts.setdefault(key, {})
            city_school_counts[key].setdefault(school.school_name, 0)
            city_school_counts[key][school.school_name] += 1

        #for c in city_school_counts.keys():
        #    print(c,city_school_counts[c])

        school_ini = city_school_counts

        print("len(schools)",len(schools))
        #schools = schools.exclude(school_site_phase3_ini__gte=1)
        #print("len(schools) excluded assigned",len(schools))
        #answered = SchoolExtra.objects.filter(school_answer_consulta_fase3__gte=1).only('school__school_id')
        #print("len(answered)",len(answered))
        #print(len(schools))
        #for s in answered:
        #print("len(schools) excluded answered",len(schools))

        

        coords = schools
        school_ids = schools.only('school_id')
        colabs = Colab.objects.filter(colab_school_id__in=school_ids)
        print("len(coords)", len(coords))
        print("len(colabs)", len(colabs))
        coords = list(chain(coords,colabs))
        print("len(coords)", len(coords))
        
    elif msg_to_addresses == 'consulta-site-fase3-prog':
        modality = 'prog'
        # all schools with compets in prog
        schools_with_compet_prog = Compet.objects.filter(compet_classif_fase2=True, compet_type__in=(3,4,5,6)).only('compet_school_id').distinct('compet_school_id').order_by('compet_school_id')

        school_prog_set = set()
        for s in schools_with_compet_prog:
            school_prog_set.add(s.compet_school_id)

        schools = School.objects.filter(school_id__in=school_prog_set).order_by("school_id")

        schools = schools.exclude(school_city='Rio de Janeiro', school_state='RJ')
        schools = schools.exclude(school_city='Salvador', school_state='BA')
        schools = schools.exclude(school_city='Fortaleza', school_state='CE')
        schools = schools.exclude(school_city='Campinas', school_state='SP')
        schools = schools.exclude(school_city='Indaiatuba', school_state='SP')
        schools = schools.exclude(school_city='São Paulo', school_state='SP')
        schools = schools.exclude(school_city='São José dos Campos', school_state='SP')
        schools = schools.exclude(school_city='Valinhos', school_state='SP')

        
        # find counts for ini
        compets_in_city = {}
        states = States.objects.all()
        comps = Compet.objects.filter(
            compet_type__in=[1, 2, 7],
            compet_classif_fase2=True
        ).select_related("compet_school")

        # group counts
        city_school_counts = {}
        for c in comps:
            school = c.compet_school
            key = (school.school_city, school.school_state)
            city_school_counts.setdefault(key, {})
            city_school_counts[key].setdefault(school.school_name, 0)
            city_school_counts[key][school.school_name] += 1

        #for c in city_school_counts.keys():
        #    print(c,city_school_counts[c])

        school_ini = copy.deepcopy(city_school_counts)
        
        # now prepare prog counts and to adresses

        schools_with_compet = Compet.objects.filter(compet_type__in=(3,4,5,6),compet_classif_fase2=True).only('compet_school_id').distinct('compet_school_id').order_by('compet_school_id')
        school_ini_set = set()
        for s in schools_with_compet:
            school_ini_set.add(s.compet_school_id)
        schools = School.objects.filter(school_id__in=school_ini_set)
        schools = schools.exclude(school_city='Rio de Janeiro', school_state='RJ')
        schools = schools.exclude(school_city='Salvador', school_state='BA')
        schools = schools.exclude(school_city='Fortaleza', school_state='CE')
        schools = schools.exclude(school_city='Campinas', school_state='SP')
        schools = schools.exclude(school_city='Indaiatuba', school_state='SP')
        schools = schools.exclude(school_city='São Paulo', school_state='SP')
        schools = schools.exclude(school_city='São José dos Campos', school_state='SP')
        schools = schools.exclude(school_city='Valinhos', school_state='SP')
        
        # to test:
        # schools = School.objects.filter(school_id=1)
        
        compets_in_city = {}
        states = States.objects.all()
        comps = Compet.objects.filter(
            compet_type__in=[3,4,5,6],
            compet_classif_fase2=True
        ).select_related("compet_school")

        # group counts
        city_school_counts = {}
        for c in comps:
            school = c.compet_school
            key = (school.school_city, school.school_state)
            city_school_counts.setdefault(key, {})
            city_school_counts[key].setdefault(school.school_name, 0)
            city_school_counts[key][school.school_name] += 1

        #for c in city_school_counts.keys():
        #    print(c,city_school_counts[c])

        school_prog = city_school_counts

        # print("len(schools)",len(schools))
        # schools = schools.exclude(school_site_phase3_prog__gte=1)
        # print("len(schools) excluded assigned",len(schools))
        # answered = SchoolExtra.objects.filter(school_answer_consulta_fase3__gte=1).only('school__school_id')
        # print("len(answered)",len(answered))
        # print(len(schools))
        # for s in answered:
        #     schools = schools.exclude(school_id=s.school_id)
        # print("len(schools) excluded answered",len(schools))

        print("len(schools)",len(schools))
        
        ### to do, make it uniform, use school in templates
        coords = schools
        
    elif msg_to_addresses == 'test':
        modality = 'ini'        
        coords = School.objects.filter(school_id=1).only('school_deleg_email','school_deleg_name','school_deleg_username').distinct()
        #colabs = Colab.objects.filter(colab_school_id=1).distinct('colab_email').order_by('colab_email').only('colab_email','colab_name')
        #coords = list(chain(coords,colabs))

    else:
        try:
            school_id = int(msg_to_addresses)
            coords = School.objects.filter(school_id__gte=school_id, school_ok=True)
        except:
            print('??')
            return 0
    print('num_emails:',len(coords))


    count,failed = 0,0
    sent = set()

    for coord in coords:
        try:
            to_address = coord.school_deleg_email
            to_name = coord.school_deleg_name
            to_school_name = coord.school_name
            username = coord.school_deleg_username
            greeting = "Caro(a) Prof(a)."
        except:
            try:
                to_address = coord.colab_email
                to_name = coord.colab_name
                to_school_name = coord.colab_school.school_name
                username = coord.colab_email
                if  coord.colab_sex == 'M':
                    greeting = "Caro Prof."
                if  coord.colab_sex == 'F':
                    greeting = "Cara Profa."
                else:
                    greeting = "Caro(a) Prof(a)."
            except:
                failed += 1
                print('\nfailed *********** {} failed'.format(coord), file=sys.stderr)
                continue
        if not to_address or not to_name or not to_school_name:
            print('******* missing data',to_address,to_name,to_school_name)
            failed += 1
            continue
        #if to_address in sent:
        #    print('\nfailed *********** {} already sent {}'.format(coord, to_address), file=sys.stderr)
        #    continue
        sent.add(to_address)

        try:
            city = coord.school_city
            state = coord.school_state
        except:
            try:
                city = coord.colab_school.school_city
                state = coord.colab_school.school_state
            except Exception as error:
                print("Could not get city and state",error,file=sys.stderr)
                sys.exit(0)

        if school_ini and (city, state) in school_ini.keys():
            extra_ini = school_ini[(city, state)]
        else:
            extra_ini = {}
        if school_prog and (city, state) in school_prog.keys():
            extra_prog = school_prog[(city, state)]
        else:
            extra_prog = {}

        context = {"greeting": greeting, 'school_name': to_school_name, 'coord_name': to_name, 'username': username, 'school': coord, 'school_ini': extra_ini, 'school_prog': extra_prog, 'modality': modality }
        
        # if msg_to_addresses in ('sede_isolada_ini'):        
        # if msg_to_addresses in ('sede_isolada_ini'):
        #     context['mod'] = 'ini'
        #     context['mod_name'] = 'Iniciação'
        #     context['mod_date'] = '15 de outubro'
        #     context['school'] = coord  # argh!
        # elif msg_to_addresses in ('sede_isolada_prog', 'sede_premiada_cfobi'):
        #     context['mod'] = 'prog'
        #     context['mod_name'] = 'Programação'
        #     context['mod_date'] = '1 de outubro'
        #     context['school'] = coord  # argh!
        # elif msg_to_addresses in ('sede_cidade_ini', 'sede_cidade_fase3_novos_alunos_ini'):
        #     context['mod'] = 'ini'
        #     context['mod_name'] = 'Iniciação'
        #     context['mod_date'] = '15 de outubro'
        #     context['school'] = coord  # argh!
        #     city = coord.school_city
        #     context['compets_info'] = compets[coord.school_id]
        #     #context['compets_info'] = sorted([[c.compet_id_full, c.compet_name, School.objects.get(school_id=int(c.compet_school_id)).school_name,
        #     #                                   LEVEL_NAME_FULL[c.compet_type]] for c in compets[coord.school_id]],
        #     #                                 key= lambda n: (n[3], n[2], n[1]))
        #     #compet_count = Compet.objects.filter(compet_type__in=(1,2,7),compet_classif_fase2=True,compet_school__school_city = city).count()
        #     #context['compets_count'] = compet_count
        # elif msg_to_addresses in ('sede_cidade_prog','sede_cidade_fase3_novos_alunos_prog'):
        #     context['mod'] = 'prog'
        #     context['mod_name'] = 'Programação'
        #     context['mod_date'] = '1 de outubro'
        #     context['school'] = coord  # argh!
        #     city = coord.school_city
        #     context['compets_info'] = compets[coord.school_id]
        #     #context['compets_info'] = sorted([[c.compet_id_full, c.compet_name, School.objects.get(school_id=int(c.compet_school_id)).school_name,
        #     #                                   LEVEL_NAME_FULL[c.compet_type]] for c in compets[coord.school_id]],
        #     #                                 key= lambda n: (n[3], n[2], n[1]))
        #     #compet_count = Compet.objects.filter(compet_type__in=(3,4,5,6),compet_classif_fase2=True,compet_school__school_city = city).count()
        #     #context['compet_count'] = compet_count
        
        body_txt = template_txt.render(context)
        if template_htm:
            body_htm = template_htm.render(context)
        else:
            body_htm = ""
        subject = msg_subject
        priority = 0

        m = QueuedMail(
            subject=subject,
            body=body_txt,
            body_html=body_htm,
            from_addr=DEFAULT_FROM_EMAIL,
            to_addr=to_address,
            priority=priority
        )
        m.save()
        #print()
        #print("-------")
        #print("queue", to_address)
        #print(body_htm)
        #print(body_txt)
        count += 1

    return count


class Command(BaseCommand):
    help = 'Send message'

    def add_arguments(self, parser):
        parser.add_argument('msg_subject', nargs='+', type=str)
        parser.add_argument('msg_template', nargs='+', type=str)
        parser.add_argument('msg_to_addresses', nargs='+', type=str)

    def handle(self, *args, **options):
        msg_subject = options['msg_subject'][0]
        msg_template = options['msg_template'][0]
        msg_to_addresses = options['msg_to_addresses'][0]
        count = send_messages(msg_subject, msg_template, msg_to_addresses)
        self.stderr.write(self.style.SUCCESS('Sent {} messages.'.format(count)))
