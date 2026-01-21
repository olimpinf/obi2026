from django.conf import settings
from django.urls import include, path, re_path

from cal import views

app_name = 'cal'
urlpatterns = [
    #path('calendario', views.calendario, name='calendar'),
    #path('calendario/<str:competition>', views.calendario, name='calendar'),

    path('', views.calendario, name='index'),
    path('obi_completo', views.calendario, name='obi_completo'),
    path('datas_importantes', views.datas_importantes, name='datas_importantes'),
]
