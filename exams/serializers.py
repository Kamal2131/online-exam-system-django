from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Exam, Question, Option, ExamRegistration
from users.models import User

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'question', 'option_text', 'is_correct', 'order']
        read_only_fields = ['question']

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'exam', 'question_text', 'question_type', 'points', 'order', 'options', 'explanation']
        read_only_fields = ['exam']

class ExamSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    creator_name = serializers.CharField(source='creator.get_full_name', read_only=True)
    
    class Meta:
        model = Exam
        fields = [
            'id', 'title', 'description', 'creator', 'creator_name', 
            'duration_minutes', 'passing_score', 'difficulty', 'is_active',
            'start_time', 'end_time', 'created_at', 'updated_at', 'questions'
        ]
        read_only_fields = ['creator', 'created_at', 'updated_at']

class ExamListSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='creator.get_full_name', read_only=True)
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Exam
        fields = [
            'id', 'title', 'description', 'creator_name', 
            'duration_minutes', 'passing_score', 'difficulty',
            'created_at', 'question_count'
        ]
    
    @extend_schema_field(serializers.IntegerField())
    def get_question_count(self, obj):
        return obj.questions.count()

class ExamRegistrationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    exam_title = serializers.CharField(source='exam.title', read_only=True)
    
    class Meta:
        model = ExamRegistration
        fields = [
            'id', 'exam', 'exam_title', 'student', 'student_name',
            'registered_at', 'started_at', 'completed_at', 'score', 'is_passed'
        ]
        read_only_fields = ['student', 'registered_at', 'started_at', 'completed_at', 'score', 'is_passed']

class AnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer = serializers.JSONField()

class ExamTakeSerializer(serializers.Serializer):
    answers = AnswerSerializer(many=True)

# For bulk import functionality
class BulkQuestionImportSerializer(serializers.Serializer):
    question_text = serializers.CharField()
    question_type = serializers.ChoiceField(choices=Question.QUESTION_TYPES)
    points = serializers.IntegerField(default=1)
    order = serializers.IntegerField(default=0)
    explanation = serializers.CharField(required=False, allow_blank=True)
    options = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )