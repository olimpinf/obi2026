from django import forms
from django.contrib.auth.models import User
from captcha.fields import CaptchaField
from principal.models import validate_username, capitalize_name
from principal.forms import SCHOOL_YEAR_CHOICES_FORM, SEX_CHOICES

class SaciRegisterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SaciRegisterForm, self).__init__(*args, **kwargs)

    def clean_saci_email(self):
        saci_email = self.cleaned_data.get('saci_email')
        if User.objects.filter(username=saci_email).exists():
            raise forms.ValidationError(
                '"%(email)s" já está registrado.',
                params={'email': saci_email},
            )
        return saci_email

    def clean_saci_name(self):
        name = self.cleaned_data['saci_name']
        tks = name.split()
        if len(tks) < 2:
            raise forms.ValidationError("Informe o nome completo.")        
        name = capitalize_name(name)
        return name
        
    def clean_saci_school_year(self):
        selection = self.cleaned_data['saci_school_year']
        if selection == "Selecione...":
            raise forms.ValidationError("Informe o ano escolar")
        return selection

    saci_name = forms.CharField(
        label='Nome', 
        max_length=200,
        required=True,
        help_text='Insira o nome completo.',
    )
    saci_email = forms.EmailField(
        label='Email',
        required=False,
        help_text='Informe um endereço válido de email. A senha de acesso será enviada para esse endereço.')
    saci_school_year = forms.ChoiceField(
        label='Ano Escolar',
        choices=(('Selecione...','Selecione...'),('Ensino Fundamental','Ensino Fundamental'),('Ensino Médio','Ensino Médio'),
                 ('Ensino Superior','Ensino Superior'),('Outro','Outro')),
        widget=forms.Select(attrs={'class':'select'}),
        required=True,
    )
    saci_sex = forms.ChoiceField(
        label='Gênero',
        choices=SEX_CHOICES,
        widget=forms.RadioSelect(attrs={'class':'horizontal'}),
        required=True,
    )
    saci_birth_year = forms.ChoiceField(
        label='Ano de Nascimento',
        choices= ( [(i,str(i)) for i in range(2015,1930,-1)] ),
        widget=forms.Select(attrs={'class':'select'}),
        required=False,
        initial=2000,
        )
    captcha = CaptchaField(label='Prove que não é um robô, digite o resultado ')

    class Meta:
        fieldsets = (
            ('Dados', {
                'fields': ('saci_name','saci_email','saci_school_year','saci_sex','saci_birth_year','captcha')}),
            )
