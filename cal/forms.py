from django import forms
from django.forms import models
from django.forms.fields import MultipleChoiceField

from .models import CalendarNationalCompetition

class CalendarForm(forms.Form):
    def clean_topics(self):
        topics = self.cleaned_data['topics']
        if len(topics)==0:
            raise forms.ValidationError(
                "Ao menos uma modalidade deve ser escolhida."
                )
        return topics

    topics = forms.MultipleChoiceField(
        label = 'Mostrar apenas eventos da',
        required=False,
        choices=[('ini','Modalidade Iniciação'), ('prog','Modalidade Programação')],
        widget=forms.CheckboxSelectMultiple(attrs={'onchange':'this.form.submit()'}),
        initial=('ini','prog'),
    )

    class Meta:
       fields = 'Filter'
       fieldsets = (
           ('Filtro', {
                   'fields': ('topics')}),
       )

# class CustomModelChoiceIterator(models.ModelChoiceIterator):
#     def choice(self, obj):
#         return (self.field.prepare_value(obj),
#                 self.field.label_from_instance(obj), obj)

# class CustomModelChoiceField(models.ModelMultipleChoiceField):
#     def _get_choices(self):
#         if hasattr(self, '_choices'):
#             return self._choices
#         return CustomModelChoiceIterator(self)
#     choices = property(_get_choices,  
#                        MultipleChoiceField._set_choices)

class FilterFormText(forms.Form):
    # def clean_filterInput(self):
    #     print("in clean, self=", self)
    #     filterInput = self.cleaned_data['filterInput']
    #     print("in clean, filterInput=", filterInput)
    #     return filterInput


    #competitions = CalendarNationalCompetition.objects.all()
    #the_choices = [(competition.name_abbrev,competition.name_abbrev) for competition in competitions]
    #print("the_choices",the_choices)
    
    # filterInput = forms.CharField(
    #     required=False,
    #     max_length=50,
    #     widget=forms.TextInput(attrs={'placeholder':'Digite aqui para filtrar','onkeyup':'filterList()'}),
    #     label="Filtrar",
    # )
    pass

class FilterForm(forms.Form):
    def clean_topics(self):
        topics = self.cleaned_data['topics']
        if len(topics)==0:
            raise forms.ValidationError(
                "Ao menos uma competição deve ser escolhida."
                )
        return topics


    competitions = CalendarNationalCompetition.objects.all()
    the_choices = [(competition.name_abbrev,competition.name_abbrev) for competition in competitions]

    show_only_test_days = forms.BooleanField(required=False)
    as_calendar = forms.BooleanField(required=False)
    as_list = forms.BooleanField(required=False)
    calendar_list = forms.MultipleChoiceField(
        required=False,
        choices=[('as_calendar','Mostrar como calendário'), ('as_list','Mostrar como lista')],
        widget=forms.CheckboxSelectMultiple(attrs={}),

    )
    
    
    filterInput = forms.MultipleChoiceField(
        label = 'Mostrar apenas eventos da',
        required=False,
        choices=the_choices, #[('ini','Modalidade Iniciação'), ('prog','Modalidade Programação')],
        widget=forms.CheckboxSelectMultiple(attrs={}),
        initial=the_choices,
    )
    

    # topics = CustomModelChoiceField(
    #     label = 'Mostrar apenas:',
    #     #queryset = CalendarNationalCompetition.objects.all().only('id','name_abbrev'),
    #     #queryset = CalendarNationalCompetition.objects.all(),
    #     #to_field_name='name_abbrev',
    #     required=False,
    #     widget = forms.CheckboxSelectMultiple(),
    #     queryset = CalendarNationalCompetition.objects.all(),
    #     initial=list(CalendarNationalCompetition.objects.all().order_by('name_abbrev').only('id','name_abbrev'))
    # )


