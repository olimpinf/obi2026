from django.contrib import admin
from .models import SaciUser

class SaciUserAdmin(admin.ModelAdmin):
    pass

# class SaciCourseAdmin(admin.ModelAdmin):
#     pass

# class SaciClassAdmin(admin.ModelAdmin):
#     pass

# class SaciExerciseAdmin(admin.ModelAdmin):
#     pass

admin.site.register(SaciUser,SaciUserAdmin)
# admin.site.register(SaciCourse,SaciCourseAdmin)
# admin.site.register(SaciClass,SaciClassAdmin)
# admin.site.register(SaciExercise,SaciExerciseAdmin)
