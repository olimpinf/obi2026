from django.conf import settings
from django.urls import include, path, re_path

from saci import views

app_name = 'saci'
urlpatterns = [
    path('', views.index, name='index'),
    path('cursos', views.courses, name='courses'),
    path('cursos/<str:course_id>/', views.show_course, name='show_course'),
    path('cursos/<str:course_id>/<str:class_id>/', views.show_class, name='show_class'),
    #path('cursos/intro_js', views.intro_js, name='intro_js'),
    path('log_event', views.log_event, name='log_event'),
    path('add_a_backup', views.add_a_backup, name='add_a_backup'),
    path('retrieve_backups', views.retrieve_backups, name='retrieve_backups'),
    path('delete_a_backup', views.delete_a_backup, name='delete_a_backup'),
    path('retrieve_a_backup', views.retrieve_a_backup, name='retrieve_a_backup'),
    path('registrar', views.register, name='saci_register'),
]
