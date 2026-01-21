from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path

from . import views
from week import views as views_dummy

app_name = 'principal'
urlpatterns = [
    path('', views.index, name='index'),
    path('ambiente_prova', views.ambiente_prova, name='ambiente_prova'),
    path('testa_correcao', views.testa_correcao, name='testa_correcao'),
    path('password_reset', views.password_reset, name='password_reset'),
    path('password_reset_compet', views.password_reset_compet, name='password_reset_compet'),
    path('password_reset_coord', views.password_reset_coord, name='password_reset_coord'),
    path('password_reset_colab', views.password_reset_other, name='password_reset_other'),
    path('redefine_senha/<str:hash>', views.redefine_senha, name='redefine_senha'),
    #path('erro/<str:msg>', views.erro, name='erro'),
    path('relata_erro/<str:page>', views.relata_erro, name='relata_erro'),

    #path('resultados/semana/info_semana', views_dummy.index),
    #path('resultados/semana/convidados_semana/', views_dummy.invited),
    path('acesso_escolas', views.acesso_escolas, name='acesso_escolas'),
    path('confirma_email', views.confirma_email, name='confirma_email'),
    path('cadastra_escola/<str:hash>', views.cadastra_escola, name='cadastra_escola'),
    path('cadastra_escola_1', views.cadastra_escola_1, name='cadastra_escola_1'),
    path('cadastra_escola_2', views.cadastra_escola_2, name='cadastra_escola_2'),
    path('cadastra_escola_3', views.cadastra_escola_3, name='cadastra_escola_3'),
    path('cadastra_escola_4', views.cadastra_escola_4, name='cadastra_escola_4'),
    path('cadastra_escola_5', views.cadastra_escola_5, name='cadastra_escola_5'),
    path('cadastra_escola_6', views.cadastra_escola_6, name='cadastra_escola_6'),
    path('cadastra_escola_7', views.cadastra_escola_7, name='cadastra_escola_7'),
    path('cadastra_escola', views.cadastra_escola, name='cadastra_escola'),
    path('cadastra_escola_fase3', views.cadastra_escola_fase3, name='cadastra_escola_fase3'),
    path('cadastra_escola_auto/<str:hash>', views.cadastra_escola_auto, name='cadastra_escola_auto'),
    path('cadastra_escola_auto_envio', views.cadastra_escola_auto_envio, name='cadastra_escola_auto_envio'),
    path('cadastra_escola_recuperada', views.cadastra_escola_recuperada, name='cadastra_escola_recuperada'),
    path('consulta_competidores', views.consulta_competidores, name='consulta_competidores'),
    path('consulta_competidores_resp', views.consulta_competidores_resp, name='consulta_competidores_resp'),
    path('consulta_escolas', views.consulta_escolas, name='consulta_escolas'),
    path('consulta_escolas_resp', views.consulta_escolas_resp, name='consulta_escolas_resp'),
    path('consulta_escolas_pre_inscricao', views.consulta_escolas_pre_inscricao, name='consulta_escolas_pre_inscricao'),
    path('consulta_escolas_pre_inscricao_resp', views.consulta_escolas_pre_inscricao_resp, name='consulta_escolas_pre_inscricao_resp'),
    path('consultas', views.consultas, name='consultas'),
    path('consultas_resp', views.consultas_resp, name='consultas_resp'),

    path('certificados/<int:year>/<str:competition>/<str:type>/<int:id>/', views.emite_certificado, name='emite_certificado'),
    path('certificados/consulta_participantes', views.consulta_participantes, name='certificados'),
    path('certificados/consulta_participantes_resp', views.consulta_participantes_resp, name='consulta_participantes_resp'),
    path('certificados/', views.consulta_participantes, name='certificados'),
    path('certificados/verifica/<str:hash>/', views.verifica_certificado, name='verifica_certificado'),
    #path('erro404', views.error_404, name='erro404'), # to visualize in debug mode
    #path('erro500', views.error_500, name='erro500'), # to visualize in debug mode
    path('mostra_escola/<int:id>/', views.mostra_escola, name='mostra_escola'),
    path('mostra_escola_pre_inscricao/<int:id>/', views.mostra_escola_pre_inscricao, name='mostra_escola_pre_inscricao'),
    #path('pratique/i<str:level>/<int:year>/f<int:phase>/<str:code>/corrige/', views.corrige_iniciacao, name='corrige_iniciacao'),
    #path('pratique/i<str:level>/<int:year>/f<int:phase>/<str:code>/', views.tarefa_iniciacao, name='tarefa_iniciacao'),
    #path('pratique2/p<str:level>/<int:year>/f<str:phase>/<str:code>/corrige/', views.corrige_programacao, name='corrige_programacao'),
    #path('pratique2/p<str:level>/<int:year>/f<str:phase>/<str:code>/resultado/', views.corrige_programacao_resultado, name='corrige_programacao_resultado'),
    #path('pratique2/p<str:level>/<int:year>/f<str:phase>/<str:code>/', views.tarefa_programacao, name='tarefa_programacao'),
    path('pre_inscricao_compet/<int:id>/', views.pre_inscricao_compet, name='pre_inscricao_compet'),


    path('consulta_cidades_fase3', views.consulta_cidades_fase3, name='consulta_cidades_fase3'),


    path('recupera_cadastro', views.recupera_cadastro, name='recupera_cadastro'),
    path('recupera_cadastro_auto/<str:hash>/', views.recupera_cadastro_auto, name='recupera_cadastro_auto'),
    path('reenvia_conf_cadastro/<str:hash>/', views.reenvia_conf_cadastro, name='reenvia_conf_cadastro'),
    #path('resultados', views.resultados, name='resultados'),
    #path('resultados_f1ini', views.resultados_f1ini, name='resultados_f1ini'),
    #path('resultados_f1prog', views.resultados_f1prog, name='resultados_f1prog'),

    path('sbc', views.sbc_index, name='sbc_index'),
    path('pix_qrcode', views.pix_qrcode, name='pix_qrcode'),

    path('accounts/profile/', views.profile, name='accounts_profile'),
    path('profile/', views.profile, name='profile'),    
    
]
