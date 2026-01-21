from django.db import models
from django.contrib.auth.models import User

class EditorBackup(models.Model):
    def __str__(self):
        return self.comment

    id = models.AutoField('ID',primary_key=True)
    timestamp = models.DateTimeField('Timestamp',auto_now_add=True,null=True, blank=True)
    task_name = models.CharField('Task name', max_length=256, null=True, blank=True)
    competition_name = models.CharField('Competition name',max_length=256, null=True, blank=True)
    comment = models.CharField('Comment',max_length=256, null=True, blank=True)
    data = models.TextField('Data',max_length=16384, null=True, blank=True)
    user = models.ForeignKey(User,verbose_name="User",on_delete=models.CASCADE)
    the_type = models.CharField('Type',max_length=256, null=True, blank=True)
    class Meta:
        db_table = 'editor_backup'
        verbose_name = 'Backup Editor'
        verbose_name_plural = 'Backups Editor'
