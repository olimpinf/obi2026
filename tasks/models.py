from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import gettext_lazy as _


class Task(models.Model):
    def __str__(self):
        return self.title

    title = models.CharField('Título',max_length=100)
    descriptor = models.CharField('Descritor',max_length=100,unique=True)
    statement = models.TextField('Enunciado')
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
    year = models.IntegerField('Ano')
    phase = models.CharField('Fase',max_length=1)
    modstr = models.CharField('Modalidade',max_length=1)
    levelstr = models.CharField('Nível (str)',max_length=1)
    level = models.IntegerField('Nível (int)')
    code = models.CharField('Código',max_length=100)
    url = models.CharField('URL',max_length=100)
    sites = models.ManyToManyField(Site, verbose_name=_('sites'))

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
