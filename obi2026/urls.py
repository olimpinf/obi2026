"""
URL configuration for obi2026 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.conf.urls import handler404, handler500

#handler400 = 'principal.views.handler400'
#handler403 = 'principal.views.handler403'
#handler404 = 'principal.views.handler404'
#handler500 = 'principal.views.handler500'

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('tobi/', include('tobi.urls')),
    path('impersonate/', include('impersonate.urls')),
    path('pratique/', include('pratique.urls')),
    #path('faq/', include('faq.urls', namespace='faq'), name='perguntas_frequentes'),
    path('', include('principal.urls')),
    path('contas/', include('django.contrib.auth.urls')),
    path('gerencia/', include('gerencia.urls')),
    path('restrito/', include('restrito.urls')),
    path('compet/', include('compet.urls')),
    path('prova/', include('exams.urls')),
    path('noticias/', include('blog.urls', namespace='weblog'), name='noticias'),
    path('fase0/', include('fase0.urls', namespace='fase0')),
    path('fase1/', include('fase1.urls', namespace='fase1')),
    path('fase2/', include('fase2.urls', namespace='fase2')),
    path('fase2b/', include('fase2b.urls', namespace='fase2b')),
    path('fase3/', include('fase3.urls', namespace='fase3')),
    path('semana/', include('week.urls')),
    #path('galeria/', include('gallery.urls')),
    path('calendario/', include('cal.urls')),
    path('saci/', include('saci.urls')),
    path('captcha/', include('captcha.urls')),

    path('restrito/noticias/', include('blog_restrito.urls', namespace='blog_restrito'), name='noticias_restrito'),

    path('cfobi/', include('cfobi.urls')),
    #path('editor/', include('editor.urls')),
    #path('api/', include('api.urls')),
    path('inep/', include('inep.urls')),

]

from django.contrib.flatpages import views

# flatpages
urlpatterns += [
    #path('pratique/', views.flatpage, {'url': 'pratique/'}, name='pratique'),
    #path('pratique/<path:url>', views.flatpage),
    #path('pratique2/', views.flatpage, {'url': 'pratique2/'}, name='pratique2'),
    #path('pratique2/<path:url>', views.flatpage),
    path('info/', views.flatpage, {'url': 'info/'}, name='apresenta'),
    path('info/apoios/', views.flatpage, {'url': 'info/apoios/'}, name='apoios'),
    path('info/competicao_feminina/', views.flatpage, {'url': 'info/competicao_feminina/'}, name='competicao_feminina'),
    path('info/como_participar_escola/', views.flatpage, {'url': 'info/como_participar_escola/'}, name='como_participar_escola'),
    path('info/como_participar_aluno/', views.flatpage, {'url': 'info/como_participar_aluno/'}, name='como_participar_aluno'),
    path('info/contato/', views.flatpage, {'url': 'info/contato/'}, name='contato'),
    path('info/comite/', views.flatpage, {'url': 'info/comite/'}, name='comite'),
    path('info/instrucoes_cadastro/', views.flatpage, {'url': 'info/instrucoes_cadastro/'}, name='instrucoes_cadastro'),
    path('info/regulamento/', views.flatpage, {'url': 'info/regulamento/'}, name='regulamento'),
    path('info/privacidade/', views.flatpage, {'url': 'info/privacidade/'}, name='privacidade'),
    path('info/cartaz/', views.flatpage, {'url': 'info/cartaz/'}, name='cartaz'),
    path('info/calendario/', views.flatpage, {'url': 'info/calendario/'}, name='calendario'),
    path('info/quem_pode_participar/', views.flatpage, {'url': 'info/quem_pode_participar/'}, name='quem_pode_participar'),
    path('info/obs/', views.flatpage, {'url': 'info/obs/'}, name='obs'),
    path('info/ambiente_prova/', views.flatpage, {'url': 'info/ambiente_prova/'}, name='ambiente_prova'),

    path('info/servicos/', views.flatpage, {'url': 'info/servicos/'}, name='servicos'),
    path('info/beneficios/', views.flatpage, {'url': 'info/beneficios/'}, name='beneficios'),
    path('info/<path:url>', views.flatpage),
    path('competicoes/', views.flatpage, {'url': 'competicoes/'}, name='competicoes'),
    path('passadas/', views.flatpage, {'url': 'passadas/'}, name='passadas'),
    path('passadas/<path:url>', views.flatpage),

    path('resultados/', views.flatpage, {'url': 'resultados/'}, name='resultados'),

    path('prepare/', views.flatpage, {'url': 'prepare/'}, name='prepare'),
    path('prepare/aplicativos/', views.flatpage, {'url': 'prepare/aplicativos/'}, name='aplicativos'),
    path('prepare/ementas/', views.flatpage, {'url': 'prepare/ementas/'}, name='ementas'),
    path('prepare/estude/', views.flatpage, {'url': 'prepare/estude/'}, name='estude'),

]

