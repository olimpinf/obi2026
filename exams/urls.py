from django.conf import settings
from django.urls import include, path, re_path

from . import views

app_name = 'exams'
urlpatterns = [
    path('', views.index, name='index'),
    path('<str:exam_descriptor>/', views.exam, name='exam'),
    path('<str:exam_descriptor>/iniciar/', views.start_exam, name='start_exam'),
    path('<str:exam_descriptor>/reiniciar/', views.restart_exam, name='restart_exam'),
    #path('<str:exam_descriptor>/mostra_subm/', views.show_submissions, name='show_submissions'),
    path('<str:exam_descriptor>/recupera_log/<int:compet_id>/<int:sub_id>', views.retrieve_res_log_coord, name='retrieve_res_log_coord'),
    path('<str:exam_descriptor>/recupera_logj/<int:compet_id>/<int:sub_id>', views.retrieve_res_log_judge_coord, name='retrieve_res_log_judge_coord'),
    path('<str:exam_descriptor>/recupera_subm/<int:compet_id>/<int:sub_id>', views.retrieve_submission_coord, name='retrieve_submission_coord'),
    path('<str:exam_descriptor>/recupera_log/<int:sub_id>', views.retrieve_res_log, name='retrieve_res_log'),
    path('<str:exam_descriptor>/recupera_subm/<int:sub_id>', views.retrieve_submission, name='retrieve_submission'),
    path('<str:exam_descriptor>/encerrar/', views.finish_exam, name='finish_exam'),
    path('<str:exam_descriptor>/revisar/', views.finish_review_exam, name='finish_review_exam'),
    path('<str:exam_descriptor>/resultado/', views.exam_review, name='review_exam'),
    path('<str:exam_descriptor>/resultado/recupera_log/<int:sub_id>', views.retrieve_res_log_judge, name='retrieve_res_log_judge'),
    path('<str:exam_descriptor>/resultado/mostra_subm/', views.show_results_prog, name='show_results_prog'),
    path('<str:exam_descriptor>/resultado/mostra_subm/<int:subm_id>/', views.show_result_details_prog, name='show_result_details_prog'),
    path('<str:exam_descriptor>/resultado/mostra_res/<int:compet_id>/', views.show_results_coord, name='show_results_coord'),
    path('<str:exam_descriptor>/resultado/mostra_res/<int:compet_id>/<int:subm_id>/', views.show_result_details_prog_coord, name='show_result_details_prog_coord'),
    path('<str:exam_descriptor>/resultado/<str:task_descriptor>/', views.exam_task_review, name='exam_task_review'),
    path('<str:exam_descriptor>/<str:task_name>/salvar', views.save_exam_answer, name='save_exam_answer'),
    path('<str:exam_descriptor>/<str:task_descriptor>/', views.exam_task, name='exam_task'),
    path('<str:exam_descriptor>/ranking/<int:compet_type>/', views.show_ranking_prog, name='show_ranking_prog'),
 ]

