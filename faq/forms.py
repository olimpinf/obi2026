from django import forms

from .models import Topic, Item

class FaqForm(forms.Form):
    def clean_topics(self):
        topics = self.cleaned_data['topics']
        if len(topics)==0:
            raise forms.ValidationError(
                "Ao menos um tópico deve ser escolhido."
                )
        return topics

    filter = forms.CharField(
        label='Termos para consulta', 
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'onchange':'this.form.submit()'}),
        help_text='Digite um ou mais termos que deseja consultar e tecle <em>Enter</em>.',
        )
    topics = forms.ModelMultipleChoiceField(
        label = 'Mostrar apenas perguntas da seção',
        queryset = Topic.objects.all().only('id','name_short'),
        to_field_name='name_short',
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'onchange':'this.form.submit()'}), #(attrs={"checked":"False"}),
        initial=list(Topic.objects.all().only('id'))
        )

    class Meta:
       fields = 'filter'
       fieldsets = (
           ('Busca nas Perguntas Frequentes', {
                   'fields': ('filter', 'topics')}),
       )


