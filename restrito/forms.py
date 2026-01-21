import string

from django import forms
from django.contrib.auth.password_validation import validate_password, password_validators_help_text_html
from principal.models import (LEVEL_CHOICES_INI, LEVEL_CHOICES_PROG,
                              PARTIC_TYPE_CHOICES_FORM, REGULAR_PUBLIC, REGULAR_PRIVATE,
                              COMPET_SORT_CHOICES, COMPET_SORT_CHOICES_CLASS, LEVEL_CHOICES_FORM, LEVEL_CHOICES_CFOBI,
                              LEVEL_CHOICES_FILTER, LEVEL_CHOICES_FILTER_INI, LEVEL_CHOICES_FILTER_PROG,LEVEL_CHOICES_FILTER_CFOBI,
                              SCHOOL_TYPE_CHOICES, SEX_CHOICES, SEX_CHOICES_CFOBI,
                              SCHOOL_YEAR_CHOICES, SCHOOL_YEAR_CHOICES_CFOBI, STATE_CHOICES, Compet, Colab,
                              PJ, P1, P2, PS,
                              School, SubWWW, validate_compet_level, validate_email_colab, validate_username_colab, capitalize_name,)
from principal.utils.utils import obi_year
from principal.models import validate_compet_feminina_level

COMPET_LEVEL_CHOICES = (('',u'Selecione...'),) + LEVEL_CHOICES_INI + LEVEL_CHOICES_PROG
COMPET_LEVEL_CHOICES_CFOBI = (('',u'Selecione...'),) + LEVEL_CHOICES_CFOBI

SCHOOL_YEAR_CHOICES_FORM = (('',u'Selecione...'),) + SCHOOL_YEAR_CHOICES
SCHOOL_YEAR_CHOICES_FORM_CFOBI = (('',u'Selecione...'),) + SCHOOL_YEAR_CHOICES_CFOBI

FORM_ID_CFOBI = ['index', 'prog', 'ini', 'nova']

class CompetInscreveForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CompetInscreveForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        try:
            school = self.request.user.deleg.deleg_school
        except:
            school = self.request.user.colab.colab_school
        compet_type = cleaned_data.get('compet_type')
        compet_year = cleaned_data.get('compet_year')
        compet_class = cleaned_data.get('compet_class')
        compet_name = cleaned_data.get('compet_name')
        compet_email = cleaned_data.get('compet_email')

        result = validate_compet_level(compet_type, compet_year, school.school_type)
        if result:
            self.add_error('compet_type', result)
        # email nao usado
        #if compet_email:
        #    compet_email.strip()
        #if not compet_email and int(compet_type) in (PJ, P1, P2, PS):
        #    self.add_error('compet_email', 'Email é obrigatório para competidores da Modalidade Programação')
        return self.cleaned_data

    def clean_compet_name(self):
        name = self.cleaned_data['compet_name']
        tks = name.split()
        if len(tks) < 2:
            raise forms.ValidationError("Informe o nome completo.")
        try:
            school_id = self.request.user.deleg.deleg_school.pk
        except:
            school_id = self.request.user.colab.colab_school.pk
        compet_exists = Compet.objects.filter(compet_name__iexact=name,compet_school_id=school_id).count()
        if compet_exists > 0:
            raise forms.ValidationError("Nome de competidor já inscrito.")
        name = capitalize_name(name)
        return name

    compet_name = forms.CharField(
        label='Nome do(a) Competidor(a)',
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        help_text='Insira o nome completo, com a grafia correta. O nome será utilizado na emissão do certificado de participação.',
    )
    compet_type = forms.ChoiceField(
        label='Modalidade',
        choices=COMPET_LEVEL_CHOICES,
        widget=forms.Select(attrs={'class':'form-select'}),
        required=True,
        help_text='Cada competidor(a) pode ser inscrito(a) em uma única modalidade.',
    )
    compet_year = forms.ChoiceField(
        label='Ano Escola',
        choices=SCHOOL_YEAR_CHOICES_FORM,
        widget=forms.Select(attrs={'class':'form-select'}),
        required=True,
    )
    compet_class = forms.CharField(
        label='Turma Escola',
        max_length=8,
        required=True,
        widget=forms.TextInput(attrs={'class':'form-control'}),        
        initial='A',
    )
    compet_sex = forms.ChoiceField(
        label='Gênero',
        choices=SEX_CHOICES,
        widget=forms.RadioSelect(attrs={'class':'horizontal'}),
        required=True,
    )
    compet_email = forms.EmailField(
        label='Email',
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control'}),        
        help_text='''Utilizado para enviar a senha de acesso à página
        pessoal de competidor na OBI. Não é necessário que seja único.
        Se não fornecido coordenador deve entregar a senha ao competidor
        (senhas de todos os competidores da escola estão disponíveis na página de coordenação).'''
    )
    compet_birth_date = forms.DateField(
        label='Data de Nascimento',
        widget=forms.SelectDateWidget(years=list(range(1980,2018)),attrs={'class':'form-select'}),
        required=False,
        initial='01/01/2010',
  )

    ###########
    # extra information

    compet_mother_name = forms.CharField(
        label='Nome da mãe do(a) Competidor(a)',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        help_text='Insira o nome completo, com a grafia correta.',
    )
    compet_cpf = forms.CharField(
        label='CPF',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        help_text='Cadastro de pessoa física.'
    )
    compet_nis = forms.CharField(
        label='NIS',
        max_length=11,
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        help_text='Número de identificação social, se aplicável.',
    )
    class Meta:
        fieldsets = (
            ('Dados Obrigatórios', {
                'fields': ('compet_name','compet_year','compet_class','compet_type','compet_sex','compet_birth_date')}
             ),
            ('Dados Opcionais', {
                'fields': ('compet_email', 'compet_mother_name', 'compet_cpf','compet_nis')}
             ),
        )


class CompetFemininaInscreveForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CompetFemininaInscreveForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        try:
            school = self.request.user.deleg.deleg_school
        except:
            school = self.request.user.colab.colab_school
        compet_type = cleaned_data.get('compet_type')
        compet_year = cleaned_data.get('compet_year')
        compet_class = cleaned_data.get('compet_class')
        compet_name = cleaned_data.get('compet_name')
        compet_email = cleaned_data.get('compet_email')

        result = validate_compet_level(compet_type, compet_year, school.school_type)
        if result:
            self.add_error('compet_type', result)

        return self.cleaned_data


    def clean_compet_name(self):
        name = self.cleaned_data['compet_name']
        tks = name.split()
        if len(tks) < 2:
            raise forms.ValidationError("Informe o nome completo.")
        try:
            school_id = self.request.user.deleg.deleg_school.pk
        except:
            school_id = self.request.user.colab.colab_school.pk
        compet_exists = Compet.objects.filter(compet_name__iexact=name,compet_school_id=school_id).count()
        if compet_exists > 0:
            raise forms.ValidationError("Nome da competidora já inscrito.")
        name = capitalize_name(name)
        return name


    compet_name = forms.CharField(
        label='Nome da Competidora',
        widget=forms.TextInput(attrs={'class':'form-control'}),        
        max_length=200,
        required=True,
        help_text='Insira o nome completo, com a grafia correta. O nome será utilizado na emissão do certificado de participação.',
    )
    compet_type = forms.ChoiceField(
        label='Modalidade',
        choices=COMPET_LEVEL_CHOICES_CFOBI,
        widget=forms.Select(attrs={'class':'form-select'}),
        required=True,
        help_text='Cada competidora pode ser inscrita em uma única modalidade.',
    )
    compet_year = forms.ChoiceField(
        label='Ano Escola',
        choices=SCHOOL_YEAR_CHOICES_FORM_CFOBI,
        widget=forms.Select(attrs={'class':'form-select'}),
        required=True,
    )
    compet_class = forms.CharField(
        label='Turma Escola',
        widget=forms.TextInput(attrs={'class':'form-control'}),        
        max_length=8,
        required=True,
        initial='A',
    )
    compet_sex = forms.ChoiceField(
        label='Gênero',
        choices=SEX_CHOICES_CFOBI,
        widget=forms.RadioSelect(attrs={'class':'horizontal'}),
        required=True,
    )
    compet_email = forms.EmailField(
        label='Email',
        required=False,
        help_text='''Utilizado para enviar a senha de acesso à página
        pessoal de competidor na OBI. Não é necessário que seja único.
        Se não fornecido coordenador deve entregar a senha ao competidor
        (senhas de todos os competidores da escola estão disponíveis na página de coordenação).'''
    )
    compet_birth_date = forms.DateField(
        label='Data de Nascimento',
        widget=forms.SelectDateWidget(years=list(range(1980,2018)),attrs={'class':'form-control'}),
        required=False,
        initial='01/01/2010',
    )

    ###########
    # extra information

    compet_mother_name = forms.CharField(
        label='Nome da mãe da Competidora',
        widget=forms.TextInput(attrs={'class':'form-control'}),        
        max_length=200,
        required=False,
        help_text='Insira o nome completo, com a grafia correta.',
    )
    compet_cpf = forms.CharField(
        label='CPF',
        widget=forms.TextInput(attrs={'class':'form-control'}),        
        max_length=200,
        required=False,
        help_text='Cadastro de pessoa física.'
    )
    compet_nis = forms.CharField(
        label='NIS',
        widget=forms.TextInput(attrs={'class':'form-control'}),        
        max_length=11,
        required=False,
        help_text='Número de identificação social.',
    )

    class Meta:
        fieldsets = (
            ('Dados Obrigatórios', {
                'fields': ('compet_name','compet_year','compet_class','compet_type','compet_sex','compet_birth_date')}
             ),
            ('Dados Opcionais', {
                'fields': ('compet_email', 'compet_mother_name', 'compet_cpf','compet_nis')}
             ),
        )


class CompetInscreveLoteForm(forms.Form):
    data = forms.FileField(
        label='Arquivo',
        required=True,
        widget=forms.FileInput(attrs={'class':'form-control'}),
        help_text='Veja o formato do arquivo nas instruções.',
    )

    class Meta:
        fieldsets = (
            ('Dados', { 'fields': ('data') }),
        )


class CompetEditaForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CompetEditaForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        try:
            school = self.request.user.deleg.deleg_school
        except:
            school = self.request.user.colab.colab_school
        if self.request.POST.get('delete'):
            return
        compet_type = cleaned_data.get('compet_type')
        compet_year = cleaned_data.get('compet_year')
        compet_class = cleaned_data.get('compet_class')
        compet_name = cleaned_data.get('compet_name')
        compet_email = cleaned_data.get('compet_email')
        compet_email_cur = cleaned_data.get('compet_email_cur')

        result = validate_compet_level(compet_type, compet_year, school.school_type)
        if result:
            self.add_error('compet_type', result)
        if compet_email:
            compet_email.strip()
        if not compet_email and int(compet_type) in (PJ, P1, P2, PS):
            self.add_error('compet_email', 'Email é obrigatório para competidores da Modalidade Programação')
        return self.cleaned_data

    def clean_compet_name(self):
        name = self.cleaned_data['compet_name']
        tks = name.split()
        if len(tks) < 2:
            raise forms.ValidationError("Informe o nome completo.")
        id = self.cleaned_data['compet_id']
        try:
            school_id = self.request.user.deleg.deleg_school.pk
        except:
            school_id = self.request.user.colab.colab_school.pk
        compet_exists = Compet.objects.filter(compet_name__iexact=name,compet_school_id=school_id).exclude(compet_id=id)
        if len(compet_exists) > 0:
            raise forms.ValidationError("Nome de competidor já inscrito.")
        name = capitalize_name(name)
        return name

    def clean_compet_mother_name(self):
        name = self.cleaned_data['compet_mother_name']
        if not name:
            return name
        tks = name.split()
        if len(tks) < 2:
            raise forms.ValidationError("Informe o nome completo.")
        name = capitalize_name(name)
        return name

    def clean_compet_cpf(self):
        cpf = self.cleaned_data['compet_cpf']
        if not cpf:
            return cpf
        cleaned = ''
        for c in cpf:
            if c in string.digits:
                cleaned += c
        cpf = cleaned
        if len(cpf) != 11:
            raise forms.ValidationError("CPF inválido.")
        cpf = f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'
        return cpf

    def clean_compet_nis(self):
        cpf = self.cleaned_data['compet_nis']
        if not cpf:
            return cpf
        cleaned = ''
        for c in cpf:
            if c in string.digits:
                cleaned += c
        cpf = cleaned
        if len(cpf) != 11:
            raise forms.ValidationError("NIS inválido.")
        cpf = f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'
        return cpf

    compet_id_full = forms.CharField(
        label='Num. Inscr.',
        max_length=9,
        required=True,
        widget=forms.TextInput(attrs={'class':'form-control','readonly':'readonly'}),
    )
    compet_id = forms.CharField(
        label='Num. Inscr.',
        max_length=9,
        required=True,
        widget=forms.TextInput(attrs={'class':'form-control','readonly':'readonly'}),
    )
    compet_name = forms.CharField(
        label='Nome do(a) Competidor(a)',
        widget=forms.TextInput(attrs={'class':'form-control'}),        
        max_length=200,
        required=True,
        help_text='Insira o nome completo, com a grafia correta. O nome será utilizado na emissão do certificado de participação.',
    )
    compet_type = forms.ChoiceField(
        label='Modalidade',
        choices=COMPET_LEVEL_CHOICES,
        widget=forms.Select(attrs={'class':'form-select'}),
        required=True,
        help_text='Cada competidor(a) pode ser inscrito(a) em uma única modalidade.',
    )
    compet_year = forms.ChoiceField(
        label='Ano Escola',
        choices=SCHOOL_YEAR_CHOICES_FORM,
        widget=forms.Select(attrs={'class':'form-select'}),
        required=True,
    )
    compet_class = forms.CharField(
        label='Turma Escola',
        widget=forms.TextInput(attrs={'class':'form-control'}),        
        max_length=8,
        required=True,
        initial='A',
    )
    compet_sex = forms.ChoiceField(
        label='Gênero',
        choices=SEX_CHOICES,
        widget=forms.RadioSelect(attrs={'class':'horizontal'}),
        required=True,
    )
    compet_email = forms.EmailField(
        widget=forms.TextInput(attrs={'class':'form-control'}),        
        label='Email',
        required=False,
    )
    compet_email_cur = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )
    compet_birth_date = forms.DateField(
        label='Data de Nascimento',
        widget=forms.SelectDateWidget(years=list(range(1990,2019)),attrs={'class':'form-control'}),
        required=False,
        )
    ###########
    # extra information

    compet_mother_name = forms.CharField(
        label='Nome da mãe do(a) Competidor(a)',
        widget=forms.TextInput(attrs={'class':'form-control'}),        
        max_length=200,
        required=False,
        help_text='Insira o nome completo, com a grafia correta.',
    )
    compet_cpf = forms.CharField(
        label='CPF',
        widget=forms.TextInput(attrs={'class':'form-control'}),        
        max_length=20,
        required=False,
        help_text='Cadastro de pessoa física do(a) competidor(a).'
    )
    compet_nis = forms.CharField(
        label='NIS',
        widget=forms.TextInput(attrs={'class':'form-control'}),        
        max_length=20,
        required=False,
        help_text='Número de identificação social do(a) competidor(a).',
    )

    class Meta:
        fieldsets = (
            ('Dados Obrigatórios', {
                'fields': ('compet_id_full', 'compet_name','compet_year','compet_class','compet_type','compet_sex','compet_birth_date')}
            ),
            ('Dados Opcionais', {
                'fields': ('compet_email', 'compet_mother_name', 'compet_cpf','compet_nis')}
            ),
            ('hidden', {
                'fields': ('compet_email_cur')}
            ),
        )


class CompetFemininaEditaForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CompetFemininaEditaForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        try:
            school = self.request.user.deleg.deleg_school
        except:
            school = self.request.user.colab.colab_school
        if self.request.POST.get('delete'):
            return
        compet_type = cleaned_data.get('compet_type')
        compet_year = cleaned_data.get('compet_year')
        compet_class = cleaned_data.get('compet_class')
        compet_name = cleaned_data.get('compet_name')
        compet_email = cleaned_data.get('compet_email')
        compet_email_cur = cleaned_data.get('compet_email_cur')

        result = validate_compet_level(compet_type, compet_year, school.school_type)
        if result:
            self.add_error('compet_type', result)

        id = int(self.cleaned_data['compet_id'])
        compet_obi = Compet.objects.get(pk=id)
        result = validate_compet_feminina_level(compet_obi.compet_type, compet_type)
        if result:
            self.add_error('compet_type', result)

        if compet_email:
            compet_email.strip()
        if not compet_email:
            self.add_error('compet_email', 'Email é obrigatório para competidoras da CF-OBI')
        return self.cleaned_data

    def clean_compet_name(self):
        name = self.cleaned_data['compet_name']
        tks = name.split()
        if len(tks) < 2:
            raise forms.ValidationError("Informe o nome completo.")
        id = self.cleaned_data['compet_id']
        try:
            school_id = self.request.user.deleg.deleg_school.pk
        except:
            school_id = self.request.user.colab.colab_school.pk
        compet_exists = Compet.objects.filter(compet_name__iexact=name,compet_school_id=school_id).exclude(compet_id=id)
        if len(compet_exists) > 0:
            raise forms.ValidationError("Nome da competidora já inscrito.")
        name = capitalize_name(name)
        return name

    def clean_compet_mother_name(self):
        name = self.cleaned_data['compet_mother_name']
        if not name:
            return name
        tks = name.split()
        if len(tks) < 2:
            raise forms.ValidationError("Informe o nome completo.")
        name = capitalize_name(name)
        return name

    def clean_compet_cpf(self):
        cpf = self.cleaned_data['compet_cpf']
        if not cpf:
            return cpf
        cleaned = ''
        for c in cpf:
            if c in string.digits:
                cleaned += c
        cpf = cleaned
        if len(cpf) != 11:
            raise forms.ValidationError("CPF inválido.")
        cpf = f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'
        return cpf

    def clean_compet_nis(self):
        cpf = self.cleaned_data['compet_nis']
        if not cpf:
            return cpf
        cleaned = ''
        for c in cpf:
            if c in string.digits:
                cleaned += c
        cpf = cleaned
        if len(cpf) != 11:
            raise forms.ValidationError("NIS inválido.")
        cpf = f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'
        return cpf

    compet_id_full = forms.CharField(
        label='Num. Inscr.',
        max_length=9,
        required=True,
        widget=forms.TextInput(attrs={'class':'form-control','readonly':'readonly'}),
    )
    compet_id = forms.CharField(
        label='Num. Inscr.',
        max_length=9,
        required=True,
        widget=forms.TextInput(attrs={'class':'form-control','readonly':'readonly'}),
    )
    compet_name = forms.CharField(
        label='Nome da Competidora',
        widget=forms.TextInput(attrs={'class':'form-control'}),        
        max_length=200,
        required=True,
        help_text='Insira o nome completo, com a grafia correta. O nome será utilizado na emissão do certificado de participação.',
    )
    compet_type = forms.ChoiceField(
        label='Modalidade',
        choices=COMPET_LEVEL_CHOICES_CFOBI,
        widget=forms.Select(attrs={'class':'form-select'}),
        required=True,
        help_text='Cada competidora pode ser inscrita em uma única modalidade.',
    )
    compet_year = forms.ChoiceField(
        label='Ano Escola',
        choices=SCHOOL_YEAR_CHOICES_FORM_CFOBI,
        widget=forms.Select(attrs={'class':'form-select'}),
        required=True,
    )
    compet_class = forms.CharField(
        label='Turma Escola',
        widget=forms.TextInput(attrs={'class':'form-control'}),        
        max_length=8,
        required=True,
        initial='A',
    )
    compet_sex = forms.ChoiceField(
        label='Gênero',
        choices=SEX_CHOICES_CFOBI,
        widget=forms.RadioSelect(attrs={'class':'horizontal'}),
        required=True,
    )
    compet_email = forms.EmailField(
        label='Email',
        widget=forms.TextInput(attrs={'class':'form-control'}),        
        required=False,
    )
    compet_email_cur = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )
    compet_birth_date = forms.DateField(
        label='Data de Nascimento',
        widget=forms.SelectDateWidget(years=list(range(1980,2018)),attrs={'class':'form-select'}),
        required=False,
        )
    ###########
    # extra information

    compet_mother_name = forms.CharField(
        label='Nome da mãe da Competidora',
        widget=forms.TextInput(attrs={'class':'form-control'}),        
        max_length=200,
        required=False,
        help_text='Insira o nome completo, com a grafia correta.',
    )
    compet_cpf = forms.CharField(
        label='CPF',
        widget=forms.TextInput(attrs={'class':'form-control'}),        
        max_length=20,
        required=False,
        help_text='Cadastro de pessoa física da competidora.'
    )
    compet_nis = forms.CharField(
        label='NIS',
        widget=forms.TextInput(attrs={'class':'form-control'}),        
        max_length=20,
        required=False,
        help_text='Número de identificação social da competidora.',
    )

    class Meta:
        fieldsets = (
            ('Dados Obrigatórios', {
                'fields': ('compet_id_full', 'compet_name','compet_year','compet_class','compet_type','compet_sex','compet_birth_date')}
            ),
            ('Dados Opcionais', {
                'fields': ('compet_email', 'compet_mother_name', 'compet_cpf','compet_nis')}
            ),
            ('hidden', {
                'fields': ('compet_email_cur')}
            ),
        )


class CompetValidaForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CompetValidaForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        try:
            school = self.request.user.deleg.deleg_school
        except:
            school = self.request.user.colab.colab_school
        compet_type = self.cleaned_data.get('compet_type')
        compet_year = self.cleaned_data.get('compet_year')
        compet_email = self.cleaned_data.get('compet_email')
        compet_email_cur = cleaned_data.get('compet_email_cur')
        result = validate_compet_level(compet_type, compet_year, school.school_type)
        if result:
            self.add_error('compet_type', result)
        return self.cleaned_data

    def clean_compet_name(self):
        name = self.cleaned_data['compet_name']
        tks = name.split()
        if len(tks) < 2:
            raise forms.ValidationError("Informe o nome completo.")
        name = capitalize_name(name)
        return name

    # dealt with in views, use the information of the update button
    # def clean_compet_name(self):
    #     name = self.cleaned_data['compet_name']
    #     school_id = self.request.user.deleg.deleg_school.school_id
    #     compet_exists = Compet.objects.filter(compet_name__iexact=name,compet_school_id=school_id)
    #     if len(compet_exists) > 0:
    #         raise forms.ValidationError("Nome de competidor já inscrito.")
    #     name = capitalize_name(name)
    #     return name

    id = forms.IntegerField(
        widget=forms.HiddenInput(),
    )

    compet_name = forms.CharField(
        label='Nome do(a) Competidor(a)',
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={'class':'form-control','readonly':'readonly'}),
        # no change here
        #help_text='Insira o nome completo, com a grafia correta. O nome será utilizado na emissão do certificado de participação.',
    )
    compet_type = forms.ChoiceField(
        label='Modalidade',
        choices=COMPET_LEVEL_CHOICES,
        widget=forms.Select(attrs={'class':'form-select'}),
        required=True,
        help_text='Cada competidor(a) pode ser inscrito(a) em uma única modalidade.',
    )
    compet_year = forms.ChoiceField(
        label='Ano Escola',
        choices=SCHOOL_YEAR_CHOICES_FORM,
        widget=forms.Select(attrs={'class':'form-select'}),
        required=True,
    )
    compet_class = forms.CharField(
        label='Turma Escola',
        widget=forms.TextInput(attrs={'class':'form-control'}),        
        max_length=8,
        required=True,
        initial='A',
    )
    compet_sex = forms.ChoiceField(
        label='Gênero',
        choices=SEX_CHOICES,
        widget=forms.RadioSelect(attrs={'class':'horizontal'}),
        required=True,
    )
    compet_email = forms.EmailField(
        label='Email',
        widget=forms.TextInput(attrs={'class':'form-control'}),        
        required=False,
    )
    compet_email_cur = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )
    compet_birth_date = forms.DateField(
        label='Data de Nascimento',
        widget=forms.SelectDateWidget(years=list(range(1980,2018)),attrs={'class':'form-select'}),
        required=False,
        )

    class Meta:
        fieldsets = (
            ('Dados', {
                'fields': ('compet_name','compet_year','compet_class','compet_type','compet_sex','compet_birth_date','compet_email')}),
            ('hidden', {
                'fields': ('id', 'compet_email_cur')}),
        )


class CompetFiltroForm(forms.Form):
    compet_type = forms.ChoiceField(
        label='Modalidade',
        choices=LEVEL_CHOICES_FILTER,
        widget=forms.Select(attrs={'class':'form-select', 'onchange':'this.form.submit()'}),
        required=False,
    )
    compet_order = forms.ChoiceField(
        label='Ordena',
        choices=COMPET_SORT_CHOICES,
        widget=forms.Select(attrs={'class':'form-select', 'onchange':'this.form.submit()'}),
        required=False,
    )
    compet_name = forms.CharField(
        label='Nome',
        max_length=200,
        required=False,
        help_text='Digite uma parte do nome desejado e tecle <em>Enter</em>.',
        widget=forms.TextInput(attrs={'class':'form-control','onchange':'this.form.submit()'}),
    )

    class Meta:
        fieldsets = (
            ('Filtros', {
                'fields': ('compet_type','compet_order','compet_name')}),
        )


class CompetFemininaFiltroForm(forms.Form):
    def __init__(self, *args, **kwargs):
        compet_type_choices = kwargs.pop('compet_type_choices', LEVEL_CHOICES_FILTER_CFOBI)
        super(CompetFemininaFiltroForm, self).__init__(*args, **kwargs)
        self.fields['compet_type'].choices = compet_type_choices

    compet_type = forms.ChoiceField(
        label='Modalidade',
        widget=forms.Select(attrs={'class':'form-select', 'onchange':'this.form.submit()'}),
        required=False,
    )
    compet_order = forms.ChoiceField(
        label='Ordena',
        choices=COMPET_SORT_CHOICES,
        widget=forms.Select(attrs={'class':'form-select', 'onchange':'this.form.submit()'}),
        required=False,
    )
    compet_name = forms.CharField(
        label='Nome',
        max_length=200,
        required=False,
        help_text='Digite uma parte do nome desejado e tecle <em>Enter</em>.',
        widget=forms.TextInput(attrs={'class':'form-control', 'onchange':'this.form.submit()'}),
    )

    class Meta:
        fieldsets = (
            ('Filtros', {
                'fields': ('compet_type','compet_order','compet_name')}),
        )


class CompetFemininaPontosFiltroForm(forms.Form):
    def __init__(self, *args, **kwargs):
        compet_type_choices = kwargs.pop('compet_type_choices', LEVEL_CHOICES_FILTER_CFOBI)
        super(CompetFemininaPontosFiltroForm, self).__init__(*args, **kwargs)
        self.fields['compet_type'].choices = compet_type_choices

    compet_type = forms.ChoiceField(
        label='Modalidade',
        widget=forms.Select(attrs={'class':'form-select', 'onchange':'this.form.submit()'}),
        required=False,
    )
    compet_order = forms.ChoiceField(
        label='Ordena',
        choices=COMPET_SORT_CHOICES+[('compet_points','Pontuação')],
        widget=forms.Select(attrs={'class':'form-select', 'onchange':'this.form.submit()'}),
        required=False,
    )
    compet_name = forms.CharField(
        label='Nome',
        max_length=200,
        required=False,
        help_text='Digite uma parte do nome desejado e tecle <em>Enter</em>.',
        widget=forms.TextInput(attrs={'class':'form-control', 'onchange':'this.form.submit()'}),
    )

    class Meta:
        fieldsets = (
            ('Filtros', {
                'fields': ('compet_type','compet_order','compet_name')}),
        )


class CompetIniPontosFiltroForm(forms.Form):
    compet_type = forms.ChoiceField(
        label='Modalidade',
        choices=LEVEL_CHOICES_FILTER_INI,
        widget=forms.Select(attrs={'class':'form-select', 'onchange':'this.form.submit()'}),
        required=False,
    )
    compet_order = forms.ChoiceField(
        label='Ordena',
        choices=COMPET_SORT_CHOICES+[('compet_points','Pontuação')],
        widget=forms.Select(attrs={'class':'form-select', 'onchange':'this.form.submit()'}),
        required=False,
    )
    compet_name = forms.CharField(
        label='Nome',
        max_length=200,
        required=False,
        help_text='Digite uma parte do nome desejado e tecle <em>Enter</em>.',
        widget=forms.TextInput(attrs={'class':'form-control', 'onchange':'this.form.submit()'}),
    )

    class Meta:
        fieldsets = (
            ('Filtros', {
                'fields': ('compet_type','compet_order','compet_name',)}),
        )

class CompetProgPontosFiltroForm(forms.Form):
    compet_type = forms.ChoiceField(
        label='Modalidade',
        choices=LEVEL_CHOICES_FILTER_PROG,
        widget=forms.Select(attrs={'class':'form-select', 'onchange':'this.form.submit()'}),
        required=False,
    )
    compet_order = forms.ChoiceField(
        label='Ordena',
        choices=COMPET_SORT_CHOICES+[('compet_points','Pontuação')],
        widget=forms.Select(attrs={'class':'form-select', 'onchange':'this.form.submit()'}),
        required=False,
    )
    compet_name = forms.CharField(
        label='Nome', 
        max_length=200,
        required=False,
        help_text='Digite uma parte do nome desejado e tecle <em>Enter</em>.',
        widget=forms.TextInput(attrs={'class':'form-control', 'onchange':'this.form.submit()'}),
    )

    class Meta:
        fieldsets = (
            ('Filtros', {
                'fields': ('compet_type','compet_order','compet_name',)}),
        )

class CompetIniFiltroForm(forms.Form):
    compet_type = forms.ChoiceField(
        label='Modalidade',
        choices=LEVEL_CHOICES_FILTER_INI,
        widget=forms.Select(attrs={'class':'form-select', 'onchange':'this.form.submit()'}),
        required=False,
    )
    compet_order = forms.ChoiceField(
        label='Ordena',
        choices=COMPET_SORT_CHOICES,
        widget=forms.Select(attrs={'class':'form-select', 'onchange':'this.form.submit()'}),
        required=False,
    )
    compet_name = forms.CharField(
        label='Nome', 
        max_length=200,
        required=False,
        help_text='Digite uma parte do nome desejado e tecle <em>Enter</em>.',
        widget=forms.TextInput(attrs={'class':'form-control', 'onchange':'this.form.submit()'}),
    )

    class Meta:
        fieldsets = (
            ('Filtros', {
                'fields': ('compet_type','compet_order','compet_name')}),
        )


class CompetProgFiltroForm(forms.Form):
    compet_type = forms.ChoiceField(
        label='Modalidade',
        choices=LEVEL_CHOICES_FILTER_PROG,
        widget=forms.Select(attrs={'class':'form-select', 'onchange':'this.form.submit()'}),
        required=False,
    )
    compet_order = forms.ChoiceField(
        label='Ordena',
        choices=COMPET_SORT_CHOICES,
        widget=forms.Select(attrs={'class':'form-select', 'onchange':'this.form.submit()'}),
        required=False,
    )
    compet_name = forms.CharField(
        label='Nome', 
        max_length=200,
        required=False,
        help_text='Digite uma parte do nome desejado e tecle <em>Enter</em>.',
        widget=forms.TextInput(attrs={'class':'form-control', 'onchange':'this.form.submit()'}),
    )

    class Meta:
        fieldsets = (
            ('Filtros', {
                'fields': ('compet_type','compet_order','compet_name')}),
        )

class CompetPreRegFiltroForm(forms.Form):
    compet_type = forms.ChoiceField(
        label='Modalidade',
        choices=LEVEL_CHOICES_FILTER,
        widget=forms.Select(attrs={'class':'form-select', 'onchange':'this.form.submit()'}),
        required=False,
    )
    compet_name = forms.CharField(
        label='Nome',
        max_length=200,
        required=False,
        help_text='Digite uma parte do nome desejado e tecle <em>Enter</em>.',
        widget=forms.TextInput(attrs={'class':'form-control', 'onchange':'this.form.submit()'}),
    )

    class Meta:
        fieldsets = (
            ('Filtros', {
                'fields': ('compet_type','compet_name')}),
        )


class CompetSenhasFiltroForm(forms.Form):
    compet_type = forms.ChoiceField(
        label='Modalidade',
        choices=LEVEL_CHOICES_FILTER,
        #widget=forms.Select(attrs={'class':'form-select', 'onchange':'this.form.submit()'}),
        widget=forms.Select(attrs={'class':'form-select'}),
        required=False,
    )
    compet_order = forms.ChoiceField(
        label='Ordena por',
        choices=COMPET_SORT_CHOICES_CLASS,
        #widget=forms.Select(attrs={'class':'form-select', 'onchange':'this.form.submit()'}),
        widget=forms.Select(attrs={'class':'form-select'}),
        required=False,
    )

    class Meta:
        fieldsets = (
            ('Filtros', {
                'fields': ('compet_type','compet_order',)}),
        )


class CompetFemininaSenhasFiltroForm(forms.Form):
    # attest = forms.ChoiceField(
    #     label='Li e concordo com a declaração acima',
    #     choices=((False, 'False'), (True,'True')),
    #     widget=forms.CheckboxInput(),
    #     required=True,
    # )
    compet_type = forms.ChoiceField(
        label='Modalidade',
        choices=LEVEL_CHOICES_FILTER_CFOBI,
        widget=forms.Select(attrs={'class':'form-select'}),
        required=False,
    )
    compet_order = forms.ChoiceField(
        label='Ordena por',
        choices=COMPET_SORT_CHOICES,
        widget=forms.Select(attrs={'class':'form-select'}),
        required=False,
    )

    class Meta:
        fieldsets = (
#            ('', {
#                'fields': ('attest',)}),
            ('Filtros', {
                'fields': ('compet_type','compet_order',)}),
        )


class CompetSenhasCmsFiltroForm(forms.Form):
    # attest = forms.ChoiceField(
    #     label='Li e concordo com a declaração acima',
    #     widget=forms.CheckboxInput(),
    #     required=True,
    # )
    compet_type = forms.ChoiceField(
        label='Nível',
        choices=LEVEL_CHOICES_FILTER_PROG,
        widget=forms.Select(attrs={'class':'form-select'}),
        required=False,
    )
    compet_order = forms.ChoiceField(
        label='Ordena por',
        choices=COMPET_SORT_CHOICES_CLASS,
        widget=forms.Select(attrs={'class':'form-select'}),
        required=False,
    )

    class Meta:
        fieldsets = (
            # ('', {
            #     'fields': ('attest',)}),
            ('Filtros', {
                'fields': ('compet_type','compet_order',)}),
        )

class EscolaEditaForm(forms.Form):
    """The only difference from EscolaInepEditaForm is the display value on school_inep_code! Must exist a better way"""

    def clean_school_inep_code(self):
        school_inep_code = int(self.cleaned_data['school_inep_code'])
        school_type = int(self.cleaned_data['school_type'])
        if school_type in [REGULAR_PUBLIC,REGULAR_PRIVATE]:
            if school_inep_code == 0:
                raise forms.ValidationError("Forneça o Código INEP da Escola.")
            # retirado, não é verdade!
            #if len(str(school_inep_code)) != 8:
            #    raise forms.ValidationError("Código INEP da Escola inválido.")
        return school_inep_code

    school_name = forms.CharField(
        label='Nome da Escola', 
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=200,
        )
    school_type = forms.ChoiceField(
        label='Tipo da Escola',
        choices=(SCHOOL_TYPE_CHOICES ),
        widget=forms.Select(attrs={'class':'form-select','onchange':'_showHideSchoolType("id_school_inep_code")'}),
        )
    school_inep_code = forms.IntegerField(
        label='Código INEP da Escola',
        help_text='Apenas para Escolas de Ensino Básico.',
        required=False,
        widget=forms.NumberInput(attrs={'style':'display:none'}),
        )
    school_phone = forms.CharField(
        label='Telefone da Escola, com DDD',
        max_length=16,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        help_text='Para contato com a Escola.',
        )
    school_zip = forms.CharField(
        label='CEP',
        max_length=10,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        help_text='Informe o CEP e pressione a tecla TAB no seu teclado; os campos Logradouro, Bairro, Cidade e Estado serão completados automaticamente. Se você não sabe o CEP, <a href="http://www.buscacep.correios.com.br/sistemas/buscacep/" target="_blank">consulte aqui</a>.'
        )
    school_address = forms.CharField(
        label='Logradouro',
        max_length=256,
        widget=forms.Textarea(attrs={'class':'form-control'}),
        required=False,
        )
    school_address_number = forms.CharField(
        label='Número',
        max_length=16,
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        )
    school_address_complement = forms.CharField(
        label='Complemento',
        max_length=128,
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        )
    school_address_district = forms.CharField(
        label='Bairro/Distrito',
        max_length=32,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        required = False,
        )
    school_city = forms.CharField(
        label='Cidade',
        max_length=128,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        )
    school_state = forms.ChoiceField(
        label='Estado',
        choices=(STATE_CHOICES),
        widget=forms.Select(attrs={'class':'form-select'}),
        )
    school_address_building = forms.CharField(
        label='Local da Prova',
        max_length=1024,
        widget=forms.Textarea(attrs={'class':'form-control'}),
        required=False,
        )
    school_address_map = forms.CharField(
        label='Mapa',
        max_length=1024,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        required=False,
        help_text='Coloque aqui um link para um mapa (por exemplo do Google Maps), indicando o local da prova.<br>Exemplo: https://www.google.com/maps/d/u/0/viewer?mid=1SJpZrtX4Xg_oyRPx1heCxYykprc&hl=en_US&ll=-22.81353899999999%2C-47.063799&z=17',
        )
    school_address_other = forms.CharField(
        label='Outras informações',
        max_length=1024,
        widget=forms.Textarea(attrs={'class':'form-control'}),
        required=False,
        help_text='Coloque aqui outras informações que forem necessárias, como por exemplo alteração no horário de aplicação das provas, por alguma restrição local.'
        )
    class Meta:
        fieldsets = (
            ('Dados da Escola', {
                    'fields': ('school_name','school_type','school_inep_code','school_phone','school_zip','school_address','school_address_number','school_address_complement','school_address_district','school_city','school_state', 'school_address_building', 'school_address_map','school_address_other')}),
        )


class EscolaEditaInepForm(forms.Form):
    """The only difference from EscolaEditaForm is the display value on school_inep_code! Must be a better way"""

    def clean_school_inep_code(self):
        school_inep_code = int(self.cleaned_data['school_inep_code'])
        school_type = int(self.cleaned_data['school_type'])
        if school_type in [REGULAR_PUBLIC,REGULAR_PRIVATE]:
            if school_inep_code == 0:
                raise forms.ValidationError("Forneça o Código INEP da Escola.")
            if len(str(school_inep_code)) != 8:
                raise forms.ValidationError("Código INEP da Escola inválido.")
        return school_inep_code

    school_name = forms.CharField(
        label='Nome da Escola',
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=200,
        )
    school_type = forms.ChoiceField(
        label='Tipo da Escola',
        choices=(SCHOOL_TYPE_CHOICES ),
        widget=forms.Select(attrs={'class':'form-select','onchange':'_showHideSchoolType("id_school_inep_code")'}),
        )
    school_inep_code = forms.IntegerField(
        label='Código INEP da Escola',
        help_text='Apenas para Escolas de Ensino Básico.',
        required=False,
        widget=forms.NumberInput(attrs={'style':'display:block'}),
        )
    school_phone = forms.CharField(
        label='Telefone da Escola, com DDD',
        max_length=16,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        help_text='Para contato com a Escola.',
        )
    school_zip = forms.CharField(
        label='CEP',
        max_length=10,
        help_text='Informe o CEP e pressione a tecla TAB no seu teclado; os campos Logradouro, Bairro, Cidade e Estado serão completados automaticamente. Se você não sabe o CEP, <a href="http://www.buscacep.correios.com.br/sistemas/buscacep/" target="_blank">consulte aqui</a>.'
        )
    school_address = forms.CharField(
        label='Logradouro',
        max_length=256,
        widget=forms.Textarea(attrs={'class':'form-control'}),
        required=False,
        )
    school_address_number = forms.CharField(
        label='Número',
        max_length=16,
        required=False,
        )
    school_address_complement = forms.CharField(
        label='Complemento',
        max_length=128,
        required=False,
        )
    school_address_district = forms.CharField(
        label='Bairro/Distrito',
        max_length=32,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        required = False,
        )
    school_city = forms.CharField(
        label='Cidade',
        max_length=128,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        )
    school_state = forms.ChoiceField(
        label='Estado',
        choices=(STATE_CHOICES),
        widget=forms.Select(attrs={'class':'form-select'}),
        #widget=forms.TextInput(attrs={'readonly':'readonly'})
        )
    school_address_building = forms.CharField(
        label='Local da Prova',
        max_length=1024,
        widget=forms.Textarea(attrs={'class':'form-control'}),
        required=False,
        )
    school_address_map = forms.CharField(
        label='Mapa',
        max_length=1024,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        required=False,
        help_text='Coloque aqui um link para um mapa (por exemplo do Google Maps), indicando o local da prova.<br>Exemplo: https://www.google.com/maps/d/u/0/viewer?mid=1SJpZrtX4Xg_oyRPx1heCxYykprc&hl=en_US&ll=-22.81353899999999%2C-47.063799&z=17',
        )
    school_address_other = forms.CharField(
        label='Outras informações',
        max_length=1024,
        widget=forms.Textarea(attrs={'class':'form-control'}),
        required=False,
        help_text='Coloque aqui outras informações que forem necessárias, como por exemplo alteração no horário de aplicação das provas, por alguma restrição local.'
        )
    class Meta:
        fieldsets = (
            ('Dados da Escola', {
                    'fields': ('school_name','school_type','school_inep_code','school_phone','school_zip','school_address','school_address_number','school_address_complement','school_address_district','school_city','school_state','school_address_building','school_address_map','school_address_other')}),
        )
        
class CoordEditaForm(forms.Form):
    #def __init__(self, user, data=None):
    #    self.user = user
    #    super(CoordEditaForm, self).__init__(data=data)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.request = kwargs.pop('request', None)
        super(CoordEditaForm, self).__init__(*args, **kwargs)


    def clean_school_deleg_name(self):
        name = self.cleaned_data['school_deleg_name']
        tks = name.split()
        if len(tks) < 2:
            raise forms.ValidationError("Informe o nome completo.")
        name = capitalize_name(name)
        return name

    def clean_school_deleg_email_conf(self):
        email = self.cleaned_data['school_deleg_email']
        email_conf = self.cleaned_data['school_deleg_email_conf']
        if email != email_conf:
            raise forms.ValidationError("Email e confirmação de email são diferentes.")
        return email_conf
    
    def clean_school_deleg_password_cur(self):
        try:
            password = self.cleaned_data['school_deleg_password']
        except:
            password = ""
        try:
            password_conf = self.cleaned_data['school_deleg_password_conf']
        except:
            password_conf = ""
        password_cur = self.cleaned_data['school_deleg_password_cur']

        if password_cur == "":
            if password or password_conf:
                raise forms.ValidationError("Para alterar a senha é necessário informar a senha atual.")
            return password_cur

        valid = self.user.check_password(password_cur)
        if not valid:
            raise forms.ValidationError("Senha incorreta.")
        return password_cur

    def clean_school_deleg_password(self):
        password = self.cleaned_data['school_deleg_password']
        if password and validate_password(password):
            raise forms.ValidationError("Senha fraca. "+password_validators_help_text_html())
        return password

    def clean_school_deleg_password_conf(self):
        try:
            password = self.cleaned_data['school_deleg_password']
        except:
            password = ""
        password_conf = self.cleaned_data['school_deleg_password_conf']
        if password != password_conf:
            raise forms.ValidationError("Senha e confirmação de senha são diferentes.")
        return password_conf

    school_deleg_name = forms.CharField(
        label='Nome',
        max_length=200,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        help_text='Insira o nome completo, com a grafia correta. O nome será utilizado na emissão do Certificado.',
        )
    school_deleg_phone = forms.CharField(
        label='Telefone pessoal, com DDD',
        max_length=16,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        help_text='Para contato em caso de emergência.',
        )
    school_deleg_email = forms.EmailField(
        label = 'Email',
        required = True,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        help_text = 'Utilize preferencialmente um email institucional.' 
        )
    school_deleg_email_conf = forms.EmailField(
        label = 'Confirme o Email',
        widget=forms.TextInput(attrs={'class':'form-control'}),
        required = True,
        )
    school_deleg_username = forms.CharField(
        label='Nome de usuário',
        max_length=64,
        widget=forms.TextInput(attrs={'class':'form-control', 'readonly':'readonly'}),
        help_text='O nome de usuário não pode ser alterado. Se é necessário alterá-lo, entre em contato com a Coordenação.',
        )
    school_deleg_password_cur = forms.CharField(
        label='Senha atual',
        max_length=64,
        widget=forms.PasswordInput(attrs={'class':'form-control'}),
        help_text='Deixe em branco se não deseja alterar a senha.',
        required = False,
        )
    school_deleg_password = forms.CharField(
        label='Nova senha',
        max_length=64,
        widget=forms.PasswordInput(attrs={'class':'form-control'}),
        help_text='Deixe em branco se não deseja alterar a senha.',
        required = False,
        )
    school_deleg_password_conf = forms.CharField(
        label='Confirme a nova senha',
        max_length=64,
        widget=forms.PasswordInput(attrs={'class':'form-control'}),
        help_text='Deixe em branco se não deseja alterar a senha.',
        required = False,
        )
    class Meta:
        fieldsets = (
            ('Coordenador Local', {
                    'fields': ('school_deleg_name','school_deleg_phone','school_deleg_email','school_deleg_email_conf')}),
            ('Conta', {
                    'fields': ('school_deleg_username','school_deleg_password_cur','school_deleg_password','school_deleg_password_conf')}),
        )

class ColabInscreveForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ColabInscreveForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        colab_email = cleaned_data.get('colab_email')
        colab_admin = cleaned_data.get('colab_admin')
        colab_admin_full = cleaned_data.get('colab_admin_full')
        result = validate_email_colab(colab_email, show_which=True)
        if result:
            self.add_error('colab_email', result)
        if colab_admin == 'S' or colab_admin_full == 'S':
            if not colab_email:
                self.add_error('colab_email', "Para habilitar colaborador como administrador o email deve ser fornecido.")
            result = validate_username_colab(colab_email)
            if result:
                self.add_error('colab_email', result)
        return self.cleaned_data

    def clean_colab_name(self):
        name = self.cleaned_data['colab_name']
        # only delegs can register colabs
        school_id = self.request.user.deleg.deleg_school.school_id
        colab_exists = Colab.objects.filter(colab_name__iexact=name,colab_school_id=school_id).count()
        if colab_exists > 0:
            raise forms.ValidationError("Nome de colaborador já inscrito.")
        tks = name.split()
        if len(tks) < 2:
            raise forms.ValidationError("Informe o nome completo.")
        name = capitalize_name(name)
        return name

    colab_name = forms.CharField(
        label='Nome do(a) Colaborador(a)', 
        max_length=200,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        required=True,
        help_text='Insira o nome completo, com a grafia correta. O nome será utilizado na emissão do Certificado.',
    )
    colab_sex = forms.ChoiceField(
        label='Gênero',
        choices=SEX_CHOICES,
        widget=forms.RadioSelect(attrs={'class':'horizontal'}),
        required=True,
        help_text='',
    )
    colab_email = forms.EmailField(
        label='Email',
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control'}),
    )
    colab_admin = forms.ChoiceField(
        label='Pode gerenciar competidores',
        choices=(('S','Sim'),('N','Não'),),
        widget=forms.RadioSelect(attrs={'class':'horizontal'}),
        required=True,
        help_text='Se habilitado, poderá inscrever/editar/remover competidores, inserir notas, mas não terá acesso às provas.',
    )
    colab_admin_full = forms.ChoiceField(
        label='Pode acessar provas',
        choices=(('S','Sim'),('N','Não'),),
        widget=forms.RadioSelect(attrs={'class':'horizontal'}),
        required=True,
        help_text='Se habilitado, além de gerenciar competidores, terá também acesso às provas.',
    )

    class Meta:
        fieldsets = (
            ('Dados', {
                'fields': ('colab_name','colab_sex','colab_email','colab_admin','colab_admin_full',)}),
        )

class ColabEditaForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ColabEditaForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        colab_email = cleaned_data.get('colab_email')
        colab_admin = cleaned_data.get('colab_admin')
        colab_admin_full = cleaned_data.get('colab_admin_full')
        colab_email_cur = cleaned_data.get('colab_email_cur')
        if colab_email != colab_email_cur:
            result = validate_email_colab(colab_email, show_which=True)
            if result:
                self.add_error('colab_email', result)
        if colab_admin == 'S' or colab_admin_full == 'S':
            if not colab_email:
                self.add_error('colab_email', "Para habilitar colaborador como administrador o email deve ser fornecido.")
        if colab_admin == 'N' and colab_admin_full == 'S':
            self.add_error('colab_email', "Para habilitar acesso à provas o colaborador deve poder gerenciar competidores.")
        return self.cleaned_data

    def clean_colab_name(self):
        name = self.cleaned_data['colab_name']
        id = self.cleaned_data['colab_id']
        school_id = self.request.user.deleg.deleg_school.school_id
        name_exists = Colab.objects.filter(colab_name__iexact=name,colab_school_id=school_id).exclude(colab_id=id)
        if len(name_exists) > 0:
            raise forms.ValidationError("Nome de colaborador já inscrito.")
        tks = name.split()
        if len(tks) < 2:
            raise forms.ValidationError("Informe o nome completo.")
        name = capitalize_name(name)
        return name

    colab_id = forms.CharField(
        widget=forms.HiddenInput(),
    )
    colab_name = forms.CharField(
        label='Nome do(a) Colaborador(a)', 
        max_length=200,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        required=True,
        help_text='Insira o nome completo, com a grafia correta. O nome será utilizado na emissão do Certificado.',
    )
    colab_sex = forms.ChoiceField(
        label='Gênero',
        choices=SEX_CHOICES,
        widget=forms.RadioSelect(attrs={'class':'horizontal'}),
        required=True,
    )
    colab_email = forms.EmailField(
        label='Email',
        widget=forms.TextInput(attrs={'class':'form-control'}),
        required=False,
    )
    colab_admin = forms.ChoiceField(
        label='Pode gerenciar competidores',
        choices=(('S','Sim'),('N','Não'),),
        widget=forms.RadioSelect(attrs={'class':'horizontal'}),
        required=True,
        help_text='Se habilitado, poderá inscrever/editar/remover competidores, inserir notas, mas não terá acesso às provas.',
    )
    colab_admin_full = forms.ChoiceField(
        label='Pode acessar provas',
        choices=(('S','Sim'),('N','Não'),),
        widget=forms.RadioSelect(attrs={'class':'horizontal'}),
        required=True,
        help_text='Se habilitado, além de gerenciar competidores, terá também acesso às provas.',
    )
    colab_email_cur = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    class Meta:
        fieldsets = (
            ('Dados', {
                'fields': ('colab_name','colab_sex','colab_email')}),
            ('Autorização de Acesso', {
                'fields': ('colab_admin','colab_admin_full')}),
            ('hidden', {
                'fields': ('colab_email_cur','colab_id')}),
        )

class CompetAutorizaProvaOnlineForm(forms.Form):
    '''Process by hand, using getlist() '''
    choices_set = forms.MultipleChoiceField(
        widget  = forms.CheckboxSelectMultiple,
    )
    choices_unset = forms.MultipleChoiceField(
        widget  = forms.CheckboxSelectMultiple,
    )

