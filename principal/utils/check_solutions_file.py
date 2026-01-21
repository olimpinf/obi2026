import os
import os.path
import re
import shutil
import subprocess
import sys
import tempfile

from principal.models import LEVEL, LEVEL_NAME, Compet, School
from principal.utils.utils import format_compet_id
from fase1.models import SubFase1

LANG_SUFIXES = {"cc":2, "cpp":2, "c++":2, "c":1, "pas":3, "p":3, "py2":4, "java":5, "js":6, "py3":7}
PROBLEM_NAMES = {
    5: {"provaf1pj_camisetas":"Camisetas da Olimpíada", "provaf1pj_tesouro":"Divisão do Tesouro", "provaf1pj_relogio":"Relógio de Atleta"},
    3: {"piloto":"Piloto Automático", "fissura":"Fissura Perigosa", "pandemia":"Pandemia"},
    4: {"acelerador":"Acelerador de Partículas","fissura":"Fissura Perigosa", "pandemia":"Pandemia", "promocao":"Promoção de Primeira"},
    6: {"acelerador":"Acelerador de Partículas","fissura":"Fissura Perigosa", "bingo":"Bingo!", "paciente":"Paciente Zero"},
}

class Error():
    def __init__(self, compet, program, comment):
        self.compet = compet
        self.program = program
        self.comment = comment

    def __eq__(self, other):
        return self.compet == other.compet and self.program == other.program

    def __lt__(self, other):
        if self.compet == other.compet:
            return self.program < other.program
        return self.compet < other.compet


def is_binary(data):
    if '\0' in data: # found null byte
        return True
    return False
    
def run(cmd, timeout):
    print('run',cmd)
    try:
        result=subprocess.run(cmd, shell=True, timeout=timeout)
    except:
        return 'Erro no processamento (timeout)'
    if result.returncode!=0:
        return 'Erro no processamento'
    return ''

def check_solutions_file(archive, level, phase, school_id):

    def log_result(archive,msg,result):
        with open(archive+"_log","w") as fin:
            fin.write("msg: {}\n".format(msg))
            for r in result:
                fin.write("{}: {} -- {}\n".format(r.compet,r.program,r.comment))

    cur_dir = os.getcwd()
    tmp_dir = tempfile.mkdtemp()
    os.chdir(tmp_dir)
    msg = ''
    result = []
    seen = {}
    pattern_num_inscr = re.compile("(?P<num>[0-9]+)-(?P<letter>[A-J])",re.IGNORECASE)
    problem_names = PROBLEM_NAMES[level]
    res = run('unzip -q %s' % archive, timeout=60)
    print('returning from run zip',res)
    if res != '':
        res = run('tar xzf %s' % archive, timeout=60)
        print('returning from run tar',res)
    
    if res != '':
        msg = "Erro ao descompactar arquivo. Certifique-se de que o arquivo é do tipo .ZIP ou .TGZ."
        log_result(archive,msg,result)
        return msg, result
    sch = School.objects.get(pk=school_id)
    school_compets = Compet.objects.filter(compet_school_id=school_id, compet_type=level)
    for root, dirs, files in os.walk(tmp_dir, topdown=False):
        base = os.path.basename(root)
        m = pattern_num_inscr.match(base)
        if not m:
            # discard this folder
            continue
        compet_id = int(m.group('num'))
        compet_id_full = base
        if compet_id_full != format_compet_id(compet_id):
            result.append(Error(compet_id_full,'','Número de inscrição incorreto'))
            continue
        try:
            compet_ok = school_compets.filter(pk=compet_id)
        except:
            compet_ok = ''
        if not compet_ok:
            result.append(Error(compet_id_full,'','Número de inscrição não corresponde a competidor da escola nesse nível'))
            continue
        for fname in files:
            fname_orig = fname
            fname = fname.lower()
            problem_name,ext = os.path.splitext(fname)
            if problem_name not in problem_names.keys():
                if ext == ".py":
                    tmpp,tmpe = os.path.splitext(problem_name)
                    if tmpe == "py2" or tmpe == ".py3":
                        problem_name = tmpp
                        ext == tmpe
                    if problem_name not in problem_names.keys():
                        result.append(Error(compet_id_full,fname_orig,'Nome de problema incorreto'))
                        continue
                else:
                    result.append(Error(compet_id_full,fname_orig,'Nome de problema incorreto'))
                    continue
            problem_name_full = problem_names[problem_name]
            if ext[1:] not in LANG_SUFIXES:
                result.append(Error(compet_id_full,fname_orig,'Extensão do nome de  problema incorreta'))
                continue
            sub_lang = LANG_SUFIXES[ext[1:]]
            if compet_id in seen.keys():
                if problem_name in seen[compet_id]:
                    result.append(Error(compet_id_full,fname_orig,'Problema repetido para este competidor'))
                    continue
                else:
                    seen[compet_id].append(problem_name)
            else:
                seen[compet_id] = [problem_name]
            try:
                with open(os.path.join(root,fname_orig),"rU") as fin:
                    sub_source = fin.read() 
            except:
                try:
                    with open(os.path.join(root,fname_orig),"rU",encoding='iso-8859-1') as fin:
                        sub_source = fin.read() 
                except:
                    result.append(Error(compet_id_full,fname_orig,'Erro ao ler o arquivo.'))
                    continue
                    
            if len(sub_source) == 0:
                result.append(Error(compet_id_full,fname_orig,'Arquivo vazio'))
                continue
            if is_binary(sub_source):
                result.append(Error(compet_id_full,fname_orig,'Arquivo deve ser do tipo texto'))
                continue
            try:
                submission = SubFase1.objects.get(compet = Compet(pk=compet_id),problem_name = problem_name)
                submission.sub_source = sub_source
                submission.sub_lang = sub_lang
                action = 'Atualizado'
            except:
                submission = SubFase1(sub_source = sub_source,
                                  sub_lang = sub_lang,
                                  compet = Compet(pk=compet_id),
                                  problem_name = problem_name,
                                  problem_name_full = problem_name_full)
                action = 'Inserido'
            submission.save()
            result.append(Error(compet_id_full,fname,'OK - {} no sistema'.format(action)))
    if not result:
        msg = 'Não foram encontradas pastas com nomes corretos (número de inscrição do competidor).'
    
    result = sorted(result)
    log_result(archive,msg,result)
    return msg, result

def usage():
    print("%s: inputarchive level phase school" % (sys.argv[0]))
    os._exit(1)


if __name__ == "__main__":
    try:
        archive = sys.argv[1]
        level =  int(sys.argv[2])
        phase =  int(sys.argv[3])
        school_id =  int(sys.argv[4])
    except:
        usage()
        os.exit(1)
            
    result = check_solutions_file(archive, level, phase, school_id)
    for r in result:
        print(r.compet, r.program, r.comment)
