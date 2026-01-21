#!/usr/bin/env python3
# copy a directory

import os
import os.path
import shutil
import sys


def usage():
    print('usage:{} page.html'.format(sys.argv[0]), file=sys.stderr)
    sys.exit(-1)

def error(s):
    print('error: {}'.format(s), file=sys.stderr)
    sys.exit(-1)

def clean(l,year,phase,level):
    l = l.replace("../../../","/")
    l = l.replace("../../","/")
    l = l.replace("../","/")
    l = l.replace("//","/")
    l = l.replace("programacao_n{}/solucoes/".format(level),"/extras/solucoes/{}f{}p{}_".format(year,phase,level))
    l = l.replace("/extras/obi{}/gabaritos/".format(year),"/extras/gabaritos/{}f{}p{}_".format(year,phase,level))
    l = l.replace("programacao_n{}/pdf/provas/ProvaOBI{}_prog_f{}n{}.pdf".format(level,year,phase,level),"/extras/provas/ProvaOBI{}f{}p{}.pdf".format(year,phase,level))
    l = l.replace("pdf/provas/ProvaOBI{}_prog_f{}n{}.pdf".format(year,phase,level),"/extras/provas/ProvaOBI{}f{}p{}.pdf".format(year,phase,level))
    l = l.replace('href="solucoes/','href="/extras/solucoes/{}f{}p{}_'.format(year,phase,level))
    l = l.replace("<h4>Programação Nível Júnior</h4>","<h2>Nível Júnior</h2>")
    l = l.replace("<h4>Programação Nível 1</h4>","<h2>Nível 1</h2>")
    l = l.replace("<h4>Programação Nível 2</h4>","<h2>Nível 2</h2>")
    l = l.replace('.cpp.txt','.cpp')
    l = l.replace('.c.txt','.c')
    l = l.replace('.py.txt','.py')
    l = l.replace('.java.txt','.java')
    l = l.replace("</div>","")
    return l

def main():
    dirfrom = sys.argv[1]
    dir,base = os.path.split(dirfrom)
    year = int(base[3:])
    if year >= 2014:
        error('not implemented')
    dirto = os.path.join(sys.argv[2],base)
    print('copying from',dirfrom,'to',dirto)
    try:
        shutil.rmtree(dirto)
    except:
        pass
    os.mkdir(dirto)

    # indice
    index = TEMPLATE_INDEX.replace('YEAR',str(year))
    with open(os.path.join(dirto,'indice.html'),'w') as file:
        file.write(index)

    # qmerito
    os.mkdir(os.path.join(dirto,'qmerito'))
    if year != 2004:
        shutil.copy(os.path.join(dirfrom,'qmerito','iniciacao1.html'), os.path.join(dirto,'qmerito','i1.html'))
        shutil.copy(os.path.join(dirfrom,'qmerito','iniciacao2.html'), os.path.join(dirto,'qmerito','i2.html'))
        shutil.copy(os.path.join(dirfrom,'qmerito','programacao1.html'), os.path.join(dirto,'qmerito','p1.html'))
        shutil.copy(os.path.join(dirfrom,'qmerito','programacao2.html'), os.path.join(dirto,'qmerito','p2.html'))
    if year > 2007:
        shutil.copy(os.path.join(dirfrom,'qmerito','programacaoJ.html'), os.path.join(dirto,'qmerito','pj.html'))

    for phase in ('1','2'):
        if phase == '2' and year <= 2005:
            continue
        os.mkdir(os.path.join(dirto,'fase{}'.format(phase)))
        inic = TEMPLATE_INI.replace('YEAR',str(year)).replace('PHASE',phase)
        if year > 2005:
            with open(os.path.join(dirto,'fase{}'.format(phase),'iniciacao.html'),'w') as file:
                file.write(inic)
        prog = TEMPLATE_PROG.replace('YEAR',str(year)).replace('PHASE',phase)
        with open(os.path.join(dirto,'fase{}'.format(phase),'programacao.html'),'w') as file:
            file.write(prog)
            if year > 2007:
                if year >= 2010:
                    name = os.path.join(dirfrom,'res_fase{}_prog'.format(phase),'programacao_nj.html')
                else:
                    name = os.path.join(dirfrom,'res_fase{}_prog'.format(phase),'programacao_nj','tarefas_solucoes.html')
                with open(name,'r') as fin:
                    data = fin.readlines()
                    for l in data[4:]:
                        l = clean(l,year,phase,'j')
                        file.write(l)
                    
            if year >= 2010:
                name = os.path.join(dirfrom,'res_fase{}_prog'.format(phase),'programacao_n1.html')
            elif year > 2005:
                name = os.path.join(dirfrom,'res_fase{}_prog'.format(phase),'programacao_n1','tarefas_solucoes.html')
            else:
                name = os.path.join(dirfrom,'res_prog','tarefas_solucoes.html')
            with open(name,'r') as fin:
                data = fin.readlines()
                for l in data[4:]:
                    l = clean(l,year,phase,1)
                    file.write(l)

            if year >= 2010:
                name = os.path.join(dirfrom,'res_fase{}_prog'.format(phase),'programacao_n2.html')
            elif year > 2005:
                name = os.path.join(dirfrom,'res_fase{}_prog'.format(phase),'programacao_n2','tarefas_solucoes.html')
            else:
                name = os.path.join(dirfrom,'res_prog','tarefas_solucoes.html')
            with open(name,'r') as fin:
                data = fin.readlines()
                for l in data[4:]:
                    l = clean(l,year,phase,1)
                    file.write(l)

    # seletiva IOI
    if year <= 2009 and year != 2004:
        phase = 'sele'
        sele = TEMPLATE_SELE
        with open(os.path.join(dirto,'seletivaIOI.html'),'w') as file:
            file.write(sele)
            with open(os.path.join(dirfrom,'seletivaIOI','tarefas_solucoes.html'),'r') as fin:
                data = fin.readlines()
                for l in data[4:]:
                    l = l.replace("solucoes/","/extras/solucoes/{}{}_".format(year,phase))
                    l = l.replace("pdf/provas/obi{}_selt".format(year),"/extras/provas/ProvaOBI{}{}".format(year,phase))
                    l = l.replace("/extras/obi{}/gabaritos/".format(year),"/extras/gabaritos/{}{}_".format(year,phase))
                    l = l.replace("gabaritos/","/extras/gabaritos/{}{}_".format(year,phase))
                    #l = l.replace("/pdf/provas/ProvaOBI{}_seletivaIOI_".format(year,phase),"/extras/provas/ProvaOBI{}{}.pdf".format(year,phase))
                    l = l.replace("http://olimpiada.ic.unicamp.br/passadas/OBI2009/seletivaIOI/pdf/","/extras/provas/")
                    l = l.replace("http://olimpiada.ic.unicamp.br/passadas/OBI2009/seletivaIOI/","/")
                    l = l.replace("//extras","/extras")
                    l = l.replace("/provas/provas","/provas")
                    l = l.replace("/../extras","/extras")
                    l = l.replace("/../../extras","/extras")
                    l = l.replace("/../../../extras","/extras")
                    l = l.replace("</div>","")
                    file.write(l)
    
TEMPLATE_SELE = '''title: Seletiva IOI
template:obi/flatpages_passadas.html
<h1>Seletiva IOI</h1>
'''

TEMPLATE_PROG = '''title: Fase PHASE - Modalidade Programação
template:obi/flatpages_passadas.html
<h1>Fase PHASE - Modalidade Programação</h1>
'''

TEMPLATE_INI = '''title: Fase PHASE - Modalidade Iniciação
template:obi/flatpages_passadas.html
<h1>Fase PHASE - Modalidade Iniciação</h1>



<h2>Iniciação 1</h2>

<ul>
<li>
<a href="/extras/provas/ProvaOBIYEAR_fPHASEi1.pdf">Caderno de Tarefas</a></li>
<li>
<a href="/extras/provas/SolucaoOBIYEAR_fPHASEi1.pdf">Caderno de Soluções</a></li>
<li>
<a href="/extras/provas/GabaritoOBIYEAR_fPHASEi1.txt">Gabarito</a></li>
</ul>

<h3>Iniciação 2</h3>

<ul>
<li>
<a href="/extras/provas/ProvaOBIYEAR_fPHASEi2.pdf">Caderno de Tarefas</a></li>
<li>
<a href="/extras/provas/SolucaoOBIYEAR_fPHASEi2.pdf">Caderno de Soluções</a></li>
<li>
<a href="/extras/provas/GabaritoOBIYEAR_fPHASEi2.txt">Gabarito</a></li>

</ul>
'''

TEMPLATE_INDEX = '''title:OBIYEAR
template:obi/flatpages_passadas.html

<p>Aqui você encontra informações sobre as OBIs de anos anteriores. Para cada
ano, estão disponíveis Tarefas, Soluções e Gabaritos.

<p>Você também pode emitir Certicados de Participação, e consultar o Quadro de Mérito.

'''

if __name__ == "__main__":
    main()
