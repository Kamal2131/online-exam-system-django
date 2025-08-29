from django.urls import path
from . import views

urlpatterns = [
    path('', views.ExamListView.as_view(), name='exam-list'),
    path('<int:pk>/', views.ExamDetailView.as_view(), name='exam-detail'),
    path('<int:exam_id>/register/', views.ExamRegistrationView.as_view(), name='exam-register'),
    path('my-registrations/', views.UserExamRegistrationsView.as_view(), name='my-exam-registrations'),
    path('<int:exam_id>/take/', views.TakeExamView.as_view(), name='take-exam'),
    path('<int:exam_id>/submit/', views.submit_exam, name='submit-exam'),
    
    
    # Question management URLs
    path('<int:exam_id>/questions/', views.QuestionListView.as_view(), name='question-list'),
    path('<int:exam_id>/questions/<int:question_id>/', views.QuestionDetailView.as_view(), name='question-detail'),
    path('<int:exam_id>/questions/<int:question_id>/options/', views.OptionListView.as_view(), name='option-list'),
    path('<int:exam_id>/questions/<int:question_id>/options/<int:option_id>/', views.OptionDetailView.as_view(), name='option-detail'),
    path('<int:exam_id>/bulk-import-questions/', views.bulk_import_questions, name='bulk-import-questions'),
]