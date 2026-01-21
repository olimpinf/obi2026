from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from django.utils.html import mark_safe

from principal.models import (LANG_SUFFIXES_NAMES, LANGUAGE_CHOICES,
                              LEVEL_CHOICES_INI, LEVEL_CHOICES_PROG, Compet, School)


#######################
# SubFase1
#######################
class SubFase1(models.Model):
    sub_id = models.AutoField(primary_key=True)
    sub_source = models.TextField()
    sub_lang = models.IntegerField(
        'Linguagem',
        choices = LANGUAGE_CHOICES,
        )
    sub_lock = models.IntegerField(null=True,default=0)
    sub_marked = models.IntegerField(null=True,default=0)
    result_id = models.IntegerField(null=True) #models.ForeignKey(Res_fase1,on_delete=models.CASCADE,null=True)
    compet = models.ForeignKey(Compet,verbose_name="Competidor",on_delete=models.PROTECT)
    problem_name = models.CharField(max_length=32)
    problem_name_full = models.CharField(max_length=128)
    sub_time = models.DateTimeField(auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'sub_fase1'

#######################
# ResFase1
#######################
class ResFase1(models.Model):
    result = models.AutoField(primary_key=True)
    result_log = models.TextField()
    compet = models.ForeignKey(Compet,verbose_name="Competidor",on_delete=models.PROTECT)
    sub = models.ForeignKey(SubFase1,on_delete=models.PROTECT)
    result_result = models.IntegerField()
    num_total_tests = models.IntegerField()
    num_correct_tests = models.IntegerField()
    problem_name = models.CharField(max_length=32)
    res_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'res_fase1'

