import string

from django import forms
from captcha.fields import CaptchaField
from principal.models import (LEVEL_CHOICES_FORM, PARTIC_TYPE_CHOICES_FORM,
                             SCHOOL_TYPE_CHOICES, SEX_CHOICES, SEX_F,
                             SEX_M, STATE_CHOICES, Compet, School, SubWWW)
from principal.models import (LEVEL_CHOICES_PROG, LEVEL_CHOICES_INI)

# begin - implementation of fieldsets
from django.forms.models import ModelFormOptions

_old_init = ModelFormOptions.__init__
def _new_init(self, options=None):
    _old_init(self, options)
    self.fieldsets = getattr(options, 'fieldsets', None)
ModelFormOptions.__init__ = _new_init

class Fieldset(object):
  def __init__(self, form, title, fields, classes, single_field):
    self.form = form
    self.title = title
    self.fields = fields
    self.classes = classes
    self.single_field = single_field
  
  def __iter__(self):
      # Similar to how a form can iterate through it's fields...
      if self.single_field:
          yield self.fields
      else:
          for field in self.fields:
              yield field

def fieldsets(self):
    meta = getattr(self, '_meta', None)
    if not meta:
        meta = getattr(self, 'Meta', None)
  
    if not meta or not meta.fieldsets:
        return
  
    for name, data in meta.fieldsets:
        if str(type(data['fields'])) != "<class 'tuple'>":
            single = True
            yield Fieldset(
                form=self,
                title=name,
                fields=(self[data.get('fields',())]),
                classes=data.get('classes', ''),
                single_field = single
                )
        else:
            single = False
            yield Fieldset(
                form=self,
                title=name,
                fields=(self[f] for f in data.get('fields',())),
                classes=data.get('classes', ''),
                single_field = single
                )

forms.BaseForm.fieldsets = fieldsets
# end implementation fieldsets

class SubmeteSolucoesForm(forms.Form):
    source_file = forms.FileField(
        label='Arquivo', 
        required=True,
        )
    compet_type = forms.ChoiceField(
        label='Modalidade',
        choices=(('', u'Selecione...'),)+LEVEL_CHOICES_PROG,
        widget=forms.Select(attrs={'class':'select'}),
        required=True,
        )

    class Meta:
        fieldsets = (
            ('', {
                    'fields': ('source_file','compet_type')},),
        )


class CorretorFolhasRespostasForm(forms.Form):
    source_file = forms.FileField(
        label='Arquivo de Folhas de Respostas',
        required=True,
        )
    compet_type = forms.ChoiceField(
        label='Modalidade',
        choices=(('', u'Selecione...'),)+LEVEL_CHOICES_INI,
        widget=forms.Select(attrs={'class':'select'}),
        required=True,
        )
    reference = forms.CharField(
        label='Referência',
        max_length=200,
        help_text='Use este campo para colocar uma identificação deste lote de Folhas de Respostas'
    )

    class Meta:
        fieldsets = (
            ('', {
                    'fields': ('source_file','compet_type','reference')},),
        )

class InserePontosIniLoteForm(forms.Form):
    source_file = forms.FileField(
        label='Arquivo com pontuações', 
        required=True,
        )
    class Meta:
        fieldsets = (
            ('', {
                    'fields': ('source_file')},),
        )

class TestForm(forms.Form):
    compet_points = forms.IntegerField(
        label='Pontos', 
        required=False,
        )
    compet_id = forms.IntegerField(
        label='Número de Inscrição', 
        required=True,
        )

    class Meta:
        fieldsets = (
            ('', {
                    'fields': ('compet_points')},),
        )


############
# Results
#
class ConsultaResForm(forms.Form):
    compet_id = forms.CharField(
        label='Número de Inscrição', 
        max_length=8,
        required=True,
        help_text='Não sabe o número de inscrição? <a href="/consulta_competidores">Consulte aqui</a>.'
        )
    captcha = CaptchaField(label='Prove que não é um robô, digite o resultado ')

    class Meta:
        fieldsets = (
            ('Dados para busca', {
                    'fields': ('compet_id','captcha')},),
        )


class ConsultaSuaSedeFase3Form(forms.Form):
    compet_id = forms.CharField(
        label='Número de inscrição', 
        max_length=8,
        required=False,
        help_text='Não sabe o número de inscrição? <a href="/consulta_competidores">Consulte aqui</a>.'
        )
    class Meta:
        fieldsets = (
            ('Dados para busca', {
                    'fields': ('compet_id')}),
        )

class ConsultaSedesFase3Form(forms.Form):

    MODALITY_CHOICES = (
        ('ini','Iniciação'), ('prog','Programação'),
    )
    
    modality = forms.ChoiceField(
        label='Modalidade',
        choices=MODALITY_CHOICES,
        widget=forms.RadioSelect(attrs={'class':'horizontal'}),
        required=True,
    )
    school_state = forms.ChoiceField(
        label='Estado',
        choices=(STATE_CHOICES),
        widget=forms.Select(attrs={'class':'select'}),
        required=False,
        help_text='<br>Deixe este campo em branco para listar todas as sedes.'
        )
    school_order = forms.ChoiceField(
        label='Ordena por',
        choices=( ('school_city','Cidade'), ('school_state','Estado') ),
        widget=forms.Select(attrs={'class':'select'}),
        required=False,
        )

    class Meta:
        fieldsets = (
            ('Dados para busca', {
                    'fields': ('modality','school_state')}),
            ('Visualização', {
                    'fields': ('school_order')}),
        )

class ConsultaResIniForm(forms.Form):
    compet_id = forms.CharField(
        label='Número de Inscrição', 
        max_length=8,
        required=True,
        help_text='Não sabe o número de inscrição? <a href="/consulta_competidores">Consulte aqui</a>.'
        )
    captcha = CaptchaField(label='Prove que não é um robô, digite o resultado ')

    class Meta:
        fieldsets = (
            ('Dados para busca', {
                    'fields': ('compet_id','captcha')},),
        )



class RecuperaSubmForm(forms.Form):
    compet_id = forms.CharField(
        label='Número de Inscrição', 
        max_length=8,
        required=True,
        help_text='Não sabe o número de inscrição? <a href="/consulta_competidores">Consulte aqui</a>.'
        )
    send_to_compet = forms.BooleanField(
        label='Envia para competidor', initial=True, required=False,
        )
    send_to_coord = forms.BooleanField(
        label='Envia para Coordenador Local', required=False,
        )

    captcha = CaptchaField(label='Prove que não é um robô, digite o resultado ')
    class Meta:
        fieldsets = (
            ('Dados para busca', {
                    'fields': (('compet_id'),('send_to_compet'), ('send_to_coord'), ('captcha'))}),
        )



class SchoolPrefIniForm(forms.Form):

    site_ini_own_compet = forms.BooleanField(
        label= 'A escola pode aplicar a Fase 3 apenas para seus alunos',
        #widget=forms.BooleanField(),
        required=False,
        )
    site_ini_all_compet = forms.BooleanField(
        label= 'A escola pode aplicar a Fase 3 para alunos de escolas da sua cidade',
        #widget=forms.BooleanField(),
        required=False,
        )
    class Meta:
        fieldsets = (
            ('Consulta', {
                    'fields': ('site_ini_own_compet','site_ini_all_compet')}),
        )
        
    
class SchoolPrefProgForm(forms.Form):

    site_prog_own_compet = forms.BooleanField(
        label= 'A escola pode aplicar a Fase 3 apenas para seus alunos',
        #widget=forms.BooleanField(),
        required=False,
        )
    site_prog_all_compet = forms.BooleanField(
        label= 'A escola pode aplicar a Fase 3 para alunos de escolas da sua cidade',
        #widget=forms.BooleanField(),
        required=False,
        )

    class Meta:
        fieldsets = (
            ('Consulta', {
                    'fields': ('site_prog_own_compet','site_prog_all_compet')}),
        )
        
    
    
        
