from django import forms

from principal.utils.utils import capitalize_name, obi_year, format_phone_number
from principal.utils.cpfcnpj import validate_cpf_cnpj
from principal.models import COMPET_SORT_CHOICES, LEVEL_CHOICES_FILTER
from week.models import Week, PARENT_TYPE_CHOICES, SHIRT_SIZE_CHOICES


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
      # Similar to how a form can iterate through its fields...
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

class ConfirmParticWeekForm(forms.Form):
    #def clean(self):
    #    cleaned_data = super().clean()
    #    return self.cleaned_data

    def clean_parent_name(self):
        name = self.cleaned_data['parent_name']
        tks = name.split()
        if len(tks) < 2:
            raise forms.ValidationError("Informe o nome completo.")
        name = capitalize_name(name)
        return name

    def clean_partic_accept(self):
        accept = self.cleaned_data['partic_accept']
        if not accept:
            raise forms.ValidationError("É necessário concondar com as regras da Semana Olímpica.")
        return accept
              
    def clean_partic_shirt_size(self):
        t = self.cleaned_data['partic_shirt_size']
        if t == 'Selecione...':
            raise forms.ValidationError("Selecione o tamanho da camiseta.")
        return t
    
    def clean_parent_type(self):
        t = self.cleaned_data['parent_type']
        if t == 'Selecione':
            raise forms.ValidationError("Selecione o tipo de representante legal.")
        return t
    
    def clean_parent_phone(self):
        n = self.cleaned_data['parent_phone']
        phone = format_phone_number(n)
        if not phone:
            raise forms.ValidationError("Informe um número de telefone válido.")
        return phone
    
    def clean_partic_phone(self):
        n = self.cleaned_data['partic_phone']
        phone = format_phone_number(n)
        if not phone:
            raise forms.ValidationError("Informe um número de telefone válido.")
        return phone
    
    parent_name = forms.CharField(
        label='Nome do pai/mãe ou responsável legal', 
        max_length=200,
        )
    parent_type = forms.ChoiceField(
        label='Tipo responsável legal',
        choices= [('Selecione...','Selecione...')] + PARENT_TYPE_CHOICES,
        )
    parent_phone = forms.CharField(
        label='Telefone do pai/mãe ou responsável legal, com DDD',
        max_length=16,
        widget=forms.TextInput(),
        #help_text='Para contato com o responsável se necessário',
        )
    parent_email = forms.EmailField(
        label = 'Email do pai/mãe ou responsável legal',
        required = True,
        )
    partic_phone = forms.CharField(
        label='Telefone (celular) do participante, com DDD',
        max_length=16,
        widget=forms.TextInput(),
        #help_text='Para contato com o participante',
        )
    partic_allergies = forms.CharField(
        label='Alergias',
        max_length=512,
        widget=forms.TextInput(),
        help_text='Alergias a alimentos, remédios, etc.',
        required=False
        )
    partic_name = forms.CharField(
        label='Nome',
        max_length=256,
        widget=forms.TextInput(attrs={'readonly':'readonly'}),
        help_text='Para alterar o nome é necessário contactar o Coordenador Local da OBI na sua escola',
        )
    partic_document = forms.CharField(
        label='Documento (RG)',
        max_length=64,
        widget=forms.TextInput(),
        help_text='Informe o número e órgão emissor (por exemplo, 12.345.678 SSP/SP)',
        )
    partic_cpf = forms.CharField(
        label='CPF',
        max_length=64,
        widget=forms.TextInput(),
        help_text='Se não tiver CPF, deixe em branco',
        required=False,
        )
    partic_accept = forms.BooleanField(
        label='Declaro que li e concordo com as Regras da Semana Olímpica',
        help_text='<br /><a href="/semana/#regras-semana">Regras da Semana Olímpica</a>',
        )

    partic_shirt_size = forms.ChoiceField(
        label='Tamanho de camiseta (altura x largura aprox. em cm)',
        choices = [('','Selecione...')] + SHIRT_SIZE_CHOICES,
        )

    class Meta:
        fieldsets = (
            ('Dados do participante', {
                'fields': ('partic_name','partic_document','partic_cpf','partic_phone','partic_shirt_size', 'partic_allergies')}),
            ('Dados do Responsável Legal', {
                'fields': ('parent_name','parent_type','parent_phone','parent_email')}),
            ('Declaração', {
                'fields': ('partic_accept',)}),
        )

class InformPaymentForm(forms.Form):

    def clean_value(self):
    #    valuestr = self.cleaned_data['value']
    #    valuestr = valuestr.replace('.','')
    #    try:
    #        val,cents = valuestr.split(',')
    #    except:
    #        try:
    #            val = str(int(valuestr))
    #            cents = '00'
    #        except:
    #            raise forms.ValidationError("Valor inválido.")
    #    if len(val) < 2 or len(cents) != 2:
    #        raise forms.ValidationError("Valor inválido.")
    #    value = float(f'{val}.{cents}')
    #    if value <= 0:
    #        raise forms.ValidationError("Valor inválido.")
    #    if len(val) > 3:
    #        return f'{val[:-3]}.{val[-3:]},{cents}'
    #    else:
    #        return f'{val},{cents}'
        valuestr = self.cleaned_data['value']

        num_commas = valuestr.count(',')

        if num_commas > 1:
            raise forms.ValidationError("Separador decimal e/ou de milhar inválido.")

        if num_commas < 1:
            check_sep = valuestr.split('.')
            if len(check_sep) >= 2:
                if len(check_sep[0]) > 3:
                    raise forms.ValidationError("Separador decimal e/ou de milhar inválido.")
                for c in check_sep[1:]:
                    if len(c) != 3:
                        raise forms.ValidationError("Separador decimal e/ou de milhar inválido.")

            valuestr = valuestr.replace('.', '')

            try:
                val = float(valuestr)
            except:
                raise forms.ValidationError("Valor inválido.")

            return f'{valuestr},00'

        if num_commas == 1:
            valuestr = valuestr.replace('.', '')
            value_parts = valuestr.split(',')

            try:
                val = float(value_parts[0])
                val = float(value_parts[1])
            except:
                raise forms.ValidationError("Valor inválido.")

            return f'{value_parts[0]},{value_parts[1][:2]:0<2}'



    def clean_doc_number(self):
        number = self.cleaned_data['doc_number']
        checked = validate_cpf_cnpj(number)
        print(number, checked)
        if not checked:
            raise forms.ValidationError("Número de CPF ou CNPJ inválido.")
        return checked

    def clean_participants(self):
        w = Week.objects.all()
        data = self.cleaned_data['participants']
        lines = data.split('\n')
        for l in lines:
            tks = l.split(',')
            if len(tks) < 2:
                raise forms.ValidationError("Formato errado, número de inscrição e nome devem ser separados por vírgula.\n"
                                            f"Linha com erro: {l}")
            id,check = tks[0].split('-')
            try:
                id = int(id)
            except:
                raise forms.ValidationError("Formato errado, número de inscrição com formato incorreto.\n"
                                            f"Linha com erro: {l}")
            try:
                p = w.get(compet_id=id)
            except:
                raise forms.ValidationError("Formato errado, número de inscrição incorreto, não corresponde a convidado.\n"
                                            f"Linha com erro: {l}")

            if p.compet.compet_id_full != tks[0].strip():
                raise forms.ValidationError("Formato errado, número de inscrição com formato incorreto.\n"
                                            f"Linha com erro: {l}")
            name = tks[1].strip()
            compet_name = p.compet.compet_name.strip()
            if name != compet_name:
                name_tks = name.split(' ')
                compet_tks = compet_name.split(' ')
                count = 0
                for n in name_tks:
                    n = n.strip()
                    for c in compet_tks:
                        c = c.strip()
                        if c and n and c == n:
                            count += 1
                if count < 2:
                    raise forms.ValidationError("Formato errado, nome incorreto, não corresponde ao número de inscrição.\n"
                                            f"Linha com erro: {l}")
        return data

    receipt_file = forms.FileField(
        label='Comprovante de pagamento', 
        required=True,
        help_text='<br>Formato do arquivo deve ser PDF, PNG ou JPEG',
        )
    participants = forms.CharField(
        label='Competidores incluídos no pagamento',
        widget=forms.Textarea(),
        required=True,
        help_text='Informe um participante por linha, cada linha contendo número de inscrição e nome, separados por vírgula. Adicione ou remova participantes editando a lista acima.',
        )
    value = forms.CharField(
        label='Valor',
        max_length=16,
        required=True,
        help_text='Informe o valor pago',
        )
    doc_name = forms.CharField(
        label='Nome',
        widget=forms.Textarea(attrs={'rows':2}),
        required=True,
        help_text='Informe o nome para emissão de Recibo e Nota Fiscal',
        )
    doc_number = forms.CharField(
        label='CNPJ ou CPF',
        max_length=32,
        required=True,
        help_text='Informe CPF ou CNPJ para emissão de Recibo e Nota Fiscal',
        )
    doc_fiscal = forms.BooleanField(
        label = '',
        required = False,
        help_text = 'Um recibo será emitido e disponibilizado para download quando o pagamento for confirmado pela SBC. Marque aqui se necessita também de Nota Fiscal. A Nota Fiscal será emitida com o mesmo nome e CPF/CNPJ do recibo.' 
        )    
    doc_address = forms.CharField(
        label='Endereço postal',
        widget=forms.Textarea(),
        required=True,
        help_text = 'Endereço para envio de Nota Fiscal. Edite se necessário.' 
        )
    doc_email = forms.EmailField(
        label = 'Email',
        required = True,
        help_text = 'Email para envio de cópia digital da Nota Fiscal. Edite se necessário.' 
        )
    doc_notice = forms.CharField(
        label = 'Observações',
        widget=forms.Textarea(attrs={'rows':2}),
        required = False,
        help_text = 'Informe aqui outras informações, como por exemplo dados adicionais que devem ser incluídos na Nota Fiscal' 
        )
    class Meta:
        fieldsets = (
            ('Dados do pagamento', {
                    'fields': ('receipt_file','value','participants')},),
            ('Dados para emissão de Recibo', {
                    'fields': ('doc_name','doc_number')},),
            ('Dados para emissão de Nota Fiscal', {
                    'fields': ('doc_fiscal','doc_email','doc_address','doc_notice')},),
        )


class SBCconfirmPaymentForm(forms.Form):

    participants = forms.CharField(
        label='Competidores incluídos no pagamento',
        widget=forms.Textarea(),
        required=True,
        help_text='Participantes incluídos no pagamento.',
        )
    value = forms.CharField(
        label='Valor',
        max_length=16,
        required=True,
        help_text='Valor pago',
        )
    doc_name = forms.CharField(
        label='Nome',
        widget=forms.Textarea(attrs={'rows':2}),
        required=True,
        help_text='Nome para emissão de Nota Fiscal',
        )
    doc_number = forms.CharField(
        label='CNPJ ou CPF',
        max_length=32,
        required=True,
        )
    doc_fiscal = forms.BooleanField(
        label = '',
        required = False,
        help_text = 'Um recibo será emitido e disponibilizado para download quando o pagamento for confirmado pela SBC. Marque aqui se necessita também de Nota Fiscal. A Nota Fiscal será emitida com o mesmo nome e CPF/CNPJ do recibo.' 
        )    
    doc_email = forms.EmailField(
        label = 'Email',
        required = True,
        help_text = 'Email para envio de cópia digital da Nota Fiscal.' 
        )
    doc_address = forms.CharField(
        label='Endereço postal',
        widget=forms.Textarea(),
        required=True,
        help_text = 'Endereço para envio da Nota Fiscal pelo correio.' 
        )
    doc_notice = forms.CharField(
        label = 'Observações',
        widget=forms.Textarea(attrs={'rows':2}),
        required = False,
        help_text = 'Informe aqui outras informações, como por exemplo dados adicionais que devem ser incluídos na Nota Fiscal' 
        )
    class Meta:
        fieldsets = (
            ('Dados do pagamento', {
                    'fields': ('receipt_file','value','participants')},),
            ('Dados para emissão de Recibo', {
                    'fields': ('doc_name','doc_number')},),
            ('Dados para emissão de Nota Fiscal', {
                    'fields': ('doc_fiscal','doc_email','doc_address','doc_notice')},),
        )

class ParticSemanaFiltroForm(forms.Form):
    partic_type = forms.ChoiceField(
        label='Tipo de participante',
        choices=list(LEVEL_CHOICES_FILTER) + [(10,'Acompanhante')],
        widget=forms.Select(attrs={'class':'select', 'onchange':'this.form.submit()'}),
        required=False,
    )
    partic_order = forms.ChoiceField(
        label='Ordena',
        choices=COMPET_SORT_CHOICES,
        widget=forms.Select(attrs={'class':'select', 'onchange':'this.form.submit()'}),
        required=False,
    )
    partic_name = forms.CharField(
        label='Nome', 
        max_length=200,
        required=False,
        help_text='Digite uma parte do nome desejado e tecle <em>Enter</em>.',
        widget=forms.TextInput(attrs={'onchange':'this.form.submit()'}),
    )

    class Meta:
        fieldsets = (
            ('Filtros', {
                'fields': ('partic_type','partic_order','partic_name')}),
        )


class ConfirmPaymentForm(forms.Form):

    receipt_file = forms.CharField(
        max_length=512,
        widget=forms.HiddenInput()
    )

    participants = forms.CharField(
        label='Competidores incluídos no pagamento',
        widget=forms.Textarea(attrs={'readonly':'readonly'}),
        required=True,
        )

    value = forms.CharField(
        label='Valor',
        max_length=16,
        required=True,
        widget=forms.TextInput(attrs={'readonly':'readonly'}),
        )

    doc_name = forms.CharField(
        label='Nome',
        widget=forms.Textarea(attrs={'rows':2, 'readonly':'readonly'}),
        required=False,
        help_text='Nome para emissão de Nota Fiscal',
        )
    doc_number = forms.CharField(
        label='CNPJ ou CPF',
        widget=forms.TextInput(attrs={'readonly':'readonly'}),
        max_length=64,
        required=False,
        )
    doc_email = forms.CharField(
        label = 'Email',
        widget=forms.TextInput(attrs={'readonly':'readonly'}),
        required = True,
        help_text = 'Email para envio de cópia digital da Nota Fiscal.' 
        )
    doc_address = forms.CharField(
        label='Endereço postal',
        widget=forms.Textarea(attrs={'rows':6, 'readonly':'readonly'}),
        required=False,
        help_text = 'Endereço para envio da Nota Fiscal pelo correio.' 
        )
    doc_fiscal = forms.BooleanField(
        label = '',
        required = False,
        help_text = 'Um recibo será emitido e disponibilizado para download quando o pagamento for confirmado pela SBC. Marque aqui se necessita também de Nota Fiscal. A Nota Fiscal será emitida com o mesmo nome e CPF/CNPJ do recibo.' 
        )    
    doc_notice = forms.CharField(
        label = 'Observações',
        widget=forms.Textarea(attrs={'rows':2}),
        required = False,
        help_text = 'Informe aqui outras informações, como por exemplo dados adicionais que devem ser incluídos na Nota Fiscal' 
        )

    class Meta:
        fieldsets = (
            ('Dados do pagamento', {
                    'fields': ('value','participants')},),
            ('Dados para emissão de Recibo', {
                    'fields': ('doc_name','doc_number')},),
            ('Dados para emissão de Nota Fiscal', {
                    'fields': ('doc_fiscal','doc_email','doc_address','doc_notice')},),
            ('hidden', {
                    'fields': ('receipt_file')}),
        )

class SBCprocessPaymentForm(forms.Form):
    payment_id = forms.CharField(
        label='ID',
        widget=forms.HiddenInput()
        )

    class Meta:
        fieldsets = (
            ('hidden', {
                    'fields': ('payment_id')},),
        )
