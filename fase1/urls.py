from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path
from restrito.views import serve_protected_document_pdf, serve_protected_document_zip

from . import views

app_name = 'fase1'
urlpatterns = [
    path('restrito/compet_lista_classif', views.compet_lista_classif, name='compet_lista_classif'),
    path('prog/restrito/lista_classif', views.compet_lista_classif_prog, name='compet_lista_classif_prog'),
    path('ini/restrito/lista_classif', views.compet_lista_classif_ini, name='compet_lista_classif_ini'),
    #path('restrito/escolhe_turno', views.escolhe_turno_prova, name='escolhe_turno_prova'),
    path('prog/restrito/correcao_prog', views.correcao_prog, name='correcao_prog'),
    path('ini/restrito/correcao_ini', views.correcao_ini, name='correcao_ini'),
    #path('prog/restrito/resultado_prelim_prog', views.resultado_prelim_prog, name='resultado_prelim_prog'),
    path('prog/restrito/resultado_prog', views.resultado_prog, name='resultado_prog'),
    path('ini/restrito/resultado_ini', views.resultado_ini, name='resultado_ini'),
    path('ini/restrito/compet_insere_pontos/<int:compet_id>/<int:compet_points>', views.compet_insere_pontos, name='compet_insere_pontos'),
    path('ini/restrito/compet_insere_pontos/<int:compet_id>/', views.compet_insere_pontos, name='compet_insere_pontos_null'),
    path('ini/restrito/inserepontosini', views.inserepontosini, name='inserepontosini'),
    path('ini/restrito/inserepontosinilote', views.inserepontosinilote, name='inserepontosinilote'),
    path('ini/restrito/inserepontosinilotelate', views.inserepontosinilotelate, name='inserepontosinilotelate'),
    path('ini/restrito/corretorfolhasrespostas', views.corretorfolhasrespostas, name='corretorfolhasrespostas'),
    path('ini/restrito/corretorfolhasrespostaslate', views.corretorfolhasrespostaslate, name='corretorfolhasrespostaslate'),
    path('ini/restrito/cadernos_tarefas', views.cadernos_tarefas_ini, name='cadernos_tarefas_ini'),
    path('ini/restrito/folha_respostas', views.folha_respostas, name='folha_respostas'),
    path('ini/restrito/folhas/<str:level_name>', views.folhas_respostas),
    path('ini/restrito/lista_presenca/<str:level_name>', views.lista_presenca),
    path('ini/restrito/pdf/<str:file>', serve_protected_document_pdf),
    path('ini/restrito/zip/<str:file>', serve_protected_document_zip),
    path('ini/restrito/passo_a_passo', views.passo_a_passo_ini, name='passo_a_passo_ini'),
    path('prog/restrito/cadernos_tarefas', views.cadernos_tarefas_prog, name='cadernos_tarefas_prog'),
    path('prog/restrito/consulta_subm_aceitas', views.consulta_subm_aceitas, name='consulta_subm_aceitas'),
    path('prog/restrito/recupera_subm_aceitas', views.recupera_subm_aceitas, name='recupera_subm_aceitas'),
    path('prog/restrito/lista_presenca/<str:level_name>', views.lista_presenca),
    path('prog/restrito/pdf/<str:file>', serve_protected_document_pdf),
    path('prog/restrito/zip/<str:file>', serve_protected_document_zip),
    path('prog/restrito/passo_a_passo', views.passo_a_passo_prog, name='passo_a_passo_prog'),
    
    path('ini/consulta_res', views.consulta_res_ini, name='consulta_res_ini'),
    path('prog/consulta_res', views.consulta_res_prog, name='consulta_res_prog'),
    path('mostra_res_coord_ini/<int:compet_id>', views.mostra_resultado_coord_ini, name='mostra_resultado_coord_ini'),
    path('mostra_res_compet', views.mostra_resultado_compet_ini, name='mostra_resultado_compet_ini'),
    path('folha_resp/<int:compet_id>', views.serve_folha_resp, name='serve_folha_resp'),
    # path('prog/consulta_subm', views.consulta_subm_prog, name='consulta_subm_prog'),
    # path('prog/recupera_subm', views.recupera_subm_prog, name='recupera_subm_prog'),
    # path('prog/restrito/submete_solucoes', views.submete_solucoes, name='submete_solucoes'),
    # path('consulta_classif', views.consulta_classif, name='consulta_classif'),
    # path('consulta_classif_resp', views.consulta_classif_resp, name='consulta_classif_resp'),
    #path('resultados/iniciacao/mostra_folha_respostas', views.mostra_folha_respostas_fase3, name='mostra_folha_respostas'),
]
