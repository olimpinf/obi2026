#!/usr/bin/env python3

import os
import re
import sys


def check_answers_file(f):
    with open(f,"r") as fin:
        data = fin.readlines()
    pattern_comment = re.compile('\s*#.*')
    pattern_alternative = re.compile('\s*(?P<num>[0-9]+)\.\s*(?P<alt>.*)')
    i = 0
    msg = ''
    errors = []
    answers = {}
    line_num = 0
    for line in data:
        line = line.strip()
        line_num += 1
        if line == '': continue
        if re.match(pattern_comment,line): continue
        m = re.match(pattern_alternative,line)
        if not m: 
           errors.append(Error(line_num,'Erro de formatação',line))
        num = int(m.group('num'))
        if num != i+1:
           errors.append(Error(line_num,'Número fora de sequência',line))
        alternative = m.group('alt').strip()
        if alternative not in ['A','B','C','C','D','E']:
                errors.append(Error(line_num,'Caractere de alternativa fora do esperado (A,B,C,D,E)',line))
        answers[i] = alternative
        i += 1
    #if num_answers != len(answers):
    #    msg = "O número de questões informado é diferente do número de respostas no arquivo de gabarito."
    if errors:
        msg = "Foram detectados erros no arquivo de gabarito. Por favor corrija e submeta novamente."
    return msg,errors,answers

class Error():
    def __init__(self, linenum, msg, line):
        self.linenum = linenum
        self.msg = msg
        self.line = line

def format_line(l, delimiter):
    return '{}'.format(delimiter).join(l)


if __name__=="__main__":

    # for check_answers_file
    try:
        fname=sys.argv[1]
    except:
        print("usage: {} gabarito.txt".format(sys.argv[0]))
        sys.exit(0)
    msg,errors,answers = check_answers_file(fname)
    for e in errors:
        print('errors:')
        print('msg',msg)
        print(e.linenum, e.msg, e.line)
        exit(1)
    ans = []
    for i in answers.keys():
        ans.append(answers[i])
    tmp = str(ans)
    tmp = tmp.replace("'",'"')
    print("'{}'".format(tmp))
    
