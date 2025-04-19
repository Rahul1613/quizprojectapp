from django.contrib.auth.views import LoginView
from django.urls import path

from teacher import views

from . import exam_slots

urlpatterns = [
    # Authentication
    path('teacherlogin/', LoginView.as_view(template_name='teacher/teacherlogin.html'), name='teacherlogin'),
    path('teachersignup/', views.teacher_signup_view, name='teachersignup'),

    # Dashboard & Exams
    path('teacher-dashboard/', views.teacher_dashboard_view, name='teacher-dashboard'),
    path('teacher-exam/', views.teacher_exam_view, name='teacher-exam'),
    path('teacher-add-exam/', views.teacher_add_exam_view, name='teacher-add-exam'),
    path('teacher-view-exam/', views.teacher_view_exam_view, name='teacher-view-exam'),
    path('delete-exam/<int:pk>/', views.delete_exam_view, name='delete-exam'),

    # Questions
    path('teacher-question/', views.teacher_question_view, name='teacher-question'),
    path('teacher-add-question/', views.teacher_add_question_view, name='teacher-add-question'),
    path('teacher-view-question/', views.teacher_view_question_view, name='teacher-view-question'),
    path('see-question/<int:pk>/', views.see_question_view, name='see-question'),
    path('remove-question/<int:pk>/', views.remove_question_view, name='remove-question'),
    path('upload-questions-csv/', views.upload_questions_csv_view, name='upload-questions-csv'),

    # Exam Slots
    path('exam-slots/', exam_slots.exam_slots_view, name='exam-slots'),
    path('teacher-slots/', exam_slots.teacher_slots_view, name='teacher-slots'),
]
