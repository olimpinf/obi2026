from django.contrib import admin
from django import forms
from django.forms.widgets import TextInput

#from .models import CalendarCompetition, CalendarEvent
from .models import CalendarNationalCompetition, CalendarNationalEvent


# class CalendarCompetitionAdmin(admin.ModelAdmin):
#     pass
#     #list_display = ('name',)
#     #fields = ('gallery_slug', 'gallery_type', 'gallery_name', 'gallery_comment',)
#     #search_fields = ('gallery_slug', 'gallery_name', 'gallery_comment')

# class CalendarEventAdmin(admin.ModelAdmin):
#     list_display = ('name','competition','show','start','finish','slug','comment')
#     prepopulated_fields = {"slug": ('competition','name',)}
#     search_fields = ('name','competition__name',)
#     widgets = {
#             'comment': forms.Textarea(),
#             }


class CalendarNationalCompetitionAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ()
        else:
            return ('name_abbrev')

    def get_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ('name', 'name_abbrev', 'link', 'order', 'show', 'color', 'color_emph')
        else:
            return ('name', 'link', 'show')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(name_abbrev=request.user.username)

    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
            super(CalendarNationalCompetitionAdmin, self).save_model(request, obj, form, change)
        else:
            obj.competition = CalendarNationalCompetition.objects.get(name_abbrev=request.user.username)
            super(CalendarNationalCompetitionAdmin, self).save_model(request, obj, form, change)

    #fields = ('name', 'coord_name', 'link', 'year_start', 'show', 'color', 'color_emph', 'description')
    list_display = ('name','show')

    
class CalendarNationalEventAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(competition__name_abbrev=request.user.username)

    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
            super(CalendarNationalEventAdmin, self).save_model(request, obj, form, change)
        else:
            obj.competition = CalendarNationalCompetition.objects.get(name_abbrev=request.user.username)
            super(CalendarNationalEventAdmin, self).save_model(request, obj, form, change)
    
    list_display = ('name','competition','show','start','finish','comment')
    widgets = {
            'comment': forms.Textarea(),
            }

#admin.site.register(CalendarCompetition,CalendarCompetitionAdmin)
#admin.site.register(CalendarEvent,CalendarEventAdmin)

admin.site.register(CalendarNationalCompetition,CalendarNationalCompetitionAdmin)
admin.site.register(CalendarNationalEvent,CalendarNationalEventAdmin)
