import os.path
from os import mkdir, rename
import logging

from django import forms
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User, UserManager
from django.core.exceptions import ValidationError
from django.core.mail import send_mail, EmailMessage
from django.db import models
from django.forms.widgets import TextInput
from django.http import HttpResponseRedirect
from django.http import FileResponse, HttpResponse
from django.shortcuts import render
from django.urls import path
from django.template.response import TemplateResponse

from principal.models import (I1, I2, IJ, LEVEL, LEVEL_NAME, Colab,
                              Compet, Deleg, InsereLoteCompetidores, School,
                              CompetAutoRegister, Language,
                              SchoolDeleg, SchoolPhase3, SchoolUnregistered, SchoolRejected, SchoolRemoved,
                              SubWWW, GeraCertificados, QueuedMail)

from principal.utils.get_certif import (get_certif_school_colabs,
                                       get_certif_school_compets)

from principal.utils.check_compet_batch import check_compet_batch
from principal.utils.utils import make_password, obi_year, capitalize_name, remove_accents
from obi.settings import MEDIA_ROOT, DEFAULT_FROM_EMAIL, DEFAULT_REPLY_TO_EMAIL
from week.models import Chaperone2

# fix it later for 4.2
#from week.models import Chaperone2

logger = logging.getLogger('cadastro')

EMAIL_MSG_ALURA_COORD = '''Novo(a) coordenador(a) inscrito(a): 

Nome: {name}
Email: {email}
Escola: {school}
Cidade: {city}
Estado: {state}
'''

EMAIL_ALURA_COORD=["ranido@gmail.com"] #, "guilherme.silveira@gmail.com", "gustavo.fujimoto@caelum.com.br", "obi2018coordenadores@robot.zapier.com"]
#EMAIL_ALURA_COORD=["ranido@gmail.com", "guilherme.silveira@gmail.com", "gustavo.fujimoto@caelum.com.br", "obi2018coordenadores@robot.zapier.com"]
EMAIL_ALURA_COMPET=["ranido@gmail.com"] #, "guilherme.silveira@gmail.com", "gustavo.fujimoto@caelum.com.br", "obi2018alunos@robot.zapier.com"]

#EMAIL_FROM="Coordenação da OBI <coordenacao@obi.ic.unicamp.br>"

class LanguageAdmin(admin.ModelAdmin):
    pass

class ColabAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.colab_school_id = request.user.deleg.deleg_school.pk
        super(ColabAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(colab_school_id=request.user.deleg.deleg_school.pk)

    list_display = ['colab_name']
    fields = ['colab_name', 'colab_email', 'colab_sex']
    radio_fields = {"colab_sex": admin.HORIZONTAL}
    #add_form_template = 'admin/add_form_compet.html'
    #change_list_template = 'admin/change_list_compet.html'
    ordering = ('colab_name',)

class Chaperone2Admin(admin.ModelAdmin):
    #def save_model(self, request, obj, form, change):
    #    obj.colab_school_id = request.user.deleg.deleg_school.pk
    #    super(ColabAdmin, self).save_model(request, obj, form, change)

    #def get_queryset(self, request):
    #    qs = super().get_queryset(request)
    #    if request.user.is_superuser:
    #        return qs
    #    return qs.filter(colab_school_id=request.user.deleg.deleg_school.pk)

    list_display = ['chaperone_name', 'chaperone_email']
    fields = ['chaperone_name', 'chaperone_email', 'chaperone_sex']
    radio_fields = {"chaperone_sex": admin.HORIZONTAL}
    #add_form_template = 'admin/add_form_compet.html'
    #change_list_template = 'admin/change_list_compet.html'
    ordering = ('chaperone_name',)

class MyCompetAdminForm(forms.ModelForm):
    def clean(self):
        self.cleaned_data["compet_name"] = capitalize_name(self.cleaned_data["compet_name"])
        # check if name is duplicate
        if self.request.user.is_superuser:
            existing_compets = Compet.objects.filter(compet_name=self.cleaned_data["compet_name"])
        else:
            school_id = self.request.user.deleg.deleg_school.pk
            existing_compets = Compet.objects.filter(compet_name=self.cleaned_data["compet_name"],compet_school_id=school_id)
        if len(existing_compets) > 0:
            # check if user is editing an existing compet, do not flag as duplicate
            if not self.compet_id: 
                raise ValidationError("Competidor já inscrito.")

        if remove_accents(self.cleaned_data["compet_name"]) in existing_compets:
            # check if user is editing an existing compet, do not flag as duplicate
            if not self.compet_id: 
                raise ValidationError("Competidor já inscrito.")
        return self.cleaned_data

class CompetAutoRegisterAdmin(admin.ModelAdmin):
    pass

class CompetAdmin(admin.ModelAdmin):
#     form = MyCompetAdminForm
#     def get_form(self, request, obj=None, **kwargs):
#         form = super(CompetAdmin, self).get_form(request, obj=obj, **kwargs)
#         # add request to form, used in MyCompetAdmin.clean()
#         form.request = request
#         # add compet_id to form, used in MyCompetAdmin.clean(), 
#         # so as not to flag as duplicate when editing  existing compet
#         if obj:
#             form.compet_id = obj.compet_id
#         else:
#             form.compet_id = None            
#         return form

#     def save_model(self, request, obj, form, change):
#         #obj.compet_name = capitalize_name(obj.compet_name)
#         super(CompetAdmin, self).save_model(request, obj, form, change)
#         if request.user.is_superuser:
#             return
#         obj.compet_school_id = request.user.deleg.deleg_school.pk
#         sch = School.objects.get(pk=obj.compet_school_id)
#         if obj.compet_email:
#             if obj.compet_type in (I1,I2,IJ):
#                 mod = 'Iniciação'
#             else:
#                 mod = 'Programação'
# #             send_mail(
# #                 'OBI2018, novo(a) competidor(a)',
# #                 EMAIL_MSG_ALURA_COMPET.format(name=obj.compet_name,
# #                                               email=obj.compet_email,
# #                                               school=sch.school_name,
# #                                               modal=mod,
# #                                               city=sch.school_city,
# #                                               state=sch.school_state),
# #                 DEFAULT_FROM_EMAIL,
# #                 EMAIL_ALURA_COMPET
# #                 )

#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         if request.user.is_superuser:
#             return qs
#         return qs.filter(compet_school_id=request.user.deleg.deleg_school.pk)

#     form = MyCompetAdminForm
    #readonly_fields = ('full_compet_id',)
    #list_display = ['full_compet_id','compet_name', 'compet_type']
    #list_display_links = ['full_compet_id','compet_name']
    #fields = ['full_compet_id','compet_name', 'compet_type', 'compet_year', 'compet_email', 'compet_sex', 'compet_birth_date']
    #radio_fields = {"compet_sex": admin.HORIZONTAL}
    #list_filter = ('compet_type',)
    #add_form_template = 'admin/add_form_compet.html'
    #change_list_template = 'admin/change_list_compet.html'
    #ordering = ('compet_id','compet_name','compet_type',)
    #search_fields = ('compet_name',)
    pass

class InsereLoteCompetidoresAdmin(admin.ModelAdmin):

    def response_add(self, request, obj, post_url_continue="admin:restrito1"):
        '''Override to check the uploaded file, show an intermediate page with results'''
        school_id = request.user.deleg.deleg_school.pk
        sch = School.objects.get(pk=school_id)
        f = request.FILES['data']
        msg,errors,validated_compets = check_compet_batch(f,school_id)
        emails = []
        if len(errors)==0 and len(msg)==0:
            res_msg = Compet.objects.bulk_create(validated_compets)
            msg = '<p>O arquivo foi processado corretamente. Foram encontrados {} competidores no arquivo. Todos os competidores foram inseridos no sistema.</p>'.format(len(validated_compets))
            for c in validated_compets:
                if c.compet_email and c.compet_email not in emails:
                    if c.compet_type in (I1,I2,IJ):
                        mod = 'Iniciação'
                    else:
                        mod = 'Programação'

                    emails.append(c.compet_email)
#                     send_mail(
#                         'OBI2018, novo(a) competidor(a)',
#                         EMAIL_MSG_ALURA_COMPET.format(name=c.compet_name,
#                                                       email=c.compet_email,
#                                                       school=sch.school_name,
#                                                       modal=mod,
#                                                       city=sch.school_city,
#                                                       state=sch.school_state),
#                         DEFAULT_FROM_EMAIL,
#                         EMAIL_ALURA_COMPET
#                         )
        else:
            msg = '''<p>Foram encontrados alguns erros durante o processamento do arquivo. Nenhum competidor do arquivo foi inserido no sistema.
<p>Por favor corrija os erros abaixo e re-submeta o arquivo.</p><p>{}</p>'''.format(msg)

        return render(request,
                      'admin/add_compet_batch_intermed.html',
              context={'msg': msg, 'errors': errors,
                       })

    add_form_template = 'admin/add_form_compet_batch.html'


class SchoolAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(school_id=request.user.deleg.deleg_school.pk)

    readonly_fields = ('school_id',)
    fields = ['school_id','school_name','school_type','school_inep_code','school_address','school_address_number','school_address_complement','school_address_district','school_city','school_phone','school_deleg_phone','school_deleg_name','school_deleg_email','school_deleg_username','school_ok','school_prev','school_is_site_phase3','school_address_building','school_address_map']
    list_display = ('school_id','school_name','school_city','school_state','school_type','school_deleg_name','school_deleg_email','school_deleg_username','school_inep_code','school_ok','num_inscr')
    widgets = {
            'school_address': forms.Textarea(),
            }
    search_fields = ('school_name','school_deleg_username', 'school_deleg_name','school_deleg_email','school_city')

    def get_actions(self, request):
        actions = super().get_actions(request)
        #actions.pop(0)  # remove the "-----"
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def remove_school(self, request, queryset):
        print("in remove_school")
        schools_removed = 0
        schools_failed = 0
        for q in queryset:
            try:
                remove_a_school(request, q)
                schools_removed += 1
            except:
                schools_failed += 1
        if schools_removed == 0:
            message_bit = "nenhuma escola foi removida com sucesso"
        elif schools_removed == 1:
            message_bit = "1 escola foi removida com sucesso"
        else:
            message_bit = "%s escolas foram removidas com sucesso" % schools_removed
        if schools_failed == 0:
            message_bit += "."
        elif schools_failed == 1:
            message_bit += "; 1 escola falhou."
        elif schools_failed == 1:
            message_bit += "; %s escolas falharam." % schools_removed
            
        self.message_user(request, message_bit)

    remove_school.short_description = "Remover escola"
    actions = [remove_school]






    
class SchoolDelegAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(school_id=request.user.deleg.deleg_school.pk)
#     def get_actions(self, request):
#         actions = super(SchoolDelegAdmin, self).get_actions(request)
#         if 'delete_selected' in actions:
#             del actions['delete_selected']
#         return actions
    
    actions = None
    readonly_fields = ('school_deleg_username',)
    #exclude = ['school_ok']
    fields = ['school_name','school_type','school_deleg_name','school_deleg_username','school_deleg_email','school_phone','school_zip','school_address','school_address_number','school_address_complement','school_address_district','school_city','school_state','school_address_building','school_address_map']
    list_display = ('school_name','school_deleg_name','school_deleg_email','school_deleg_username')
    widgets = {
            'school_address': forms.Textarea(),
            }
    search_fields = ('school_name','school_deleg_name','school_deleg_email','school_deleg_username')

def authorize_a_school(request, q, password):
    ''' authorizes a school: create a local coordinator user, send email with password
    '''

    subject = obi_year() + ' - Cadastro finalizado'
    message_authorized = """
Caro(a) Prof(a). {contact_name},

mais uma vez, obrigado por cadastrar a escola

      {school_name}

na Olimpíada Brasileira de Informática.

O processo de cadastramento da escola foi finalizado e o acesso ao sistema de inscrição de competidores está habilitado. A inscrição de competidores deve ser feita na página da OBI:

https://olimpiada.ic.unicamp.br

seguindo o link "Acesso Escolas" no alto da página inicial, usando o nome de usuário e a senha a seguir:

nome de usuário: {username}
senha: {password}

Por favor note que no momento estão abertas apenas as inscrições para a Competição Feminina da OBI2025.

---
Coordenação da OBI2025
Email: olimpinf@ic.unicamp.br
WhatsApp e Telegram: (19) 3199-7399

Organização:  Instituto de  Computação -  UNICAMP
Promoção:  Sociedade Brasileira de Computação
"""

    #print("authorize_a_school")
    logger.info("start authorize_a_school: {}, {}".format(q.school_deleg_name, q.school_name))
    try:
        user = User.objects.get(username=q.school_deleg_username)
        logger.info("existing user!")
        print("existing user!")
    except:
        user = User.objects.create_user(q.school_deleg_username, q.school_deleg_email, password)
        #print("creating user")
    #print("user", user)
    user.last_name = q.school_deleg_name
    user.is_staff = False
    g = Group.objects.get(name='local_coord')
    g.user_set.add(user)
    #print("group", g)
    user.save()
    deleg = Deleg()
    deleg.user = user
    deleg.deleg_school_id = q.pk
    
    deleg.save()
    q.school_ok = True
    q.save()
    # send email to new coordinator
    # #print("send email to coordinator")
    body =  message_authorized.format(contact_name=q.school_deleg_name,
                                   school_name=q.school_name,
                                   username=q.school_deleg_username,
                                   password=password
                                   )
    # send_mail(
    #     subject,
    #     body,
    #     DEFAULT_FROM_EMAIL,
    #     [q.school_deleg_email]
    # )
    # # send email to obi
    # print("send email to obi")
    # send_mail(
    #     subject,
    #     body,
    #     DEFAULT_FROM_EMAIL,
    #     [DEFAULT_FROM_EMAIL]
    # )

    # # and try another way...
    # print("send EmailMessage")
    # from_addr = DEFAULT_FROM_EMAIL,
    # to_addr = (user.email,)
    # to_addr = q.school_deleg_email
    # msg = EmailMessage(subject, body, from_addr, to_addr, reply_to=[DEFAULT_REPLY_TO_EMAIL])

    m = QueuedMail(subject=subject, body=body, from_addr=DEFAULT_FROM_EMAIL, to_addr=q.school_deleg_email)
    m.save()
    m = QueuedMail(subject=subject, body=body, from_addr=DEFAULT_FROM_EMAIL, to_addr='ranido@unicamp.br')
    m.save()

def remove_a_school(request, q):
    ''' remove a school
        '''
    
    removed = SchoolRemoved(
        school_inep_code = q.school_inep_code,
        school_code = q.school_code,
        school_name = q.school_name,
        school_type = q.school_type,
        school_deleg_name = q.school_deleg_name,
        school_deleg_email = q.school_deleg_email,
        school_deleg_username = q.school_deleg_username,
        school_is_known = q.school_is_known,
        school_state = q.school_state,
        school_city = q.school_city,
        school_zip = q.school_zip,
        school_address = q.school_address,
        school_address_number = q.school_address_number,
        school_address_complement = q.school_address_complement,
        school_address_district = q.school_address_district,
        school_phone = q.school_phone,
        school_deleg_phone = q.school_deleg_phone,
    )
    removed.save()
    
    if q.school_ok:
        username = q.school_deleg_username
        try:
            print(f"will delete username {username}")
            user = User.objects.get(username=username)
            print(f"will delete user {user}")
            user.delete()
        except:
            pass
    q.delete()
        

    
def deny_a_school(request, q, reason):
    ''' reject a school
    '''
    if reason == 'deny':
        subject = obi_year() + ' - Cadastro não válido'
        message_denied = """
Caro(a) Prof(a). {contact_name},

recebemos uma solicitação, em seu nome, para cadastrar a escola

      {school_name}

na Olimpíada Brasileira de Informática. Lamentamos mas não foi possível confirmar os dados informados.

Por favor note que:
  * o cadastro deve ser feito por um(a) professor(a) da escola (ocasionalmente,
    pode também ser feito por um(a) funcionário(a) designado pelo Diretor da
    escola).
  * o endereço de correio eletrônico e o telefone pessoal informados devem ser 
    da pessoa nomeada como Coordenador Local da OBI.
  * o endereço de correio eletrônico informado deve ser preferencialmente
    um endereço institucional.
  * o endereço postal deve estar correto e atualizado.
  * o telefone da escola deve estar correto e atualizado.
  * se aplicável, o código INEP da escola deve estar correto e atualizado.

Por favor preencha um novo cadastro com os dados corretos em

https://olimpiada.ic.unicamp.br/info/como_participar_escola/

Atenciosamente

---
Coordenação da OBI2025
Email: olimpinf@ic.unicamp.br
WhatsApp e Telegram: (19) 3199-7399

Organização:  Instituto de  Computação -  UNICAMP
Promoção:  Sociedade Brasileira de Computação
"""
    elif reason == 'already_registered':
        subject = obi_year() + ' - Cadastro repetido'
        message_denied = """
Caro(a) Prof(a). {contact_name},

recebemos uma solicitação, em seu nome, para cadastrar a escola

      {school_name}

na Olimpíada Brasileira de Informática. Informamos que já há um cadastro
ativo para essa escola, com outro professor como Coordenador Local da OBI,
e houve alunos inscritos na OBI do ano passado utilizando esse cadastro.
Assim, sua solicitação de novo cadastro foi rejeitada.

Para saber quem é o Coordenador Local cadastrado, faça uma consulta à lista
de escolas cadastradas:

https://olimpiada.ic.unicamp.br/consulta_escolas

Se houve mudança de Coordenador Local da OBI, por favor preencha um novo
cadastro, mas informe sobre a mudança de coordenador marcando o campo 
correspondente no formulário.

Atenciosamente,

---
Coordenação da OBI2025
Email: olimpinf@ic.unicamp.br
WhatsApp e Telegram: (19) 3199-7399

Organização:  Instituto de  Computação -  UNICAMP
Promoção:  Sociedade Brasileira de Computação
"""

    rejected = SchoolRejected(
        school_inep_code = q.school_inep_code,
        school_code = q.school_code,
        school_name = q.school_name,
        school_type = q.school_type,
        school_deleg_name = q.school_deleg_name,
        school_deleg_email = q.school_deleg_email,
        school_deleg_username = q.school_deleg_username,
        school_is_known = q.school_is_known,
        school_state = q.school_state,
        school_city = q.school_city,
        school_zip = q.school_zip,
        school_address = q.school_address,
        school_address_number = q.school_address_number,
        school_address_complement = q.school_address_complement,
        school_address_district = q.school_address_district,
        school_phone = q.school_phone,
        school_deleg_phone = q.school_deleg_phone,
        school_reason = reason
    )
    rejected.save()

    # send email to coordinator
    # xxx

    if reason in ('deny','already_registered'):
        body = message_denied.format(contact_name=q.school_deleg_name,
                                     school_name=q.school_name)

        m = QueuedMail(subject=subject, body=body, from_addr=DEFAULT_FROM_EMAIL, to_addr=q.school_deleg_email)
        m.save()

        # send_mail(
        #     subject,
        #     message_denied.format(contact_name=q.school_deleg_name,
        #                           school_name=q.school_name
        #                           ),
        #     DEFAULT_FROM_EMAIL,
        #     [q.school_deleg_email]
        # )
        # # send email to obi
        # send_mail(
        #     subject,
        #     message_denied.format(contact_name=q.school_deleg_name,
        #                           school_name=q.school_name
        #                           ),
        #     DEFAULT_FROM_EMAIL,
        #     [DEFAULT_FROM_EMAIL]
        # )
    q.delete()


class SchoolUnregisteredAdmin(admin.ModelAdmin):
    readonly_fields = ('school_id',)
    search_fields = ['school_name','school_city','school_deleg_name','school_deleg_email','school_deleg_username']
    fields = ['school_id','school_name','school_type','school_inep_code','school_is_known','school_deleg_name','school_deleg_email','school_deleg_username',
              'school_deleg_phone','school_phone','school_zip','school_address','school_address_number','school_address_complement','school_city','school_state']
    list_display = ('school_id','school_name','school_is_known','school_email_cur','school_email_prev','school_name_prev','school_deleg_name_prev','school_name_repeated','school_name_city_repeated','school_change_coord','school_is_site_phase3','school_deleg_name','school_deleg_email','school_city','school_state','school_name_prev_full')
    ordering = ('school_id','school_name','school_city')

    def get_actions(self, request):
        actions = super().get_actions(request)
        #actions.pop(0)  # remove the "-----"
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        #if request.user.is_superuser:
        #    return qs
        return qs.filter(school_ok=False).order_by('pk')

    def authorize_school(self, request, queryset):
        schools_authorized = 0
        schools_failed = 0
        for q in queryset:
            if True:
                password = make_password()
                authorize_a_school(request,q,password)
                schools_authorized += 1
            else:
                schools_failed += 1
        if schools_authorized == 0:
            message_bit = "nenhuma escola foi autorizada com sucesso"
        elif schools_authorized == 1:
            message_bit = "1 escola foi autorizada com sucesso"
        else:
            message_bit = "%s escolas foram autorizadas com sucesso" % schools_authorized
        if schools_failed == 0:
            message_bit += "."
        elif schools_failed == 1:
            message_bit += "; 1 escola falhou."
        elif schools_failed == 1:
            message_bit += "; %s escolas falharam." % schools_authorized
            
        self.message_user(request, message_bit)

    def authorize_school_group(self, request, queryset):
        schools_authorized = 0
        schools_failed = 0
        # use same password for all schools in group
        password = make_password()
        for q in queryset:
            try:
                authorize_a_school(request,q,password)
                schools_authorized += 1
            except:
                schools_failed += 1
        if schools_authorized == 0:
            message_bit = "nenhuma escola foi autorizada com sucesso"
        elif schools_authorized == 1:
            message_bit = "1 escola foi autorizada com sucesso"
        else:
            message_bit = "%s escolas foram autorizadas com sucesso" % schools_authorized
        if schools_failed == 0:
            message_bit += "."
        elif schools_failed == 1:
            message_bit += "; 1 escola falhou."
        elif schools_failed == 1:
            message_bit += "; %s escolas falharam." % schools_authorized
            
        self.message_user(request, message_bit)

    def deny_school(self, request, queryset):
        schools_denied = 0
        schools_failed = 0
        for q in queryset:
            deny_a_school(request,q,"deny")
            try:
                schools_denied += 1
            except:
                schools_failed += 1
        if schools_denied == 0:
            message_bit = "nenhuma escola foi negada com sucesso"
        elif schools_denied == 1:
            message_bit = "1 escola foi negada com sucesso"
        else:
            message_bit = "%s escolas foram negadas com sucesso" % schools_denied
        if schools_failed == 0:
            message_bit += "."
        elif schools_failed == 1:
            message_bit += "; 1 escola falhou."
        elif schools_failed == 1:
            message_bit += "; %s escolas falharam." % schools_denied
            
        self.message_user(request, message_bit)

    def deny_school_duplicate(self, request, queryset):
        schools_denied = 0
        schools_failed = 0
        for q in queryset:
            deny_a_school(request,q,"already_registered")
            try:
                schools_denied += 1
            except:
                schools_failed += 1
        if schools_denied == 0:
            message_bit = "nenhuma escola foi negada com sucesso"
        elif schools_denied == 1:
            message_bit = "1 escola foi negada com sucesso"
        else:
            message_bit = "%s escolas foram negadas com sucesso" % schools_denied
        if schools_failed == 0:
            message_bit += "."
        elif schools_failed == 1:
            message_bit += "; 1 escola falhou."
        elif schools_failed == 1:
            message_bit += "; %s escolas falharam." % schools_denied
            
        self.message_user(request, message_bit)


    def deny_school_dismiss(self, request, queryset):
        schools_denied = 0
        schools_failed = 0
        for q in queryset:
            deny_a_school(request,q,"dismiss")
            try:
                schools_denied += 1
            except:
                schools_failed += 1
        if schools_denied == 0:
            message_bit = "nenhuma escola foi negada com sucesso"
        elif schools_denied == 1:
            message_bit = "1 escola foi negada com sucesso"
        else:
            message_bit = "%s escolas foram negadas com sucesso" % schools_denied
        if schools_failed == 0:
            message_bit += "."
        elif schools_failed == 1:
            message_bit += "; 1 escola falhou."
        elif schools_failed == 1:
            message_bit += "; %s escolas falharam." % schools_denied
            
        self.message_user(request, message_bit)

    def dummy(self, request, queryset):
        '''dummy action to make a divider
        '''
        
    authorize_school.short_description = "Autorizar escola"
    authorize_school_group.short_description = "Autorizar escolas com mesma senha"
    deny_school.short_description = "Negar escola"
    deny_school_duplicate.short_description = "Negar, escola duplicada"
    deny_school_dismiss.short_description = "Desconsiderar"
    dummy.short_description = "------"
    actions = [authorize_school,authorize_school_group,dummy,deny_school,deny_school_duplicate,deny_school_dismiss]
    widgets = {
            'school_address': forms.Textarea(),
            }
    search_fields = ('school_name', 'school_deleg_username', 'school_deleg_name','school_city',)


class SchoolPhase3Admin(admin.ModelAdmin):
    fields = ['school_name','school_deleg_name','school_deleg_email','school_deleg_username',
              'school_deleg_phone','school_phone','school_zip','school_address','school_address_number','school_address_complement','school_city','school_state']
    list_display = ('school_name','school_id','school_deleg_name','school_deleg_email','school_city','school_state')
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        #if request.user.is_superuser:
        #    return qs
        return qs.filter(school_is_site_phase3=False).order_by('pk')

    def authorize_school(self, request, queryset):
        schools_authorized = 0
        schools_failed = 0
        for q in queryset:
            try:
                q.school_is_site_phase3 = True
                #q.school_site_phase3 = q.pk
                #q.school_site_phase3_ini = q.pk
                #q.school_site_phase3_prog = q.pk
                q.save()
                user = User.objects.get(username=q.school_deleg_username)
                g = Group.objects.get(name='fase3_coord')
                g.user_set.add(user)
                schools_authorized += 1
            except:
                schools_failed += 1
        if schools_authorized == 0:
            message_bit = "nenhuma sede foi autorizada com sucesso"
        elif schools_authorized == 1:
            message_bit = "1 sede foi autorizada com sucesso"
        else:
            message_bit = "%s sede foram autorizadas com sucesso" % schools_authorized
        if schools_failed == 0:
            message_bit += "."
        elif schools_failed == 1:
            message_bit += "; 1 sede falhou."
        elif schools_failed > 1:
            message_bit += "; %s sedes falharam." % schools_authorized
            
        self.message_user(request, message_bit)

    authorize_school.short_description = "Autorizar Sede Fase 3"
    actions = [authorize_school]
    widgets = {
            'school_address': forms.Textarea(),
            }
    search_fields = ('school_name', 'school_deleg_username', 'school_deleg_name','school_city',)

class DelegInline(admin.StackedInline):
    model = Deleg
    can_delete = False
    verbose_name_plural = 'delegado'

class DelegAdmin(admin.ModelAdmin):
    list_display = ('deleg_id', 'user', 'deleg_school')
    search_fields = ('deleg_id',)
    ordering = ('deleg_id',)

class QueuedMailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'to_addr', 'time_in',)
    search_fields = ('subject', 'body',)
    ordering = ('-time_in',)

class SubWWWAdmin(admin.ModelAdmin):
    list_display = ('problem_name_full','problem_name','sub_lang')

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (DelegInline, )

class GeraCertificadosAdmin(admin.ModelAdmin):
#     enable_change_view = False

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('', self.admin_site.admin_view(self.gera_certificados),name='gera_certificados'),
            path('compet/', self.admin_site.admin_view(self.gera_certificados_compet),name='gera_certificados_compet'),
            path('colab/', self.admin_site.admin_view(self.gera_certificados_colab),name='gera_certificados_colab'),
            #path('<str:certif_type>/', self.admin_site.admin_view(self.gera_certificados), name='gera_certificados'),
            ]
        return my_urls + urls
    
#     def get_model_perms(self, request):
#         """
#         Return empty perms dict thus hiding the model from admin index.
#         """
#         return {}
    
    def get_queryset(self, request):
        #qs = super().get_queryset(request).filter(compet_type__in=[IJ,I1,I2],compet_classif_fase3 = True).order_by('compet_type','-compet_points_fase3')
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        qs = qs.filter(compet_school_id=request.user.deleg.deleg_school.pk)
        return qs

    def gera_certificados(self, request):
        # ...
        context = dict(
           self.admin_site.each_context(request),
        )
        return TemplateResponse(request, "fase3/admin/gera_certificados.html", context)

    def gera_certificados_compet(self, request):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="certificados_compet.pdf"'
        school_id = request.user.deleg.deleg_school.pk
        year = obi_year(as_int=True)
        file_data = get_certif_school_compets(school_id,year)
        response.write(file_data)
        return response

    def gera_certificados_colab(self, request):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="certificados_colab.pdf"'
        school_id = request.user.deleg.deleg_school.pk
        year = obi_year(as_int=True)
        file_data = get_certif_school_colabs(school_id,year)
        response.write(file_data)
        return response

admin.site.site_title = obi_year()
admin.site.site_header = obi_year()
admin.site.index_title = 'Ações de coordenação disponíveis'
admin.site.site_url = None
#admin.site.app_index_template = 'admin/app_index.html'
#admin.site.index_template = 'admin/index_admin.html'

# principal
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Compet, CompetAdmin)
admin.site.register(CompetAutoRegister, CompetAutoRegisterAdmin)
admin.site.register(Colab, ColabAdmin)
admin.site.register(Deleg, DelegAdmin)
admin.site.register(Language,LanguageAdmin)

# fix it later for 4.2
#admin.site.register(Chaperone2, Chaperone2Admin)

#admin.site.register(SchoolPhase3,SchoolPhase3Admin)
admin.site.register(SchoolDeleg,SchoolDelegAdmin)
admin.site.register(School,SchoolAdmin)
admin.site.register(SchoolUnregistered,SchoolUnregisteredAdmin)

admin.site.register(QueuedMail,QueuedMailAdmin)
admin.site.register(Chaperone2,Chaperone2Admin)
#admin.site.register(InsereLoteCompetidores,InsereLoteCompetidoresAdmin)
#admin.site.register(GeraCertificados,GeraCertificadosAdmin)

# class Restrito1AdminSite(AdminSite):
#     site_header = u'OBI2018'
#     site_title = u'OBI2018'
#     index_title = u'Coordenação Local'
#     site_url = None

# restrito1_site = Restrito1AdminSite(name='restrito1')
# restrito1_site.register(Compet, CompetAdmin)
# restrito1_site.register(Colab, ColabAdmin)
# restrito1_site.register(Deleg)
# restrito1_site.register(School,SchoolDelegAdmin)
#restrito1_site.register(UploadCompetBatch,UploadCompetBatchAdmin)
#restrito1_site.register(UploadSubmissionsPhase1,UploadSubmissionsPhase1Admin)
