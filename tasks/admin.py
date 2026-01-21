from django.contrib import admin

from .models import Alternative, Question, Task


class TaskAdmin(admin.ModelAdmin):
    list_display = ('title','descriptor','url')
    search_fields = ('descriptor',)

admin.site.register(Task, TaskAdmin)
admin.site.register(Question)
admin.site.register(Alternative)
