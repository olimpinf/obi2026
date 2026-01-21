from django.db import models

class Topic(models.Model):
    '''Topics for faq (like professores, competidores)'''

    def __str__(self):
        return self.name

    name = models.CharField('Tópico',max_length=100)
    name_short = models.CharField('Tópico',max_length=32)
    order = models.IntegerField('Ordem')
    class Meta:
        db_table = 'faq_topic'

class Item(models.Model):
    '''Question/Answer'''

    def __str__(self):
        return self.question
    
    #def topic(self):
    #    "Returns topic of item"
    #    return self.topic.name_short

    slug = models.CharField('Slug',max_length=32)
    question = models.TextField('Pergunta')
    answer = models.TextField('Resposta')
    active = models.BooleanField('Ativa',help_text='')
    topic = models.ForeignKey(Topic,verbose_name="Tópico",on_delete=models.CASCADE)
    order = models.IntegerField('Ordem')
    class Meta:
        db_table = 'faq_item'
