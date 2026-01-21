# urls.py

from django.urls import path
from django.conf import settings
from . import views

app_name = 'editor'
urlpatterns = [
#    path('', views.serve_editor, name='editor_index'),
#    path('<path:path>', views.serve_editor, name='editor_files'),
    # path('retrieve_backups', views.retrieve_backups, name='retrieve_backups'),
    # path('retrieve_a_backup', views.retrieve_a_backup, name='retrieve_a_backup'),
    # path('delete_a_backup', views.delete_a_backup, name='delete_a_backup'),
    # path('add_a_backup', views.add_a_backup, name='add_a_backup'),
]
