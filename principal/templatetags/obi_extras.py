import os.path
import re

from django import template
from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.template import Context, RequestContext, Template
from django.template.defaultfilters import stringfilter
from django.utils.http import urlencode

from principal.models import LEVEL, LEVEL_NAME, LEVEL_NAME_FULL, SCHOOL_YEAR_FULL, School
from principal.utils.utils import format_compet_id
from obi.settings import YEAR

# fix it later for 4.2
from cal.models import CalendarNationalEvent
#from exams.settings import EXAMS
#from fase2.models import PointsFase2

register = template.Library()

@register.filter
def dictsum(d):
    if d:
        return sum(d.values())
    else:
        return 0

@register.filter
def has_cfobi(year):
    if int(year) >= 2023:
        return True
    return False

@register.filter
@stringfilter
def obi_escape_url(s):
    s = s.replace('/','--')
    #s = urlencode({'page': s})
    return s

@register.filter
@stringfilter
def newline_to_break(s):
    s = s.replace('\n','<br/>')
    #s = urlencode({'page': s})
    return s

@register.filter
def inlist(value, arg):
    try:
        # Convert the argument to a list of integers
        int_list = [int(x) for x in arg.split(',')] if isinstance(arg, str) else arg
        return value in int_list
    except (ValueError, TypeError):
        return False


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def get_last_component_as_int(url):
    val = {'i0': 1, 'ij':0, 'i1':1, 'i2':2, 'p0': 4, 'pj':3, 'p1':4, 'p2':5, 'ps':6, 'pu':6, 'cfobi_pj':3, 'cfobi_p1':4, 'cfobi_p2':5 }
    return val[url.url.split('/')[-2]]
    
@register.filter
def sort_flatpages(flatpages):
    sorted_list = sorted(flatpages, key=get_last_component_as_int)
    return sorted_list

@register.filter
def get_list_item(value, arg):
    try:
        return value[arg]
    except (IndexError, TypeError):
        return ''

@register.filter
def split_title(t):
    title = t.split(" - ")
    return title

@register.filter
def title_start(t):
    title = t[:4].strip()
    return title

@register.filter
def count_slashes(url):
    return url.count('/')

@register.filter
def first_token(url):
    return url[0:url.find('/',2)+1]

def find_nth(haystack: str, needle: str, n: int) -> int:
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start

@register.filter
def first_2tokens(url):
    return url[0:find_nth(url,'/',3)+1]

@register.filter
@stringfilter
def morf(sex):
    if sex == 'F':
        return 'a'
    else:
        return 'o'


@register.filter
def format_level_full(level):
    return LEVEL_NAME_FULL[level]


@register.filter
@stringfilter
def obi_date_year(s):
    return "{}{}".format(s,YEAR)

@register.filter
@stringfilter
def obi_date_last_year(s):
    return "{}{}".format(s,YEAR-1)


@register.filter
@stringfilter
def obi_date(slug):
    #print('fix it later for 4.2',slug)
    event = CalendarNationalEvent.objects.get(slug=slug)
    date = event.start
    return date

@register.filter
@stringfilter
def obi_date_finish(slug):
    event = CalendarNationalEvent.objects.get(slug=slug)
    date = event.finish
    return date

@register.filter
@stringfilter
def obi_comment(slug):
    event = CalendarNationalEvent.objects.get(slug=slug)
    comment = event.comment
    return comment

#@register.filter
#@stringfilter
#def obi_level_name_full(level):
#    return LEVEL_NAME_FULL[int(level)]

@register.simple_tag
def multiply(factor1, factor2):
    return float(factor1) * float(factor2)

@register.simple_tag
def do_round(value, value_precision):
    if value_precision == 0:
        return "{}".format(
            int(round(value))
        )
    else:
        return "{}".format(
            round(value, value_precision)
        )

@register.filter
@stringfilter
def format_currency(v):
    if not v:
        return 0
    thou = "."
    dec = ","
    s = '{:.2f}'.format(float(v))
    integer, decimal = s.split(".")
    integer = re.sub(r"\B(?=(?:\d{3})+$)", thou, integer)
    return integer + dec + decimal

@register.filter
@stringfilter
def format_number_thousands(v):
    if not v:
        return 0
    thou = "."
    s = '{:.2f}'.format(float(v))
    integer, decimal = s.split(".")
    integer = re.sub(r"\B(?=(?:\d{3})+$)", thou, integer)
    return integer


@register.simple_tag
def go_to_url(url):
    return "window.location='" + url +"'; return false;"

@register.filter
def obi_user_group(user):
    if user.is_authenticated:
        if user.groups.filter(name='local_coord').exists():
            return 'local_coord'
        elif user.groups.filter(name='compet').exists():
            return 'compet'
        elif user.groups.filter(name='colab').exists():
            return 'colab'
        elif user.groups.filter(name='colab_full').exists():
            return 'colab_full'
    return ''

@register.filter
@stringfilter
def obi_capitalize_name(s):
    tks=s.split()
    name = ''
    for nt in tks:
        if nt.lower() in ['de','da','do','e','das','dos']:
            name +=' '+nt.lower()
        else:
            name +=' '+nt.capitalize()
    return name.strip()

@register.filter
def obi_get_phase3_cities(id):
    id = int(id)
    school = School.objects.get(pk=id)
    cities = set()
    if school.school_site_phase3_type == 3:
        schools = School.objects.filter(school_site_phase3_ini=id) | School.objects.filter(school_site_phase3_prog=id)
    elif school.school_site_phase3_type == 1:
        schools = School.objects.filter(school_site_phase3_ini=id)
    elif school.school_site_phase3_type == 2:
        schools = School.objects.filter(school_site_phase3_prog=id)
    else:
        schools = []
    #print()
    #print('school city',school.school_city)
    for s in schools:
        cities.add(s.school_city)
        #print('  ',s.school_name,s.school_city)
    cities = sorted(list(cities))
    cities = ", ".join(cities)
    return cities

@register.filter
@stringfilter
def obi_level_name_full(path):
    # path: p1/2017/f1/cofre/
    m = re.search('(?P<levelshort>[ip][j12us])/(?P<year>[0-9]{4})/f(?P<phase>[123])/(?P<code>.*)',path)
    if m == None:
        m = re.search('(?P<levelshort>[ip][j12us])/$',path)
        if m == None:
            return ''
    return LEVEL_NAME_FULL[LEVEL[m.group('levelshort').upper()]]


@register.filter
@stringfilter
def obi_modstr(path):
    # path: p1/2017/f1/cofre/
    m = re.search('(?P<levelshort>[ip][j12us])/(?P<year>[0-9]{4})/f(?P<phase>[123])/(?P<code>.*)',path)
    if m == None:
        m = re.search('(?P<levelshort>[ip][j12us])/$',path)
        if m == None:
            return ''
    return m.group('levelshort')[0]

@register.filter
@stringfilter
def obi_levelstr(path):
    # path: p1/2017/f1/cofre/
    m = re.search('(?P<levelshort>[ip][j12us])/(?P<year>[0-9]{4})/f(?P<phase>[123])/(?P<code>.*)',path)
    if m == None:
        m = re.search('(?P<levelshort>[ip][j12us])/$',path)
        if m == None:
            return ''
    return m.group('levelshort')[1]

@register.filter
@stringfilter
def obi_levelnum(path):
    to_num = {'ij':7, 'i1':1, 'i2':2, 'pj':5, 'p1':3, 'p2':4, 'pu':6, 'ps':6}
    #print('path',path)
    # path: p1/2017/f1/cofre/
    m = re.search('(?P<levelshort>[ip][j12us])/(?P<year>[0-9]{4})/f(?P<phase>[123])/(?P<code>.*)',path)
    if m == None:
        m = re.search('(?P<levelshort>[ip][j12us])/$',path)
        if m == None:
            m = re.search('(?P<levelshort>[ip][j12us]).*',path)
            if m == None:
                return ''
    try:
        return to_num[m.group('levelshort')]
    except:
        return ''

@register.filter
@stringfilter
def obi_task_year(path):
    # path: p1/2017/f1/cofre/
    m = re.search('(?P<levelshort>[ip][j12us])/(?P<year>[0-9]{4})/f(?P<phase>[123])/(?P<code>.*)',path)
    try:
        return int(m.group('year'))
    except:
        return ''

@register.filter
@stringfilter
def obi_task_phase(path):
    # path: p1/2017/f1/cofre/
    m = re.search('(?P<levelshort>[ip][j12us])/(?P<year>[0-9]{4})/f(?P<phase>[123])/(?P<code>.*)',path)
    try:
        return m.group('phase')
    except:
        return ''


@register.filter
@stringfilter
def obi_build_task_ini_path(descriptor):
    m = re.search('(?P<year>[0-9]{4})f(?P<phase>[123])i(?P<level>[j12])_(?P<code>.*)',descriptor)
    if m == None:
        return ''
    return "{}/f{}/i{}/{}".format(m.group('year'),m.group('phase'),m.group('level'),m.group('code'))

@register.filter
@stringfilter
def obi_year(path):
    pattern = re.compile('(OBI[0-9]{4})')
    m = pattern.search(path)
    if m == None:
        return ''
    return m.group(0)

@register.filter
@stringfilter
def obi_only_year(path):
    pattern = re.compile('/passadas/OBI([0-9]{4})')
    m = pattern.search(path)
    if m == None:
        return ''
    return m.groups()[0]

@register.filter
@stringfilter
def obi_phase(path):
    pattern = re.compile('(fase[0-9])')
    m = pattern.search(path)
    if m == None:
        return ''
    return m.group(0)

@register.filter
@stringfilter
def obi_phase(path):
    pattern = re.compile('/passadas/OBI[0-9]{4}/(fase[0-9])')
    m = pattern.search(path)
    if m == None:
        return ''
    return m.groups()[0]

@register.filter
@stringfilter
def obi_modality(path):
    pattern = re.compile('/passadas/OBI[0-9]{4}/fase[0-9]/(programacao|iniciacao)')
    m = pattern.search(path)
    if m == None:
        return ''
    return m.groups()[0]

@register.filter
@stringfilter
def obi_start_path_year(path):
    pattern = re.compile('(/passadas/OBI[0-9]{4})')
    m = pattern.search(path)
    if m == None:
        return ''
    return m.group(0)

@register.filter
@stringfilter
def obi_problem_source(path):
    pattern = re.compile('(?P<year>[0-9]{4})f(?P<phase>[0-9])')
    m = pattern.search(path)
    if m == None:
        return 'nada'
    return 'OBI{}, Fase {}'.format(m.group('year'),m.group('phase'))

@register.filter
@stringfilter
def obi_problem_short_name(path):
    s=path.split('/')
    return s[-2]

@register.filter
@stringfilter
def obi_is_index_passadas(path):
    pattern = re.compile('(OBI[0-9]{4})/$')
    m = pattern.search(path)
    if m == None:
        return None
    return m.group(0)


# @register.filter
# @stringfilter
# def obi_problem_form(path):
#     pattern = re.compile('(?P<problem>[0-9]+f[0-9]p.*[^/])')
#     m = pattern.search(path)
#     if m == None:
#         return 'nada'
#     return 'pratique/programacao/submete_solucao?problem={}/'.format(m.group('problem'))

@register.filter
@stringfilter
def obi_problem(path):
    pattern = re.compile('(?P<problem>[0-9]+f[0-9]p.*[^/])')
    m = pattern.search(path)
    if m == None:
        return 'nada'
    return m.group('problem')

@register.filter
@stringfilter
def obi_pratique_years(path):
    if 'nivelj' in path:
        return ['2008','2009','2010','2011','2012','2013','2014','2015','2016','2017']
    elif 'nivel1' in path:
        return ['2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017']
    elif 'nivelu' in path:
        return ['2014','2015','2016','2017']
    else:
        return ['2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017']

@register.filter
@stringfilter
def obi_problem_level(path):
    pattern = re.compile('(?P<level>/pratique/programacao/nivel./)') #(?P<year>[0-9]+)f[0-9]p')
    m = pattern.search(path)
    if m == None:
        return ''
    return m.group('level')

@register.filter
@stringfilter
def obi_problem_level_string(path):
    pattern = re.compile('/pratique/programacao/(?P<level>nivel.)/(?P<year>[0-9]+)f[0-9]p')
    m = pattern.search(path)
    if m == None:
        return ''
    l = m.group('level')
    level_str = {'nivelj':'Nível Júnior','nivel1':'Nível 1','nivel2':'Nível 2','nivelu':'Nível Sênior','nivels':'Seletiva IOI'}
    return level_str[l]


#obi_path_to_name = {'qmerito':'Quadros de Medalhas','passadas':'Anos Anteriores','pratique':'Pratique','programacao':'Modalidade Programação','iniciacao':'Modalidade Iniciação','nivelj':'Nível Júnior','nivel1':'Nível 1','nivel2':'Nível 2','nivelu':'Nível Sênior','nivels':'Seletiva IOI','fase1':'Fase 1','fase2':'Fase 2'}

@register.filter
@stringfilter
def obi_you_are_here_paths(path):
    tmp = path.split('/')
    # first item is '', so start at second
    paths = [('/','Início')]
    if tmp[1] == 'restrito':
        paths = [('/restrito','Coordenação')]
        #paths.append(('/restrito','Coordenação'))
    elif tmp[1] == 'compet':
        paths.append(('/compet','Competidor'))
    page_url='/'
    for i in range(1,len(tmp)-2):
        page_url=page_url+str(tmp[i])+'/'
        try:
            flatpage = FlatPage.objects.get(url=page_url)
            page_name = flatpage.title
        except:
            continue
            #page_name = obi_path_to_name[tmp[i]]
        paths.append((page_url,page_name))
    return paths


@register.filter
@stringfilter
def obi_school_name_from_user(s):
    try:
        sch = School.objects.get(school_deleg_username=s)
        return str(sch)
    except:
        return s

@register.filter
@stringfilter
def obi_format_compet_id(id):
    return format_compet_id(id)

@register.filter
@stringfilter
def obi_format_compet_type_short(id):
    try:
        level = LEVEL_NAME[int(id)]
    except:
        level = f"unknown {id}"
    return level

@register.filter
@stringfilter
def obi_format_compet_type_full(id):
    return LEVEL_NAME_FULL[int(id)]

@register.filter
@stringfilter
def obi_format_school_year_full(id):
    return SCHOOL_YEAR_FULL[id]

@register.filter
@stringfilter
def obi_format_exam_duration(t):
    try:
        t = int(t)
    except:
        return t
    if t % 60 == 0:
        h = t // 60
        if h == 1:
            nt = "1 hora"
        else:
            nt = f"{h} horas"
    else:
        nt = f'{t} minutos'
    return nt

@register.filter
@stringfilter
def obi_uuencode_compet(path):
    import base64
    s = base64.b64encode(bytes(path,encoding='utf-8'))
    return str(s,encoding='ascii')

@register.simple_tag
def get_points_fase2(compet, turn):
    try:
        p = PointsFase2.objects.get(compet=compet)
        if turn=='A':
            points = p.points_a
        else:
            points = p.points_b
    except:
        points = ''
    return points

# to use variables and tags in flatpages
# example of use:
# {{ FLATPAGE.CONTENT|LOAD_STATIC }}
@register.filter
@stringfilter
def load_static(val):
#There's a better way to do this. Must investigate.
#anyways we create template object, and pass it data via context and fill it with render
    tval = Template(val)
    con = Context({'STATIC_URL': settings.STATIC_URL})
    return tval.render(con)

@register.filter
@stringfilter
def load_static_ref(val):
    context = RequestContext(val, {'STATIC_URL':settings.STATIC_URL})
    return context

