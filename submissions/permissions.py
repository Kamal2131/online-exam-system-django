from rest_framework import permissions

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'student'

class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'teacher'

class IsOwnerOrTeacher(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.user_type == 'teacher' and obj.exam.creator == request.user:
            return True
        return obj.student == request.user