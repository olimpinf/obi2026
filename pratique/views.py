import os
import paramiko
import re
from time import sleep

from django.shortcuts import render
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect

from cms.models import CMSsubmissionResults
from principal.utils.utils import write_uploaded_file
from tasks.views import rendertask
from tasks.models import Task, Question, Alternative
from .forms import SubmeteSolucaoPratiqueForm

from obi.settings import SSH_HOSTNAME_PRATIQUE, SSH_USERNAME_PRATIQUE

DEFAULT_TEMPLATE = 'tasks/default.html'

fix_descriptor = {
    '2021f1p1_torneio': '2021f1pj_torneio',
    '2021f1ps_torneio': '2021f1pj_torneio',
    '2021f1p2_idade': '2021f1pj_idade',
    '2021f1p2_zero': '2021f1p1_zero',
    '2021f1p2_tempo': '2021f1p1_tempo',
    '2021f1ps_torneio': '2021f1pj_torneio',
    '2021f1ps_zero': '2021f1p1_zero',
    '2021f1ps_tempo': '2021f1p1_tempo',
    '2021f1p2_tempo': '2021f1p1_tempo',
    '2021f1p2_zero': '2021f1p1_zero',
    '2021f1ps_zero': '2021f1p1_zero',
    #'2021f2p1_robo': '2021f2pj_robo',
    '2021f2p1_tenis': '2021f2pj_tenis',
    '2021f2ps_tenis': '2021f2pj_tenis',
    '2021f2p1_media': '2021f2pj_media',
    '2021f2p2_media': '2021f2pj_media',
    '2021f2p1_potencia': '2021f2pj_potencia',
    '2021f2p1_recorde': '2021f2pj_recorde',
    '2021f2p2_lista': '2021f2p1_lista',
    '2021f2ps_lista': '2021f2p1_lista',
    '2021f2p2_calculo': '2021f2p1_calculo',
    '2021f2p2_retangulo': '2021f2p1_retangulo',
    '2021f2ps_retangulo': '2021f2p1_retangulo',
    '2021f2ps_passatempo':'2021f2p2_passatempo',
    '2021f2ps_poligrama': '2021f2p2_poligrama',
    '2021f2ps_sanduiche': '2021f2p2_sanduiche',
    '2021f2ps_senha': '2021f2p2_senha',
    
    '2020f1p1_piloto': '2020f1pj_piloto',
    '2020f1p2_fissura': '2020f1p1_fissura',
    '2020f1ps_fissura': '2020f1p1_fissura',
    '2020f1p2_pandemia': '2020f1p1_pandemia',
    '2020f1ps_acelerador': '2020f1p2_acelerador',
    '2020f1p1_tesouro': '2020f1pj_tesouro',
    '2020f1p2_promocao': '2020f1p1_promocao',
    '2020f1ps_irmaos': '2020f1p2_irmaos',
    '2020f1p2_camisetas': '2020f1pj_camisetas',
    '2020f1ps_camisetas': '2020f1pj_camisetas',
    '2020f2p1_lesma': '2020f2pj_lesma',
    '2020f2p2_formiga': '2020f2p1_formiga',
    '2020f2ps_formiga': '2020f2p1_formiga',
    '2020f2ps_fotografia': '2020f2p2_fotografia',
    '2020f2p2_estrada': '2020f2p1_estrada',
    '2020f2ps_estrada': '2020f2p1_estrada',
    '2020f3ps_calorias': '2020f3pj_calorias',
    '2020f3p2_atlanta': '2020f3pj_atlanta',
    '2020f3p1_torre': '2020f3pj_torre',
    '2020f3ps_torre': '2020f3pj_torre',
    '2020f3p2_rede': '2020f3p1_rede',
    '2020f3p2_jogo': '2020f3p1_jogo',
    '2020f3ps_jogo': '2020f3p1_jogo',
    '2020f3p2_trem': '2020f3p1_trem',
    '2020f3ps_trem': '2020f3p1_trem',
    #'': '',
    
    '2019f1p1_idade': '2019f1pj_idade',
    '2019f1p2_idade': '2019f1pj_idade',
    '2019f1ps_chuva': '2019f1p2_chuva',
    '2019f1ps_idade': '2019f1pj_idade',
    '2019f1ps_imperial': '2019f1p2_imperial',
    '2019f1ps_soma': '2019f1p2_soma',
    '2019f2p1_nota': '2019f2pj_nota',
    '2019f2p2_matriz': '2019f2p1_matriz',
    '2019f2ps_matriz': '2019f2p2_matriz',
    '2019f2ps_supermercado': '2019f2p2_supermercado',
    '2019f3p1_manchas': '2019f3pj_manchas',
    '2019f3p2_manchas': '2019f3pj_manchas',
    '2019f3p1_parcelamento': '2019f3pj_parcelamento',
    '2019f3ps_etiquetas': '2019f3p2_etiquetas',
    '2019f3ps_mesa': '2019f3p2_mesa',
    '2019f3ps_metro': '2019f3p2_metro',
    '2019f3ps_computador': '2019f3p2_computador',
    '2019f3p2_mesa': '2019f3p1_mesa',
    '2019f3p2_parcelamento': '2019f3pj_parcelamento',
    '2019f3p2_pares': '2019f3pj_pares',
    '2019f3ps_xadrez': '2019f3p2_xadrez',

    '2018f1ps_figurinhas': '2018f1p2_figurinhas',
    '2018f1ps_piso': '2018f1p2_piso',
    '2018f2p1_capsulas': '2018f2pj_capsulas',
    '2018f2ps_elevador': '2018f2p2_elevador',
    '2018f2ps_fuga': '2018f2p2_fuga',
    '2018f3p1_batalha': '2018f3pj_batalha',
    '2018f3p1_troca': '2018f3pj_troca',
    '2018f3ps_baldes': '2018f3p2_baldes',
    '2018f3ps_bolas': '2018f3p2_bolas',
    '2018f3ps_cinco': '2018f3p2_cinco',
    '2018f3ps_muro': '2018f3p2_muro',

    '2017f1ps_botas': '2017f1p2_botas',
    '2017f1ps_game10': '2017f1p2_game10',
    '2017f2p1_montanha': '2017f2pj_montanha',
    '2017f2p1_tabuleiro': '2017f2pj_tabuleiro',
    '2017f2ps_frete': '2017f2p2_frete',
    '2017f2ps_mapa': '2017f2p2_mapa',
    '2017f2ps_papel': '2017f2p2_papel',
    '2017f2ps_xerxes': '2017f2p2_xerxes',
    '2017f3p1_gomoku': '2017f3pj_gomoku',
    '2017f3p1_zip': '2017f3pj_zip',
    '2017f3ps_arranhaceu': '2017f3p2_arranhaceu',
    '2017f3ps_codigo': '2017f3p2_codigo',
    '2017f3ps_imperio': '2017f3p2_imperio',
    '2017f3ps_postes': '2017f3p2_postes',
    '2016f2p1_medalhas': '2016f2pj_medalhas',
    '2016f2p1_caverna': '2016f2pj_caverna',

    '2015f2p1_impedimento': '2015f2pj_impedido',
    '2015f2ps_calculo': '2015f2p2_calculo',
    '2015f2ps_chocolate': '2015f2p2_chocolate',
    '2015f2p1_torre': '2015f2pj_torre',

    '2013f1p1_capital': '2013f1pj_capital',

    '2011f1p2_quadrado': '2011f2p2_quadrado',
    '2011f2pj_calculadora': '2011f2p1_calculadora',
    '2011f1p1_corrida': '2011f1pj_corrida',

    '2009f2p1_banda':'2009f2pj_banda',
    '2009f2p2_chocolate': '2009f2p1_chocolate',
    '2009f2pj_maratona': '2009f2pj_maratona',
    '2009f1p1_overflow': '2009f1p1_overflow',
    '2009f1p1_papel': '2009f1pj_papel',
    
    '2008f1p1_obi': '2008f1pj_obi',
    '2008f1p2_obi': '2008f1pj_obi',
    '2008f1p2_telefone': '2008f1p1_telefone',
    '2008f2p1_auto': '2008f2pj_auto',
    '2008f2p2_auto': '2008f2pj_auto',

    '2007f2p2_tele': '2007f2p1_tele',

    '2006f2p2_lobo': '2006f2p1_lobo',
}

MESSAGE_PRATIQUE_OFF = 'Devido a problemas técnicos, o Pratique está instável/indisponível no momento. O serviço retornará ao funcionamento normal assim que possível.'

def teste(request):
    return render(request,'pratique/teste.html', {})

def index(request):
    return render(request,'pratique/index.html', {})

def index_level(request, level):
    mod = level[0] # only first letter
    return render(request,'pratique/index_level.html', {'mod':mod, 'modlevel': level})

def example_c(request, level):
    mod = level[0] # only first letter
    return render(request,'pratique/example_c.html', {'mod': mod, 'modlevel': level})

def example_cpp(request, level):
    mod = level[0] # only first letter
    return render(request,'pratique/example_cpp.html', {'mod': mod, 'modlevel': level})

def example_py(request, level):
    mod = level[0] # only first letter
    return render(request,'pratique/example_py.html', {'mod': mod, 'modlevel': level})

def example_java(request, level):
    mod = level[0] # only first letter
    return render(request,'pratique/example_java.html', {'mod': mod, 'modlevel': level})

def example_js(request, level):
    mod = level[0] # only first letter
    return render(request,'pratique/example_js.html', {'mod': mod, 'modlevel': level})

def tarefa_iniciacao(request,year,phase,level,code,show_answers=False):
    descriptor = '{}f{}i{}_{}'.format(year,phase,level,code)
    if request.POST.get("show_answers"):
        show_answers = True
    else:
        show_answers = False
    return rendertask(request, descriptor, show_answers=show_answers, mod='i')

def tarefa_programacao(request,year,phase,level,code,show_answers=False):
    descriptor = '{}f{}p{}_{}'.format(year,phase,level,code)
    if request.POST.get("show_answers"):
        show_answers = True
    else:
        show_answers = False
    #messages.warning(request, MESSAGE_PRATIQUE_OFF)
    return rendertask(request, descriptor, show_answers=show_answers, mod='p')

# must fix when new pratique is deployed
LANG = {'1':'C17 / gcc', '2':'C++17 / g++', '3':'Pascal / fpc', '7':'Python 3 / CPython', '5':'Java / JDK', '6':'Javascript'}

def corrige_programacao(request,year,phase,level,code):

    #return render(request, 'pratique/corrige_programacao_erro.html', {'msg': 'em manutenção, estamos atualizando o servidor Pratique'})

    descriptor = '{}f{}p{}_{}'.format(year,phase,level,code)
    # print(descriptor)
    try:
        descriptor = fix_descriptor[descriptor]
    except:
        pass
    # print('fixed_descriptor:',descriptor)

    if request.method == 'POST':
        # print('request is POST')
        # create a form instance and populate it with data from the request:
        form = SubmeteSolucaoPratiqueForm(request.POST,request.FILES)
        # check whether it is valid:
        if form.is_valid():
            print('form is valid')
            source_path = write_uploaded_file(request.FILES['data'],request.FILES['data'].name,'sub_www')
            # print('uploaded source',source_path)
            try:
                with open(source_path,"r") as fin:
                    source = fin.read()
                    #print('is utf8')
            except:
                try:
                    with open(source_path,"r", encoding='latin1') as fin:
                        #print('is latin1')
                        source = fin.read()
                except:
                    # do not remove, to see its type
                    #os.remove(source_path)
                    print('wrong encoding')
                    #messages.warning(request, MESSAGE_PRATIQUE_OFF)
                    return render(request, 'pratique/corrige_programacao_erro.html', {'msg': 'codificação não é utf-8 ou latin1'})

            problem_name=form.cleaned_data['problem_name']
            problem_name = descriptor
            problem_name_full = form.cleaned_data['problem_name_full']
            contest_id = 1
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            tries = 4
            ok = False
            print("will connect")
            for t in range(tries):
                try:
                    ssh.connect(hostname=SSH_HOSTNAME_PRATIQUE, username=SSH_USERNAME_PRATIQUE)
                    ok = True
                    break
                except:
                    print('connect failed, sleeping')
                    sleep(0.5)
            if not ok:
                #messages.warning(request, MESSAGE_PRATIQUE_OFF)
                return render(request, 'pratique/corrige_programacao_erro.html', {'msg': 'conexão com o servidor falhou'})
            print("connected")

            remote_path =  os.path.join('/','tmp',os.path.basename(source_path))
            ftp_ssh=ssh.open_sftp()
            ftp_ssh.put(source_path, remote_path)
            ftp_ssh.close()

            username='00000-J'
            CMD1 = "source /home/olimpinf/cms_venv/bin/activate"
            CMD2 = f"/home/olimpinf/cms_venv/bin/cmsAddSubmissionOBI -c {contest_id} -f '{problem_name}.%l':{remote_path} {username} {problem_name}"
            cmd = ";".join([CMD1, CMD2])
            print(cmd)
            stdin, stdout, stderr = ssh.exec_command(cmd)
            error = stderr.read().decode()
            if error:
                print(f'\n****************\nstderr={error}\n****************\n')
                #messages.warning(request, MESSAGE_PRATIQUE_OFF)
                return render(request, 'pratique/corrige_programacao_erro.html', {'msg': 'conexão com o servidor falhou durante a execução'})
            out = stdout.read().decode()
            print(f'\n****************\ncmd={cmd}\n****************\n')
            print(f'\n****************\nstdout={out}\n****************\n')

            ##### remove source and remote
            os.remove(source_path)
            cmd = 'rm {}'.format(remote_path)
            stdin, stdout, stderr = ssh.exec_command(cmd)

            try:
                sub_pattern = re.compile(r'ID:(\d+)')
                m = re.search(sub_pattern,out)
                cms_submission_id = int(m.group(1))
            except:
                ssh.close()
                #messages.warning(request, MESSAGE_PRATIQUE_OFF)
                return render(request, 'pratique/corrige_programacao_erro.html', {'msg': 'conexão com o servidor falhou, não retornou valor'})

            # print('cms_submission_id', cms_submission_id)
            ssh.close()
            #submission = SubWWW(sub_source=source,sub_lang=form.cleaned_data['sub_lang'],problem_name=form.cleaned_data['problem_name'],problem_name_full=form.cleaned_data['problem_name_full'],team_id=0,cms_submission_id=cms_submission_id)
            #submission.save()
            # save the submission data in session
            #request.session['submission_sub_id']=submission.sub_id
            #language = LANG[form.cleaned_data['sub_lang']]
            language = form.cleaned_data['sub_lang']
            #print(language)
            request.session['submission_sub_id']=cms_submission_id
            request.session['language']=language
            request.session['submission_problem_name_full']=form.cleaned_data['problem_name_full'],
            request.session['problem_request_path']=form.cleaned_data['problem_request_path'],
            subm_ctx={
                'problem_request_path': form.cleaned_data['problem_request_path'],
                'problem_name_full': form.cleaned_data['problem_name_full'],
                'language': language,
                'problem_level': request.path,
                'sub_id': cms_submission_id,
                }
            #messages.warning(request, MESSAGE_PRATIQUE_OFF)
            return render(request, 'pratique/corrige_programacao_resp.html', subm_ctx)

        else:
            pass
            # print('form is not valid')
            # print(form)
    #messages.warning(request, MESSAGE_PRATIQUE_OFF)
    return rendertask(request, descriptor, show_answers=False, mod='p')

def corrige_programacao_resultado(request,level,code,year,phase):
    #print("corrige_programacao_resultado")
    try:
        sub_id = request.session['submission_sub_id']
        problem_name_full = request.session['submission_problem_name_full'][0]
    except:
        sub_id=0
        problem_name_full = ''
    try:
        problem_request_path = request.session['problem_request_path']
    except:
        problem_request_path = ''
    # clear session data
    request.session['submission_sub_id'] = 0
    request.session['submission_problem_name_full'] = None
    # do not erase, in case of user reloading
    #request.session['problem_request_path'] = None
    language = request.session['language']
    subm_ctx = {
        'problem_name_full': problem_name_full,
        'language': language,
        'problem_request_path': problem_request_path,
        'msg': '',
        'log': "",}
    wait_tries = 20
    if sub_id == 0: # user is reloading page?
        subm_ctx['msg']='Por favor re-submeta sua solucão. Não atualize a página enquanto espera o resultado, pois isso impede que a resposta seja mostrada corretamente.'
    else:
        ok = False
        for i in range(1, wait_tries):
            # print('tries', i)
            sleep(3)
            # print('connecting to DB')
            cms_result = CMSsubmissionResults.objects.using('corretor_cms').filter(submission_id=sub_id)
            if len(cms_result) == 0:
                print('not yet...')
                continue
            cms_result = cms_result.get()
            print('got result',cms_result)

            try:
                junk = cms_result.score
                print('score:',cms_result.score)
            except:
                #print('no score')
                pass

            if cms_result.score == None:
                #print('empty score')
                continue

            try:
                junk = cms_result.evaluation_outcome
                #print('outcome:',cms_result.evaluation_outcome)
            except:
                #print('no outcome')
                pass
                #   continue
            if cms_result.evaluation_outcome != 'ok':
                #print('outcome not ok')
                pass
                # don't need it?
                #    continue

            if cms_result.dataset.time_limit_lang and cms_result.dataset.time_limit_lang[language]:
                time_limit_lang = cms_result.dataset.time_limit_lang[language]
            else:
                time_limit_lang = cms_result.dataset.time_limit # default

            #print("mem_limit_lang",cms_result.dataset.memory_limit_lang)
            #print("mem_limit",cms_result.dataset.memory_limit)
            if cms_result.dataset.memory_limit_lang and cms_result.dataset.memory_limit_lang[language]:
                memory_limit_lang = cms_result.dataset.memory_limit_lang[language]
            else:
                memory_limit_lang = cms_result.dataset.memory_limit # default
            #print("mem_limit_lang",memory_limit_lang)
                
            score_details =  cms_result.score_details
            max_time = 0
            max_memory = 0
            for s in score_details:
                for t in s['testcases']:
                    if t["time"] > max_time:
                        max_time = t["time"]
                    if t["memory"] and t["memory"] > max_memory:
                            max_memory = t["memory"]

            subm_ctx['sr'] = cms_result
            subm_ctx['max_time'] = max_time
            subm_ctx['max_memory'] = max_memory
            subm_ctx['time_limit'] = time_limit_lang
            subm_ctx['memory_limit'] = memory_limit_lang 
            ok = True
            #print("break in ok",ok)
            break;

        if not ok:
            subm_ctx['msg'] = 'Ocorreu um problema durante o processamento de sua solução. Se o problema persistir, por favor contate o administrador do site.'

    #messages.warning(request, MESSAGE_PRATIQUE_OFF)
    #print("corrige_programacao_resultado")
    return render(request, 'pratique/corrige_programacao_resultado_cms.html', subm_ctx)

def corrige_iniciacao(request,year,phase,level,code,show_answers=False):
    correct_answers = 0
    if request.method == 'POST':
        try:
            descriptor = request.POST['descriptor']
        except:
            raise
        try:
            task = Task.objects.get(descriptor=descriptor)
        except:
            raise
        questions = Question.objects.filter(task=task)
        total_questions = len(questions)
        if not questions:
            raise
        for q in questions:
            if str(q.num) in request.POST.keys():
                try:
                    answer = Alternative.objects.filter(question=q).get(num=request.POST[str(q.num)],correct=True)
                    correct_answers += 1
                except:
                    print("exception!")
                    pass
        # find level/modality from descriptor
        tmp = re.match('[0-9]{4}f(?P<phase>[123s])(?P<mod>[ip])(?P<level>[j12us])_',descriptor)
        tmp_mod = tmp.group('mod')
        tmp_level = tmp.group('level')
        context={'correct_answers':correct_answers,'total_questions':total_questions,'task':task}
        return render(request,'tasks/tarefa_iniciacao_resp.html', context)
    else:
        return render(request,'500.html', {})
