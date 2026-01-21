from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path
from restrito.views import serve_protected_document_pdf, serve_protected_document_zip

from . import views

app_name = 'fase0'
urlpatterns = [
    # path('ini/restrito/cadernos_tarefas', views.cadernos_tarefas_ini, name='cadernos_tarefas_ini'),
    # path('ini/restrito/folha_respostas', views.folha_respostas, name='folha_respostas'),
    # path('ini/restrito/folhas/<str:level_name>', views.folhas_respostas),
    # path('ini/restrito/lista_presenca/<str:level_name>', views.lista_presenca),
    # path('ini/restrito/passo_a_passo', views.passo_a_passo_ini, name='passo_a_passo_ini'),
    # path('ini/restrito/pdf/<str:file>', serve_protected_document_pdf),
    path('prog/restrito/cadernos_tarefas', views.cadernos_tarefas_prog, name='cadernos_tarefas_prog'),
    path('prog/restrito/passo_a_passo', views.passo_a_passo_prog, name='passo_a_passo_prog'),
    path('prog/restrito/lista_presenca/<str:level_name>', views.lista_presenca),
    # path('prog/restrito/pdf/<str:file>', serve_protected_document_pdf),
    path('prog/restrito/zip/<str:file>', serve_protected_document_zip),

    # path('prog/consulta_subm', views.consulta_subm_prog, name='consulta_subm_prog'),
    # path('prog/recupera_subm', views.recupera_subm_prog, name='recupera_subm_prog'),
    # path('prog/restrito/submete_solucoes', views.submete_solucoes, name='submete_solucoes'),
    # path('consulta_classif', views.consulta_classif, name='consulta_classif'),
    # path('consulta_classif_resp', views.consulta_classif_resp, name='consulta_classif_resp'),
    #path('resultados/iniciacao/mostra_folha_respostas', views.mostra_folha_respostas_fase3, name='mostra_folha_respostas'),
]
