from rest_framework import serializers
from .models import ExamAttempt, Answer
from exams.models import Exam, Question, Option
from django.utils import timezone

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'option_text']

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'points', 'order', 'options']

class ExamSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    is_available = serializers.SerializerMethodField()
    
    class Meta:
        model = Exam
        fields = '__all__'
    
    def get_is_available(self, obj):
        now = timezone.now()
        return obj.is_active

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'answer_text']
        read_only_fields = ['id']

class ExamAttemptSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    
    class Meta:
        model = ExamAttempt
        fields = ['id', 'exam', 'student', 'start_time', 'end_time', 'is_submitted', 'score', 'passed', 'answers']
        read_only_fields = ['id', 'student', 'start_time', 'end_time', 'score', 'passed']
    
    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        attempt = ExamAttempt.objects.create(**validated_data)
        
        for answer_data in answers_data:
            answer = Answer.objects.create(attempt=attempt, **answer_data)
            answer.check_answer()  # Check if answer is correct
        
        # Calculate score after submission
        if validated_data.get('is_submitted', False):
            attempt.end_time = timezone.now()
            attempt.calculate_score()
        
        return attempt
    
    def validate(self, data):
        # Check if exam is active
        if not data['exam'].is_active:
            raise serializers.ValidationError("This exam is not currently available.")
        
        # Check if student has already attempted this exam
        if ExamAttempt.objects.filter(student=data['student'], exam=data['exam']).exists():
            raise serializers.ValidationError("You have already attempted this exam.")
        
        return data