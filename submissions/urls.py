from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExamViewSet, ExamAttemptViewSet

router = DefaultRouter()
router.register(r'exams', ExamViewSet, basename='exam')
router.register(r'attempts', ExamAttemptViewSet, basename='examattempt')

urlpatterns = [
    path('', include(router.urls)),
]