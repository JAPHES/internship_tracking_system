from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import User
from apps.accounts.permissions import IsAdmin, IsStudent

from .filters import StudentProfileFilter
from .models import StudentProfile
from .serializers import StudentProfileSerializer


class StudentProfileViewSet(viewsets.ModelViewSet):
    serializer_class = StudentProfileSerializer
    filterset_class = StudentProfileFilter
    search_fields = ["registration_number", "user__email", "user__first_name", "user__last_name"]
    ordering_fields = ["registration_number", "created_at", "user__last_name"]
    ordering = ["registration_number"]

    def get_queryset(self):
        queryset = StudentProfile.objects.select_related("user")
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none()
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.STUDENT:
            return queryset.filter(user=user)
        return queryset.none()

    def get_permissions(self):
        if self.action in {"list", "create", "destroy"}:
            return [IsAdmin()]
        return [IsAuthenticated()]

    def perform_destroy(self, instance):
        instance.user.delete()


class MyStudentProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = StudentProfileSerializer
    permission_classes = [IsStudent]

    def get_object(self):
        return self.request.user.student_profile
