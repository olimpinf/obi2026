from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import gettext_lazy as _
from principal.models import Compet, School, LANGUAGE_CHOICES
from principal.models import CompetCfObi

class Task(models.Model):
    def __str__(self):
        return self.title

    title = models.CharField('Título',max_length=100)
    descriptor = models.CharField('Descritor',max_length=100,unique=True)
    statement = models.TextField('Enunciado')
    order = models.IntegerField('Ordem',null=True)
    template_name = models.CharField(
        _('template name'),
        max_length=70,
        blank=True,
        help_text=_(
            "Example: 'taskpages/contact_page.html'. If this isn't provided, "
            "the system will use 'taskpages/default.html'."
        ),
    )
    registration_required = models.BooleanField(
        _('registration required'),
        help_text=_("If this is checked, only logged-in users will be able to view the page."),
        default=False,
    )
    exam = models.CharField('Prova',max_length=16)
    phase = models.CharField('Fase',max_length=1)
    modstr = models.CharField('Modalidade',max_length=1)
    levelstr = models.CharField('Nível (str)',max_length=1)
    level = models.IntegerField('Nível (int)')
    code = models.CharField('Código',max_length=100)
    url = models.CharField('URL',max_length=100)
    #sites = models.ManyToManyField(Site, verbose_name=_('sites'))

class Question(models.Model):
    def __str__(self):
        return " ".join(self.text.split()[:8])

    task = models.ForeignKey(Task,on_delete=models.CASCADE)
    text = models.TextField('Questão')
    num = models.IntegerField('Número')

class Alternative(models.Model):
    def __str__(self):
        return " ".join(self.text.split()[:8])

    question = models.ForeignKey(Question,on_delete=models.CASCADE)
    text = models.TextField('Alternativa')
    correct = models.BooleanField('Correta')
    num = models.IntegerField('Número')

#######################
# TesteFase1 - warmup
#######################
class TesteFase1(models.Model):
    id = models.AutoField(primary_key=True)
    compet = models.OneToOneField(Compet,verbose_name="Competidor",on_delete=models.CASCADE)
    school = models.ForeignKey(School,verbose_name="Escola",on_delete=models.CASCADE)
    log = models.TextField(null=True)
    answers = models.TextField(null=True)
    correct_answers = models.TextField(null=True)
    num_correct_answers = models.TextField(null=True)
    shuffle_pattern = models.CharField(max_length=16,null=True)
    subm_remaining = models.IntegerField(null=True,default=0)
    time_start = models.DateTimeField(null=True)
    time_finish = models.DateTimeField(null=True)
    time_extra = models.IntegerField(null=True,default=0)
    completed = models.BooleanField('Concluído',null=True) # copied results
    class Meta:
        db_table = 'teste_fase1'

#######################
# SubWWW
#######################
class SubTesteFase1(models.Model):
    sub_id = models.AutoField(primary_key=True)
    sub_source = models.TextField()
    sub_lang = models.IntegerField(
        'Linguagem',
        choices = LANGUAGE_CHOICES,
        )
    sub_lock = models.IntegerField(null=True,default=0)
    sub_marked = models.IntegerField(null=True,default=0)
    result_id = models.IntegerField(null=True) #models.ForeignKey(Res_www,on_delete=models.CASCADE,null=True)
    problem_name = models.CharField(max_length=32)
    problem_name_full = models.CharField(max_length=128)
    sub_file = models.FileField() 
    sub_time = models.DateTimeField(auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'sub_teste_fase1'
        verbose_name = u'SubTesteFase1'
        verbose_name_plural = u'SubTesteFase1'

class SubTesteFase1Judge(models.Model):
    sub_id = models.AutoField(primary_key=True)
    sub_source = models.TextField()
    sub_lang = models.IntegerField(
        'Linguagem',
        choices = LANGUAGE_CHOICES,
        )
    sub_lock = models.IntegerField(null=True,default=0)
    sub_marked = models.IntegerField(null=True,default=0)
    result_id = models.IntegerField(null=True) #models.ForeignKey(Res_www,on_delete=models.CASCADE,null=True)
    problem_name = models.CharField(max_length=32)
    problem_name_full = models.CharField(max_length=128)
    sub_file = models.FileField() 
    sub_time = models.DateTimeField(null=True) #  WILL COPY TIME FROM ORIGINAL SUBMISSION (auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'sub_teste_fase1_judge'
        verbose_name = u'SubTesteFase1Judge'
        verbose_name_plural = u'SubTesteFase1Judge'


class ResTesteFase1(models.Model):
    result_id = models.AutoField(primary_key=True)
    result_log = models.TextField()
    sub = models.ForeignKey(SubTesteFase1,on_delete=models.CASCADE)
    result_result = models.IntegerField()
    num_total_tests = models.IntegerField()
    num_correct_tests = models.IntegerField()
    problem_name = models.CharField(max_length=32)
    result_time = models.DateTimeField(auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'res_teste_fase1'

class ResTesteFase1Judge(models.Model):
    result_id = models.AutoField(primary_key=True)
    result_log = models.TextField()
    sub = models.ForeignKey(SubTesteFase1Judge,on_delete=models.CASCADE)
    result_result = models.IntegerField()
    num_total_tests = models.IntegerField()
    num_correct_tests = models.IntegerField()
    problem_name = models.CharField(max_length=32)
    result_time = models.DateTimeField(auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'res_teste_fase1_judge'

###############
# Prova Turno A
###############

class ExamFase1(models.Model):
    id = models.AutoField(primary_key=True)
    compet = models.OneToOneField(Compet,verbose_name="Competidor",on_delete=models.CASCADE)
    school = models.ForeignKey(School,verbose_name="Escola",on_delete=models.CASCADE)
    log = models.TextField(null=True)
    answers = models.TextField(null=True)
    correct_answers = models.TextField(null=True)
    num_correct_answers = models.TextField(null=True)
    shuffle_pattern = models.CharField(max_length=16,null=True)
    subm_remaining = models.IntegerField(null=True,default=0)
    time_start = models.DateTimeField(null=True)
    time_finish = models.DateTimeField(null=True)
    time_extra = models.IntegerField(null=True,default=0)
    completed = models.BooleanField('Concluído',null=True) # copied results
    class Meta:
        db_table = 'exam_fase1'

class SubProvaFase1A(models.Model):
    sub_id = models.AutoField(primary_key=True)
    sub_source = models.TextField()
    sub_lang = models.IntegerField(
        'Linguagem',
        choices = LANGUAGE_CHOICES,
        )
    sub_lock = models.IntegerField(null=True,default=0)
    sub_marked = models.IntegerField(null=True,default=0)
    result_id = models.IntegerField(null=True) #models.ForeignKey(Res_www,on_delete=models.CASCADE,null=True)
    problem_name = models.CharField(max_length=32)
    problem_name_full = models.CharField(max_length=128)
    sub_file = models.FileField() 
    sub_time = models.DateTimeField(auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'sub_prova_fase1a'
        verbose_name = u'SubProvaFase1A'
        verbose_name_plural = u'SubProvaFase1A'

class SubProvaFase1AJudge(models.Model):
    sub_id = models.AutoField(primary_key=True)
    sub_source = models.TextField()
    sub_lang = models.IntegerField(
        'Linguagem',
        choices = LANGUAGE_CHOICES,
        )
    sub_lock = models.IntegerField(null=True,default=0)
    sub_marked = models.IntegerField(null=True,default=0)
    result_id = models.IntegerField(null=True) #models.ForeignKey(Res_www,on_delete=models.CASCADE,null=True)
    problem_name = models.CharField(max_length=32)
    problem_name_full = models.CharField(max_length=128)
    sub_file = models.FileField() 
    sub_time = models.DateTimeField(null=True) #  WILL COPY TIME FROM ORIGINAL SUBMISSION (auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'sub_prova_fase1a_judge'
        verbose_name = u'SubProvaFase1AJudge'
        verbose_name_plural = u'SubProvaFase1AJudge'


class ResProvaFase1A(models.Model):
    result_id = models.AutoField(primary_key=True)
    result_log = models.TextField()
    sub = models.ForeignKey(SubProvaFase1A,on_delete=models.CASCADE)
    result_result = models.IntegerField()
    num_total_tests = models.IntegerField()
    num_correct_tests = models.IntegerField()
    problem_name = models.CharField(max_length=32)
    result_time = models.DateTimeField(auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'res_prova_fase1a'

class ResProvaFase1AJudge(models.Model):
    result_id = models.AutoField(primary_key=True)
    result_log = models.TextField()
    sub = models.ForeignKey(SubProvaFase1AJudge,on_delete=models.CASCADE)
    result_result = models.IntegerField()
    num_total_tests = models.IntegerField()
    num_correct_tests = models.IntegerField()
    problem_name = models.CharField(max_length=32)
    result_time = models.DateTimeField(auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'res_prova_fase1a_judge'

###############
# Prova Turno B
###############
class ExamFase1b(models.Model):
    id = models.AutoField(primary_key=True)
    compet = models.OneToOneField(Compet,verbose_name="Competidor",on_delete=models.CASCADE)
    school = models.ForeignKey(School,verbose_name="Escola",on_delete=models.CASCADE)
    log = models.TextField(null=True)
    answers = models.TextField(null=True)
    correct_answers = models.TextField(null=True)
    num_correct_answers = models.TextField(null=True)
    shuffle_pattern = models.CharField(max_length=16,null=True)
    subm_remaining = models.IntegerField(null=True,default=0)
    time_start = models.DateTimeField(null=True)
    time_finish = models.DateTimeField(null=True)
    time_extra = models.IntegerField(null=True,default=0)
    completed = models.BooleanField('Concluído',null=True) # copied results
    class Meta:
        db_table = 'exam_fase1b'

class SubProvaFase1B(models.Model):
    sub_id = models.AutoField(primary_key=True)
    sub_source = models.TextField()
    sub_lang = models.IntegerField(
        'Linguagem',
        choices = LANGUAGE_CHOICES,
        )
    sub_lock = models.IntegerField(null=True,default=0)
    sub_marked = models.IntegerField(null=True,default=0)
    result_id = models.IntegerField(null=True) #models.ForeignKey(Res_www,on_delete=models.CASCADE,null=True)
    problem_name = models.CharField(max_length=32)
    problem_name_full = models.CharField(max_length=128)
    sub_file = models.FileField() 
    sub_time = models.DateTimeField(auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'sub_prova_fase1b'
        verbose_name = u'SubProvaFase1B'
        verbose_name_plural = u'SubProvaFase1B'

class SubProvaFase1BJudge(models.Model):
    sub_id = models.AutoField(primary_key=True)
    sub_source = models.TextField()
    sub_lang = models.IntegerField(
        'Linguagem',
        choices = LANGUAGE_CHOICES,
        )
    sub_lock = models.IntegerField(null=True,default=0)
    sub_marked = models.IntegerField(null=True,default=0)
    result_id = models.IntegerField(null=True) #models.ForeignKey(Res_www,on_delete=models.CASCADE,null=True)
    problem_name = models.CharField(max_length=32)
    problem_name_full = models.CharField(max_length=128)
    sub_file = models.FileField() 
    sub_time = models.DateTimeField(null=True) #  WILL COPY TIME FROM ORIGINAL SUBMISSION (auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'sub_prova_fase1b_judge'
        verbose_name = u'SubProvaFase1BJudge'
        verbose_name_plural = u'SubProvaFase1BJudge'


class ResProvaFase1B(models.Model):
    result_id = models.AutoField(primary_key=True)
    result_log = models.TextField()
    sub = models.ForeignKey(SubProvaFase1B,on_delete=models.CASCADE)
    result_result = models.IntegerField()
    num_total_tests = models.IntegerField()
    num_correct_tests = models.IntegerField()
    problem_name = models.CharField(max_length=32)
    result_time = models.DateTimeField(auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'res_prova_fase1b'

class ResProvaFase1BJudge(models.Model):
    result_id = models.AutoField(primary_key=True)
    result_log = models.TextField()
    sub = models.ForeignKey(SubProvaFase1BJudge,on_delete=models.CASCADE)
    result_result = models.IntegerField()
    num_total_tests = models.IntegerField()
    num_correct_tests = models.IntegerField()
    problem_name = models.CharField(max_length=32)
    result_time = models.DateTimeField(auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'res_prova_fase1b_judge'


###############
# Prova Fase 2
###############
class ExamFase2(models.Model):
    id = models.AutoField(primary_key=True)
    compet = models.OneToOneField(Compet,verbose_name="Competidor",on_delete=models.CASCADE)
    school = models.ForeignKey(School,verbose_name="Escola",on_delete=models.CASCADE)
    log = models.TextField(null=True)
    answers = models.TextField(null=True)
    correct_answers = models.TextField(null=True)
    num_correct_answers = models.TextField(null=True)
    shuffle_pattern = models.CharField(max_length=16,null=True)
    subm_remaining = models.IntegerField(null=True,default=0)
    time_start = models.DateTimeField(null=True)
    time_finish = models.DateTimeField(null=True)
    time_extra = models.IntegerField(null=True,default=0)
    completed = models.BooleanField('Concluído',null=True) # copied results
    class Meta:
        db_table = 'exam_fase2'

class ExamFase2b(models.Model):
    id = models.AutoField(primary_key=True)
    compet = models.OneToOneField(Compet,verbose_name="Competidor",on_delete=models.CASCADE)
    school = models.ForeignKey(School,verbose_name="Escola",on_delete=models.CASCADE)
    log = models.TextField(null=True)
    answers = models.TextField(null=True)
    correct_answers = models.TextField(null=True)
    num_correct_answers = models.TextField(null=True)
    shuffle_pattern = models.CharField(max_length=16,null=True)
    subm_remaining = models.IntegerField(null=True,default=0)
    time_start = models.DateTimeField(null=True)
    time_finish = models.DateTimeField(null=True)
    time_extra = models.IntegerField(null=True,default=0)
    completed = models.BooleanField('Concluído',null=True) # copied results
    class Meta:
        db_table = 'exam_fase2b'

class SubProvaFase2(models.Model):
    sub_id = models.AutoField(primary_key=True)
    sub_source = models.TextField()
    sub_lang = models.IntegerField(
        'Linguagem',
        choices = LANGUAGE_CHOICES,
        )
    sub_lock = models.IntegerField(null=True,default=0)
    sub_marked = models.IntegerField(null=True,default=0)
    result_id = models.IntegerField(null=True) #models.ForeignKey(Res_www,on_delete=models.CASCADE,null=True)
    problem_name = models.CharField(max_length=32)
    problem_name_full = models.CharField(max_length=128)
    sub_file = models.FileField() 
    sub_time = models.DateTimeField(auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'sub_prova_fase2'
        verbose_name = u'SubProvaFase2'
        verbose_name_plural = u'SubProvaFase2'

class SubProvaFase2Judge(models.Model):
    sub_id = models.AutoField(primary_key=True)
    sub_source = models.TextField()
    sub_lang = models.IntegerField(
        'Linguagem',
        choices = LANGUAGE_CHOICES,
        )
    sub_lock = models.IntegerField(null=True,default=0)
    sub_marked = models.IntegerField(null=True,default=0)
    result_id = models.IntegerField(null=True) #models.ForeignKey(Res_www,on_delete=models.CASCADE,null=True)
    problem_name = models.CharField(max_length=32)
    problem_name_full = models.CharField(max_length=128)
    sub_file = models.FileField() 
    sub_time = models.DateTimeField(null=True) #  WILL COPY TIME FROM ORIGINAL SUBMISSION (auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'sub_prova_fase2_judge'
        verbose_name = u'SubProvaFase2Judge'
        verbose_name_plural = u'SubProvaFase2Judge'


class ResProvaFase2(models.Model):
    result_id = models.AutoField(primary_key=True)
    result_log = models.TextField()
    sub = models.ForeignKey(SubProvaFase2,on_delete=models.CASCADE)
    result_result = models.IntegerField()
    num_total_tests = models.IntegerField()
    num_correct_tests = models.IntegerField()
    problem_name = models.CharField(max_length=32)
    result_time = models.DateTimeField(auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'res_prova_fase2'

class ResProvaFase2Judge(models.Model):
    result_id = models.AutoField(primary_key=True)
    result_log = models.TextField()
    sub = models.ForeignKey(SubProvaFase2Judge,on_delete=models.CASCADE)
    result_result = models.IntegerField()
    num_total_tests = models.IntegerField()
    num_correct_tests = models.IntegerField()
    problem_name = models.CharField(max_length=32)
    result_time = models.DateTimeField(auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'res_prova_fase2_judge'

###############
# Prova Fase 3
###############
class ExamFase3(models.Model):
    id = models.AutoField(primary_key=True)
    compet = models.OneToOneField(Compet,verbose_name="Competidor",on_delete=models.CASCADE)
    school = models.ForeignKey(School,verbose_name="Escola",on_delete=models.CASCADE)
    log = models.TextField(null=True)
    answers = models.TextField(null=True)
    correct_answers = models.TextField(null=True)
    num_correct_answers = models.TextField(null=True)
    shuffle_pattern = models.CharField(max_length=16,null=True)
    subm_remaining = models.IntegerField(null=True,default=0)
    time_start = models.DateTimeField(null=True)
    time_finish = models.DateTimeField(null=True)
    time_extra = models.IntegerField(null=True,default=0)
    completed = models.BooleanField('Concluído',null=True) # copied results
    class Meta:
        db_table = 'exam_fase3'

class SubProvaFase3(models.Model):
    sub_id = models.AutoField(primary_key=True)
    sub_source = models.TextField()
    sub_lang = models.IntegerField(
        'Linguagem',
        choices = LANGUAGE_CHOICES,
        )
    sub_lock = models.IntegerField(null=True,default=0)
    sub_marked = models.IntegerField(null=True,default=0)
    result_id = models.IntegerField(null=True) #models.ForeignKey(Res_www,on_delete=models.CASCADE,null=True)
    problem_name = models.CharField(max_length=32)
    problem_name_full = models.CharField(max_length=128)
    sub_file = models.FileField()
    sub_time = models.DateTimeField(auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'sub_prova_fase3'
        verbose_name = u'SubProvaFase3'
        verbose_name_plural = u'SubProvaFase3'

class SubProvaFase3Judge(models.Model):
    sub_id = models.AutoField(primary_key=True)
    sub_source = models.TextField()
    sub_lang = models.IntegerField(
        'Linguagem',
        choices = LANGUAGE_CHOICES,
        )
    sub_lock = models.IntegerField(null=True,default=0)
    sub_marked = models.IntegerField(null=True,default=0)
    result_id = models.IntegerField(null=True) #models.ForeignKey(Res_www,on_delete=models.CASCADE,null=True)
    problem_name = models.CharField(max_length=32)
    problem_name_full = models.CharField(max_length=128)
    sub_file = models.FileField() 
    sub_time = models.DateTimeField(null=True) #  WILL COPY TIME FROM ORIGINAL SUBMISSION (auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'sub_prova_fase3_judge'
        verbose_name = u'SubProvaFase3Judge'
        verbose_name_plural = u'SubProvaFase3Judge'


class ResProvaFase3(models.Model):
    result_id = models.AutoField(primary_key=True)
    result_log = models.TextField()
    sub = models.ForeignKey(SubProvaFase3,on_delete=models.CASCADE)
    result_result = models.IntegerField()
    num_total_tests = models.IntegerField()
    num_correct_tests = models.IntegerField()
    problem_name = models.CharField(max_length=32)
    result_time = models.DateTimeField(auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'res_prova_fase3'

class ResProvaFase3Judge(models.Model):
    result_id = models.AutoField(primary_key=True)
    result_log = models.TextField()
    sub = models.ForeignKey(SubProvaFase3Judge,on_delete=models.CASCADE)
    result_result = models.IntegerField()
    num_total_tests = models.IntegerField()
    num_correct_tests = models.IntegerField()
    problem_name = models.CharField(max_length=32)
    result_time = models.DateTimeField(auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'res_prova_fase3_judge'


###############
# Prova CF-OBI
###############
class ExamCfObi(models.Model):
    id = models.AutoField(primary_key=True)
    # ranido - changing to compet
    #compet = models.OneToOneField(CompetCfObi,verbose_name="Competidora",on_delete=models.CASCADE)
    compet = models.OneToOneField(Compet,verbose_name="Competidora",on_delete=models.CASCADE)
    # school is not needed anymore
    #school = models.ForeignKey(School,verbose_name="Escola",on_delete=models.CASCADE)
    #log = models.TextField(null=True)
    #answers = models.TextField(null=True)
    #correct_answers = models.TextField(null=True)
    #num_correct_answers = models.TextField(null=True)
    #shuffle_pattern = models.CharField(max_length=16,null=True)
    #subm_remaining = models.IntegerField(null=True,default=0)
    time_start = models.DateTimeField(null=True)
    time_finish = models.DateTimeField(null=True)
    time_extra = models.IntegerField(null=True,default=0)
    completed = models.BooleanField('Concluído',null=True) # copied results
    class Meta:
        db_table = 'exam_cfobi'

class SubProvaCfObi(models.Model):
    sub_id = models.AutoField(primary_key=True)
    sub_source = models.TextField()
    sub_lang = models.IntegerField(
        'Linguagem',
        choices = LANGUAGE_CHOICES,
        )
    sub_lock = models.IntegerField(null=True,default=0)
    sub_marked = models.IntegerField(null=True,default=0)
    result_id = models.IntegerField(null=True)
    problem_name = models.CharField(max_length=32)
    problem_name_full = models.CharField(max_length=128)
    sub_file = models.FileField()
    sub_time = models.DateTimeField(auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'sub_prova_cfobi'
        verbose_name = u'SubProvaCfObi'
        verbose_name_plural = u'SubProvaCfObi'

class SubProvaCfObiJudge(models.Model):
    sub_id = models.AutoField(primary_key=True)
    sub_source = models.TextField()
    sub_lang = models.IntegerField(
        'Linguagem',
        choices = LANGUAGE_CHOICES,
        )
    sub_lock = models.IntegerField(null=True,default=0)
    sub_marked = models.IntegerField(null=True,default=0)
    result_id = models.IntegerField(null=True)
    problem_name = models.CharField(max_length=32)
    problem_name_full = models.CharField(max_length=128)
    sub_file = models.FileField()
    sub_time = models.DateTimeField(null=True) #  WILL COPY TIME FROM ORIGINAL SUBMISSION (auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'sub_prova_cfobi_judge'
        verbose_name = u'SubProvaCfObiJudge'
        verbose_name_plural = u'SubProvaCfObiJudge'


class ResProvaCfObi(models.Model):
    result_id = models.AutoField(primary_key=True)
    result_log = models.TextField()
    sub = models.ForeignKey(SubProvaCfObi,on_delete=models.CASCADE)
    result_result = models.IntegerField()
    num_total_tests = models.IntegerField()
    num_correct_tests = models.IntegerField()
    problem_name = models.CharField(max_length=32)
    result_time = models.DateTimeField(auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'res_prova_cfobi'

class ResProvaCfObiJudge(models.Model):
    result_id = models.AutoField(primary_key=True)
    result_log = models.TextField()
    sub = models.ForeignKey(SubProvaCfObiJudge,on_delete=models.CASCADE)
    result_result = models.IntegerField()
    num_total_tests = models.IntegerField()
    num_correct_tests = models.IntegerField()
    problem_name = models.CharField(max_length=32)
    result_time = models.DateTimeField(auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'res_prova_cfobi_judge'
