import math

from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter

from exams.models import Task, Question, Alternative
from exams.views import check_exam_status, get_exam_start, get_exam_finish
from exams.settings import EXAMS

register = template.Library()

@register.filter
def get_exam_compet_status(exam_descriptor,compet):
    ok,exam,status,msg = check_exam_status(exam_descriptor, compet)
    return (ok,msg)

@register.filter
def get_exam_compet_start(exam_descriptor,compet):
    start = get_exam_start(exam_descriptor, compet)
    return start

@register.filter
def get_exam_compet_finish(exam_descriptor,compet):
    finish = get_exam_finish(exam_descriptor, compet)
    return finish

@register.filter
@stringfilter
def format_status_text(s):
    s = s.replace('[','')
    s = s.replace(']','')
    s = s.replace("'",'')
    return s

@register.filter
@stringfilter
def translate(s):
    tr = {'Correct': 'Correto', 'Output is correct': 'A saída está correta',
          "Not correct": "Incorreto", "Partially correct": "Parcialmente correto",
          "Outcome": "Resultado", "Execution time": "Tempo de execução",
          "Memory used": "Memória usada", "Compilation succeeded": "Compilação terminou sem erros.",
          "Compilation succeeded": "Compilação terminou sem erros.",
          "Output is partially correct": "A saída está parcialmente correta",
          "Output isn't correct": "A saída está errada",
          "Outcome": "Resultado", "Details": "Detalhes", "Execution time": "Tempo de execução",
          "Memory used": "Memória usada",
          "Compilation output": "Compilação", "Compilation outcome": "Resultado da compilação",
          "Compilation succeeded": "Compilação terminou com sucesso",
          "Compilation failed": "Compilação terminou com falha",
          "Standard output": "Saída Padrão (stdout):", "Standard error": "Saída de erro padrão (stderr):",
          "Execution killed (could be triggered by violating memory limits)": "Execução interrompida (provavelmente violação de limite de memória)",
          "Execution failed because the return code was nonzero": "Erro durante a execução (código de retorno diferente de zero)",
          "Execution timed out": "Excedeu o tempo limite de execução",
          }
    try:
        return tr[s]
    except:
        return s

@register.filter
@stringfilter
def format_size( n):
    """Format the given number of bytes.
    Format the size of a file, a memory allocation, etc. which is
    given as a number of bytes. Use the most appropriate unit, from
    bytes up to tebibytes. Always show the entire integral part plus
    as many fractional digits as needed to reach at least three
    significant digits in total, except when this would mean showing
    sub-byte values (happens only for less than 100 bytes).

    n (int): a size, as number of bytes.

    return (str): the formatted size.
    """
    n = abs(int(n))

    PREFIX_FACTOR = 1024
    SIZE_UNITS = [None, " KB", " MB", " GB", " TB"]
    if n < PREFIX_FACTOR:
        return f"{roun(n)} Bytes"
    for unit in SIZE_UNITS[1:]:
        n /= PREFIX_FACTOR
        if n < PREFIX_FACTOR:
            # f = copy.copy(self.locale.decimal_formats[None])
            # if 1000 <= n < 1024 d can be negative, cap to 0 decimals
            d = max(0, 2 - math.floor(math.log10(n)))
            return f"{round(n,d)} {unit}"
    return f"{round(n)} {SIZE_UNITS[-1]}"

@register.simple_tag
def format_score(score, max_score, score_precision):
    if score == None:
        score = 0
    if score_precision == 0:
        return "%s / %s" % (
            int(round(score, score_precision)),
            int(round(max_score, score_precision))
        )
    else:
        return "%s / %s" % (
            round(score, score_precision),
            round(max_score, score_precision)
        )

@register.simple_tag
def get_score_class(score, max_score):
    if score == None:
        return "score_0"
    elif score <= 0:
        return "score_0"
    elif score >= max_score:
        return "score_100"
    else:
        return "score_0_100"

@register.simple_tag
def get_submission_result(submission_results, id):
    return submission_results.get(submission_id=id)

@register.simple_tag
def reflect(obj, reflection):
    objlist = list(obj)
    new_obj = []
    for i in reflection:
        new_obj.append(objlist[i-1])
    return new_obj

@register.simple_tag
def reflected(val, reflection):
    return reflection[val-1]

@register.filter
@stringfilter
def obi_get_task_id(s):
    s=s[s.find('_')+1:]
    return s

@register.simple_tag
def get_num_answers_correct_exam(descriptor, answers):
    total,answered = 0,0
    for a in answers[descriptor].keys():
        total += 1
        if answers[descriptor][a] > 0:
            answered += 1
    return '{}/{}'.format(answered, total)

@register.simple_tag
def get_num_answers_exam(descriptor, answers):
    #print('descriptor',descriptor)
    #print('answers',answers)
    total,answered = 0,0
    for a in answers[descriptor].keys():
        total += 1
        if answers[descriptor][a] > 0:
            answered += 1
    if answered == total:
        return f'{answered}/{total}'
    else:
        return f'<font color="red">{answered}</font>/{total}'

@register.simple_tag
def get_num_answers_exam_total(answers, level):
    total_tasks,total_questions,answered = 0,0,0
    for descriptor in answers.keys():
        total_tasks += 1
        for a in answers[descriptor].keys():
            total_questions += 1
            if answers[descriptor][a] > 0:
                answered += 1
    return (total_tasks,total_questions,total_questions-answered)

class TaskNode(template.Node):
    def __init__(self, context_name, exam_descriptor, level):
        self.context_name = context_name
        self.exam_descriptor = template.Variable(exam_descriptor)
        self.level = template.Variable(level)
        self.user = None # todo

    def render(self, context):
        #print(self.exam_descriptor.resolve(context))
        #print(self.level.resolve(context))
        tasks = Task.objects.filter(exam=self.exam_descriptor.resolve(context),level=self.level.resolve(context)).order_by('order','title')
        #print(tasks)
        context[self.context_name] = tasks
        return ''


@register.tag
def get_tasks(parser, token):
    """
    Retrieve all task objects available for the current site and
    visible to the specific user (or visible to all users if no user is
    specified). Populate the template context with them in a variable
    whose name is defined by the ``as`` clause.

    Syntax::

        {% get_tasks exam_descriptor level as context_name %}

    """
    bits = token.split_contents()
    syntax_message = ("%(tag_name)s expects a syntax of %(tag_name)s "
                      "exam_descriptor level as context_name" %
                      {'tag_name': bits[0]})
    # Must have 5 bits in the tag
    if len(bits) == 5:
        exam_descriptor = bits[1]
        level = bits[2]
        if bits[-2] != 'as':
            raise template.TemplateSyntaxError(syntax_message)
        context_name = bits[-1]
        return TaskNode(context_name, exam_descriptor=exam_descriptor, level=level)
    else:
        raise template.TemplateSyntaxError(syntax_message)

@register.simple_tag
def get_tasks_objects(exam_descriptor,level):
    tasks = Task.objects.filter(exam=exam_descriptor,level=level).order_by('order')
    return tasks

@register.simple_tag
def get_question_objects(task):
    questions = Question.objects.filter(task=task).order_by('num')
    return questions

@register.simple_tag
def get_alternative_objects(question):
    alternatives = Alternative.objects.filter(question=question).order_by('num')
    return alternatives

@register.simple_tag
def get_answers_task(answers, task_descriptor):
    return answers[task_descriptor]
