import string

from django import forms
# begin - implementation of fieldsets
from django.forms.models import ModelFormOptions

from cadastro.models import (LEVEL_CHOICES_FORM, PARTIC_TYPE_CHOICES_FORM, PRI,
                             PUB, SCHOOL_TYPE_CHOICES, SEX_CHOICES, SEX_F,
                             SEX_M, STATE_CHOICES, Compet, School, SubWWW)
from cadastro.utils.utils import obi_year

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
                    'fields': ('school_state')}),
            ('Visualização', {
                    'fields': ('school_order')}),
        )
