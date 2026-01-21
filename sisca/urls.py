from django.conf import settings
from django.urls import include, path, re_path

from sisca import views

urlpatterns = [
    path('', views.index, name='sisca_index'),
    path('gerador', views.gerador, name='sisca_gerador'),
    path('gerador_gabarito_ini', views.gerador_gabarito_ini, name='sisca_gerador_gabarito_ini'),
    path('gerador_gabarito', views.gerador_gabarito, name='sisca_gerador_gabarito'),
    path('corretor', views.corretor, name='sisca_corretor'),
]
