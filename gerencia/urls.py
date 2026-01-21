from django.conf import settings
from django.urls import include, path, re_path

from gerencia import views

urlpatterns = [
    path('', views.index, name='gerencia_index'),
    path('envia_convite_recupera', views.envia_convite_recupera, name='gerencia_envia_convite_recupera'),
    path('envia_mensagem', views.envia_mensagem, name='gerencia_envia_mensagem'),
    path('test', views.test, name='test'),
]
