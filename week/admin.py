from django.contrib import admin

from principal.models import Compet

from .models import Week


class WeekAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        #return qs.filter(compet__compet_rank_final__lte=30)
        return 
    list_display = ('participant_name', 'form_info','tax_value','full_compet_id',)
    exclude = ('compet', 'colab', 'deleg',)
'''
    fields = ('participant_name', 'form_info','paying','paid','tax_value','shirt_size','full_compet_id',\
              'school','colab','chaperone','arrival_place','arrival_time','van_arrival_time',\
              'departure_place','departure_time','van_departure_time')
    #readonly_fields = ('participant_name','full_compet_id',)
    #search_fields = ('compet__compet_name','colab__colab_name',)
'''
admin.site.register(Week,WeekAdmin)
