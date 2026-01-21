from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from django.utils.html import mark_safe

from principal.models import (LANG_SUFFIXES_NAMES, LANGUAGE_CHOICES,
                              LEVEL_CHOICES_INI, LEVEL_CHOICES_PROG, Compet, School)


#######################
# Points Turn A and B
#######################
class PointsFase2(models.Model):
    id = models.AutoField(primary_key=True)
    compet = models.ForeignKey(Compet,verbose_name="Competidor",on_delete=models.PROTECT)
    points_a = models.IntegerField(null=True)
    points_b = models.IntegerField(null=True)
    classif_a = models.BooleanField(default=False) 
    classif_b = models.BooleanField(default=False) 
    class Meta:
        db_table = 'points_fase2'

#######################
# SubFase2
#######################
class SubFase2(models.Model):
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
        db_table = 'sub_fase2'

#######################
# ResFase2
#######################
class ResFase2(models.Model):
    result = models.AutoField(primary_key=True)
    result_log = models.TextField()
    compet = models.ForeignKey(Compet,verbose_name="Competidor",on_delete=models.PROTECT)
    sub = models.ForeignKey(SubFase2,on_delete=models.PROTECT)
    result_result = models.IntegerField()
    num_total_tests = models.IntegerField()
    num_correct_tests = models.IntegerField()
    problem_name = models.CharField(max_length=32)
    res_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'res_fase2'

