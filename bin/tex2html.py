#!/usr/bin/env python3

import sys,re,os,getopt,shutil

IMAGES_DIR = "/static/img/task_images"

template_sample='''<table width="100%s" cellspace="2" border="1">
  <tr>
    <td valign="top" width="50%s">
      <b>Entrada</b>
      <pre>
%s
</pre>
      </td>
    <td valign="top" width="50%s">
      <b>Saída</b>
      <pre>
%s
	</pre>
      </td>
    </tr>
</table>

<p>&nbsp;</p>
'''

def process_ini(data,problem_code):
    pat_task_title=re.compile(r"\\task{([^}]*)}")
    #pat_task=re.compile(r"\\task{([^}]*)}")
    #pat_task=re.compile(r"\\task {(.*)}")
    match = re.search(pat_task_title,data)
    if match:
        task_title = match.groups()[0]
    else:
        task_title = 'NONE' 
    statement=re.sub(r"(\\task{[^}]*})", '', data) # remove
    statement=re.sub(r'\\question\{((?:.|\n)*?)\}','\\\question\\n\\1\n', statement)#, flags=re.DOTALL)
    first = statement.find('question\n')
    #print('first=',first)
    new = statement[:first]
    new += re.sub(r'\\item',r'\alternative', statement[first:])
    m = re.search(r'(%\s*corre.+)', statement)
    if m:
        new=re.sub(r'(%\s*corre.+)','\\\correct', new)
    else:
        print('task',problem_code,'does not have correct alternative',file=sys.stderr)
    new = re.sub("%.*$",'\n',new) # comment
    return new, task_title

def generate(ifilename,outputfile,title,modality,problem_name="",template_type="task",order="",header=""):
    with open(ifilename) as f:
        data=f.read()
    if modality == 'i':
        data, title = process_ini(data,problem_name)
        header = 'title:{}\ntemplate:{}/tarefa_iniciacao.html'.format(title,template_type)
    else:
        header = 'title:{}\ntemplate:{}/tarefa_programacao.html'.format(title,template_type)
    if order:
        header += '\norder:{}'.format(order)

    pat_comment=re.compile("\%.*")
    pat_money=re.compile(r"(R\\\$)")
    pat_not_money=re.compile(r"\$([^$]*)\$")
    pat_tt=re.compile("{\\\\tt ([^}]*)}")
    pat_texttt=re.compile("\\\\texttt{([^}]*)}")
    pat_emph=re.compile("\\\\emph{([^}]*)}")
    pat_vspace=re.compile("\\\\vspace{([^}]*)}")
    pat_hspace=re.compile("\\\\hspace{([^}]*)}")
    pat_subsection=re.compile("\\\\subsection\**\\s?{([^}]*)}")
    pat_section=re.compile("\\\\section\**\\s?{([^}]*)}")
    pat_hex=re.compile("\\\\hex{([^}]*)}")
    pat_paragraph=re.compile("\\n\\n")
    pat_begin_itemize=re.compile("\\\\begin{itemize}")
    pat_end_itemize=re.compile("\\\\end{itemize}")
    pat_begin_minipage=re.compile("\\\\begin{minipage}.*")
    pat_end_minipage=re.compile("\\\\end{minipage}")
    pat_begin_figure=re.compile("(\\\\begin{figure}.*)")
    pat_include_graphics_name=re.compile(r"([^%].*(?:CWD|PASTA)/imagen?s/(?P<name>.*)\.pdf)")
    #pat_include_graphics=re.compile(r"(.*(?:CWD|PASTA)/imagen?s/{}\.pdf)")
    pat_item=re.compile("\\\\item")
    pat_superscript=re.compile("(\\w)\\^(\\w)")
    pat_subscript=re.compile("(?:\<img src=\")(\\w)\\_(\\w)")
    pat_verbatim=re.compile(r"\\begin{verbatim}((?:.|\n)*?)\\end{verbatim}")
    pat_inputdescline=re.compile(r"\\inputdescline{((?:.|\n)*?)}")
    pat_inputdesc=re.compile(r"\\inputdesc{((?:.|\n)*?)}")
    pat_outputdesc=re.compile(r"\\outputdesc{((?:.|\n)*?)}")
    pat_outputdescline=re.compile(r"\\outputdescline{((?:.|\n)*?)}{((?:.|\n)*?)}")
    pat_it=re.compile(r"{\\it((?:.|\n)*?)}")
    pat_begin_tabular=re.compile(r"\\begin{tabular}.*")

    data=re.sub(pat_comment,"",data)
    # must process image before substitutions
    matched = re.search(pat_include_graphics_name,data)
    idx = 0
    for matched in re.finditer(pat_include_graphics_name,data):
        idx += 1
        print(ifilename, 'has figure',matched.group('name')+'.pdf',file=sys.stderr)
        # uses 'images' or 'images'? try both
        ifigpath = os.path.join(os.path.dirname(ifilename),'images',matched.group('name')+'.pdf')
        if not os.path.exists(ifigpath):
            ifigpath = os.path.join(os.path.dirname(ifilename),'imagens',matched.group('name')+'.pdf')
        ofigdir = os.path.dirname(outputfile.name)
        if not os.path.isdir(os.path.join(ofigdir,'img')):
            os.mkdir(os.path.join(ofigdir,'img'))
        ofigdir = os.path.join(ofigdir,'img')
        #if not os.path.isdir(os.path.join(ofigdir,'img',problem_name)):
        #    os.mkdir(os.path.join(ofigdir,'img',problem_name))
        fig_name = matched.group('name')
        if idx == 1:
            ofigfilename = problem_name
        else:
            ofigfilename = problem_name+'_'+str(idx)
        ofigpath = os.path.join(ofigdir,ofigfilename)
        try:
            shutil.copy(ifigpath,ofigpath+'.pdf')
            os.system('convert -density 150 {} {}'.format(ofigpath+'.pdf', ofigpath+'.png'))
            os.system('rm {}'.format(ofigpath+'.pdf'))
        except:
            print('cannot find figure', ifigpath,file=sys.stderr)

        pat = re.compile(r"(.*(?:CWD|PASTA)/imagen?s/{}\.pdf)".format(matched.group('name')))
        data=re.sub(pat,'<div class="center"><img src="{}.png" width="350px" /></div>'.format(os.path.join(IMAGES_DIR,ofigfilename)),data)

    data=re.sub(pat_it,'<i>\\1</i>',data)
    data=re.sub(pat_inputdesc,'\n<h3>Entrada</h3>\n\\1',data)
    data=re.sub(pat_inputdescline,'\n<h3>Entrada</h3>\nA entrada consiste de uma única linha que contém \\1',data)
    data=re.sub(pat_outputdesc,'\n<h3>Saída</h3>\n\\1',data)
    data=re.sub(pat_outputdescline,'\n<h3>Saída</h3>\nSeu programa deve produzir uma única linha, contendo \\1, \\2',data)
    data=re.sub(pat_section,'<h2>\\1</h2>',data)
    data=re.sub(pat_subsection,'<h3>\\1</h3>',data)
    data=re.sub(pat_hex,'<span class="tt">0x\\1</span>',data)
    data=re.sub(pat_emph,'<i>\\1</i>',data)
    data=re.sub(pat_tt,'<span class="ttt">\\1</span>',data)
    data=re.sub(pat_texttt,'<span class="ttt">\\1</span>',data)
    data=re.sub(pat_vspace,'',data)
    data=re.sub(pat_hspace,'',data)
    data=re.sub(pat_verbatim,'\n<pre>\\1</pre>\n',data)
    data=re.sub(pat_begin_itemize,'<ul>',data)
    data=re.sub(pat_end_itemize,'</ul>',data)
    data=re.sub(pat_item,'<li>',data)
    data=re.sub(pat_begin_minipage,'',data)
    data=re.sub(pat_end_minipage,'',data)
    data=re.sub(pat_begin_figure,'',data)
    data=re.sub(pat_superscript,'\\1<sup>\\2</sup>',data)
    data=re.sub(pat_subscript,'\\1<sub>\\2</sub>',data)
    data=re.sub(pat_begin_tabular,"",data)
    data=re.sub(pat_not_money,'\\1',data)
    data=re.sub(pat_money,"R$ ",data)
    #print(data)


    data=data.strip()
    data=data.replace('``','&quot;')
    data=data.replace("\'\'",'&quot;')
    data=data.replace('\\begin{multicols}{2}','');
    data=data.replace('\\end{multicols}','');
    data=data.replace('\\center','');
    data=data.replace('\\columnbreak','');
    data=data.replace('\\noindent','  ');
    data=data.replace("\\end{enumerate}",'</ol>')
    data=data.replace("\\end{figure}",'')
    data=data.replace("\\end{tabular}",'')
    data=data.replace("\exemplo",'')
    data=data.replace("\sampleio",'\n<h3>Exemplos</h3>\n')
    data=data.replace('\\rightarrow',' &rarr; ');
    data=data.replace('\\bigskip','');
    data=data.replace('\\medskip','');
    data=data.replace('\\smallskip','');
    data=data.replace('\\leq',' &leq; ');
    data=data.replace('\\le',' &leq; ');
    data=data.replace('\\geq',' &geq; ');
    data=data.replace('\\ge',' &geq; ');
    data=data.replace('\\neq',' &neq; ');
    data=data.replace('\\ne',' &neq; ');
    #data=data.replace('\\\\',' <br> ');
    data=data.replace('\\\\','');
    data=data.replace('\\noindent','  ');
    data=data.replace('\\_','_');
    data=data.replace('R\\$','R$');
    data=data.replace('\\textasciitilde','~');
    data=data.replace('\\vfill','');
    data=data.replace(r"\begin{center}",'<div class="center">')
    data=data.replace(r"\end{center}",'</div>')
    ## carefull:
    #data=data.replace('{','');
    #data=data.replace('}','');
    #data=re.sub(pat_paragraph,'\n\n<p>',data)

    if header:
        print(header, file=outputfile)
    else:
        print('<h2>{}</h2>'.format(title), file=outputfile)
    print('<p>', file=outputfile)
    print(data.strip(), file=outputfile)

    if modality=='p':
        base=os.path.dirname(ifilename)
        for i in range(1,10):
            if os.path.exists(os.path.join(base,"sample-%d.in" % i)):
                with open(os.path.join(base,"sample-%d.in" % i)) as f:
                    input=f.read()
                with open(os.path.join(base,"sample-%d.sol" % i)) as f:
                    output=f.read()
                print(template_sample % ("%","%",input.strip(),"%",output.strip()), file=outputfile)
            else:
                break

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:t:", ["help", "ofilename=", "problem", "title="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    title = 'Title'
    problem = '9999f1i1_test'
    ofilename = None
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-o", "--ofilename"):
            ofilename = a
        elif o in ("-p", "--problem"):
            problem = a
        elif o in ("-t", "--title"):
            title = a
        else:
            assert False, "unhandled option"

    if ofilename:
        try:
            ofile = open(ofilename,"w")
        except:
            assert False, "cannot open file {} for writing".format(ofilename)
    else:
        ofile = sys.stdout
    if len(args) == 0:
        usage()
    elif len(args) == 1:
        generate(args[0],ofile,title=title,problem_name=problem)
    else:
        usage

if __name__ == "__main__":
    main()
