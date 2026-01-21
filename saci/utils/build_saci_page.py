#!/usr/bin/env python3

VERSION= 0.1

import getopt
import os
import os.path
import shutil
import subprocess
import sys, re
from glob import glob
from tempfile import NamedTemporaryFile
import base64

ratingTxt ='''
  <div style="width:130px;position:relative;right:0px;top:10px;float:right">
    <div style="margin-left:auto;margin-right:auto">
      <div id="ratingStars%d" style="margin-left:auto;margin-right:auto"><span></span></div>
      <div id="ratingMsg%d" class="rank">
	%s
      </div>
    </div>
  </div>
'''

# languages
EN=0
PT=1

translate = {
    'cancel': ['Cancel','Cancela'],
    'clear': ['Clear','Limpa'],
    'data_intro_video': ['Start by watching the video on this space. You can watch it in full frame, using the video controls.','Inicie assistindo ao vídeo da aula neste espaço. Você pode assistir em tela cheia, usando os controles do vídeo.'],
    'delete': ['Delete','Remove'],
    'do_a_tour': ['Do a tour','Faça um passeio'],
    'exercise': ['Challenge','Desafio'],
    'execute': ['Execute','Executa'],
    'expected_output': ['Expected Output','Saída Esperada'],
    'format': ['Format','Formata'],
    'help': ['Help','Ajuda'],
    'input': ['Input','Entrada'],
    'institute_of_computing': ['Institute of Computing','Instituto de Computação'],
    'lang': ['en','pt'],
    'my_course': ['My course','Meu curso'],
    'obi': ['Brazilian Olympiad in Informatics','Olimpíada Brasileira de Informática'],
    'output': ['Output','Saída'],
    'program': ['Editor','Editor'],
    'programming_the_future': ['Project Programming the Future','Projeto Programando o Futuro'],
    'rate_this_class': ['Rate this class','Avalie esta aula'],
    'rate_this_exercise': ['Rate this challenge','Avalie este desafio'],
    'report_a_problem': ['Report a problem','Relate um problema'],
    'retrieve': ['Retrieve','Recupera'],
    'revision_tab': ['Review','Revisão'],
    'save': ['Save','Salva'],
    'send': ['Send','Envia'],
    'solutions_tab': ['Solutions','Soluções'],
    'submit': ['Submit','Submete'],
    'video_tab': ['Video','Aula'],
    'work_area': ['Work Area','Área de Trabalho']
}

def encode(s):
    encodedBytes = base64.b64encode(s.encode("utf-8"))
    encodedStr = str(encodedBytes, "utf-8")
    return encodedStr
    
def build_page(course_name_full,course_name_short,class_index,user,base,minify,lang,prog_lang,blockly):
    u"Build page."
    curdir=os.getcwd()
    #d1,d2=target.split('_')
    dir=os.path.join(course_name_short,str(class_index))
    #print("building base {}, course_name_short {}, class_index {}, dir {}".format(base,course_name_short,class_index,dir),file=sys.stderr)
    if class_index != 'editor':
        class_index = int(class_index)
        prev,next=get_prev_next_classes(base,course_name_short,class_index,lang)
    else:
        prev,next='',''
    #print >> sys.stderr,prev,next
    exec(open(os.path.join(base, dir, 'info')).read(),globals())

    ########
    # video
    ########
    video_div,video_tab = "",""
    num_ratings = 0
    if video:
        num_ratings += 1
        video_tab += '<li style="margin-left: 10px;">%s</li>\n' % (translate["video_tab"][lang])
        video_div += '''
  <div id="VideoPanel"> <!-- video panel  start -->
    <div style="clear:both">{}</div>
    <div style="padding:5px;clear:both">&nbsp;</div>
    <div style="margin:auto;clear:both"><!--video-->
      <div style="margin:auto">
        <div id="player" style="margin:auto"></div>
      </div>
    </div><!-- end video-->
  </div> <!-- video panel end -->
'''.format(ratingTxt % (0,0,'Avalie esta aula'))

    ########
    # revision
    ########
    revision_div,revision_tab = "",""
    if os.path.exists(os.path.join(base, dir, 'revision.html')):
        revision_tab += '<li style="margin-left: 10px;">%s</li>\n' % (translate["revision_tab"][lang])
        revision_div += '<div style="padding:10px;position:relative"> <!-- revisao -->'
        revision_div += ratingTxt % (num_ratings,num_ratings,'Avalie esta revisão') # used to rate the class, exercise number is 0
        with open(os.path.join(base, dir, 'revision.html')) as tmp_file:
            revision_div += tmp_file.read()
        revision_div += "<p>&nbsp;</p>"
        revision_div +="</div> <!-- end revisao -->"
        num_ratings += 1

    ########
    # exercises
    ########
    if blockly:
        with open(os.path.join(base, dir, 'toolbox.xml')) as tmp_file:
            toolbox = tmp_file.read()
    else:
        toolbox = ''
    exercise_tabs,exercise_statement_divs='',''
    hints,samples,tests,results,solutions,solutions_src=[],[],[],[],[],[]
    exercise_titles = [];
    more_than_one = os.path.exists(os.path.join(base, dir,'exercises','%d' % 2))
    for ex in range(1,5):
        if not os.path.exists(os.path.join(base, dir,'exercises','%d' % ex)):
            break
        else:
            if more_than_one:
                exercise_tabs += '<li style="margin-left: 10px;">%s %d</li>\n' % (translate['exercise'][lang],ex)
            else:
                exercise_tabs += '<li style="margin-left: 10px;">%s</li>\n' % (translate['exercise'][lang])
            exercise_statement_divs += '<div style="padding:10px; position:relative"> <!-- exercise %d -->\n' % ex
            exercise_statement_divs += ratingTxt % (ex+num_ratings-1,ex+num_ratings-1,'%s' % (translate['rate_this_exercise'][lang]));

            with open(os.path.join(base, dir, 'exercises', '%d' % ex, 'statement.html')) as tmp_file:
                text = tmp_file.read()
                inipos = 4+text.find("<h2>")
                endpos = text.find("</h2>")
                ex_title = text[inipos:endpos]
                exercise_titles.append(ex_title)
                endpos += 5
                exercise_statement_divs += '\n<center>\n%s\n</center>' % (text[:endpos])
                exercise_statement_divs += text[endpos:];
            exercise_statement_divs += '<p>&nbsp;</p>'

            with open(os.path.join(base, dir, 'exercises', '%d' % ex, 'solution.html')) as tmp_file:
                solution_text = tmp_file.read()

            exercise_statement_divs += '<h3><span class="graycolor">Solução</span></h3><p class="graycolor">Aqui você encontra um exemplo de solução para o desafio. Mas antes de ver a solução tente resolvê-lo, criando a sua própria solução.</p>';
            sol_template='''<a href="#" id="solution-ex%d-show" class="showLink" onclick="_showHide('solution-ex%d');return false;">
<span class="graycolor">Solução do Desafio</span>
</a>
<div id="solution-ex%d" class="seeMore">
<a href="#" id="solution-ex%d-hide" class="hideLink" onclick="_showHide('solution-ex%d');return false;">
<font color="#888">Solução do Desafio</font>
</a>
<div class="seeMoreContent">
%s
</div>
</div>
<p>&nbsp;</p>
'''
            exercise_statement_divs +=sol_template % (ex+1,ex+1,ex+1,ex+1,ex+1,solution_text)
            exercise_statement_divs += '<p>&nbsp;</p></div> <!-- end exercise %d -->\n' % ex
            
            try:
                with open(os.path.join(base, dir, 'exercises', '%d' % ex, 'hints')) as tmp_file:
                    thehints=tmp_file.read()
            except:
                    thehints='\n\n'
            tmp=thehints.strip() #.encode('latin-1')
            tmp=tmp.replace('\n\n','<_newline_>')
            tmp=tmp.replace('\n',' ')
            tmp=tmp.replace('  ',' ')
            thehints=tmp.replace('<_newline_>','\n')
            #print >> sys.stderr, thehints
            #print >> sys.stderr, '--------'
            hints.append(thehints)
            with open(os.path.join(base, dir, 'exercises', '%d' % ex, 'sample')) as tmp_file:
                samples.append(tmp_file.read())
            with open(os.path.join(base, dir, 'exercises', '%d' % ex, 'solution')) as tmp_file:
                solutions_src.append(tmp_file.read())
            inp,sol=[],[]
            for test_num in range(1,51):
                if not os.path.exists(os.path.join(base, dir,'exercises','%d' % ex, 'tests', '%d.in' % test_num)):
                    break
                with open(os.path.join(base, dir, 'exercises', '%d' % ex, "tests","%d.in" % test_num)) as tmp_file:
                    inp.append(tmp_file.read())
                with open(os.path.join(base, dir, 'exercises', '%d' % ex, "tests","%d.sol" % test_num)) as tmp_file:
                    sol.append(tmp_file.read())
            tests.append(inp)
            results.append(sol)

    if blockly:
        _blockly = 'blockly_'
    else:
        _blockly = ''
    if minify:
        _minify = '_min'
    else:
        _minify = ''
    #print(os.path.join(base,'template_{}{}{}.html'.format(_blockly,prog_lang,_minify)),file=sys.stderr)
    with open(os.path.join(base,course_name_short,'template_{}{}{}.html'.format(_blockly,prog_lang,_minify))) as template_file:
            template = template_file.read()

    if user=='naoregistrado@saci' or user=='notregistered@saci':
        user = ''
        login = '<a href="/contas/login/?next=/saci/cursos">login</a>'
        register = '<a href="/saci/registrar">registrar</a>'
    else:
        user = 'Benvindo, ' + user
        login = '<a href="/contas/logout/">logout</a>'
        register = ''

    ######## REMOVE, for testing only #######
    #user='ranido@gmail.com'
    #course_base='cursos_r'

    titlehead = re.sub('<[^>]*>',"",title.strip())
    template = template.replace("#course_name#",course_name_full.strip())
    template = template.replace("#course_ref#",course_name_short.strip().lower())
    template = template.replace("#prevclass#",prev)
    template = template.replace("#nextclass#",next)
    template = template.replace("#titlehead#",titlehead)
    template = template.replace("#title#",title.strip())
    template = template.replace("#video#",video)
    template = template.replace("#video_div#",video_div)
    template = template.replace('#video_tab#',video_tab)
    template = template.replace("#revision_div#",revision_div)
    template = template.replace('#revision_tab#',revision_tab)
    template = template.replace("#exercise_tabs#",exercise_tabs)
    template = template.replace("#exercise_statement_divs#",exercise_statement_divs)
    template = template.replace("#hiddensamples#",encode("^".join(samples)))
    template = template.replace("#hiddenhints#",encode("^".join(hints)))
    template = template.replace("#hiddentests#",pack_test(tests))
    template = template.replace("#hiddenresults#",pack_test(results))
    #template = template.replace("#solutions#",build_solutions(solutions,lang))
    template = template.replace("#user#",user)
    template = template.replace("#login#",login)
    template = template.replace("#register#",register)
    template = template.replace("#hiddencourse#",course_name_short.strip())
    template = template.replace("#hiddenclassindex#",str(class_index))
    template = template.replace("#hiddensolutions#",encode("^".join(solutions_src)))
    if revision_tab:
        template = template.replace("#revision_is_present#","1")
    else:
        template = template.replace("#revision_is_present#","0")
    if video_tab:
        template = template.replace("#video_is_present#","1")
    else:
        template = template.replace("#video_is_present#","0")
        
    template = template.replace("#blockly_toolbox#",toolbox)

    # language dependent strings
    template = template.replace('#clear#',translate['clear'][lang])
    template = template.replace('#cancel#',translate['cancel'][lang])
    template = template.replace('#data_intro_video#',translate['data_intro_video'][lang])
    template = template.replace('#delete#',translate['delete'][lang])
    template = template.replace('#do_a_tour#',translate['do_a_tour'][lang])
    template = template.replace('#execute#',translate['execute'][lang])
    template = template.replace('#expected_output#',translate['expected_output'][lang])
    template = template.replace('#format#',translate['format'][lang])
    template = template.replace('#help#',translate['help'][lang])
    template = template.replace('#input#',translate['input'][lang])
    template = template.replace('#institute_of_computing#',translate['institute_of_computing'][lang])
    template = template.replace('#lang#',translate['lang'][lang])
    template = template.replace('#my_course#',translate['my_course'][lang])
    template = template.replace('#obi#',translate['obi'][lang])
    template = template.replace('#output#',translate['output'][lang])
    template = template.replace('#program#',translate['program'][lang])
    template = template.replace('#program_tab#',translate['program'][lang])
    template = template.replace('#programming_the_future#',translate['programming_the_future'][lang])
    template = template.replace('#report_a_problem#',translate['report_a_problem'][lang])
    template = template.replace('#retrieve#',translate['retrieve'][lang])
    template = template.replace('#save#',translate['save'][lang])
    template = template.replace('#send#',translate['send'][lang])
    #template = template.replace('#solutions_tab#',translate['solutions_tab'][lang])
    template = template.replace('#submit#',translate['submit'][lang])
    template = template.replace('#work_area#',translate['work_area'][lang])

    unusedbuttons=''
    for u in range(len(exercise_titles)+1,11):
        unusedbuttons += '<button id="solveitBTN%d">Resolve</button>\n' % u
    template = template.replace("#unusedbuttons#",unusedbuttons)

    return template

def pack_test(t):
    if len(t) == 0:
        return encode("")
    pack=[]
    for i in range(len(t)):
        s = ";".join(t[i])
        pack.append(s)
    return encode("^".join(pack)).replace('\n','')

def build_solutions(s,lang):
    html = ratingTxt % (1+len(s),1+len(s),translate['rate_this_class'][lang])
    html += '<h2>Soluções para os exercícios</h2><p>Nesta seção você encontra exemplos de soluções para os exercícios. Mas antes de ver a solução para um exercício tente resolvê-lo, criando a sua própria solução.</p>';
    sol_template='''<a href="#" id="solution-ex%d-show" class="showLink" onclick="_showHide('solution-ex%d');return false;">
Solução do Exercício %d
</a>
<div id="solution-ex%d" class="seeMore">
<a href="#" id="solution-ex%d-hide" class="hideLink" onclick="_showHide('solution-ex%d');return false;">
Solução do Exercício %d
</a>
<div class="seeMoreContent">
%s
</div>
</div>
<p>&nbsp;</p>
'''
    for i in range(len(s)):
        html+=sol_template % (i+1,i+1,i+1,i+1,i+1,i+1,i+1,s[i])
    html+='<p>&nbsp;</p>'
    return html

def get_prev_next_classes(base,course_name_short,current_class,lang):
    classes=[]
    for dir in os.listdir(os.path.join(base,course_name_short)):
        try:
            exec(open(os.path.join(base, course_name_short, dir, 'info')).read(),globals())
            #title1,title2=title.split('-')
            #title_num=int(title1[4:])
            if public=="yes" and index != 0:
                classes.append([index,title,course_name_short,int(dir)])
        except:
            pass

    classes.sort()
    # in file info, index must be zero to remove previous/next links
    if index != 0:
        if lang==EN:
            str_prev,str_next='previous class','next class'
        else:
            str_prev,str_next='aula anterior','próxima aula'
    else:
        str_prev,str_next='',''
    prev,next=str_prev,str_next
    for i in range(len(classes)):
        if classes[i][3]==current_class:
            if i>0:
                prev='<a href="/saci/cursos/{}/{}" class="prevClass">{}</a> &nbsp; &bull; &nbsp; '.format(classes[i-1][2],classes[i-1][3],str_prev)
            if i<len(classes)-1:
                next='<a href="/saci/cursos/{}/{}" class="nextClass">{}</a>'.format(classes[i+1][2],classes[i+1][3],str_next)
            break;
    return prev,next;
        

def parse_arguments():
    optlist, args = getopt.gnu_getopt(sys.argv[1:], 'bemvu:c:p')
    minify,lang,prog_lang,blockly=False,PT,'js',False
    for flag, arg in optlist:
        if flag == '-v':
            print("build version %s" % VERSION, file=sys.stderr)
            sys.exit(0)
        if flag == '-b':
            blockly=True;
        if flag == '-m':
            minify=True;
        if flag == '-u':
            user=arg
        if flag == '-c':
            course=arg
        if flag == '-e':
            lang=EN
        if flag == '-p':
            prog_lang='py'
    if lang==EN:
        user,course_name_full,course_name_short='notregistered@saci','Introduction do computer programming','intro_js'
    else:
        user,course_name_full,course_name_short='naoregistrado@saci','Introdução à programação de computadores','intro_js'

    if len(args) != 2:
        usage()
    course_name_short = args[0]
    class_index = args[1]
    course_name_full = 'Nome do curso'
    return course_name_full,course_name_short,class_index,user,minify,lang,prog_lang,blockly

def usage():
    print("usage: {} course class".format(sys.argv[0]),file=sys.stderr)
    sys.exit(-1)
    
def _main():
    course_name_full,course_name_short,class_index,user,minify,lang,prog_lang,blockly = parse_arguments()
    base=os.path.dirname('.');
    print('building', course_name_short, class_index, file=sys.stderr)
    txt=build_page(course_name_full,course_name_short,class_index,user,base,minify,lang,prog_lang,blockly)
    if txt: print(txt)

if __name__ == '__main__':
    _main()

