from django.views.decorators.cache import cache_page
from django.urls import re_path

from . import views

app_name = "weblog"
urlpatterns = [
    re_path(
        '(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)/',
        cache_page(60 * 60 * 2)(views.BlogDateDetailView.as_view()),
        name="entry"
    ),
    re_path(
        '(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/',
        cache_page(60 * 60 * 2)(views.BlogDayArchiveView.as_view()),
        name="archive-day"
    ),
    re_path(
        '(?P<year>\d{4})/(?P<month>\d{2})/',
        cache_page(60 * 60 * 2)(views.BlogMonthArchiveView.as_view()),
        name="archive-month"
    ),
    re_path(
        '(?P<year>\d{4})/',
        cache_page(60 * 60 * 2)(views.BlogYearArchiveView.as_view()),
        name="archive-year"
    ),
    re_path(
        '',
        cache_page(60 * 60 * 2)(views.BlogArchiveIndexView.as_view()),
        name="index"
    ),
]
