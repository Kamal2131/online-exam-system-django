from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Exam, Question, Option, ExamRegistration
from django.db import transaction
from .serializers import (
    ExamSerializer, ExamListSerializer,
    ExamRegistrationSerializer, ExamTakeSerializer,
    QuestionSerializer, OptionSerializer
)
from users.models import User
from drf_spectacular.utils import extend_schema, OpenApiParameter


# --------------------
# Custom Permissions
# --------------------
class IsTeacherOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['teacher', 'admin']


# --------------------
# Exam List + Create
# --------------------
@extend_schema(
    parameters=[
        OpenApiParameter(name='difficulty', description='Filter by difficulty', required=False, type=str),
        OpenApiParameter(name='search', description='Search by title', required=False, type=str),
        OpenApiParameter(name='ordering', description='Order by field (- for descending)', required=False, type=str),
    ]
)
class ExamListView(generics.ListCreateAPIView):
    serializer_class = ExamListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Exam.objects.filter(is_active=True)

        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)

        # Search by title
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)

        # Ordering
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering in ['title', '-title', 'created_at', '-created_at', 'difficulty']:
            queryset = queryset.order_by(ordering)

        return queryset

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsTeacherOrAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


# --------------------
# Exam Detail
# --------------------
class ExamDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsTeacherOrAdmin()]
        return [permissions.IsAuthenticated()]


# --------------------
# Exam Registration
# --------------------
class ExamRegistrationView(generics.CreateAPIView):
    serializer_class = ExamRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ExamRegistration.objects.all()

    def create(self, request, *args, **kwargs):
        exam_id = self.kwargs.get('exam_id')
        exam = get_object_or_404(Exam, id=exam_id, is_active=True)

        now = timezone.now()
        # Validate exam window
        if exam.start_time and now > exam.start_time:
            return Response({"error": "Registration closed, exam already started."}, status=400)
        if exam.end_time and now > exam.end_time:
            return Response({"error": "Exam already ended."}, status=400)

        # Check if already registered
        if ExamRegistration.objects.filter(exam=exam, student=request.user).exists():
            return Response({"error": "Already registered for this exam."}, status=400)

        # Create registration
        registration = ExamRegistration.objects.create(
            exam=exam,
            student=request.user
        )

        serializer = self.get_serializer(registration)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# --------------------
# User’s Exam Registrations
# --------------------
class UserExamRegistrationsView(generics.ListAPIView):
    serializer_class = ExamRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ExamRegistration.objects.filter(student=self.request.user)


# --------------------
# Take Exam
# --------------------
class TakeExamView(generics.RetrieveAPIView):
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        exam_id = self.kwargs.get('exam_id')
        exam = get_object_or_404(Exam, id=exam_id, is_active=True)

        now = timezone.now()
        if exam.start_time and now < exam.start_time:
            self.permission_denied(self.request, message="Exam has not started yet.")
        if exam.end_time and now > exam.end_time:
            self.permission_denied(self.request, message="Exam already ended.")

        # Check if user is registered
        get_object_or_404(
            ExamRegistration,
            exam=exam,
            student=self.request.user,
            completed_at__isnull=True
        )

        return exam


# --------------------
# Submit Exam
# --------------------
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, is_active=True)

    # Check registration
    registration = get_object_or_404(
        ExamRegistration,
        exam=exam,
        student=request.user,
        completed_at__isnull=True
    )

    serializer = ExamTakeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    answers = serializer.validated_data['answers']

    # Bulk fetch questions + options
    questions = exam.questions.prefetch_related("options").all()
    question_map = {q.id: q for q in questions}

    total_questions = len(question_map)
    correct_answers = 0

    for answer in answers:
        qid = answer.get('question_id')
        user_answer = answer.get('answer')

        question = question_map.get(qid)
        if not question:
            continue  # invalid question id ignored

        if question.question_type == 'multiple_choice':
            correct_option = question.options.filter(is_correct=True).first()
            if correct_option and str(correct_option.id) == str(user_answer):
                correct_answers += 1

        elif question.question_type == 'multiple_select':
            # For multiple correct answers
            correct_set = set(map(str, question.options.filter(is_correct=True).values_list("id", flat=True)))
            user_set = set(map(str, user_answer if isinstance(user_answer, list) else [user_answer]))
            if correct_set == user_set:
                correct_answers += 1

        # TODO: handle other question types (text, numeric, etc.)

    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    is_passed = score >= exam.passing_score

    # Update registration
    registration.score = score
    registration.is_passed = is_passed
    registration.completed_at = timezone.now()
    registration.save()

    return Response({
        "score": score,
        "is_passed": is_passed,
        "correct_answers": correct_answers,
        "total_questions": total_questions
    })


# --------------------
# Question Management
# --------------------
class QuestionListView(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        exam_id = self.kwargs.get('exam_id')
        exam = get_object_or_404(Exam, id=exam_id)
        # Ensure user has permission to view questions for this exam
        if exam.creator != self.request.user and self.request.user.role != 'admin':
            raise permissions.PermissionDenied("You don't have permission to view questions for this exam.")
        return Question.objects.filter(exam=exam)

    def perform_create(self, serializer):
        exam_id = self.kwargs.get('exam_id')
        exam = get_object_or_404(Exam, id=exam_id)
        # Ensure user has permission to add questions to this exam
        if exam.creator != self.request.user and self.request.user.role != 'admin':
            raise permissions.PermissionDenied("You don't have permission to add questions to this exam.")
        serializer.save(exam=exam)


class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        return Question.objects.all()

    def get_object(self):
        question = get_object_or_404(Question, id=self.kwargs.get('question_id'))
        # Ensure user has permission to modify this question
        if question.exam.creator != self.request.user and self.request.user.role != 'admin':
            raise permissions.PermissionDenied("You don't have permission to modify this question.")
        return question


class OptionListView(generics.ListCreateAPIView):
    serializer_class = OptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        question_id = self.kwargs.get('question_id')
        question = get_object_or_404(Question, id=question_id)
        # Ensure user has permission to view options for this question
        if question.exam.creator != self.request.user and self.request.user.role != 'admin':
            raise permissions.PermissionDenied("You don't have permission to view options for this question.")
        return Option.objects.filter(question=question)

    def perform_create(self, serializer):
        question_id = self.kwargs.get('question_id')
        question = get_object_or_404(Question, id=question_id)
        # Ensure user has permission to add options to this question
        if question.exam.creator != self.request.user and self.request.user.role != 'admin':
            raise permissions.PermissionDenied("You don't have permission to add options to this question.")
        serializer.save(question=question)


class OptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        return Option.objects.all()

    def get_object(self):
        option = get_object_or_404(Option, id=self.kwargs.get('option_id'))
        # Ensure user has permission to modify this option
        if option.question.exam.creator != self.request.user and self.request.user.role != 'admin':
            raise permissions.PermissionDenied("You don't have permission to modify this option.")
        return option


# --------------------
# Bulk Question Import
# --------------------
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsTeacherOrAdmin])
@transaction.atomic
def bulk_import_questions(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    
    # Check permission
    if exam.creator != request.user and request.user.role != 'admin':
        return Response({"error": "You don't have permission to add questions to this exam."}, status=403)
    
    # Expected format: list of questions with options
    # [
    #   {
    #     "question_text": "What is 2+2?",
    #     "question_type": "multiple_choice",
    #     "points": 1,
    #     "order": 1,
    #     "explanation": "Basic arithmetic",
    #     "options": [
    #       {"option_text": "3", "is_correct": false, "order": 1},
    #       {"option_text": "4", "is_correct": true, "order": 2},
    #       {"option_text": "5", "is_correct": false, "order": 3}
    #     ]
    #   },
    #   ...
    # ]
    
    data = request.data
    if not isinstance(data, list):
        return Response({"error": "Expected a list of questions"}, status=400)
    
    created_questions = []
    
    for question_data in data:
        options_data = question_data.pop('options', [])
        
        # Create question
        question_serializer = QuestionSerializer(data=question_data)
        if question_serializer.is_valid():
            question = question_serializer.save(exam=exam)
            
            # Create options for this question
            for option_data in options_data:
                option_serializer = OptionSerializer(data=option_data)
                if option_serializer.is_valid():
                    option_serializer.save(question=question)
                else:
                    # If any option is invalid, rollback the transaction
                    raise serializers.ValidationError(option_serializer.errors)
            
            created_questions.append(question)
        else:
            # If any question is invalid, rollback the transaction
            raise serializers.ValidationError(question_serializer.errors)
    
    return Response(
        QuestionSerializer(created_questions, many=True).data,
        status=status.HTTP_201_CREATED
    )