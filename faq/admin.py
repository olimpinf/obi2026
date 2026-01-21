from django.contrib import admin
from .models import Topic, Item

class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_short', 'order')
    #fields = ('text', 'order')
    #search_fields = ('gallery_slug', 'gallery_name', 'gallery_comment')

class ItemAdmin(admin.ModelAdmin):
    list_display = ('topic', 'question', 'order')
    #fields = ('text', 'order')
    #search_fields = ('gallery_slug', 'gallery_name', 'gallery_comment')

admin.site.register(Topic,TopicAdmin)
admin.site.register(Item,ItemAdmin)

