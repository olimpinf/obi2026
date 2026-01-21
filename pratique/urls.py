from django.urls import include, path, re_path


from . import views

app_name = 'pratique'
urlpatterns = [
    path('', views.index, name='index'),
    path('teste', views.teste, name='teste'),
    
    path('<str:level>/', views.index_level, name='index_level'),
    path('<str:level>/exemplo_c', views.example_c, name='example_c'),
    path('<str:level>/exemplo_cpp', views.example_cpp, name='example_cpp'),
    path('<str:level>/exemplo_py', views.example_py, name='example_py'),
    path('<str:level>/exemplo_java', views.example_java, name='example_java'),
    path('<str:level>/exemplo_js', views.example_js, name='example_js'),
    path('i<str:level>/<int:year>/f<int:phase>/<str:code>/corrige/', views.corrige_iniciacao, name='corrige_iniciacao'),
    path('i<str:level>/<int:year>/f<int:phase>/<str:code>/', views.tarefa_iniciacao, name='tarefa_iniciacao'),
    path('p<str:level>/<int:year>/f<str:phase>/<str:code>/corrige/', views.corrige_programacao, name='corrige_programacao'),
    path('p<str:level>/<int:year>/f<str:phase>/<str:code>/resultado/', views.corrige_programacao_resultado, name='corrige_programacao_resultado'),
    path('p<str:level>/<int:year>/f<str:phase>/<str:code>/', views.tarefa_programacao, name='tarefa_programacao'),
]
