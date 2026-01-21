from django import template
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.defaultfilters import stringfilter

from tasks.models import Task

register = template.Library()


class TaskNode(template.Node):
    def __init__(self, context_name, year, phase, level):
        self.context_name = context_name
        self.year = template.Variable(year)
        self.phase = template.Variable(phase)
        self.level = template.Variable(level)
        self.user = None # todo

    def render(self, context):
        if 'request' in context:
            site_pk = get_current_site(context['request']).pk
        else:
            site_pk = settings.SITE_ID
        tasks = Task.objects.filter(sites__id=site_pk)
        #tasks = tasks.filter(
        #        descriptor__startswith=self.starts_with.resolve(context))
        #tasks = tasks.filter(year=self.year.resolve(context),phase=self.phase.resolve(context),modstr=self.modstr.resolve(context),levelstr=self.levelstr.resolve(context)).order_by('title')
        tasks = tasks.filter(year=self.year.resolve(context),phase=self.phase.resolve(context),level=self.level.resolve(context)).order_by('title')
        # If the provided user is not authenticated, or no user
        # was provided, filter the list to only public flatpages.
        if self.user:
            user = self.user.resolve(context)
            if not user.is_authenticated:
                tasks = tasks.filter(registration_required=False)
        else:
            tasks = tasks.filter(registration_required=False)

        context[self.context_name] = tasks
        return ''


@register.filter
@stringfilter
def get_task_short_name(descriptor):
    tmp = descriptor.split('_')
    return tmp[-1]

@register.tag
def get_tasks(parser, token):
    """
    Retrieve all task objects available for the current site and
    visible to the specific user (or visible to all users if no user is
    specified). Populate the template context with them in a variable
    whose name is defined by the ``as`` clause.

    Syntax::

        {% get_tasks year phase level as context_name %}

    """
    bits = token.split_contents()
    syntax_message = ("%(tag_name)s expects a syntax of %(tag_name)s "
                      "year phase level as context_name" %
                      {'tag_name': bits[0]})
    # Must have 6 bits in the tag
    if len(bits) == 6:
        year = bits[1]
        phase = bits[2]
        level = bits[3]
        if bits[-2] != 'as':
            raise template.TemplateSyntaxError(syntax_message)
        context_name = bits[-1]
        return TaskNode(context_name, year=year, phase=phase, level=level)
    else:
        raise template.TemplateSyntaxError(syntax_message)

#########
# menu
#########

class MenuNode(template.Node):
    def __init__(self, context_name, level):
        self.context_name = context_name
        self.level = template.Variable(level)

    def render(self, context):
        if 'request' in context:
            site_pk = get_current_site(context['request']).pk
        else:
            site_pk = settings.SITE_ID
        tasks = Task.objects.filter(sites__id=site_pk)
        tasks = tasks.filter(level=self.level.resolve(context)).values('year','phase').distinct().order_by('-year','phase')
        menu = []
        first = True
        for t in tasks:
            if first:
                first = False
                item = {'year': t['year'],'phases':[t['phase']]}
            else:
                if t['year'] != item['year']:
                    menu.append(item)
                    item = {'year': t['year'],'phases':[t['phase']]}
                else:
                    item['phases'].append(t['phase'])
        menu.append(item)
        context[self.context_name] = menu
        return ''

@register.tag
def get_task_menu(parser, token):
    """
    Retrieve all years/phases there are tasks for current site and modality.
    Populate the template context with them in a variable
    whose name is defined by the ``as`` clause.

    Syntax:

        {% get_task_menu level as context_name %}

    """
    bits = token.split_contents()
    syntax_message = ("%(tag_name)s expects a syntax of "
                      "%(tag_name)s level as context_name" %
                      {'tag_name': bits[0]})
    # Must have 4 bits in the tag
    if len(bits) == 4:
        level = bits[1]
        if bits[-2] != 'as':
            raise template.TemplateSyntaxError(syntax_message)
        context_name = bits[-1]
        return MenuNode(context_name, level=level)
    else:
        raise template.TemplateSyntaxError(syntax_message)
