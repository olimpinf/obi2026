import os.path
import logging
import json

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.mail import send_mail
from django.contrib.auth.models import Group, User, UserManager
from django.http import JsonResponse

from obi.settings import BASE_DIR, DEFAULT_FROM_EMAIL
from .forms import SaciRegisterForm
from .models import SaciUser, SaciEvent, SaciBackup
from .utils.build_saci_page import build_page
from .utils.build_class_list import build_class_list
from principal.utils.utils import make_password


logger = logging.getLogger('OBI')

def index(request):
    return render(request, 'saci/index.html', {})

#def intro_js(request):
#    return render(request, 'saci/intro_js.html', {})

def courses(request):
    return render(request, 'saci/cursos.html', {})

def show_course(request,course_id):
    base = os.path.join(BASE_DIR,'attic','saci')
    if course_id == 'intro_js':
        return render(request, 'saci/intro_js.html', {})
    elif course_id == 'python':
        page = build_class_list("Programação para Iniciantes (Blockly+Python)", course_id, base)
        return render(request, 'saci/a_course.html', {'page': page})
    else:
        return render(request, 'saci/index.html', {})
        
        
def show_class(request,course_id,class_id):
    if course_id == 'intro_js' or course_id == 'provaf1' or course_id == 'provaf2' or course_id == 'prova':
        with open(os.path.join(BASE_DIR,'attic','saci','cursos',course_id,str(class_id))+'.html') as f:
            page = f.read()
    else:
        if str(request.user) == 'AnonymousUser':
            user = 'naoregistrado@saci'
            #if class_id != 'editor' and course_id == 'python' and int(class_id) >= 5:
            #    return render(request, 'saci/need_to_be_registered.html')
        else:
            user = str(request.user)
        #base = '/Users/ranido/Documents/OBI/saci/curso'
        base = os.path.join(BASE_DIR,'attic','saci','cursos')
        minify = True
        lang = 1
        prog_lang = 'py'
        blockly = True
        target = '{}_{}'.format(course_id,class_id)
        course_name_full = 'Programação para Iniciantes (Blockly+Python)'
        page = build_page(course_name_full,course_id,class_id,user,base,minify,lang,prog_lang,blockly)

    return render(request, 'saci/a_class.html', {'page': page})

def retrieve_backups(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=501)
    user = request.user
    data = json.loads(request.body.decode("utf-8"))
    backups = SaciBackup.objects.filter(user=user,the_type=data['the_type']).order_by("the_time").values()
    data = list(backups)
    return JsonResponse(data, safe=False) 

def retrieve_a_backup(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=501)
    user = request.user
    data = json.loads(request.body.decode("utf-8"))
    backup = SaciBackup.objects.filter(user=user,the_type=data['the_type'], id=data['id']).only('data').values()
    return JsonResponse(backup[0]['data'], safe=False) 

def delete_a_backup(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=501)
    user = request.user
    data = json.loads(request.body.decode("utf-8"))
    try:
        SaciBackup.objects.get(user=user,the_type=data['the_type'], id=data['id']).delete()
    except:
        return HttpResponse(status=501)
    return HttpResponse(status=204)

def add_a_backup(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=501)
    user_id = request.user.pk
    data = json.loads(request.body.decode("utf-8"))
    b = SaciBackup()
    b.the_type = data['the_type']
    b.user_id = user_id
    b.course = data['course']
    b.class_name = data['class_name']
    b.exercise =  data['exercise']
    b.data = data['data']
    b.comment = data['comment']
    b.save()
    return HttpResponse(status=204)

def log_event(request):
    if not request.user.is_authenticated:
        user_id = User.objects.get(username='olimpinf').pk
    else:
        user_id = request.user.pk
    data = json.loads(request.body.decode("utf-8"))
    e = SaciEvent()
    e.the_type = data['the_type']
    e.user_id = user_id
    e.course = data['course']
    e.class_index = int(data['class_index'])
    e.exercise =  data['exercise']
    e.code = data['code']
    e.total_tests = data['total_tests']
    e.correct_tests = data['correct_tests']
    e.save()
    return HttpResponse(status=204)


EMAIL_MSG_USER_PASSWD = '''{greeting} {name},

obrigado por se registrar no Ambiente Saci da Olimpíada Brasileira de Informática. Para acessar os cursos do Ambiente Saci utilize as seguintes credenciais:

usuário: {user}
senha: {password}

O link para acesso é:

https://olimpiada.ic.unicamp.br/contas/login/?next=/saci/

Bom proveito nos cursos!
---
Olimpíada Brasileira de Informática
https://www.sbc.org.br/obi
'''

def register(request):
    def send_email_saciuser_registered(name,sex,email,password):
        logger.info("send_email_saciuser_registered, user={}".format(email))
        if sex == 'F':
            greeting = 'Prezada'
        else:
            greeting = 'Prezado'
        msg = EMAIL_MSG_USER_PASSWD
        send_mail(
            'Saci, registro',
            msg.format(greeting=greeting,
                       name=name,
                       user=email,
                       password=password),
            DEFAULT_FROM_EMAIL,
            [email]
        )
        logger.info("SENT send_email_saciuser_registered, user={}".format(email))


    if request.method == 'POST':
        form = SaciRegisterForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            email = f['saci_email']
            saci_user = SaciUser()
            saci_user.sex = f['saci_sex']
            saci_user.school_year = f['saci_school_year']
            saci_user.birth_year = f['saci_birth_year']
            username = email
            password = make_password()
            user = User.objects.create_user(username, email, password)
            user.last_name = f['saci_name']
            user.is_staff = False
            g = Group.objects.get(name='saci')
            g.user_set.add(user)
            user.save()
            saci_user.user = user
            saci_user.save()
            send_email_saciuser_registered(user.last_name,saci_user.sex,email,password)
            return render(request, 'saci/register_resp.html', {})
    else:
        form = SaciRegisterForm()
    return render(request, 'saci/register.html', {'form': form })

