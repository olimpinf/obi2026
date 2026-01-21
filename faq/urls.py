from django.conf import settings
from django.urls import include, path, re_path

from faq import views

app_name = "faq"
urlpatterns = [
    path('', views.index, name='index'),
]
