from django.db import models

# Create your models here.

class CMSparticipation(models.Model):
    id = models.AutoField('ID',primary_key=True)
    ip = models.TextField('IP',null=True,blank=True)
    starting_time = models.DateTimeField(u'Starting Time',null=True,blank=True)
    delay_time = models.DateTimeField(u'Delay Time',null=True,blank=True)
    extra_time = models.DateTimeField(u'Extra Time',null=True,blank=True)
    password = models.TextField('Password',null=True,blank=True)
    #hidden = models.BooleanField('Hidden',null=True,blank=True)
    user_id = models.IntegerField('User')
    contest_id = models.IntegerField('Contest')
    class Meta:
        db_table = 'participations'

class CMSuser(models.Model):
    def __str__(self):
        return self.username

    id = models.AutoField('ID',primary_key=True)
    first_name = models.CharField('Nome',max_length=100,blank=True, null=True)
    last_name = models.CharField('Sobrenome',max_length=100)
    username = models.TextField('Username',unique=True)
    password = models.TextField('Password')
    #email = models.CharField('Email',max_length=100,blank=True, null=True)
    #timezone = models.CharField('Timezone',max_length=100,blank=True, null=True)
    #preferred_languages = models.JSONField('Pref. Languages',max_length=100,blank=True, null=True)
    #participations = models.ManyToManyField(CMSParticipation)
    class Meta:
        db_table = 'users'

class CMScommand(models.Model):
    '''Commands to be sent to CMS DB
    '''

    def __str__(self):
        return self.username

    id = models.AutoField('ID',primary_key=True)
    command = models.CharField('First Name',max_length=10,blank=True, null=True)
    first_name = models.CharField('First Name',max_length=100,blank=True, null=True)
    last_name = models.CharField('Last Name',max_length=100,blank=True, null=True)
    username = models.CharField('Username',max_length=100,blank=True, null=True)
    password = models.CharField('Password',max_length=255,blank=True, null=True)
    compet_type = models.IntegerField('Compet Type')
    contest_id = models.IntegerField('Contest',blank=True,null=True)
    time = models.DateTimeField('Time',auto_now_add=True)
    done = models.BooleanField('Done', default=False)
    #email = models.CharField('Email',max_length=100,blank=True, null=True)
    #timezone = models.CharField('Timezone',max_length=100,blank=True, null=True)
    #preferred_languages = models.JSONField('Pref. Languages',max_length=100,blank=True, null=True)
    #participations = models.ManyToManyField(CMSParticipation)
    class Meta:
        db_table = 'cms_command'



class CMStask(models.Model):
    id = models.AutoField('ID',primary_key=True)
    num = models.IntegerField('Num')
    contest_id = models.IntegerField('Contest')
    name = models.CharField('Name',max_length=100)
    title = models.CharField('Title',max_length=100)
    class Meta:
        db_table = 'tasks'

class CMSdataset(models.Model):
    id = models.AutoField('ID',primary_key=True)
    task = models.ForeignKey(CMStask,verbose_name="Task",on_delete=models.CASCADE)
    autojudge = models.BooleanField('Autojudge',blank=True, null=True)
    time_limit_lang = models.JSONField('Time limit languages',max_length=256,blank=True, null=True)
    memory_limit_lang = models.JSONField('Memory limit languages',max_length=256,blank=True, null=True)
    time_limit = models.FloatField('time_limit', blank=True, null=True)
    memory_limit = models.BigIntegerField('memory_limit', blank=True, null=True)

    class Meta:
        db_table = 'datasets' 

class CMSsubmissions(models.Model):
    id = models.AutoField('ID',primary_key=True)
    participation = models.ForeignKey(CMSparticipation,verbose_name="Participation",on_delete=models.CASCADE)
    task = models.ForeignKey(CMStask,verbose_name="Task",on_delete=models.CASCADE)
    timestamp = models.DateTimeField('Timestamp')
    language = models.CharField('Language',max_length=32)
    comment = models.TextField('Comment')
    official = models.BooleanField('Done', blank=True, null=True)
    class Meta:
        db_table = 'submissions'

class CMSsubmissionResults(models.Model):
    submission = models.ForeignKey(CMSsubmissions,verbose_name="Submission",on_delete=models.CASCADE)
    dataset = models.ForeignKey(CMSdataset,verbose_name="Dataset",on_delete=models.CASCADE)
    compilation_text = models.TextField('Compilation text',blank=True, null=True)
    compilation_stdout = models.TextField('Compilation stdout',blank=True, null=True)
    compilation_stderr = models.TextField('Compilation stderr',blank=True, null=True)
    score = models.FloatField('Score',blank=True, null=True)
    score_details = models.JSONField('Score detais',max_length=256,blank=True, null=True)
    public_score = models.FloatField('Public score',blank=True, null=True)
    public_score_details = models.JSONField('Public score detais',max_length=256,blank=True, null=True)
    evaluation_outcome = models.TextField('Evaluation outcome',blank=True, null=True)
    # django requires a primary key, fake one with compilation_sandbox
    compilation_sandbox = models.CharField('Compilation sandbox',max_length=512, primary_key=True)
    class Meta:
        db_table = 'submission_results'

class CMSFiles(models.Model):
    id = models.AutoField('ID',primary_key=True)
    submission = models.ForeignKey(CMSsubmissions,verbose_name="Submission",on_delete=models.CASCADE)
    filename = models.TextField('Filename')
    digest = models.TextField('Digest')
    class Meta:
        db_table = 'files'

class CMSFsobjects(models.Model):
    digest = models.TextField('Digest',primary_key=True)
    loid = models.IntegerField('Large object')
    description = models.TextField('Description')
    class Meta:
        db_table = 'fsobjects'

class LocalSubmissions(models.Model):
    id = models.AutoField('ID',primary_key=True)
    compet_id = models.IntegerField('Compet')
    compet_type = models.IntegerField('Compet type')
    submission_id = models.IntegerField('Submission')
    contest_id = models.IntegerField('Contest')
    task_name = models.CharField('Name',max_length=100)
    task_title = models.CharField('Title',max_length=100)
    timestamp = models.DateTimeField('Timestamp')
    language = models.CharField('Language',max_length=32)
    comment = models.TextField('Comment')
    official = models.BooleanField('Done', blank=True, null=True)
    source = models.BinaryField('Source', blank=True, null=True)
    filename = models.CharField('Filename',max_length=32)

    class Meta:
        db_table = 'local_submissions'

class LocalSubmissionResults(models.Model):
    id = models.AutoField('ID',primary_key=True)
    local_subm = models.ForeignKey(LocalSubmissions,verbose_name="Local Submission",on_delete=models.CASCADE)
    compet_id = models.IntegerField('Compet')
    compet_type = models.IntegerField('Compet type')
    submission_id = models.IntegerField('Submission')
    dataset_id = models.IntegerField('Dataset',blank=True, null=True)
    contest_id = models.IntegerField('Contest')
    compilation_text = models.TextField('Compilation text',blank=True, null=True)
    compilation_stdout = models.TextField('Compilation stdout',blank=True, null=True)
    compilation_stderr = models.TextField('Compilation stderr',blank=True, null=True)
    score = models.FloatField('Score',blank=True, null=True)
    score_details = models.JSONField('Score detais',max_length=256,blank=True, null=True)
    public_score = models.FloatField('Public score',blank=True, null=True)
    public_score_details = models.JSONField('Public score detais',max_length=256,blank=True, null=True)

    class Meta:
        db_table = 'local_submission_results'

class ExtraLocalSubmissions(models.Model):
    id = models.AutoField('ID',primary_key=True)
    compet_id = models.IntegerField('Compet')
    compet_type = models.IntegerField('Compet type')
    submission_id = models.IntegerField('Submission')
    contest_id = models.IntegerField('Contest')
    task_name = models.CharField('Name',max_length=100)
    task_title = models.CharField('Title',max_length=100)
    timestamp = models.DateTimeField('Timestamp')
    language = models.CharField('Language',max_length=32)
    comment = models.TextField('Comment')
    official = models.BooleanField('Done', blank=True, null=True)
    source = models.BinaryField('Source', blank=True, null=True)
    filename = models.CharField('Filename',max_length=32)
    
    class Meta:
        db_table = 'extra_local_submissions'


class LocalFiles(models.Model):
    id = models.AutoField('ID',primary_key=True)
    local_subm = models.ForeignKey(LocalSubmissions,verbose_name="Local Submission",on_delete=models.CASCADE)
    submission_id = models.IntegerField('Submission')
    compet_type = models.IntegerField('Compet type')
    contest_id = models.IntegerField('Contest')
    filename = models.TextField('Filename')
    digest = models.TextField('Digest')
    class Meta:
        db_table = 'local_files'

class LocalFsobjects(models.Model):
    id = models.AutoField('ID',primary_key=True)
    local_subm = models.ForeignKey(LocalSubmissions,verbose_name="Local Submission",on_delete=models.CASCADE)
    compet_type = models.IntegerField('Compet type')
    contest_id = models.IntegerField('Contest')
    digest = models.TextField('Digest')
    loid = models.IntegerField('Large object')
    description = models.TextField('Description')
    class Meta:
        db_table = 'local_fsobjects'


# class PGlargeobjects(models.Model):
#     loid = models.IntegerField('Loid')
#     pageno = models.IntegerField('Pageno')
#     data = models.BinaryField('Data')
#     class Meta:
#         db_table = 'postgres.pg_largeobject'
#         unique_together = ('loid','pageno')

# class CMSPGlargeobjects(models.Model):
#     loid = models.IntegerField('Loid')
#     pageno = models.IntegerField('Pageno')
#     data = models.BinaryField('Data')
#     class Meta:
#         db_table = 'pg_largeobject'
#         unique_together = ('loid','pageno')
