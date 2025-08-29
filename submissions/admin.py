from django.contrib import admin
from .models import ExamAttempt, Answer

@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'start_time', 'end_time', 'is_submitted', 'score', 'passed']
    list_filter = ['is_submitted', 'passed', 'exam']
    search_fields = ['student__username', 'exam__title']

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'is_correct']
    list_filter = ['is_correct']
    search_fields = ['attempt__student__username', 'question__question_text']