from django.urls import path
from restrito.views import serve_protected_document_pdf, serve_protected_document_zip

from . import views

app_name = 'fase3'
urlpatterns = [
    #path('restrito/escolhe_turno', views.escolhe_turno_prova, name='escolhe_turno_prova'),
    #path('prog/restrito/correcao_prog', views.correcao_prog, name='correcao_prog'),
    path('ini/restrito/correcao_ini', views.correcao_ini, name='correcao_ini'),
    path('ini/restrito/status', views.compet_show_status_ini, name='compet_show_status_ini'),
    path('ini/restrito/corretorfolhasrespostas', views.corretorfolhasrespostas, name='corretorfolhasrespostas'),
    path('ini/restrito/corretorfolhasrespostas_admin/<int:school_id>', views.corretorfolhasrespostas_admin, name='corretorfolhasrespostas_admin'),
    path('ini/restrito/cadernos_tarefas', views.cadernos_tarefas_ini, name='cadernos_tarefas_ini'),
    path('ini/restrito/folha_respostas/<str:level_name>', views.folha_respostas, name='folha_respostas'),
    path('ini/restrito/folhas/<str:level_name>', views.folhas_respostas),
    path('ini/restrito/lista_presenca/<str:level_name>', views.lista_presenca),
    path('ini/restrito/pdf/<str:file>', serve_protected_document_pdf),
    path('ini/restrito/zip/<str:file>', serve_protected_document_zip),
    path('ini/restrito/verifica_ini', views.verifica_ini, name='verifica_ini'),
    path('prog/restrito/cadernos_tarefas', views.cadernos_tarefas_prog, name='cadernos_tarefas_prog'),
    path('prog/restrito/correcao_prog', views.correcao_prog, name='correcao_prog'),
    path('prog/restrito/lista_presenca/<str:level_name>', views.lista_presenca),
    path('prog/restrito/pdf/<str:file>', serve_protected_document_pdf),
    path('prog/restrito/zip/<str:file>', serve_protected_document_zip),

    path('prog/restrito/resultado_prog', views.resultado_prog, name='resultado_prog'),
    path('ini/restrito/resultado_ini', views.resultado_ini, name='resultado_ini'),
    path('ini/consulta_res', views.consulta_res_ini, name='consulta_res_ini'),
    path('prog/consulta_res', views.consulta_res_prog, name='consulta_res_prog'),

    path('mostra_sede_fase3/<int:id>', views.mostra_sede_fase3, name='mostra_sede_fase3'),
    path('mostra_sede_fase3_coord/<str:mod>', views.mostra_sede_fase3_coord, name='mostra_sede_fase3_coord'),

    path('compet_lista_prog', views.compet_lista_prog, name='compet_lista_prog'),
    path('compet_lista_ini', views.compet_lista_ini, name='compet_lista_ini'),
    path('compet_lista/<str:mod>', views.compet_lista, name='compet_lista'),

    # path('mapa_sedes/<str:map_type>', views.mapa_sedes, name='mapa_sedes'),
    path('consulta_sua_sede', views.consulta_sua_sede, name='consulta_sua_sede'),
    path('consulta_sedes', views.consulta_sedes, name='consulta_sedes'),
    path('mostra_res_ini', views.mostra_resultado_compet_ini, name='mostra_resultado_compet_ini'),
    path('mostra_res_coord_ini/<int:compet_id>', views.mostra_resultado_coord_ini, name='mostra_resultado_coord_ini'),
    path('folha_resp/<int:compet_id>', views.serve_folha_resp, name='serve_folha_resp'),
    # path('school_has_compet_classif/<str:mod>', views.school_has_compet_classif, name='school_has_compet_classif'),
    # path('resultados/iniciacao/consulta_res_ini', views.consulta_res_ini, name='consulta_res_ini'),
    # path('resultados/iniciacao/mostra_folha_respostas', views.mostra_folha_respostas, name='mostra_folha_respostas'),
    # path('resultados/programacao/consulta_res_prog', views.consulta_res_prog, name='consulta_res_prog'),
    # path('resultados/programacao/consulta_subm_prog', views.consulta_subm_prog, name='consulta_subm_prog'),
    # path('resultados/programacao/recupera_subm_prog', views.recupera_subm_prog, name='recupera_subm_prog'),
    path('restrito/consulta_pref_fase3_ini', views.consulta_pref_fase3_ini, name='consulta_pref_fase3_ini'),
    path('restrito/consulta_pref_fase3_prog', views.consulta_pref_fase3_prog, name='consulta_pref_fase3_prog'),
    path('restrito/compet_recupera_cadastro/<str:mod>', views.compet_recupera_cadastro, name='compet_recupera_cadastro'),

]
