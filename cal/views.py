import copy
import calendar
import locale
import random
from datetime import date, timedelta
from io import StringIO

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.contrib import messages

from obi.settings import YEAR

from .models import CalendarCompetition, CalendarEvent
from .models import CalendarNationalCompetition, CalendarNationalEvent
from .forms import CalendarForm, FilterForm

def test(request):
    return render(request, 'cal/test.html', {})

def daterange(start_date, finish_date):
    for n in range(1 + int ((finish_date - start_date).days)):
        yield start_date + timedelta(n)

def show_test_days(request):
    return render(request, 'cal/test.html', {})
    
def find_event(day, events):
    found= []
    for e in events:
        finish_date = e.finish
        start_date = e.start
        for single_date in daterange(start_date, finish_date):
            if day == single_date.strftime("%d_%m_%Y"):
                #print("found",e.name,e.competition.name)
                found.append(e)
    if len(found) > 1:
        # conflict
        if len(found) > 2:
            color = 'black-bkgd'
        else:
            holyday = False
            for f in found:
                if f.competition.name == 'Feriado':
                    holyday = True
            if not holyday:
                color = 'black-bkgd'
            else:
                if found[0].competition.name == 'Feriado':
                    color = found[0].competition.color
                else:
                    color = found[1].competition.color
    else:
        # if found[0].emph:
        #     color = found[0].competition.color_emph
        # else:
        #     color = found[0].competition.color
        color = found[0].competition.color
    text,name_abbrev = '',''
    test_day = False
    for f in found:
        #text += "{}: {}<br />".format(f.competition.name_abbrev,f.name)
        text += "{}: {}<br />".format(f.competition.name,f.name)
        name_abbrev = f.competition.name_abbrev
        test_day |= f.test_day
    return color, text, name_abbrev, test_day

def index(request):
    return render(request, 'cal/index.html', {})


def calendario(request, competition=""):

    year = YEAR
    
    #competitions = CalendarNationalCompetition.objects.filter(show=True).exclude(name='Feriado Nacional').order_by('name')
    competitions = CalendarNationalCompetition.objects.filter(show=True).order_by('order')
    if competition != "":
        competitions.filter(name_abbrev=competition)
    
    form, competition_list, not_checked, alert_message, as_calendar = process_form(request, competitions, competition)

    if request.user.is_authenticated:
        events = CalendarNationalEvent.objects.filter(year=year)
    else:
        if competition != "":
            events = CalendarNationalEvent.objects.filter(show=True,competition=competition,year=year)
        else:
            events = CalendarNationalEvent.objects.filter(show=True,year=year)
            
    for excluded in not_checked:
        events = events.exclude(competition__name_abbrev = excluded)

    all_events = events

    print("events",events)
    
    js = StringIO()
    print("<script>var year = {};".format(year),file=js)
    thecalendar = 'calendario'
    print("var thecalendar = '{}';".format(thecalendar),file=js)
    # all events for the popup when there is conflict
    cal_events = {}
    day_with_event = set()
    for e in all_events:
        if e.competition not in competitions:
            continue
        finish_date = e.finish # timezone.localtime(e.finish)
        start_date = e.start   # timezone.localtime(e.start)
        for single_date in daterange(start_date, finish_date):
            day_with_event.add(single_date.strftime("%d_%m_%Y"))
            if single_date.strftime("%d_%m_%Y") not in cal_events.keys():
                cal_events[single_date.strftime("%d_%m_%Y")] = {}
            if e.competition.name_abbrev not in cal_events[single_date.strftime("%d_%m_%Y")]:
                cal_events[single_date.strftime("%d_%m_%Y")][e.competition.name_abbrev] = []
            if e.comment:
                comment = e.comment
            else:
                comment = ""
            link = competitions.filter(name=e.competition.name)
            if len(link) == 0:
                link = ''
            elif competitions.filter(name=e.competition.name)[0].link:
                link = competitions.filter(name=e.competition.name)[0].link
            else:
                link = ''
            cal_events[single_date.strftime("%d_%m_%Y")][e.competition.name_abbrev].append({"competition_name":e.competition.name,"name":e.name,"date":single_date.strftime("%d_%m_%Y"),"weekday":single_date.strftime("%w"),"start_hour":start_date.strftime("%H"),"start_minute":start_date.strftime("%M"),"finish_hour":finish_date.strftime("%H"),"finish_minute":finish_date.strftime("%M"),"comment": comment, "link":link})
    print('var cal_events =', cal_events, file=js)

    # visible events - must be after all events, because day_with_event is used after

    day_with_event = set()
    for e in events:
        if e.competition not in competitions:
            continue

        finish_date = e.finish
        start_date = e.start
        for single_date in daterange(start_date, finish_date):
            day_with_event.add(single_date.strftime("%d_%m_%Y"))

    print("</script>",file=js)

    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    html = StringIO()
    weekheader = calendar.weekheader(3)
    month_name = calendar.month_name
    #calendar.setfirstweekday(calendar.SUNDAY)
    #cal = calendar.Calendar(firstweekday=6)
    cal = calendar.Calendar()
    print('<div id="div_calendar">',file=html,end='')
    print('<div class="cal-year">',file=html,end='')
    print('<div class="cal-year-grid">',file=html,end='')
    for m in range(1,13):
        print('<div class="cal-month">',file=html,end='')
        print('<div class="cal-month-name">{}</div>'.format(month_name[m]),file=html,end='')
        print('<div class="cal-month-grid">',file=html,end='')
        order = 0
        for w in weekheader.split():
            print('<div class="cal-day of-week">{}</div>'.format(w),file=html,end='')
            order += 1
        for i in cal.itermonthdays(year, m):
            if i==0:
                val = "&nbsp;"
                print('<div class="cal-day">{}</div>'.format(val),file=html,end='')
            else:
                val = i
                day = "{:02d}_{:02d}_{}".format(i,m,year)
                if day in day_with_event:
                    # find color
                    color,name,name_abbrev,test_day = find_event(day,all_events)
                    if test_day:                        
                        print(f'<div name="event" id="{name_abbrev}_show" class="cal-day {color} cal-order-{order} cal-tooltip">{val}<span class="cal-tooltiptext">{name}</span></div>',file=html,end='')
                        print(f'<div name="event"  id="{name_abbrev}_hide" style="display:none" class="cal-day">{val}</div>',file=html,end='')
                    else:
                        print(f'<div name="event" id="{name_abbrev}_on" class="cal-day {color} cal-order-{order} cal-tooltip">{val}<span class="cal-tooltiptext">{name}</span></div>',file=html,end='')
                        print(f'<div name="event"  id="{name_abbrev}_off" style="display:none" class="cal-day">{val}</div>',file=html,end='')
                        
                else:
                    print('<div class="cal-day">{}</div>'.format(val),file=html,end='')
            order += 1
        while order <= 48:
            print('<div class="cal-day blank">&nbsp;</div>',file=html,end='')
            order += 1

        print('</div><!-- cal-month-grid -->',file=html,end='')
        print('</div><!-- cal-month -->',file=html,end='')
    print('</div><!-- cal-year-grid -->',file=html,end='')
    print('</div><!-- cal-year -->',file=html,end='')
    print('</div><!-- div_calendar -->',file=html)
            
    print(file=html)
    print(js.getvalue(),file=html)

    ##########
    # as list

    # split events in start and finish if appropriate
    split_events = []
    for e in events:
        if e.competition not in competitions:
            continue
        # if (('prog' in checked) and (str(e.competition) == 'Modalidade Programação')) or \
        #    (('ini' in checked) and str(e.competition) == 'Modalidade Iniciação') or \
        #    str(e.competition) == 'Torneio Feminino de Computação' or \
        #    str(e.competition) == 'Geral':
        if e.start.day == e.finish.day:
            e.sort_date = e.start
            split_events.append(e)
        else:
            tmp = copy.deepcopy(e)
            e.finish = None
            e.sort_date = e.start
            split_events.append(e)
            tmp.start = None
            tmp.sort_date = tmp.finish
            split_events.append(tmp)
    split_events.sort(key=lambda x: x.sort_date)
    the_list = split_events
    
    return render(request, 'cal/calendario.html', {'form': form , 'the_list': the_list, 'the_calendar': html.getvalue(), 'year': year, 'competition_list':competition_list, 'html':html.getvalue(), 'alert_message': alert_message, 'as_calendar': 'as_calendar'})

def process_form(request, competitions, the_competition):

    checked = []
    not_checked = []
    filterInput = ''
    as_calendar = True
    if request.method == 'POST':
        if 'removeFilter' in request.POST:
            filterInput = ""
            request.session['filterInput']=""
        form = FilterForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            if 'as_list' in f['calendar_list']:
                as_calendar = False
            #else:
            #    print("as_calendar")
                
            # if 'removeFilter' in request.POST:
            #     filterInput = ""
            #     data = {'filterInput': filterInput}
            #     form = FilterForm(initial=data)
            # else:
            #     pass
            #     #filterInput = f['filterInput']

            checked = form.cleaned_data['filterInput']

            # request.session['filterInput']=filterInput
            # filterInput = filterInput.lower()
            # if filterInput:
            #     for competition in competitions:
            #         if competition.name.lower().find(filterInput) >= 0:
            #             checked.append(competition.name_abbrev)
            #         else:
            #             not_checked.append(competition.name_abbrev)
            # else:
            #     checked = [competition.name_abbrev for competition in competitions]
        else:
            print("form.errors",form.errors)
            #messages.error(request, form.errors)
    else:
        form = FilterForm()
        if the_competition != "":
            checked = [the_competition]
        else:
            checked = [competition.name_abbrev for competition in competitions]
        # if 'filterInput' in request.session.keys():
        #     filterInput = request.session['filterInput']
        #     for competition in competitions:
        #         if competition.name.lower().find(filterInput) >= 0:
        #             checked.append(competition.name_abbrev)
        #         else:
        #             not_checked.append(competition.name_abbrev)
        # else:
        #     checked = [competition.name_abbrev for competition in competitions]
        #     filterInput = ''
        # data = {'filterInput': filterInput}
        # form = FilterForm(initial=data)
        
    alert_message = ""
    if len(checked) == 0:
        #messages.error(request, "Escolha ao menos uma competição")
        alert_message = "Escolha ao menos uma competição"
    
    for competition in competitions:
        if competition.name_abbrev not in checked:
            not_checked.append(competition.name_abbrev)

    #the_list = ''
    competition_list = '<div id="div_competition_list">'
    i = 0
    
    for competition in competitions:
        if competition.name_abbrev in checked:
            display = ""
            is_checked = "checked"
        else:
            display = "none"
            is_checked = ""


        # the_list +=  f'<li style="list-style-type: none; display:{display}"><input type="checkbox" name="topics" value="{competition.name_abbrev}</div><div style="margin-bottom: 3px"><span class="{competition.color}" style="width:20px;height:20px;vertical-align:middle;text-align:center;display:inline-block">&nbsp;</span>&nbsp;<a href="{competition.link}" target="_blank">{competition.name}</a></label></li>'
        competition_list += f'<div style="margin-bottom: 3px; text-indent: -45px; padding-left: 45px;"><input type="checkbox" name="filterInput" value="{competition.name_abbrev}" id="{competition.name_abbrev}" {is_checked} onchange="showCompetition({competition.name_abbrev})">&nbsp;<span class="{competition.color}" style="width:20px;height:20px;vertical-align:middle;text-align:center;display:inline-block"></span>&nbsp; '
        if competition.link != None:            
            competition_list += f'{competition.name_abbrev} - <a href="{competition.link}">{competition.name}</a>'
        else:
            competition_list += f'{competition.name}'
        competition_list += '</div>\n\n'

        i += 1
            
    competition_list += '</div>\n'

    
    return form, competition_list, not_checked, alert_message, as_calendar


def datas_importantes(request):
    return render(request, 'cal/datas_importantes.html', {})
