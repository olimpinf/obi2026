#!/usr/bin/env python3
# generate flatpages from compiled data

import getopt
import html
import os
import re
import shutil
import string
import sys


def usage():
    print('usage:{} dirname'.format(sys.argv[0]), file=sys.stderr)
    sys.exit(-1)

def error(s):
    print('error:{}'.format(s), file=sys.stderr)
    usage()

def generate(dirname):
    if not os.path.isdir(dirname):
        print("error: -a needs a directory as argument")
        usage()
    
    pattern = re.compile('obi(?P<year>[0-9]{4})')
    m = re.search(pattern,dirname)
    if m:
        year = int(m.group('year'))
        generate_pages(year,dirname)
    for root, dirs, files in os.walk(dirname):
        for dir in dirs:
            m = re.search(pattern,dir) 
            if m:
                year = int(m.group('year'))
                generate_pages(year,os.path.join(root,dir))

def generate_pages(year,dirname):
    '''Generates a flatpage from compiled data'''
    print('generate',year,dirname)
    DEST_DIR = 'html/passadas_new/'
    TEMPLATE = 'flatpages_passadas.html'
    TEMPLATE_INDEX = 'flatpage_index_passadas.html'
    languages = {'.c':'C','.cpp':'C++','.cc':'C++','.pas':'Pascal','.py':'Python 2','.py2':'Python 2','.py3':'Python 3','.java':'Java','.js':'Javascript'}
    str_level = {'1':'1', '2':'2', 'j':'Júnior', 'J':'Júnior'}
    try:
        with open(os.path.join(dirname,'info.txt'),"r") as f:
            infodata = f.readlines()
    except:
        error('cannot read info.txt file')
        usage()

    if year >= 2018:
        phases = ['1','2','3']
        plevels = ['J','1','2','U']
        ilevels = ['J','1','2']
        ulevels = ['0']
        INDEX = '''
<p>A OBI{} foi realizada em três fases, nas Modalidades Iniciação (níveis 1 e 2) e Programação (níveis Júnior, 1, 2 e Sênior)</p>
<p>Nesta área você encontra os cadernos de tarefas das provas, exemplos de soluções e os gabaritos utilizados na correção.
 Você pode também consultar o Quadro de Medalhas de cada modalidade e emitir certificados de participação.</p>
'''

    elif year == 2017:
        phases = ['1','2','3']
        plevels = ['J','1','2']
        ilevels = ['1','2']
        ulevels = ['0']
        INDEX = '''
<p>A OBI{} foi realizada em três fases, nas Modalidades Iniciação (níveis 1 e 2), Programação (níveis Júnior, 1 e 2) e Universitária (nível único).</p>
<p>Nesta área você encontra os cadernos de tarefas das provas, exemplos de soluções e os gabaritos utilizados na correção.
 Você pode também consultar o Quadro de Medalhas de cada modalidade e emitir certificados de participação.</p>
'''
    elif year in [2014,2015,2016]:
        phases = ['1','2']
        plevels = ['J','1','2']
        ilevels = ['1','2']
        ulevels = ['0']
        INDEX = '''
<p>A OBI{} foi realizada em duas fases, nas Modalidades Iniciação (níveis 1 e 2), Programação (níveis Júnior, 1 e 2) e Universitária (nível único).</p>
<p>Nesta área você encontra os cadernos de tarefas das provas, exemplos de soluções e os gabaritos utilizados na correção.
 Você pode também consultar o Quadro de Medalhas de cada modalidade e emitir certificados de participação.</p>
'''
    elif year in [2008,2009,2010,2011,2012,2013]:
        phases = ['1','2']
        plevels = ['J','1','2']
        ilevels = ['1','2']
        ulevels = []
        INDEX = '''
<p>A OBI{} foi realizada em duas fases, nas Modalidades Iniciação (níveis 1 e 2) e  Programação (níveis Júnior, 1 e 2).</p>
<p>Nesta área você encontra os cadernos de tarefas das provas, exemplos de soluções e os gabaritos utilizados na correção.
 Você pode também consultar o Quadro de Medalhas de cada modalidade e emitir certificados de participação.</p>
'''
    elif year in [2006,2007]:
        phases = ['1','2']
        plevels = ['1','2']
        ilevels = ['1','2']
        ulevels = []
        INDEX = '''
<p>A OBI{} foi realizada em duas fases, nas Modalidades Iniciação (níveis 1 e 2) e  Programação (níveis 1 e 2).</p>
<p>Nesta área você encontra os cadernos de tarefas das provas, exemplos de soluções e os gabaritos utilizados na correção.
 Você pode também consultar o Quadro de Medalhas de cada modalidade e emitir certificados de participação.</p>
'''
    elif year in [2005]:
        phases = ['0']
        plevels = ['1','2']
        ilevels = ['1','2']
        ulevels = []
        INDEX = '''
<p>A OBI{} foi realizada em uma única fase, nas Modalidades Iniciação (níveis 1 e 2) e  Programação (níveis 1 e 2).</p>
<p>Nesta área você encontra os cadernos de tarefas das provas, exemplos de soluções e os gabaritos utilizados na correção.
 Você pode também consultar o Quadro de Medalhas de cada modalidade e emitir certificados de participação.</p>
'''
    elif year in [2002,2003,2004]:
        phases = ['0']
        plevels = ['0']
        ilevels = ['0']
        ulevels = []
        INDEX = '''
<p>A OBI{} foi realizada em uma única fase, nas Modalidades Iniciação (um único nível) e  Programação (um único nível).</p>
<p>Nesta área você encontra os cadernos de tarefas das provas, exemplos de soluções e os gabaritos utilizados na correção.
 Você pode também consultar o Quadro de Medalhas de cada modalidade e emitir certificados de participação.</p>
'''
    elif year in [1999,2000,2001]:
        phases = ['0']
        plevels = ['0']
        ilevels = []
        ulevels = []
        INDEX = '''
<p>A OBI{} foi realizada em uma única fase e apenas na Modalidade Programação (um único nível).</p>
<p>Nesta área você encontra os cadernos de tarefas das provas, exemplos de soluções e os gabaritos utilizados na correção.
 Você pode também consultar o Quadro de Medalhas de cada modalidade e emitir certificados de participação.</p>
'''
    else:
        error('Year?')
        usage()

    # generate index page
    destdir = DEST_DIR
    os.makedirs(destdir,exist_ok=True)
    htmlfile = open(os.path.join(destdir,'OBI{}.html'.format(year)),'w')
    print('title: OBI{}'.format(year),file=htmlfile)
    print('template:{}'.format(TEMPLATE),file=htmlfile)
    print(INDEX.format(year),file=htmlfile)
    htmlfile.close()

    # special case, OBI2002, participantes
    if year == 2002:
        destdir = os.path.join(DEST_DIR,'OBI{}'.format(year),'iniciacao')
        os.makedirs(destdir,exist_ok=True)
        htmlfile = open(os.path.join(destdir,'participantes.html'),'w')
        print('title: Participantes - Modalidade Iniciação',file=htmlfile)
        print('template: {}'.format(TEMPLATE),file=htmlfile)
        print('<h1>Participantes<br/> Modalidade Iniciação</h1>',file=htmlfile)
        part = "obi/static/extras/obi{}/participantes_iniciacao.html".format(year)
        with open(part,'r') as pf:
            pdata = pf.read()
        htmlfile.write(pdata)
        htmlfile.close()

    # generate pages qmerito
    destdir = os.path.join(DEST_DIR,'OBI{}'.format(year),'qmerito')
    os.makedirs(destdir,exist_ok=True)

    # qmerito modalidade iniciação
    print('merito inic commented',ilevels)
#     for level in ilevels:
#         qm = "obi/static/extras/obi{}/qmerito/i{}.html".format(year,level.lower())
#         if os.path.isfile(qm):
#             htmlfile = open(os.path.join(destdir,'i{}.html'.format(level)),'w')
#             if level == '0':
#                 if year < 2004:
#                     print('title: Classificação - Modalidade Iniciação',file=htmlfile)
#                     print('template: {}'.format(TEMPLATE),file=htmlfile)
#                     print('<h1>Classificação <br/> Modalidade Iniciação</h1>',file=htmlfile)
#                 else:
#                     print('title: Quadro de Medalhas - Modalidade Iniciação',file=htmlfile)
#                     print('template: {}'.format(TEMPLATE),file=htmlfile)
#                     print('<h1>Quadro de Medalhas <br/> Modalidade Iniciação</h1>',file=htmlfile)
#             else:
#                 print('title: Quadro de Medalhas - Modalidade Iniciação Nível {}'.format(level),file=htmlfile)
#                 print('template: {}'.format(TEMPLATE),file=htmlfile)
#                 print('<h1>Quadro de Medalhas <br/> Modalidade Iniciação Nível {}</h1>'.format(level),file=htmlfile)
#             with open(qm,'r') as qf:
#                 qmdata = qf.read()
#             htmlfile.write(qmdata)
#             htmlfile.close()
#         else:
#             print('missing qmerito',qm)

    # qmerito modalidade programação
    print('merito prog commented')
#     for level in plevels:
#         qm = "obi/static/extras/obi{}/qmerito/p{}.html".format(year,level.lower())
#         if os.path.isfile(qm):
#             htmlfile = open(os.path.join(destdir,'p{}.html'.format(level)),'w')
#             if level == '0':
#                 if year < 2004:
#                     print('title: Classificação - Modalidade Programação',file=htmlfile)
#                     print('template:{}'.format(TEMPLATE),file=htmlfile)
#                     print('<h1>Classificação <br/> Modalidade Programação</h1>',file=htmlfile)
#                 else:
#                     print('title: Quadro de Medalhas - Modalidade Programação',file=htmlfile)
#                     print('template:{}'.format(TEMPLATE),file=htmlfile)
#                     print('<h1>Quadro de Medalhas <br/> Modalidade Programação</h1>',file=htmlfile)
#             else:
#                 print('title: Quadro de Medalhas - Modalidade Programação Nível {}'.format(str_level[level]),file=htmlfile)
#                 print('template:{}'.format(TEMPLATE),file=htmlfile)
#                 print('<h1>Quadro de Medalhas <br/> Modalidade Programação Nível {}</h1>'.format(level),file=htmlfile)
#             with open(qm,'r') as qf:
#                 qmdata = qf.read()
#             htmlfile.write(qmdata)
#             htmlfile.close()
#         else:
#             print('missing qmerito',qm)

#     # qmerito modalidade universitária
#     for level in ulevels:
#         qm = "obi/static/extras/obi{}/qmerito/pu.html".format(year)
#         if os.path.isfile(qm):
#             htmlfile = open(os.path.join(destdir,'pu.html'),'w')
#             print('title: Quadro de Medalhas - Modalidade Universitária',file=htmlfile)
#             print('template:{}'.format(TEMPLATE),file=htmlfile)
#             print('<h1>Quadro de Medalhas <br/> Modalidade Universitária</h1>',file=htmlfile)
#             with open(qm,'r') as qf:
#                 qmdata = qf.read()
#             htmlfile.write(qmdata)
#             htmlfile.close()
#         else:
#             print('missing qmerito',qm)

    # generate pages programação
    for phase in phases:
        if phase=='0':
            destdir = os.path.join(DEST_DIR,'OBI{}'.format(year))
        else:
            destdir = os.path.join(DEST_DIR,'OBI{}'.format(year),'fase{}'.format(phase))
        os.makedirs(destdir,exist_ok=True)
        htmlfile = open(os.path.join(destdir,'programacao.html'),'w')
        if phase == '0':
            print('title: Modalidade Programação',file=htmlfile)
            print('template:{}'.format(TEMPLATE),file=htmlfile)
            print('<h1>Modalidade Programação</h1>',file=htmlfile)            
        else:
            print('title: Fase {} - Modalidade Programação'.format(phase),file=htmlfile)
            print('template:{}'.format(TEMPLATE),file=htmlfile)
            print('<h1>Fase {} - Modalidade Programação</h1>'.format(phase),file=htmlfile)
    
        for level in plevels:
            if level != '0':
                print('<h2>Nível {}</h2>'.format(level),file=htmlfile)
            prova = "obi/static/extras/obi{}/provas/ProvaOBI{}_f{}p{}.pdf".format(year,year,phase,level.lower())
            if not os.path.isfile(prova):
                print('missing prova',prova)
                sys.exit(-1)
            print('<ul><li><a href="/static/extras/obi{}/provas/ProvaOBI{}_f{}p{}.pdf">Caderno de tarefas da prova</a></li>'.format(year,year,phase,level.lower()),file=htmlfile)
            editorial = "obi/static/extras/obi{}/provas/EditorialOBI{}_f{}p{}.pdf".format(year,year,phase,level.lower())
            if not os.path.isfile(editorial):
                print('missing editorial',editorial)
            else:
                print('<li><a href="/static/extras/obi{}/provas/EditoriaOBI{}_f{}p{}.pdf">Soluções comentadas</a>.</li>'.format(year,year,phase,level.lower()),file=htmlfile)
            # solucoes
            print('<li>Exemplos de soluções:',file=htmlfile)
            print('<ul>',file=htmlfile)
            pattern_start = re.compile('F{}P{}'.format(phase,level))
            pattern_end = re.compile('F.P.')
            pattern_solutions_str = '(?P<pname>{}f.p._\\w*) (?P<name>.*)'.format(year)
            pattern_solutions = re.compile(pattern_solutions_str)
            start = 0
            for i in range(len(infodata)):
                m = re.match(pattern_start,infodata[i])
                if m:
                    start = i
            prob_name = []
            for line in infodata[start+1:]:
                line = line.strip()
                if line == '':
                    continue
                if re.match(pattern_end,line):
                    break
                m = re.match(pattern_solutions,line)
                if m:
                    prob_name.append([m.group('pname'),m.group('name')])
                    print('<li>{}:'.format(m.group('name')),file=htmlfile)
                    #problem = '{}f{}p{}_{}'.format(year,phase.lower(),level.lower(),m.group('pname'))
                    problem = m.group('pname')
                    solutions = []
                    for root, dirs, files in os.walk(os.path.join(dirname,'solucoes',problem)):
                        solutions = files
                    sols = string.ascii_uppercase
                    list_sols = []
                    for i in range(len(solutions)):
                        tmp,lang = os.path.splitext(solutions[i])
                        if lang not in ('.c','.cpp','.py','.java','.js','.pas'):
                            continue 
                        list_sols.append('<a href="/static/extras/obi{}/solucoes/{}/{}">Solução {}</a> ({})'.format(year,problem,solutions[i],sols[i],languages[lang]))
                    print(", ".join(list_sols),file=htmlfile)
                    print('</li>',file=htmlfile)
            print('</ul><li>Gabaritos:<ul>',file=htmlfile)
            for problem in prob_name:
                print('<li><a href="/static/extras/obi{}/gabaritos/{}.zip">{}</a></li>'.format(year,problem[0],problem[1]),file=htmlfile)
            print('</ul></li></ul>',file=htmlfile)
        htmlfile.close()

        # seletiva IOI
        phase = 'S'
        destdir = os.path.join(DEST_DIR,'OBI{}'.format(year))
        provas = []
        first = True
        for day in [0,1,2,3,4]:
            prova = "obi/static/extras/obi{}/provas/ProvaOBI{}_sel{}.pdf".format(year,year,day)
            if os.path.isfile(prova):
                provas.append(day)
                if first:
                    htmlfile = open(os.path.join(destdir,'seletivaIOI.html'),'w')
                    print('title: Seletiva IOI',file=htmlfile)
                    print('template:{}'.format(TEMPLATE),file=htmlfile)
                    print('<h1>Seletiva IOI</h1>',file=htmlfile)
                    first = False
        for p in provas:
            if p != 0:
                print('<h2>Prova {}</h2>'.format(p),file=htmlfile)
            print('<ul><li><a href="/static/extras/obi{}/provas/ProvaOBI{}_sel{}.pdf">Caderno de tarefas da prova</a></li>'.format(year,year,p),file=htmlfile)
            print('<li>Exemplos de soluções:<ul>',file=htmlfile)
            pattern_start = re.compile('FSP.')
            pattern_end = re.compile('F.P.')
            pattern_solutions_str = '(?P<pname>{}fsp._\\w*) Prova {} - (?P<name>.*)'.format(year,p)
            pattern_solutions = re.compile(pattern_solutions_str)
            start = 0
            for i in range(len(infodata)):
                m = re.match(pattern_start,infodata[i])
                if m:
                    start = i
            prob_name = []
            for line in infodata[start+1:]:
                line = line.strip()
                if line == '':
                    continue
                if re.match(pattern_end,line):
                    break
                m = re.match(pattern_solutions,line)
                if m:
                    prob_name.append([m.group('pname'),m.group('name')])
                    print('<li>{}:'.format(m.group('name')),file=htmlfile)
                    #problem = '{}f{}p{}_{}'.format(year,phase.lower(),level.lower(),m.group('pname'))
                    problem = m.group('pname')
                    for root, dirs, files in os.walk(os.path.join(dirname,'solucoes',problem)):
                        solutions = files
                    sols = string.ascii_uppercase
                    list_sols = []
                    for i in range(len(solutions)):
                        tmp,lang = os.path.splitext(solutions[i])
                        list_sols.append('<a href="/static/extras/obi{}/solucoes/{}/{}">Solução {}</a> ({})'.format(year,problem,solutions[i],sols[i],languages[lang]))
                    print(", ".join(list_sols),file=htmlfile)
                    print('</li>',file=htmlfile)

            print('</ul><li>Gabaritos:<ul>',file=htmlfile)
            for problem in prob_name:
                print('<li><a href="/static/extras/obi{}/gabaritos/{}.zip">{}</a>'.format(year,problem[0],problem[1]),file=htmlfile)
            print('</ul>',file=htmlfile)

            print('</ul>',file=htmlfile)
        if not first:
            htmlfile.close()

    # generate pages iniciação
    if len(ilevels)==0:
        return
    if len(phases)==0:
        destdir = os.path.join(DEST_DIR,'OBI{}'.format(year))
    for phase in phases:
        if phase=='0':
            destdir = os.path.join(DEST_DIR,'OBI{}'.format(year))
        else:
            destdir = os.path.join(DEST_DIR,'OBI{}'.format(year),'fase{}'.format(phase))
        os.makedirs(destdir,exist_ok=True)
        htmlfile = open(os.path.join(destdir,'iniciacao.html'),'w')
        if phase == '0':
            print('title: Modalidade Iniciação',file=htmlfile)
            print('template: {}'.format(TEMPLATE),file=htmlfile)
            print('<h1>Modalidade Iniciação</h1>',file=htmlfile)            
        else:
            print('title: Fase {} - Modalidade Iniciação'.format(phase),file=htmlfile)
            print('template: {}'.format(TEMPLATE),file=htmlfile)
            print('<h1>Fase {} - Modalidade Iniciação</h1>'.format(phase),file=htmlfile)
    
        for level in ilevels:
            if level != '0':
                print('<h2>Nível {}</h2>'.format(level),file=htmlfile)
            prova = "obi/static/extras/obi{}/provas/ProvaOBI{}_f{}i{}.pdf".format(year,year,phase,level.lower())
            if not os.path.isfile(prova):
                print('missing prova',prova)
                #sys.exit(-1)
                continue
            print('<ul><li><a href="/static/extras/obi{}/provas/ProvaOBI{}_f{}i{}.pdf">Caderno de tarefas da prova</a></li>'.format(year,year,phase,level.lower()),file=htmlfile)
            editorial = "obi/static/extras/obi{}/provas/SolucaoOBI{}_f{}i{}.pdf".format(year,year,phase,level.lower())
            if not os.path.isfile(editorial):
                print('missing solution',editorial)
            else:
                print('<li><a href="/static/extras/obi{}/provas/SolucaoOBI{}_f{}i{}.pdf">Soluções comentadas</a></li>'.format(year,year,phase,level.lower()),file=htmlfile)
            gab = "obi/static/extras/obi{}/gabaritos/{}f{}i{}.txt".format(year,year,phase,level.lower())
            if not os.path.isfile(gab):
                print('missing gabarito',gab)
            else:
                print('<li><a href="/static/extras/obi{}/gabaritos/{}f{}i{}.txt">Gabarito</a></li></ul>'.format(year,year,phase,level.lower()),file=htmlfile)
        htmlfile.close()


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "au", ["all", "update"])
    except getopt.GetoptError as err:
        print(err, file=sys.stderr) 
        usage()
    all = False
    update = False
    for o, a in opts:
        if o in ("-a", "--all"):
            all = True
        elif o in ("-u", "--update"):
            update = True
        else:
            assert False, "unhandled option"

    try:
        fname = args[0]
    except:
        print('error: need a filename',file=sys.stderr)
        usage()
    if os.path.isdir(fname):
        generate(fname)
    else:
        usage()

if __name__ == "__main__":
    main()
