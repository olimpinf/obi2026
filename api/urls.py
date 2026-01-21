# urls.py

from django.urls import path
from django.conf import settings
from . import views

app_name = 'api'
urlpatterns = [
    path('retrieve_backups', views.retrieve_backups, name='retrieve_backups'),
    path('retrieve_a_backup', views.retrieve_a_backup, name='retrieve_a_backup'),
    path('delete_a_backup', views.delete_a_backup, name='delete_a_backup'),
    path('add_a_backup', views.add_a_backup, name='add_a_backup'),
]
