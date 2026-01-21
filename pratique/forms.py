from django import forms


class SubmeteSolucaoPratiqueForm(forms.Form):
    '''Used to upload submissions'''
    data = forms.FileField(
        label='Arquivo', 
        error_messages={'required': 'Escolha o arquivo'},
        )
    sub_lang = forms.ChoiceField(
        label='',
        # for cms
        choices=( (None,'Linguagem'), ('C17 / gcc','C17 / gcc'), ('C++17 / g++','C++17 / g++'), ('Pascal / fpc','Pascal / fpc'), ('Python 3 / CPython','Python 3 / CPython'), ('Java / JDK','Java / JDK'), ('Javascript','Javascript'), ),
        #choices=( (None,'Linguagem'), (1,'C11 / gcc'), (2,'C++17 / g++'), (3,'Pascal / fpc'), (7,'Python 3 / CPython'), (5,'Java / JDK'), (6,'Javascript'), ),
        widget=forms.Select(attrs={'class':'select'}),
        )
    problem_name = forms.CharField(max_length=32,widget=forms.HiddenInput())
    problem_name_full = forms.CharField(max_length=128,widget=forms.HiddenInput())
    problem_request_path = forms.CharField(max_length=256,widget=forms.HiddenInput())

    class Meta:
        fields = (('data','sub_lang'))
        #model = SubWWW
