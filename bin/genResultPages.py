#!/usr/bin/env python3

import sys,re,os,getopt
from io import StringIO

LEVEL_NAME = {'j': 'Júnior', '1': '1', '2':'2', 'u': 'Sênior', 's': 'Sênior'}

def usage():
    print('usage:\n   {} [-h] [-m modality] [-n name] [-p phase] [-y year] output-dir'.format(sys.argv[0]))

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hm:n:p:y:", ["help","modality","name","phase", "year"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    f = None
    phase = None
    modality = 'p'
    year = 2020
    name = str(year)
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-m", "--modality"):
            modality = a
        elif o in ("-n", "--name"):
            name = a
        elif o in ("-y", "--year"):
            year = a
        elif o in ("-p", "--phase"):
            phase = int(a)
        else:
            assert False, "unhandled option"


    if len(args) > 0:
        outputdir = args[0]
    else:
        usage()
    if not os.path.exists(outputdir):
        os.mkdir(outputdir)
    base = os.path.split(outputdir)[0]
    
    print('year =', year)
    print('name =', name)
    print('modality =', modality)
    print('phase =', phase)
    print('base =', base)
    print('outputdir =', outputdir)

    if modality=='p':
        pat_problem=re.compile("includeProblem\{(?P<title>[^}]*)\}\{(?P<dirname>[^}]*)\}\{(?P<codename>[^}]*)\}")
    else:
        #pat_problem=re.compile("incluir\{../tarefas/(?P<dirname>[^}]*)\}")
        pat_problem=re.compile("includeTask\{../tasks/(?P<dirname>[^}]*)\}")

    if modality == 'p':
        base = 'prog'
        levels = ('j','1','2','u')
        modality_name = 'Programação'
    else:
        base = 'inic'
        levels = ('j','1','2')
        modality_name = 'Iniciação'

    if phase==None:
        phases = (1,2,3)
    else:
        phases = [phase]
    for phase in phases: #,2): #,3):
        print('phase =',phase)
        result_page = StringIO()
        print('title:Fase {} - Modalidade {}\ntemplate:flatpages_passadas.html'.format(phase,modality_name),file=result_page)
        for level in levels:
        tasks = []
            print("<h2>Nível {}</h2>".format(LEVEL_NAME[level]),file=result_page)
            print("<ul>",file=result_page)
            if modality=='p':
                print('<li><a href="/static/extras/obi{}/provas/ProvaOBI{}_f{}p{}.pdf">Caderno de tarefas da prova</a></li>'.format(year,year,phase,level))
                print('<li>Exemplos de soluções:',file=result_page)
                print('<ul>',file=result_page)

                print('modality =',modality)
                print('phase =',phase)
                with open(os.path.join(base,"fase-{}".format(phase),"documents","ProvaOBI{}_f{}p{}.tex".format(year,phase,level))) as f:

                    tex_prova=f.read()
            else:
                print('<li><a href="/static/extras/obi{}/provas/ProvaOBI{}_f{}p{}.pdf">Caderno de tarefas da prova</a></li>'.format(year,year,phase,level),file=result_page)
                print('<li>Exemplos de soluções:',file=result_page)
                with open(os.path.join(base,"fase-{}".format(phase),"documents","ProvaOBI{}_f{}i{}.tex".format(year,phase,level))) as f:

                    tex_prova=f.read()
                
            m = re.findall(pat_problem,tex_prova)
            print(m)
            order = 1
            for matched in m:
                if modality == 'i':
                    problem_code = matched
                    #problems = 'tarefas'
                    problems = 'tasks'
                    documents = ''
                    statement = 'enunciado.tex'
                else:
                    problem_code = matched[2]
                    problems = 'problems'
                    documents = 'documents'
                    statement = 'statement.tex'
                    title = matched[0]
                    problem_name="{}f{}{}{}_{}".format(name,phase,modality,level,problem_code)
                    print('<li> {}:'.format(title),file=result_page)
                    tasks.append((title,problem_name))
                    #	<a href="/static/extras/obi2019/solucoes/2019f1pj_domino/domino_py2.py">Solução A</a> (Python 2), 

            # gabaritos
            print('</ul>',file=result_page)
            print('<li>Gabaritos:',file=result_page)
            print('<ul>',file=result_page)
            for t in tasks:
                print('<li><a href="/static/extras/obi{}/gabaritos/{}f{}p{}_{}.zip">{}</a></li>'.format(name,phase,modality,level,t[1],t[0]))
        
            print('</ul>',file=result_page)
        print('-----------')
        print(result_page.getvalue())
                #ifilename = os.path.join(base,"fase-{}".format(phase),problems,problem_code,documents,statement)
                #ofilename = os.path.join(outputdir,"{}f{}{}{}_{}.html".format(name,phase,modality,level,problem_code))
                #ofile = open(ofilename,'w')

                #if name==year:
                    # it is a task
                #    print(ifilename,ofile,title,modality,problem_name="{}f{}{}{}_{}".format(name,phase,modality,level,problem_code),template_type="tasks")
                #else:
                    # it is an exam
                #    print(ifilename,ofile,title,modality,problem_name="{}f{}{}{}_{}".format(name,phase,modality,level,problem_code),template_type="exams",order=order)
                #order += 1


if __name__ == "__main__":
    main()
