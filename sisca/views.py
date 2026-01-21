import logging
import os.path
import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.shortcuts import render, redirect
from reportlab.pdfgen import canvas

from sisca.utils.build_answer_sheet import draw_page, draw_pages
from sisca.utils.utils import (check_answers_file, check_partic_batch,
                               pack_and_send)

from .forms import CorrigeFolhasRespostasForm, GeraFolhasRespostasForm, GeraGabaritoIniForm, GeraGabaritoForm

logger = logging.getLogger(__name__)

BLACKLIST = ['kehakay194@moonran.com']

def in_sisca_group(user):
    """Use with a ``user_passes_test`` decorator to restrict access to 
    authenticated users who are in the "coord" group."""
    #return user.is_authenticated and user.groups(name='coord').exists()
    #print(user.is_authenticated,user.groups.filter(name__in=['sisca','local_coord']).exists())
    #print(user.is_authenticated,user.groups.filter(name=['local_coord']).exists())
    #print(user.is_authenticated,user.groups.filter(name=['sisca']).exists())
    return user.is_authenticated and user.groups.filter(name__in=['sisca','local_coord']).exists()
    #return user.is_authenticated and user.groups.filter(name__in=['local_coord', 'coord3']).exists()


#@user_passes_test(in_sisca_group) #, login_url='/accounts/login/')
def index(request):
    return render(request, 'sisca/desativado.html', {})

def gerador(request):
    return render(request, 'sisca/desativado.html', {})
    if request.method == 'POST':
        form = GeraFolhasRespostasForm(request.POST, request.FILES)
        # check whether it's valid:
        if form.is_valid():
            num_pages = 0
            f = form.cleaned_data
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="FolhaRespostas.pdf"'
            p = canvas.Canvas(response)
            try:
                in_file = request.FILES['source_file']
            except:
                in_file = None
            if not f['label2']:
                 f['label2'] = ''
            if not f['label3']:
                 f['label3'] = ''
            if not f['label4']:
                 f['label4'] = ''
            if f['num_dig'] > 6 and f['check_id']:
                messages.error(request, "Para identificação não numérica ou numérica com número de dígitos maior do que 6 não é possível incluir o dígito de verificação.")
                return render(request, 'sisca/gerador.html', {'form': form})
            if in_file:
                msg,errors,validated = check_partic_batch(in_file,int(f['num_dig']))
                if len(msg)==0 and len(errors)==0:
                    num_pages = draw_pages(p, validated, f['label1'], f['label2'], f['label3'], f['label4'], f['num_questions'], f['num_dig'], f['check_id'], f['num_alternatives'], obi=False)
                else:
                    return render(request, 'sisca/erros_gerador.html', {'msg':msg, 'errors': errors})
            else:
                if f['num_dig'] > 6:
                    messages.error(request, "Para identificação não numérica ou numérica com número de dígitos maior do que 6 é necessário fornecer um arquivo de participantes.")
                    return render(request, 'sisca/gerador.html', {'form': form})
                draw_page(p, f['label1'], f['label2'], f['label3'], f['label4'], f['num_questions'], f['num_dig'], f['check_id'], f['num_alternatives'], id="", name= "", obi=False)
                num_pages = 1
            logger.info("sisca gera folha respostas client_ip={}, num_pages={}".format(request.META.get('REMOTE_ADDR'),num_pages))
            p.save()
            return response 


    # if a GET (or any other method) we'll create a blank form
    else:
        form = GeraFolhasRespostasForm()
    return render(request, 'sisca/gerador.html', {'form': form})


def corretor(request):
    ## manutenção
    ## manutenção
    ## manutenção
    #error_msg = 'Sistema em manutenção, por favor aguarde'
    #error_msg = 'Sistema indisponível devido à correção das provas da OBI.'
    #return render(request, 'sisca/corretor_resp.html', {'error_msg':error_msg, 'errors': {}})
    ## manutenção
    return render(request, 'sisca/desativado.html', {})
    if request.method == 'POST':
        form = CorrigeFolhasRespostasForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data
            if f['email'] in BLACKLIST:
                return render(request, 'sisca/corretor_resp.html', {'error_msg': 'ERROR', 'errors': {}})
                
            answer_file = request.FILES['answer_file']
            msg,errors,validated = check_answers_file(answer_file, f['num_questions'], f['num_alternatives'])
            if msg != '' or len(errors)>0:
                return render(request, 'sisca/corretor_resp.html', {'error_msg':msg, 'errors': errors})
            f1 = form.save(commit = False)
            #f1.save(using='sisca')
            f1.save()
            source_file = os.path.join(settings.MEDIA_ROOT,str(f1.source_file))
            answer_file = os.path.join(settings.MEDIA_ROOT,str(f1.answer_file))
            error_msg = pack_and_send(f['email'],f['reference'],source_file,answer_file)
            if not error_msg:
                os.remove(source_file)
                os.remove(answer_file)
            return render(request, 'sisca/corretor_resp.html', {'error_msg':error_msg, 'errors': {}})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CorrigeFolhasRespostasForm()
    return render(request, 'sisca/corretor.html', {'form': form})

def gerador_gabarito(request):
    return render(request, 'sisca/desativado.html', {})
    num_questions = request.session['sisca_num_questions']        
    num_alternatives = request.session['sisca_num_alternatives']        
    if request.method == 'POST':
        form = GeraGabaritoForm(request.POST, num_questions=num_questions, num_alternatives=num_alternatives)
        if form.is_valid():
            if 'submit' in request.POST:
                f = form.cleaned_data
                answers = [[] for i in range(num_questions)]
                for k in f.keys():
                    m = re.match('question_(?P<question_num>\d+)', k)
                    if m:
                        question_num = int(m.group('question_num'))
                        for alternative in f[k]:
                            answers[question_num].append(alternative)

                content = ''
                if 'sisca_comment' in request.session.keys() and request.session['sisca_comment']:
                    comment_lines = request.session['sisca_comment'].split('\n')
                    content += '#==============\n'
                    content += '# Gabarito para\n'
                    for line in comment_lines:
                        content += '# ' + line + '\n'
                        content += '#==============\n\n'
                for i in range(len(answers)):
                    if 'X' in answers[i]:
                        content += f'{i+1}. -\n'
                    elif 'U' in answers[i]:
                        content += f'{i+1}. =\n'
                    elif len(answers[i]) == num_alternatives:
                        content += f'{i+1}. *\n'
                    else:
                        content += f'{i+1}. ' + ','.join(answers[i]) + '\n'

                response = HttpResponse(content, content_type='text/plain')
                response['Content-Disposition'] = 'attachment; filename="gabarito.txt"'
                return response
            
    # if a GET (or any other method) we'll create a blank form
    else:
        form = GeraGabaritoForm(num_questions=num_questions, num_alternatives=num_alternatives)

    comment = ''
    if 'sisca_comment' in request.session.keys() and request.session['sisca_comment']:
        comment_lines = request.session['sisca_comment'].split('\n')
        for line in comment_lines:
            comment += line + '<br />'
    return render(request, 'sisca/gerador_gabarito.html', {'form': form, 'comment': comment}) 

def gerador_gabarito_ini(request):
    return render(request, 'sisca/desativado.html', {})
    if request.method == 'POST':
        form = GeraGabaritoIniForm(request.POST, request.FILES)
        # check whether it's valid:
        if form.is_valid():
            f = form.cleaned_data
            request.session['sisca_comment']=f['comment']
            request.session['sisca_num_questions']=int(f['num_questions'])
            request.session['sisca_num_alternatives']=int(f['num_alternatives'])
            return redirect(f'/sisca/gerador_gabarito')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = GeraGabaritoIniForm()
    return render(request, 'sisca/gerador_gabarito_ini.html', {'form': form})
