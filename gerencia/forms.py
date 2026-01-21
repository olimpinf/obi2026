from django import forms
from django.core.validators import validate_email

class MultiEmailField(forms.Field):
    def to_python(self, value):
        """Normalize data to a list of strings."""
        # Return an empty list if no input was given.
        if not value:
            return []
        return value.split(',')

    def validate(self, value):
        """Check if value consists only of valid emails."""
        # Use the parent's handling of required fields, etc.
        super().validate(value)
        for email in value:
            validate_email(email)


class EnviaConviteRecuperaForm(forms.Form):
    subject = forms.CharField(label='Assunto',required=False)
    class Meta:
        fieldsets = (
            ('Mensagem', {
                    'fields': (('subject'),)}),
        )

class EnviaMensagemForm(forms.Form):
    subject = forms.CharField(label='Assunto')
    message = forms.CharField(label='Texto da Mensagem',widget=forms.Textarea)
    dest_groups = forms.MultipleChoiceField(
        label = '',
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=(('local_coord','Coordenadores locais'),
                 ('colab','Colaboradores'),
                 ('compet_prog','Competidores Programação'),
                 ('compet_inic','Competidores Iniciação'),
                 ),
    )
    email_list = MultiEmailField(label='Email',required=False,help_text='Lista de endereços separados por vírgulas')
    class Meta:
        fieldsets = (
            ('Mensagem', {
                    'fields': (('subject'),('message'))}),
            ('Destinatários', {
                    'fields': (('dest_groups'),('email_list'))}),

        )
