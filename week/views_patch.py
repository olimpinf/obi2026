from django.shortcuts import render

from .models import Week


# Create your views here.
def index(request):
    #logger.debug("this is a debug message!")
    return render(request, 'week/index.html', {})

def invited(request):
    return render(request, 'week/convidados.html', {})

def monitors(request):
    return render(request, 'week/monitores.html', {})

def instructors(request):
    return render(request, 'week/professores.html', {})

def documents(request):
    return render(request, 'week/forms_e_docs.html', {})

def agenda(request):
    return render(request, 'week/agenda.html', {})

def participants(request):
    qs_i1 = Week.objects.filter(compet__compet_type=1).order_by('compet__compet_name')
    qs_i2 = Week.objects.filter(compet__compet_type=2).order_by('compet__compet_name')
    qs_pj = Week.objects.filter(compet__compet_type=5).order_by('compet__compet_name')
    qs_p1 = Week.objects.filter(compet__compet_type=3).order_by('compet__compet_name')
    qs_p2 = Week.objects.filter(compet__compet_type=4).order_by('compet__compet_name')
    #for i in qs_i1:
    #    print(i.compet.compet_name)
    #    print(i.form)
    qs_ap = Week.objects.filter(colab__colab_id__gt=0,paid=True).order_by('colab__colab_name') | \
        Week.objects.filter(chaperone__chaperone_id__gt=0,paid=True).order_by('chaperone__chaperone_name')
    qs_an = Week.objects.filter(colab__colab_id__gt=0,paid=False).order_by('colab__colab_name') | \
        Week.objects.filter(chaperone__chaperone_id__gt=0,paid=False).order_by('chaperone__chaperone_name')
    context = {
        'invited': (
            {'level':'Iniciação 1','participants':qs_i1},
            {'level':'Iniciação 2','participants':qs_i2},
            {'level':'Programação Júnior','participants':qs_pj},
            {'level':'Programação 1','participants':qs_p1},
            {'level':'Programação 2','participants':qs_p2},
            {'level':'Acompanhantes Pagantes','participants':qs_ap},
            {'level':'Acompanhantes não Pagantes','participants':qs_an},
            ),
        }
    return render(request, 'week/participantes.html', context)

def arrivals(request):
    qs_airport = Week.objects.filter(arrival_place='Aeroporto').order_by('arrival_time')
    qs_bus_station = Week.objects.filter(arrival_place='Rodoviária').order_by('arrival_time')
    qs_hotel = Week.objects.filter(arrival_place='Hotel').order_by('arrival_time')
    qs_no_info = Week.objects.filter(arrival_place=None).order_by('compet__compet_name')
    context = {
        'airport': (
            {'participants':qs_airport},
            ),
        'bus_station': (
            {'participants':qs_bus_station},
            ),
        'hotel': (
            {'participants':qs_hotel},
            ),
        'no_info': (
            {'participants':qs_no_info},
            ),
        }
    return render(request, 'week/arrivals.html', context)

def departures(request):
    qs_airport = Week.objects.filter(departure_place='Aeroporto').order_by('departure_time')
    qs_bus_station = Week.objects.filter(departure_place='Rodoviária').order_by('departure_time')
    qs_hotel = Week.objects.filter(departure_place='Hotel').order_by('compet__compet_name')
    qs_no_info = Week.objects.filter(departure_place=None).order_by('compet__compet_name')
    context = {
        'airport': (
            {'participants':qs_airport},
            ),
        'bus_station': (
            {'participants':qs_bus_station},
            ),
        'hotel': (
            {'participants':qs_hotel},
            ),
        'no_info': (
            {'participants':qs_no_info},
            ),
        }
    return render(request, 'week/departures.html', context)
