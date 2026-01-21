from django.db.models import Q
from django.shortcuts import render
from functools import reduce

from .forms import FaqForm
from .models import Item

OMIT = ('de', 'da', 'do', 'para', 'ou','e', 'com', 'por')
        
def index(request):
    queryset = {}
    
    if request.method == 'POST':
        form = FaqForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            queryset = Item.objects.filter(topic__id__in=f['topics'])
            if not request.user.is_authenticated:
                queryset.exclude(topic__name_short='coordenadores')
            tmp = f['filter'].replace(',',' ').split(' ')
            terms = set()
            for t in tmp:
                if len(t)<=1 and not t.isdigit(): continue
                if t in OMIT: continue
                terms.add(t)
            if terms:
                queryset = queryset.filter(reduce(lambda x, y: x | y , [Q(question__icontains=t) | Q(answer__icontains=t) for t in terms]),active=True).order_by('topic__order','order')
            else:
                queryset = queryset.filter(active=True).order_by('topic__order','order')
            return render(request, 'faq/index.html', {'queryset': queryset, 'form': form})
    else:
        form = FaqForm()
        queryset = Item.objects.filter(active=True).order_by('topic__order','order')
        if not request.user.is_authenticated:
            queryset.exclude(topic__name_short='coordenadores')
    return render(request, 'faq/index.html', {'queryset': queryset, 'form': form})
