from datetime import date, timedelta

from django import template
from django.db.models import Q


from ..models import CalendarNationalEvent

register = template.Library()

@register.inclusion_tag('cal/entry_snippet.html')
def render_next_cal_entries(num, header_tag=''):
    today=date.today()
    entries = CalendarNationalEvent.objects.filter(~Q(competition__name='Feriado Nacional'),start__gte=today).order_by('start','finish')[:num]
    #print("render", today, num, entries)
    return {
        'entries': entries,
        'header_tag': header_tag,
    }



