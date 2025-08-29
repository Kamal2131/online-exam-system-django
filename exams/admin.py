from django.contrib import admin
from .models import Exam, Question, Option, ExamRegistration

class OptionInline(admin.TabularInline):
    model = Option
    extra = 1  # Number of empty option forms to display

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    show_change_link = True

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'difficulty', 'duration_minutes', 'passing_score', 'is_active', 'created_at')
    list_filter = ('difficulty', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    inlines = [QuestionInline]
    readonly_fields = ('created_at', 'updated_at')
    
    # Prepopulate the slug field from the title
    # prepopulated_fields = {'slug': ('title',)}  # Optional: if you add a slug field

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'question_text', 'question_type', 'points', 'order')
    list_filter = ('question_type', 'exam')
    search_fields = ('question_text',)
    inlines = [OptionInline]
    list_editable = ('order',)  # Allow editing order directly from list view

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('question', 'option_text', 'is_correct')
    list_filter = ('is_correct', 'question__exam')
    search_fields = ('option_text', 'question__question_text')

@admin.register(ExamRegistration)
class ExamRegistrationAdmin(admin.ModelAdmin):
    list_display = ('exam', 'student', 'registered_at', 'completed_at', 'score', 'is_passed')
    list_filter = ('is_passed', 'exam', 'registered_at')
    search_fields = ('student__username', 'exam__title')
    readonly_fields = ('registered_at',)