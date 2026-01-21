import string

from django import forms
from captcha.fields import CaptchaField
from principal.models import (I1, I2, IJ, LANG_SUFFIXES_NAMES, LEVEL,
                             LEVEL_NAME, LEVEL_NAME_FULL, P1, P2, PJ, PS,
                             Compet, School)
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

class ConsultaResIniForm(forms.Form):
    compet_id = forms.CharField(
        label='Número de Inscrição', 
        max_length=8,
        required=True,
        help_text='Não sabe o número de inscrição? <a href="/consulta_competidores">Consulte aqui</a>.'
        )
    captcha = CaptchaField(label='Prove que não é um robô, digite os caracteres ')

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

    captcha = CaptchaField(label='Prove que não é um robô, digite os caracteres ')
    class Meta:
        fieldsets = (
            ('Dados para busca', {
                    'fields': (('compet_id'),('send_to_compet'), ('send_to_coord'), ('captcha'))}),
        )

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
        widget=forms.FileInput(attrs={'class':'form-control'}),
        required=True,
        )
    compet_type = forms.ChoiceField(
        label='Modalidade',
        choices=(('', u'Selecione...'),)+LEVEL_CHOICES_INI,
        widget=forms.Select(attrs={'class':'form-select'}),
        required=True,
        )
    reference = forms.CharField(
        label='Referência',
        max_length=200,
        widget=forms.TextInput(attrs={'class':'form-control'}),        
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

class SchoolTurnChoiceForm(forms.Form):
    turn_choices = (('A','A'), ('B','B'))
    turn_ini = forms.ChoiceField(
        label='Turno Modalidade Iniciação',
        choices=turn_choices,
        #widget=forms.RadioSelect(attrs={'class':'horizontal'}),
        widget=forms.RadioSelect(),
        )
    turn_prog = forms.ChoiceField(
        label='Turno Modalidade Progamação',
        choices=turn_choices,
        #widget=forms.RadioSelect(attrs={'class':'horizontal'}),
        widget=forms.RadioSelect(),
        )

    class Meta:
        fieldsets = (
            ('', {
                'fields': ('turn_ini','turn_prog')}),
        )
