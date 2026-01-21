from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_protect

from tasks.models import Alternative, Question, Task

DEFAULT_TEMPLATE = 'tasks/default.html'

# This view is called from FlatpageFallbackMiddleware.process_response
# when a 404 is raised, which often means CsrfViewMiddleware.process_view
# has not been called even if CsrfViewMiddleware is installed. So we need
# to use @csrf_protect, in case the template needs {% csrf_token %}.
# However, we can't just wrap this view; if no matching flatpage exists,
# or a redirect is required for authentication, the 404 needs to be returned
# without any CSRF checks. Therefore, we only
# CSRF protect the internal implementation.


def rendertask(request, descriptor, mod, show_answers):
    """
    Public interface to the flat page view.

    Models: `tasks.tasks`
    Templates: Uses the template defined by the ``template_name`` field,
        or :template:`tasks/default.html` if template_name is not defined.
    Context:
        task
            `tasks.tasks` object
    """
    site_id = get_current_site(request).id
    try:
        t = get_object_or_404(Task, descriptor=descriptor, sites=site_id)
    except Http404:
        raise
    if mod != 'i':
        return render_task(request, t)
    questions = Question.objects.filter(task=t).order_by('num')
    for q in questions:
        alternatives = Alternative.objects.filter(question=q).order_by('num')
        q.alternatives = alternatives
    t.questions = questions
    return render_task(request, t, show_answers=show_answers)


@csrf_protect
def render_task(request, f, show_answers=False):
    """
    Internal interface to the task page view.
    """
    # If registration is required for accessing this page, and the user isn't
    # logged in, redirect to the login page.
    if f.registration_required and not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.path)
#     if f.template_name:
#         template = loader.select_template((f.template_name, DEFAULT_TEMPLATE))
#     else:
#         template = loader.get_template(DEFAULT_TEMPLATE)

    template = loader.get_template(f.template_name)

    # To avoid having to always use the "|safe" filter in task templates,
    # mark the title and content as already safe (since they are raw HTML
    # content in the first place).
    f.title = mark_safe(f.title)
    f.statement = mark_safe(f.statement)
    f.show_answers = show_answers
    context = {'task': f}
    response = HttpResponse(template.render(context, request))
    return response
