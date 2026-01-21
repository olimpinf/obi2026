from django.urls import include, path, re_path

from . import views

app_name = 'inep'
urlpatterns = [
    path('consulta/<int:inep_code>', views.consulta, name='consulta'),
]
