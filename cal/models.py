from django.db import models
from django.core.validators import EmailValidator

from obi.settings import YEAR

RED_BKGD = "red-bkgd"
DARK_RED_BKGD = "dark-red-bkgd"
LIGHT_RED_BKGD = "light-red-bkgd"
BLUE_BKGD = "blue-bkgd"
MIDDLE_BLUE_BKGD = "middle-blue-bkgd"
DARK_BLUE_BKGD = "dark-blue-bkgd"
LIGHT_BLUE_BKGD = "light-blue-bkgd"
DARK_PURPLE_BKGD = "dark-purple-bkgd"
LIGHT_PURPLE_BKGD = "light-purple-bkgd"
GREEN_BKGD = "green-bkgd"
DARK_GREEN_BKGD = "dark-green-bkgd"
LIGHT_GREEN_BKGD = "light-green-bkgd"
YELLOW_BKGD = "yellow-bkgd"
ORANGE_BKGD = "orange-bkgd"
BROWN_BKGD = "brown-bkgd"        
GREY_BKGD = "grey-bkgd"        

EVENT_COLORS = (
  (RED_BKGD, "red-bkgd"),
  (DARK_RED_BKGD, "dark-red-bkgd"),
  (LIGHT_RED_BKGD, "light-red-bkgd"),
  (BLUE_BKGD, "blue-bkgd"),
  (DARK_BLUE_BKGD, "dark-blue-bkgd"),
  (MIDDLE_BLUE_BKGD, "middle-blue-bkgd"),
  (LIGHT_BLUE_BKGD, "light-blue-bkgd"),
  (DARK_PURPLE_BKGD, "dark-purple-bkgd"),
  (LIGHT_PURPLE_BKGD, "light-purple-bkgd"),
  (GREEN_BKGD, "green-bkgd"),
  (DARK_GREEN_BKGD, "dark-green-bkgd"),
  (LIGHT_GREEN_BKGD, "light-green-bkgd"),
  (YELLOW_BKGD, "yellow-bkgd"),
  (ORANGE_BKGD, "orange-bkgd"),
  (BROWN_BKGD, "brown-bkgd"),
  (GREY_BKGD, "grey-bkgd"),
)


class CalendarCompetition(models.Model):
    def __str__(self):
        return self.name

    id = models.AutoField('ID',primary_key=True)
    name = models.CharField('Nome da competição',max_length=200)
    name_abbrev = models.CharField('Nome da Competição Abreviado',max_length=32)
    show = models.BooleanField('Mostrar',default=True)
    link = models.CharField('Link',max_length=256, null=True, blank=True)
    color = models.CharField(
        'Cor',
        max_length=30,
        choices = EVENT_COLORS,
        )
    color_emph = models.CharField(
        'Cor Enfatizada',
        max_length=30,
        choices = EVENT_COLORS,
        null=True,
        blank=True
        )
    class Meta:
        db_table = 'calendar_competition'
        verbose_name = 'Competição OBI'
        verbose_name_plural = 'Competições OBI'
    
class CalendarEvent(models.Model):
    def __str__(self):
        return self.name

    id = models.AutoField('ID',primary_key=True)
    name = models.CharField('Nome do Evento',max_length=200)
    competition = models.ForeignKey(CalendarCompetition,verbose_name="Competição",on_delete=models.CASCADE)
    show = models.BooleanField('Mostrar',default=True)
    start = models.DateField('Início')
    finish = models.DateField('Final')
    emph = models.BooleanField('Enfatizar',default=False)    
    comment = models.TextField('Detalhes',null=True,blank=True)
    slug = models.SlugField('Slug',unique=True,max_length=80)
    class Meta:
        db_table = 'calendar_event'
        verbose_name = 'Evento OBI'
        verbose_name_plural = 'Eventos OBI'
        ordering = ['competition__name','start']

class CalendarNationalCompetition(models.Model):
    def __str__(self):
        return self.name

    id = models.AutoField('ID',primary_key=True)
    name = models.CharField('Nome da competição',max_length=200)
    name_abbrev = models.CharField('Nome Abreviado da Competição',max_length=32)
    #coord_name = models.CharField('Nome do coordenador',max_length=200)
    #description = models.TextField('Descrição',null=True,blank=True)
    #email = models.CharField('Email de contato',max_length=100,validators = [EmailValidator(message=u'Por favor entre um endereço válido de email')], null=True, blank=True)
    #year_start = models.IntegerField('Ano da primeira edição',null=True,blank=True)
    order = models.IntegerField('Ordenação',null=True,blank=True)
    show = models.BooleanField('Mostrar',default=True)
    link = models.CharField('Link',max_length=256, null=True, blank=True)
    color = models.CharField(
        'Cor',
        max_length=30,
        choices = EVENT_COLORS,
        )
    color_emph = models.CharField(
        'Cor Enfatizada',
        max_length=30,
        choices = EVENT_COLORS,
        null=True,
        blank=True
        )
    class Meta:
        db_table = 'calendar_national_competition'
        verbose_name = 'Competição Nacional'
        verbose_name_plural = 'Competições Nacionais'
    
class CalendarNationalEvent(models.Model):
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Check how the current values differ from ._loaded_values. For example,
        # prevent changing the creator_id of the model. (This example doesn't
        # support cases where 'creator_id' is deferred).
        self.year = YEAR
        self.year = self.start.year
        super().save(*args, **kwargs)
    
    id = models.AutoField('ID',primary_key=True)
    year = models.IntegerField('Ano',editable=False,null=True,blank=True)
    name = models.CharField('Nome do Evento',max_length=200)
    competition = models.ForeignKey(CalendarNationalCompetition,verbose_name="Competições",on_delete=models.CASCADE)
    show = models.BooleanField('Mostrar',default=True)
    start = models.DateField('Início')
    finish = models.DateField('Final')
    test_day = models.BooleanField('Prova',default=False,help_text="Deixar sem marcar se não for prova (por exemplo, último dia de inscrição)")    
    comment = models.TextField('Detalhes',null=True,blank=True)
    last_update = models.DateTimeField('Última Atualização',auto_now=True,null=True,blank=True,editable=False)
    emph = models.BooleanField('Enfatizar',default=False)    
    slug = models.SlugField('Slug',unique=True,max_length=80)
    
    class Meta:
        db_table = 'calendar_national_event'
        verbose_name = 'Evento Nacional'
        verbose_name_plural = 'Eventos Nacionais'
        #ordering = ['competition__name','start']
        ordering = ['start']

