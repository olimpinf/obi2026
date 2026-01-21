#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time, sys, os, traceback, tempfile, getpass, signal, \
       fcntl, getopt, base64, string, subprocess, \
       shlex, re
import psycopg2, psycopg2.extras
import resource, shlex
import signal
from io import  StringIO

UsageMessage = \
    """
    obi.py [-h] [-f config-file ] [-c] [-d] [-r] [-i] 
      -c:   compile only, do not execute
      -d:   debugging mode
      -f:   reads an alternative configuration file (default: 'obi_config')
      -h:   prints this help message
      -i:   interactive mode - asks for submission id
                   (default: processes all submissions)
      -r:   resets all submissions to unprocessed
    """

lang_ext={1:'c',2:'c',3:'pas',4:'py',5:'java',6:'js',7:'py'}


#------------------------------------------------------------------------#
#  Defaults for the configuration                                        #
#------------------------------------------------------------------------#

CONFIG_FILE_NAME = 'obi_config'

DEBUG = False

HOST = ""         # must be defined in the config file
DB_NAME = ""      # must be defined in the config file
USER_NAME = ""    # must be defined in the config file
PROBLEMS_DIR = "" # must be defined in the config file relative to scripts directory

PASSWORD = ""     # will be requested if not defined in the config file

# Optional definitions

PROC_ID = "Checker"+str(os.getppid())      # default process id
LOG_FILE = ""              # no logging if ""; relative to scripts directory
TEMP_DIR = "/tmp"
TIME_FILE = "time"
STATUS_FILE = "status"
TEMP_FILE_SUFFIX = ".obi"
COMPILE_LOG_FILE = "COMPILE_LOG"
TEST_LOG_FILE = "testLog"
TEST_PREFIX = "test"
TEST_SUFFIX_MAX = 20
INPUT_FILE = "input"
OUTPUT_FILE = "output"
RESULT_FILE = "result"
LIMITS_FILE = "limits"
POINTS_FILE = "points"
CHECKING_PROGRAM = "corrector"
EXEC_UID = 99
EXEC_GID = 99
SANDBOX_PROGRAM = ""
FILTER_PROGRAM = ""
DIFF="/usr/bin/diff -q "
SLEEP_TIME = 10
MAX_TRIALS = 6
LOCK_SLEEP_TIME = 1
MAX_LOCK_TRIALS = 5
ABORT_FIRST_ERROR = False

# Execution error codes
RUN_TIME_ERROR = "E"
EMPTY_OUTPUT_ERROR = "S"
SIGKILL_ERROR = "V"
TIME_LIMIT_EXCEEDED = "T"
INVALID_REF_ERROR = "M"
CORRECT_RESULT = "."
INCORRECT_RESULT = "X"
CORRECT_EXECUTION = "."


# Language dependant messages (default: English)

REPORT_HEADER = "TEST REPORT FOR THE TEAM  %d (sub_id %d)\n\n"
                               #  %d %d will be replaced  by the team_id and sub_id

HEADER_SEPARATOR = "\n===================================================================\n"

PROBLEM_NAME = "PROBLEM %s\n"                  # %s will be replaced by the problem full name
LANGUAGE_NAME = "LINGUAGEM %s\n\n"            # %s will be replaced by the language name

COMPILATION_SUCCESSFUL = "Successful compilation\n"
COMPILATION_WARNINGS = "Compilation with warnings:\n\n"
COMPILATION_UNSUCCESSFUL = "Unsuccessful compilation:\n"

TESTING_PHASE = "\nTesting phase\n"
TEST_HEADER = "Test %d:\n"                   # %s will be replaced by the test id character
EXECUTION_TIME = "    Execution time (CPU): %s seconds\n"
                                               # %s will be replaced by the value
EXECUTION_MESSAGE = "    Execution message:\n"
POINTS_RECEIVED = "\n%d out of %d point\n"

TEST_SEPARATOR = "\n===================================================================\n"

#------------------------------------------------------------------------#

obiGlobals = globals()
scriptDir = os.getcwd()

gnuTime = "/usr/bin/time -f %s -o %s "   # 1: %U (can't put it here!
                                         # 2: time-file


#------------------------------------------------------------------------#
#  Functions                                                             #
#------------------------------------------------------------------------#

class Result (object):
    def __init__(self, running_time = None):
        if running_time is not None:
            self.running_time = running_time

def handler_timeout(signum, frame):
    print("Timeout!")
    WriteLog("Timeou exception\n")
    raise ObiException("Timeout")

def parse_limit(l):
    if type(l)==int:
        return 1024*int(l)
    tmp=re.match("(\d+)GB",l,re.IGNORECASE)
    if tmp:
        return 1024*1024*1024*int(tmp.group(1))
    tmp=re.match("(\d+)MB",l,re.IGNORECASE)
    if tmp:
        return 1024*1024*int(tmp.group(1))
    tmp=re.match("(\d+)KB",l,re.IGNORECASE)
    if tmp:
        return 1024*int(tmp.group(1))
    print("*** could not parse limit ", l)
    sys.exit(-1)

def run_solution(sub_lang,
                 sol_fn,
                 input_fn,
                 output_fn,
                 error_fn,
                 status_fn,
                 cpu_limit = 1000,
                 mem_limit = 1024,
                 file_limit = 1024,
                 language = 1):

    def parse_status(f):
        status = {}
        if not os.path.exists(status_fn):
            return status
        with open(status_fn) as fs:
            status_lines = fs.readlines()
        for l in status_lines:
            key,value = l.split(":")
            status[key.strip()] = value.strip()
        return status

    Debug("run_solution %s %s" % (sol_fn,input_fn))
    Debug("cpu_limit: {}".format(cpu_limit))
    time_limit=1.0*cpu_limit/1000
    mem_limit=parse_limit(mem_limit)
    mem_limit=int(mem_limit/1000)
    stack_limit=mem_limit
    file_limit=parse_limit(file_limit)
    file_limit = int(file_limit/1000)
    # Set the signal handler and a 5*RLIMIT_CPU-second alarm

    # for python: --dir /etc
    # for java --dir /usr/lib/jvm -p
    if sub_lang == 5: # java
        run_command = "/usr/local/bin/isolate --dir /usr/lib/jvm --processes --wall-time={} --time={} --fsize={} --mem={} --stdout={} --stderr={} --meta={} --run {} < {}".format(5*time_limit, time_limit, file_limit, mem_limit, output_fn, error_fn, status_fn, sol_fn, input_fn)
    elif sub_lang == 4 or sub_lang == 7: # python
        run_command = "/usr/local/bin/isolate --dir /etc --processes --wall-time={} --time={} --fsize={} --mem={} --stdout={} --stderr={} --meta={} --run {} < {}".format(5*time_limit, time_limit, file_limit, mem_limit, output_fn, error_fn, status_fn, sol_fn, input_fn)
    elif sub_lang == 6: # js
        run_command = "/usr/local/bin/isolate --dir /etc/alternatives --processes --wall-time={} --time={} --fsize={} --mem={} --stdout={} --stderr={} --meta={} --run {} < {}".format(5*time_limit, time_limit, file_limit, mem_limit, output_fn, error_fn, status_fn, sol_fn, input_fn)
    else: # C, C++
        run_command = "/usr/local/bin/isolate --wall-time={} --time={} --fsize={} --mem={} --stdout={} --stderr={} --meta={} --run {} < {}".format(5*time_limit, time_limit, file_limit, mem_limit, output_fn, error_fn, status_fn, sol_fn, input_fn)
    # with os.system the signals are not handled correctly
    #os.system("/usr/local/bin/isolate --wall-time={} --time={} --fsize={} --mem={} --stdout={} --stderr={} --meta={} --run {} < {}".format(5*time_limit, time_limit, file_limit, mem_limit, output_fn, error_fn, status_fn, sol_fn, input_fn))
    with open("/dev/null", "w") as devnull:
        p = subprocess.Popen(run_command, stderr=devnull, shell=True)
    os.waitpid(p.pid, 0)
    result = Result()
    status = parse_status(status_fn)
    if 'status' in status.keys():
        if status['status'] == 'TO':
            result.status = TIME_LIMIT_EXCEEDED
        elif status['status'] == 'SG':
            if status['exitsig'] == '11':
                result.status = INVALID_REF_ERROR
            else:
                result.status = SIGKILL_ERROR
        elif status['status'] == 'RE':
            result.status = RUN_TIME_ERROR
        else:
            result.status = 'SANDBOX_ERROR'
    else:
        if (not os.path.exists(output_fn) or (os.path.getsize(output_fn)==0)):
            result.status = EMPTY_OUTPUT_ERROR
        else:
            # do not check return(0) or exit(0)
            result.status = CORRECT_EXECUTION
    return result

def is_binary(filename):
    """Return true if the given filename is binary.
    @raise EnvironmentError: if the file does not exist or cannot be accessed.
    @attention: found @ http://bytes.com/topic/python/answers/21222-determine-file-type-binary-text on 6/08/2010
    @author: Trent Mick <TrentM@ActiveState.com>
    @author: Jorge Orpinel <jorge@orpinel.com>"""
    fin = open(filename, 'rb')
    try:
        CHUNKSIZE = 1024
        while 1:
            chunk = fin.read(CHUNKSIZE)
            if b'\0' in chunk: # found null byte
                return True
            if len(chunk) < CHUNKSIZE:
                break # done
    finally:
        fin.close()

    return False

class ObiException(Exception):
    def __init__(self, value):
        self.value = value

#---------------------------------------------------------------------------

def Debug(s):
    if DEBUG:
        sys.stderr.write(s+"\n")


#---------------------------------------------------------------------------

def CurrentTime():
  return time.strftime('%Hh%Mm%Ss',time.localtime(time.time()))

#---------------------------------------------------------------------------

def CurrentDate():
  return time.strftime('%Y-%m-%d',time.localtime(time.time()))

#---------------------------------------------------------------------------

def WriteLogSafe(m):
    """
    Writes into the log file the string 'm' followed by a new line;
    safe under multiple processes.
    """
    global logging
    if logging:
        locked = False
        for k in range(MAX_LOCK_TRIALS):
          try:
           logFile = file(LOG_FILE,'a')
           fcntl.flock(logFile.fileno(),fcntl.LOCK_EX | fcntl.LOCK_NB)
           locked = True
           break
          except IOError:
           time.sleep(LOCK_SLEEP_TIME)
        if locked:
          logFile.seek(0,2)
          logFile.write(CurrentDate()+" "+CurrentTime()+": "+m+"\n")
          fcntl.flock(logFile.fileno(),fcntl.LOCK_UN)
          logFile.close()
        else:
          raise ObiException("WriteLog")

def WriteLog(m):
    """
    Writes into the log file the string 'm' followed by a new line
    """
    global logging
    if logging:
        with open(LOG_FILE,'a') as logFile :
            logFile.write(CurrentDate()+" "+CurrentTime()+": "+m+"\n")

#---------------------------------------------------------------------------

def CleanRes(res):
    """ Cleans superflous bits froma process execution result """
    return (res >> 8) & 255

#---------------------------------------------------------------------------

def reset_submissions():
    """ Resets all submissions in the data base to the unselected state. """
    try:
        curs.execute("delete from %s where result_id > 0; select setval('%s_result_id_seq', 1, false)" % (TABLE_RESULT,TABLE_RESULT));
        curs.execute("update %s set sub_lock=0, sub_marked=0 where sub_id >0" % (TABLE_SUBMISSION))
        conn.commit()
    except:
        traceback.print_exc()
        raise  ObiException("reset_submission")

#---------------------------------------------------------------------------

def get_languages():
    """ Gets information about the languages. """
    BINDIR='/home/corretor/bin'
    try:
      data=[[1, 'C', 'sub.c', BINDIR+'/compila_C.sh', './sub.exe'],
              [2, 'C++', 'sub.c', BINDIR+'/compila_C++.sh', './sub.exe'],
              [3, 'Pascal', 'sub.pas', BINDIR+'/compila_Pascal.sh', './sub'],
              [4, 'Python2', 'sub.py', BINDIR+'/compila_Python2.sh', './sub.exe'],
              [5, 'Java', 'solucao.java', BINDIR+'/compila_Java.sh', './sub.exe'],
              [6, 'Javascript', 'sub.js', BINDIR+'/compila_JavascriptNode.sh', './sub.exe'],
              [7, 'Python3', 'sub.py', BINDIR+'/compila_Python3.sh', './sub.exe']]
      return data
    except:
        traceback.print_exc()
        raise  ObiException("get_languages")

#---------------------------------------------------------------------------

def get_teams():
    """ Gets information about the teams from the data base. Used by PCSS """

    try:
        conn = psycopg1.connect(ConnectCommand)
        curs = conn.cursor()
        curs.execute("select team_id,team_name from team order by team_id asc")
        data = curs.dictfetchall()
        conn.commit()
        conn.close()
        return data
    except:
        traceback.print_exc()
        raise  ObiException("get_teams")

#---------------------------------------------------------------------------

def get_submission():
    """ Gets the next available submission from the data base and marks it as selected. """
    conn = psycopg2.connect(ConnectCommand)
    conn.set_client_encoding('UTF8')
    curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        curs.execute("""
                lock table %s in exclusive mode;
                create temp table t_lock as
                select sub_id, sub_lang, sub_source, team_id, problem_name, problem_name_full
                from %s where problem_name<>'compensacao' and sub_lock=0 and sub_id=(select min(sub_id) from %s where sub_lock=0 and problem_name<>'compensacao' );
                update %s set sub_lock=1 where sub_id = (select sub_id from t_lock);
                select *
                from t_lock
                """ % (TABLE_SUBMISSION,TABLE_SUBMISSION,TABLE_SUBMISSION,TABLE_SUBMISSION))
        data = curs.fetchone()
        conn.commit()
        #########################
        # only process if needed
        #########################
        # if data:
        #     id = data['sub_id']
        #     print(id)
        #     command = "select num_correct_tests from %s where sub_id=%d" % (TABLE_RESULT, id)
        #     curs.execute(command)
        #     tmp = curs.fetchone()
        #     print(tmp)
        #     if tmp and tmp['num_correct_tests']==100:
        #         print("NOT PROCESSING sub_id={}, problem_name={} ({})".format(id,data['problem_name'],tmp['num_correct_tests']))
        #         conn.close()
        #         return []
            
        conn.close()
        return data
    except:
        traceback.print_exc()
        raise  ObiException("get_submission")

#---------------------------------------------------------------------------

def get_submission_fair(id):
    """ Gets the next available submission from the data base and marks it as selected. """
    id=int(id)
    #print 'get_submission_fair',id
    try:
        curs.execute("""
                lock table %s in exclusive mode;
                create temp table t_lock as
                select sub_id, sub_lang, problem_id, sub_source, team_id, problem_name, problem_name_full
                from %s where sub_lock=0 and sub_id=(select min(sub_id) from %s where sub_lock=0 and team_id=%d );
                update %s set sub_lock=1 where sub_id = (select sub_id from t_lock);
                select *
                from t_lock
                """ % (TABLE_SUBMISSION,TABLE_SUBMISSION,TABLE_SUBMISSION,id,TABLE_SUBMISSION))
        data = curs.fetchone()
        conn.commit()
        return data
    except:
        traceback.print_exc()
        raise  ObiException("get_submission")

#---------------------------------------------------------------------------

def get_the_submission(num):
    """ Gets the submission with sub_id=num from the data base and marks it as selected. """
    conn = psycopg2.connect(ConnectCommand)
    conn.set_client_encoding('UTF8')
    curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        curs.execute("""
            lock table %s in exclusive mode;
            update %s set sub_lock=1 where sub_id = %d;
            select sub_id, sub_lang, sub_source, team_id, problem_name, problem_name_full
            from %s where sub_id=%d;
            """ % (TABLE_SUBMISSION, TABLE_SUBMISSION, num, TABLE_SUBMISSION, num))
        data = curs.fetchone()
        conn.commit()
        conn.close()
        return data
    except:
        traceback.print_exc()
        raise  ObiException("get_the_submission")


#---------------------------------------------------------------------------

def put_result(id, team_id, problem_name, result, log, \
               num_total_tests, num_correct_tests):
    """ Returns the results to the data base. """
    conn = psycopg2.connect(ConnectCommand)
    conn.set_client_encoding('UTF8')
    curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    command = "select num_correct_tests from %s where sub_id=%d" % (TABLE_RESULT, id)
    curs.execute(command)
    data = curs.fetchone()
    if data and num_correct_tests < data['num_correct_tests']:
        #print("NOT UPDATING sub_id={}, problem_name={}, num_correct_tests={} ({})".format(id,problem_name,num_correct_tests,data['num_correct_tests']))
        return
    from datetime import datetime
    try:
        cur_time = time.time()
        command = "delete from %s where sub_id=%d" % (TABLE_RESULT, id)
        curs.execute(command)

        command = "insert into {} (result_result, sub_id, team_id, problem_name, result_log, num_total_tests, num_correct_tests, result_time) values('{}', {}, {}, '{}', '{}', {}, {}, '{}')".format(TABLE_RESULT, result, id, team_id, problem_name, log, num_total_tests, num_correct_tests, datetime.now())

        curs.execute(command)
        command = "update %s set sub_marked=1 where sub_id=%d" % (TABLE_SUBMISSION,id)
        curs.execute(command)
        conn.commit()
        conn.close()
        #print("UPDATING sub_id={}, problem_name={}, num_correct_tests={} ({})".format(id,problem_name,num_correct_tests,data['num_correct_tests']))
    except:
        traceback.print_exc()
        raise  ObiException("put_result")

#---------------------------------------------------------------------------

def put_marked(id, site):
    """ Returns the results to the data base. """
    try:
        command = "update %s set sub_marked=1 where sub_id=%d and site_id=%d" % (TABLE_SUBMISSION,id, site)
        curs.execute(command)
        conn.commit()
    except:
        traceback.print_exc()
        raise  ObiException("put_marked")

#---------------------------------------------------------------------------

LANG_NAME_SEL = 0
LANG_SUBMIT_NAME_SEL =1
LANG_COMPILE_SEL = 2
LANG_EXECUTE_SEL = 3

def GetLanguages():
    try:
        langName = {}
        langSubmitName = {}
        langCompile = {}
        langExecute = {}
        for ld in get_languages():
            id = ld[0]
            langName[id] = ld[1]
            langSubmitName[id] = ld[2]
            langCompile[id] = ld[3]
            langExecute[id] = ld[4]
        return langName, langSubmitName, langCompile, langExecute
    except:
         raise  ObiException("GetLanguages")

#---------------------------------------------------------------------------

PROBLEM_NAME_SEL = 0
PROBLEM_FULL_NAME_SEL = 1

def GetProblems():
    try:
        problemName = {}
        problemFullName = {}
        for pd in get_problems():
            id = pd["problem_id"]
            problemName[id] = pd["problem_name"]
            problemFullName[id] = pd["problem_name_full"]
        return problemName, problemFullName
    except:
         raise  ObiException("GetProblems")

#---------------------------------------------------------------------------

def ProcessSubmission(Languages, Problems, submitData):
    RESULT = 0
    #try: MUST REVERT
    if True:
        # submission data
        subId = submitData["sub_id"]               # int
        competId = submitData["team_id"]             # int
        subLang = int(submitData["sub_lang"])      # str
        #subTime = submitData["sub_time"]           # float
        subSource = submitData["sub_source"]          # text
        #subsrc = bytes(subsrc,'ascii')
        #subSource = base64.decodestring(subsrc)
        #problemId = submitData["problem_id"]                # int            
        problemName = submitData["problem_name"]            # str
        problemNameFull = submitData["problem_name_full"]   # str
        
        WriteLog("subId: %s competId: %s  subLang: %d problemName: %s problemNameFull: %s" % (subId, competId, subLang, problemName, problemNameFull))
        print("subId: %s competId: %s  subLang: %d problemName: %s problemNameFull: %s" % (subId, competId, subLang, problemName, problemNameFull))
        
        # language paramers
        sourceName = Languages[LANG_SUBMIT_NAME_SEL][subLang]
        execName = Languages[LANG_EXECUTE_SEL][subLang]
        compileCommand = Languages[LANG_COMPILE_SEL][subLang]
    try:
        if compileCommand!='':
            if subLang==5: #java
                tmpProblemName='solucao'
                if CAPITALIZE_JAVA:
                    tmpProblemName=problemName[0].upper()+problemName[1:]
                sourceName=tmpProblemName+".java"
                compileCommand = compileCommand+" %s.java %s" % (tmpProblemName,execName)
            else:
                compileCommand = compileCommand+" %s %s" % (sourceName, execName)
        # files
        Debug("compile command:"+compileCommand)
        subprocess.run(["/usr/local/bin/isolate", "--cleanup"], stderr=subprocess.PIPE)
        res = subprocess.run(["/usr/local/bin/isolate", "--cleanup"], stderr=subprocess.PIPE, timeout=1)
        if res.returncode != 0:
            WriteLog('Error in isolate cleanup')
            raise 'boom'
        res = subprocess.run(["/usr/local/bin/isolate", "--init"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1)
        if res.returncode != 0:
            WriteLog('Error in isolate init')
            raise 'boom'
        execDir = res.stdout.decode().strip()
        execDir = os.path.join(execDir,'box')
        Debug("Processing submission %s from compet %s " % (subId,competId))
        Debug("Exec dir: "+execDir)
        os.chdir(execDir)
        execString = Languages[LANG_EXECUTE_SEL][subLang]
        
        with open("INFO","w") as infoFile:
            infoFile.write("submission %s from compet %s\n" % (subId,competId))
        with open(sourceName,"w") as sourceFile:
            try:
                sourceFile.write(subSource)
                sourceFile.close()
            except:
                sourceFile.write(subSource.decode('latin-1'))
                sourceFile.close()

        Debug("Program: \n--------\n"+str(subSource)+"\n----------\n")
        
        # Test report
        report = StringIO()
        report_error = StringIO()
        Debug("Problem Name: %s, problem Full Name: %s" % (problemName, problemNameFull))
        #report.write(REPORT_HEADER  % (subId))
        #report.write(TEAM_ID % competId)
        report.write(PROBLEM_NAME % problemNameFull)
        report.write(LANGUAGE_NAME % Languages[LANG_NAME_SEL][subLang])
        
        # compile
        subSource=subSource.strip()
        if subSource=='':
            report.write(COMPILATION_UNSUCCESSFUL)
            report.write(COMPILATION_SOURCE_EMPTY)
            RESULT = 1              # unsuccessful compilation
            compRes = 1
        elif compileCommand!='':
            if is_binary(sourceName):
                report.write(COMPILATION_UNSUCCESSFUL)
                report.write(COMPILATION_NOT_A_SOURCE)
                compRes = 1
            else:               
                Debug('Compile command: %s\n' % compileCommand)

                compileError=tempfile.NamedTemporaryFile()
                compileOutput=tempfile.NamedTemporaryFile()
                compRes = subprocess.call(shlex.split(compileCommand),
                                          stdout = compileError,
                                          stderr = compileError,shell=False)

                if compRes==0:
                    #if not os.path.exists(COMPILE_LOG_FILE) or os.path.getsize(COMPILE_LOG_FILE)==0:
                    report.write(COMPILATION_SUCCESSFUL)
                else:
                    report.write(COMPILATION_UNSUCCESSFUL)
                    #report.write(compOutput)
                    with open(compileError.name,"r") as f:
                        tmplog=f.read(4000)
                        #tmpclean,s='',0
                        #for c in tmplog:
                        #    if c in string.printable:
                        #        tmpclean+=c
                    report_error.write(tmplog+' ...\n\n')
                    #report_error.write(tmpclean[0:4000]+' ...\n\n')
                    #compileLog = open(compileError.name,"r")

                    #report_error.write(compileLog.read())
                    #compileLog.close()
        else:
            compRes = 0        # self executable
            os.chmod(sourceName,0o700)
        execRes = []
        numPoints = 0
        numTotalPoints = 0
        pointsDict = {}                   # dictionary for points for every test

        problemDir = os.path.join(problemsDir,problemName)

        if not os.path.exists(problemDir):
            raise ObiException("Cannot find problem directory  "+problemDir)

        #if 'LIMIT_DATASIZE' in globals():
        #    print("DATASIZE IN globals")
        limitsFile = os.path.join(problemDir,LIMITS_FILE)
        limits={"LIMIT_EXECTIME":1000,"LIMIT_FILESIZE":"1KB"}
        if os.path.exists(limitsFile):
            with open(limitsFile,"r") as f:
                exec(f.read(),limits)
                
        ################
        # the only limits used from user configuration are
        # LIMIT_EXECTIME
        # LIMIT_FILESIZE
        # The others are fixed:
        # C/C++/Pascal:
        #  LIMIT_DATASIZE="512MB";
        # also, compile_Java.sh fixes the limits for java
        limits["LIMIT_DATASIZE"]="512MB"
        if subLang==4 or subLang==7: # 
            limits["LIMIT_DATASIZE"]="756MB"
        elif subLang==5: # Java
            limits["LIMIT_DATASIZE"]="3000MB"
        elif subLang==6: # Javascript nodejs
            limits["LIMIT_DATASIZE"]="1GB"

        if compRes==0:                    # successful compilation (or none)
            pointsFileName = os.path.join(problemDir,POINTS_FILE)
            if os.path.exists(pointsFileName):
                try:
                    pointsFile = open(pointsFileName,"r")
                    points = int(pointsFile.readline())
                    pointsFile.close()
                except:
                    raise ObiException("Problems in points file "+pointsFileName)
            else:
                Debug("Points file not found")
                points = 1

            report.write(TESTING_PHASE % (int(limits['LIMIT_EXECTIME'])))
            #report.write(TESTING_PHASE)

            for nch in range(1,1+TEST_SUFFIX_MAX):          # iterate over tests to calculate total number of points
                ch = str(nch)
                testDir = os.path.join(problemDir,TEST_PREFIX+ch)
                if not os.path.exists(testDir): # no more tests
                    break
                pointsDict[ch] = points
                numTotalPoints = numTotalPoints+points
            
            if numTotalPoints == 0:
                raise ObiException("Cannot find tests for problem ",testDir)

            checkingProg = os.path.join(problemDir,CHECKING_PROGRAM)
            if not os.path.exists(checkingProg):
                checkingProg = DIFF
                checkingCommand = checkingProg+" %s  %s"  # 1: results; 2: template
            else:
                #checkingCommand = checkingProg+" %s  %s %s %s >/dev/null"  # 1: results; 2: template
                checkingCommand = checkingProg+" %s  %s %s %s"  # 1: results; 2: template

            if not COMPILE_ONLY:
                for nch in range(1,1+TEST_SUFFIX_MAX):          # iterate over tests directories
                    ch = str(nch)
                    testDir = os.path.join(problemDir,TEST_PREFIX+ch)
                    Debug("testDir: %s\n" % testDir)
                    report.write(TEST_SEPARATOR)
                    if not os.path.exists(testDir): # no more tests
                        break
                    report.write(TEST_HEADER % nch)
                    TOTAL_ERROR_RESULT = 0
                    case_error_result = 0
                    for tnch in range(1,1+INPUT_SUFFIX_MAX):          # iterate over test cases
                        print('.',end='',file=sys.stderr)
                        sys.stderr.flush()
                        tch = str(tnch)
                        inputFile = os.path.join(testDir,INPUT_FILE+tch)
                        if not os.path.exists(inputFile):
                             # using box naming convention?
                            inputFile = os.path.join(testDir,"%d.%s"% (tnch,"in"))
                            if not os.path.exists(inputFile):
                                Debug("NO MORE TESTS, inputFile: %s\n" % inputFile)
                                break
                        Debug("inputFile " + inputFile)
                        report.write(TEST_CASE_SEPARATOR)
                        #report.write(TEST_CASE_HEADER % tnch)

                        outputFile = os.path.join(testDir,OUTPUT_FILE+tch)
                        if not os.path.exists(outputFile):
                             # using box naming convention?
                            outputFile = os.path.join(testDir,"%d.%s"% (tnch,"sol"))
                            if not os.path.exists(outputFile):
                                msg="Cannot find test output file for problem", testDir,tnch,OUTPUT_FILE
                                print(msg)
                                raise ObiException("Cannot find test output file for problem %s, test %s, case %s" % (Problems[PROBLEM_NAME_SEL][problemId], TEST_PREFIX+ch, "%d.%s" % (tnch,INPUT_FILE)))
                        Debug("inputFile " + inputFile)

                        resultFile = RESULT_FILE+ch+'_'+tch
                        errorFile = TEST_LOG_FILE+ch+'_'+tch
                        timeFile = TIME_FILE+ch+'_'+tch
                        statusFile = STATUS_FILE+ch+'_'+tch
                        Debug("subLang: {}".format(subLang))
                        Debug("LANG_EXECUTE_SEL: {}".format(LANG_EXECUTE_SEL))
                        testResult=run_solution(sub_lang=subLang,
                                                sol_fn=Languages[LANG_EXECUTE_SEL][subLang],
                                                input_fn=inputFile,
                                                output_fn = resultFile,
                                                error_fn = errorFile,
                                                status_fn = statusFile,
                                                cpu_limit = limits['LIMIT_EXECTIME'],
                                                mem_limit = limits['LIMIT_DATASIZE'],
                                                file_limit = limits['LIMIT_FILESIZE'])

                        Debug("*** status %s" % testResult.status)

                        if os.path.exists(errorFile) and os.path.getsize(errorFile)!=0 and testResult.status not in (CORRECT_EXECUTION, TIME_LIMIT_EXCEEDED):
                            report_error.write(EXECUTION_MESSAGE)
                            report_error.write("Teste %d, caso %d:\n" % (nch,tnch))
                            with open(errorFile,"r") as f:
                                try:
                                    tmplog=f.read(500)
                                except:
                                    tmplog='Erro na leitura do log'
                                #tmpclean,s='',0
                                #for c in tmplog:
                                #    if c in string.printable:
                                #        tmpclean+=c
                            report_error.write(tmplog+'\n')
                            #report_error.write(tmpclean[0:200]+'\n\n')
                            
                        if testResult.status==CORRECT_EXECUTION:
                            if FILTER_PROGRAM:
                                os.system("cp %s Raw_%s" % (resultFile,resultFile))

                                os.system("%s < %s > tmp; mv tmp %s" % (FILTER_PROGRAM, resultFile, resultFile))
                                os.system("%s < %s > tmp; mv tmp %s" % (FILTER_PROGRAM, outputFile, "filtered_output"))
                                outputFile="filtered_output"
                            if checkingProg == DIFF:
                                chkcomm = checkingCommand % (resultFile,outputFile)
                            else:
                                #INPUT_FILE_PATH, OUTPUT_FILE_PATH, CONTESTER_OUTPUT_FILE_PATH, CONTESTER_SOURCE_FILE_PATH
                                chkcomm = checkingCommand % (inputFile, outputFile,resultFile,resultFile)
                            Debug("chkcomm=%s" % chkcomm)
                            diffRes = subprocess.call(shlex.split(chkcomm),stdout=open('/dev/null','w'),stderr=open('/dev/null','w'),shell=False)
                            if diffRes!=0:
                                case_error_result = 4
                                report.write(INCORRECT_RESULT)
                            else:
                                case_error_result=0
                                report.write(CORRECT_RESULT)                    
                                # report.write(EXECUTION_TIME % (execTime))
                        elif testResult.status==TIME_LIMIT_EXCEEDED:
                            # File size exeeded, report error?
                            report.write(TIME_LIMIT_EXCEEDED)
                            case_error_result = 5
                        elif testResult.status==SIGKILL_ERROR:
                            # File size exeeded, report specific error?
                            report.write(SIGKILL_ERROR)
                            case_error_result = 5
                        elif testResult.status==EMPTY_OUTPUT_ERROR:
                            report.write(EMPTY_OUTPUT_ERROR)
                            case_error_result = 6
                        elif testResult.status==SIGKILL_ERROR:
                            report.write(SIGKILL_ERROR)
                            case_error_result = 7
                        elif testResult.status==INVALID_REF_ERROR:
                            report.write(INVALID_REF_ERROR)
                            case_error_result = 7
                        else:
                            report.write(RUN_TIME_ERROR)
                            case_error_result = 8
                            
                        TOTAL_ERROR_RESULT = TOTAL_ERROR_RESULT + case_error_result

                    if (TOTAL_ERROR_RESULT == 0):
                        numPoints = numPoints+pointsDict[ch]
                        report.write(POINTS_RECEIVED % (pointsDict[ch]))
                    else:
                        report.write(POINTS_RECEIVED % (0))
                        if ABORT_FIRST_ERROR:
                            break           # no more tests
                        else:
                            RESULT = 2 # indicate failure
                
                execRes.append(TOTAL_ERROR_RESULT)
        report.write(TOTAL_POINTS_RECEIVED % (numPoints, numTotalPoints))
            
        WriteLog(("Results subId %s: ") % subId + str((compRes,execRes)))
        if compRes==0:
            report.write(LEGEND)
        reportText = report.getvalue()
        if report_error.getvalue().strip():
            reportText += "\n\n\n------------------------------------------------------------------\n"
            reportText += "Mensagens de Erro\n"
            reportText += "------------------------------------------------------------------\n\n"
            reportText += report_error.getvalue()

        # Rmk.: 'reportText' can't contain single quotes!
        reportText=reportText.replace("\'", "\"")
        reportText=reportText.replace("`",'"')
        reportText=reportText.replace("‘",'"')
        reportText=reportText.replace("’",'"')


        #####
        # Temporary report output
        print("\n------------------------------------------------------------------")
        print(reportText)
        print("------------------------------------------------------------------\n")
        #####
        if not DEBUG:
            os.system("/usr/local/bin/isolate --cleanup")
        else:
            pass
            #os.system("rm -fR "+execDir) # delete anyway!
        
        Debug("Submission %s processed: " % subId+str((compRes, execRes, numTotalPoints, numPoints)))
        Debug("***********************************************************")
        Debug("Exec dir: "+execDir)
        sys.stderr.flush()
        sys.stdout.flush()
        put_result(subId, competId, problemName, RESULT, reportText, \
                       numTotalPoints, numPoints)  ##########
    except ObiException as e:

        WriteLog("Exception '%s' while processing submission %s" % \
                     (e.value,submitData["sub_id"]))
        print("Exception '%s' while processing submission %s" % \
            (e.value,submitData["sub_id"]))



#------------------------------------------------------------------------#
#  Main program                                                          #
#------------------------------------------------------------------------#

if __name__ == '__main__':

    # Signal QUIT (3) or INT (2) will stop processing after completing a submission
    quitSignal = False

    def QuitHandler(signum, frame):
        global quitSignal
        quitSignal = True

    signal.signal(signal.SIGQUIT,QuitHandler)
    signal.signal(signal.SIGINT,QuitHandler)

    # Processing options

    opts, args = getopt.getopt(sys.argv[1:],"Ccdf:hirp:",[])
    HARD_DEBUG = False
    COMPILE_ONLY = False
    CAPITALIZE_JAVA = False
    obi_accept_mode = False
    reset = False
    seletiva_ioi=False
    interactive = False
    FORCE_PYTHON_VERSION=''
    for o,a in opts:
        if o=='-h':
            print(UsageMessage)
            os._exit(0)
        if o=='-f':
            CONFIG_FILE_NAME = a
        if o=='-c':
            COMPILE_ONLY = True
        if o=='-C':
            CAPITALIZE_JAVA = True
        if o=='-d':
            HARD_DEBUG = True
        if o=='-o':
            obi_accept_mode = True
        if o=='-r':
            reset = True
        if o=='-s':
            seletiva_ioi = True
        if o=='-i':
            interactive = True
        if o=='-n':
            PROC_ID = a
        if o=='-p':
            FORCE_PYTHON_VERSION = a


    try:
        with open(CONFIG_FILE_NAME,"rU") as f:
            #code = compile(f.read(), "somefile.py", 'exec')
            exec(f.read(),obiGlobals) #, global_vars, local_vars)
        #execfile(CONFIG_FILE_NAME)
    except:
        print("\nNo configuration %s file found or not valid \n" % CONFIG_FILE_NAME)
        traceback.print_exc()
        os._exit(1)

    if HOST=="" or DB_NAME=="" or USER_NAME=="" or PROBLEMS_DIR=="":
        print("\nOne of the configuration items is missing:  HOST, DB_NAME, USER_NAME or PROBLEMS_DIR\n")
        sys.exit(1)

    if PASSWORD=="":
        PASSWORD = getpass.getpass()

    if HARD_DEBUG:           # override config file
        DEBUG = True

    ConnectCommand = "host="+HOST+ \
             " dbname="+DB_NAME+   \
             " user="+USER_NAME+   \
             " password="+PASSWORD

    teams=[]
    if seletiva_ioi:
        teams = get_teams()
        min_team_id=int(teams[0]['team_id'])
        max_team_id=int(teams[-1]['team_id'])
        print('TEAMS',teams)


    #problemsDir = os.path.join(scriptDir,PROBLEMS_DIR)
    problemsDir = PROBLEMS_DIR
    Debug("Problem dir: "+problemsDir)
    if not os.path.exists(problemsDir):
        print("\nCannot find problems directory "+problemsDir)
        sys.exit(1)

    logging = (LOG_FILE!="")
    #if logging:
    #    LOG_FILE = os.path.join(scriptDir,LOG_FILE)
    #else:
    #    print "\nNo logging"

    tempfile.tempdir = TEMP_DIR
        
    # Main body
    try:
        if interactive:
            message = "Starting OBI processor '%s' in interactive mode - type 0 or <enter> to exit" % PROC_ID
        else:
            message = "Starting OBI processor '%s' in continuous mode - type Ctrl-C to stop" % PROC_ID
        WriteLog(message)
        print("\n"+message+"\n")

        if reset:
            reset_submissions()

        Languages = GetLanguages()
        if FORCE_PYTHON_VERSION=='2':
            Languages[2][7]=Languages[2][4]
        if FORCE_PYTHON_VERSION=='3':
            Languages[2][4]=Languages[2][7]
            
        Debug(str(Languages))

        Problems = '' # just to declare the name...
        Debug("Retrieving problem name from user request")

        if not interactive:
            last_used_team=0
            while (True):
                countTrials = 0
                found = False
                while not found:
                    if quitSignal:
                        WriteLog("Execution terminated by a QUIT or INT signal\n")
                        print("\nExecution terminated by a QUIT or INT signal\n")
                        sys.exit(0)
                    if seletiva_ioi:
                        for i in xrange(len(teams)):
                            last_used_team+=1
                            if last_used_team>max_team_id:
                                last_used_team=min_team_id
                            submitData = get_submission_fair(last_used_team)
                            if submitData:
                                break
                    else:
                        submitData = get_submission()
                    if not submitData:
                        countTrials = countTrials+1
                        if countTrials>MAX_TRIALS:
                            WriteLog("No submissions for %d x %d seconds" % (MAX_TRIALS,SLEEP_TIME))
                            #print("Waiting for more submissions ...")
                            countTrials = 0
                        time.sleep(SLEEP_TIME)
                    else:
                        found = True
                print("Retrieved submission %s from %d, %s.%s" % (submitData["sub_id"],submitData["team_id"],submitData["problem_name"],lang_ext[int(submitData["sub_lang"])]))
                try:
                    ProcessSubmission(Languages, Problems, submitData)
                except:
                    print("Exception when processing sub_id=%d" % submitData["sub_id"])
                    WriteLog("Exception when processing sub_id=%d" % submitData["sub_id"])
        else:

            while True:
                subNum = input("\nSubmission: ")
                if subNum=="" or subNum=="q" or subNum=="0" or subNum=="x":
                    break
                try:
                    subNum = int(subNum)
                    print('before')
                    submitData = get_the_submission(subNum)
                except:
                    # must be a file name
                    subFileName,subProblem,subLanguage=subNum.split()
                    with open(subFileName,"r") as f:
                        src=bytes(f.read(),'utf-8')
                        #src=str(src,'ascii')                        
                    submitData={"sub_id":0,"team_id":0,"site_id":0,"sub_lang":int(subLanguage),"sub_time":0,\
                                    "sub_source":src,"sub_time":0,"sub_penalty":0,"sub_tries":0,\
                                    "problem_id":0,"problem_name":subProblem,"problem_name_full":'Problem'}
                if not submitData:
                    print("Submission %d not found or processed already" % subNum)
                else:
                    Debug("Retrieved submission %s" % submitData["sub_id"])
                    try:
                        ProcessSubmission(Languages, Problems, submitData)
                    except:
                        print("Exception when processing sub_id=%d" % submitData["sub_id"])
                        WriteLog("Exception when processing sub_id=%d" % submitData["sub_id"])

            print("\nExecution finished\n")

    except ObiException as e:
        print("Exception in %s\n" % e.value)
        WriteLog("Exception in %s\n" % e.value)

    except:
        print("Unexpected exception")
        traceback.print_exc()
        WriteLog("Unexpected exception\n")
        
