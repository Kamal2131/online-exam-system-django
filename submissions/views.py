from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ExamAttempt, Answer
from .serializers import ExamSerializer, ExamAttemptSerializer, QuestionSerializer  # Add ExamSerializer import
from .permissions import IsStudent, IsTeacher, IsOwnerOrTeacher
from exams.models import Exam
from django.utils import timezone

class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ExamSerializer  # This was causing the error
    permission_classes = [IsAuthenticated]
    queryset = Exam.objects.all()
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'student':
            return Exam.objects.filter(is_active=True)
        elif user.user_type == 'teacher':
            return Exam.objects.filter(creator=user)
        return Exam.objects.all()
    
    @action(detail=True, methods=['post'], permission_classes=[IsStudent])
    def start_attempt(self, request, pk=None):
        exam = self.get_object()
        
        # Check if exam is active
        if not exam.is_active:
            return Response(
                {"error": "This exam is not currently available."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if student has already attempted this exam
        if ExamAttempt.objects.filter(student=request.user, exam=exam).exists():
            return Response(
                {"error": "You have already attempted this exam."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create a new attempt
        attempt = ExamAttempt.objects.create(
            student=request.user,
            exam=exam
        )
        
        return Response({
            "attempt_id": attempt.id,
            "message": "Exam attempt started successfully.",
            "start_time": attempt.start_time
        })
    
    @action(detail=True, methods=['get'], permission_classes=[IsStudent])
    def questions(self, request, pk=None):
        exam = self.get_object()
        questions = exam.questions.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

class ExamAttemptViewSet(viewsets.ModelViewSet):
    serializer_class = ExamAttemptSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrTeacher]
    queryset = ExamAttempt.objects.all()
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'student':
            return ExamAttempt.objects.filter(student=user)
        elif user.user_type == 'teacher':
            # Teachers can see attempts for exams they created
            return ExamAttempt.objects.filter(exam__creator=user)
        return ExamAttempt.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsStudent])
    def submit(self, request, pk=None):
        attempt = self.get_object()
        
        if attempt.student != request.user:
            return Response(
                {"error": "You are not authorized to submit this attempt."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if attempt.is_submitted:
            return Response(
                {"error": "This attempt has already been submitted."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update attempt as submitted
        attempt.is_submitted = True
        attempt.end_time = timezone.now()
        attempt.save()
        
        # Calculate score
        attempt.calculate_score()
        
        return Response({
            "message": "Exam submitted successfully.",
            "score": attempt.score,
            "passed": attempt.passed
        })