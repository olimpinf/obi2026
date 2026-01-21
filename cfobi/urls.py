from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path
from restrito.views import serve_protected_document_pdf, serve_protected_document_zip

from . import views

app_name = 'cfobi'
urlpatterns = [
    path('restrito/compet_lista_desclassif', views.compet_lista_desclassif, name='compet_lista_desclassif'),
    path('restrito/compet_lista_classif', views.compet_lista_classif, name='compet_lista_classif'),
    path('cfobi/restrito/lista_classif', views.compet_lista_classif_prog, name='compet_lista_classif_prog'),
    #path('restrito/escolhe_turno', views.escolhe_turno_prova, name='escolhe_turno_prova'),
    path('cfobi/restrito/resultado_prog', views.resultado_prog, name='resultado_prog'),
    path('cfobi/restrito/correcao_prog', views.correcao_prog, name='correcao_prog'),

    path('cfobi/restrito/cadernos_tarefas_prog', views.cadernos_tarefas_prog, name='cadernos_tarefas_prog'),
    path('cfobi/restrito/lista_presenca/<str:level_name>', views.lista_presenca),
    path('cfobi/restrito/pdf/<str:file>', serve_protected_document_pdf),
    path('cfobi/restrito/zip/<str:file>', serve_protected_document_zip),
    path('cfobi/restrito/passo_a_passo', views.passo_a_passo_prog, name='passo_a_passo_prog'),

]
