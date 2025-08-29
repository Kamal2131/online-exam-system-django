from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from exams.models import Exam, Question

User = get_user_model()

class ExamAttempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_attempts')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='attempts')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    is_submitted = models.BooleanField(default=False)
    score = models.FloatField(default=0)
    passed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('student', 'exam')
    
    def calculate_score(self):
        # Calculate the score based on answers
        answers = self.answers.all()
        total_marks = 0
        obtained_marks = 0
        
        for answer in answers:
            total_marks += answer.question.points
            if answer.is_correct:
                obtained_marks += answer.question.points
        
        if total_marks > 0:
            self.score = (obtained_marks / total_marks) * 100
            self.passed = self.score >= self.exam.passing_score
            self.save()
        
        return self.score

class Answer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('attempt', 'question')
    
    def check_answer(self):
        if self.question.question_type in ['multiple_choice', 'true_false']:
            # For multiple choice, check if the selected option is correct
            if self.question.question_type == 'multiple_choice':
                try:
                    selected_option = self.question.options.get(option_text=self.answer_text)
                    self.is_correct = selected_option.is_correct
                except Option.DoesNotExist:
                    self.is_correct = False
            # For true/false, compare directly
            elif self.question.question_type == 'true_false':
                # Assuming the correct answer is stored in the first option
                correct_option = self.question.options.filter(is_correct=True).first()
                if correct_option:
                    self.is_correct = self.answer_text.strip().lower() == correct_option.option_text.strip().lower()
            
            self.save()
        # For short answer questions, is_correct remains False until manually graded
        return self.is_correct