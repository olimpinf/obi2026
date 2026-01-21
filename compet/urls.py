from django.conf import settings
from django.urls import include, path, re_path

from . import views

app_name = 'compet'
urlpatterns = [
    path('', views.index, name='index'),
    path('certificado_semana', views.emite_certificado_semana, name='certificado_semana'),
    path('compet_sede_fase3', views.compet_sede_fase3, name='compet_sede_fase3'),
    path('emite_carta', views.emite_carta, name='emite_carta'),
    path('emite_carta_treinamento', views.emite_carta_treinamento, name='emite_carta_treinamento'),
    path('get_exam_ua', views.get_exam_ua, name='get_exam_ua'),
]
