import logging
from django import template

from ..models import Entry

register = template.Library()
logger = logging.getLogger('gerencia')


@register.inclusion_tag('blog_restrito/entry_snippet.html')
def render_latest_blog_entries(num, summary_first=False, hide_readmore=False, header_tag=''):
    entries = Entry.objects.all()
    entries = entries.published()[:num]
    #logger.info('render_latest_blog_entries {}'.format(entries))
    return {
        'entries': entries,
        'summary_first': summary_first,
        'header_tag': header_tag,
        'hide_readmore': hide_readmore,
    }


@register.inclusion_tag('blog_restrito/month_links_snippet.html')
def render_month_links():
    entries = Entry.objects.all()
    entries = entries.published().dates('pub_date', 'month', order='DESC')
    #logger.info('render_month_links {}'.format(entries))
    return {
        'dates': entries,
    }
