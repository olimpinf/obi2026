from django import forms
from django.forms import ModelForm
from django.http import QueryDict

from .models import CorrigeFolhasRespostas, GeraFolhasRespostas, GeraGabarito, NUM_QUESTION_CHOICES, NUM_ALTERNATIVE_CHOICES, ALTERNATIVE_CHOICES


class GeraFolhasRespostasForm(ModelForm):
    class Meta:
        model = GeraFolhasRespostas
        fields = ['label1','label2','label3','label4','num_dig','check_id','num_questions','num_alternatives','source_file']
        #fields = ['label1','label2','label3','label4','num_dig','check_id','num_questions','source_file']
        fieldsets = (
            ('Informação do Teste', {
                    'fields': ('label1','label2','label3','label4','num_questions', 'num_alternatives')}),
            ('Identificação dos Participantes', {
                    'fields': ('num_dig', 'check_id')}),
            ('Arquivo de participantes', {
                    'fields': ('source_file')}),
        )

class CorrigeFolhasRespostasForm(ModelForm):
    class Meta:
        model = CorrigeFolhasRespostas
        fields = ['source_file','answer_file','num_questions','num_alternatives','reference','email']
        #fields = ['source_file','answer_file','reference','email']
        fieldsets = (
            ('Informação do Teste', {
                    'fields': ('source_file','answer_file','num_questions','num_alternatives','reference')}),
                    #'fields': ('source_file','answer_file','reference')}),
            ('Contato', {
                    'fields': ('email')}),
        )

class GeraGabaritoIniForm(ModelForm):
    class Meta:
        model = GeraGabarito
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 2}),
        }
        fields = ['num_questions','num_alternatives','comment']
        fieldsets = (
            ('Informação do Teste', {
                    'fields': ('num_questions','num_alternatives','comment')}),
        )

class GeraGabaritoForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.num_questions = kwargs.pop('num_questions')
        self.num_alternatives = kwargs.pop('num_alternatives')
        super(GeraGabaritoForm, self).__init__(*args, **kwargs)
        choices = ALTERNATIVE_CHOICES[:self.num_alternatives] + [ALTERNATIVE_CHOICES[-1]]
        for i in range(self.num_questions):
            self.fields['question_%s' % i] = forms.MultipleChoiceField(label=f'{i+1}', choices=choices, widget=forms.CheckboxSelectMultiple)
            #self.fields['question_%s' % i].widget.attrs.update({'class': 'checkbox-inline'})

    def clean(self):
        cleaned_data = super().clean()
        for i in range(self.num_questions):
            chosen = cleaned_data.get(f'question_{i}')
            if chosen and len(chosen) > 1:
                if ('U' in chosen and 'X' in chosen):
                    self.add_error(f'question_{i}','"Anulada" e "Não usada" não podem ser ambas escolhidas.')
                elif ('U' in chosen or 'X' in chosen):
                    self.add_error(f'question_{i}','Questão "Anulada" ou "Não usada" não pode ter alternativa escolhida')

        return cleaned_data
