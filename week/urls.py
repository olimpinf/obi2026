from django.conf import settings
from django.urls import include, path, re_path

from week import views

app_name = 'week'
urlpatterns = [
    path('', views.index, name='index'),
    path('info_seletiva', views.info_seletiva, name='info_seletiva'),
    path('conteudo', views.conteudo, name='conteudo'),
    #path('participantes_seletiva', views.participants_seletiva, name='partic_seletiva'),
    path('participantes', views.participants, name='partic'),
    path('agenda', views.agenda, name='agenda'),
    path('ecos', views.ecos, name='ecos'),
    path('ecos_instituicoes', views.ecos_instituicoes, name='ecos_instituicoes'),
    path('agenda_aulas', views.classes, name='classes'),
    path('ini1', views.ini1, name='ini1'),
    path('progj', views.progj, name='progj'),
    path('prog1', views.ini1, name='prog1'),
    path('convidados', views.invited, name='invited'),
    path('emite_certificado/<str:type>/<str:id>', views.emite_certificado, name='emite_certificado'),
    #path('agenda', views.agenda, name='agenda'),
    path('programa', views.programa, name='program'),
    path('chegadas', views.arrivals, name='arrivals'),
    path('chegadas2', views.arrivals2, name='arrivals2'),
    path('camisetas', views.camisetas, name='camisetas'),
    path('partidas', views.departures, name='departures'),
    path('partidas2', views.departures2, name='departures2'),
    path('monitores', views.monitors, name='monitors'),
    path('professores', views.instructors, name='instructors'),
    path('certificados', views.certificados, name='certificados'),
    path('palestras', views.palestras, name='palestras'),
    path('cerimonia', views.cerimonia, name='cerimonia'),
    path('emite_carta_professor<int:id>', views.emite_carta_professor, name='emite_carta_professor'),
    path('documentos', views.documentos, name='documentos'),
    path('confirmar', views.confirm, name='confirm'),
    path('negar', views.deny, name='deny'),
    path('negar_conf', views.do_deny, name='do_deny'),
    path('informa_pagamento', views.inform_payment, name='inform_payment'),
    path('emite_recibo/<str:id>', views.emit_receipt, name='emit_receipt'),
    path('processa_pagamento', views.process_payment, name='process_payment'),
    path('sbc_lista_pagamento', views.sbc_list_payment, name='sbc_list_payment'),
    path('sbc_pagamento/<str:id>', views.sbc_show_payment, name='sbc_show_payment'),
]
