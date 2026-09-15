from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import User
from apps.accounts.permissions import IsAdmin, IsSupervisor
from apps.students.models import StudentProfile
from apps.students.serializers import StudentSummarySerializer

from .filters import SupervisorProfileFilter
from .models import SupervisorProfile
from .serializers import SupervisorProfileSerializer


class SupervisorProfileViewSet(viewsets.ModelViewSet):
    serializer_class = SupervisorProfileSerializer
    filterset_class = SupervisorProfileFilter
    search_fields = ["staff_number", "user__email", "user__first_name", "user__last_name"]
    ordering_fields = ["staff_number", "created_at", "user__last_name"]
    ordering = ["user__last_name", "user__first_name"]

    def get_queryset(self):
        queryset = SupervisorProfile.objects.select_related("user")
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none()
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.SUPERVISOR:
            return queryset.filter(user=user)
        return queryset.none()

    def get_permissions(self):
        if self.action in {"list", "create", "destroy"}:
            return [IsAdmin()]
        return [IsAuthenticated()]

    def perform_destroy(self, instance):
        instance.user.delete()


class MySupervisorProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = SupervisorProfileSerializer
    permission_classes = [IsSupervisor]

    def get_object(self):
        return self.request.user.supervisor_profile


class MyAssignedStudentsView(generics.ListAPIView):
    queryset = StudentProfile.objects.none()
    serializer_class = StudentSummarySerializer
    permission_classes = [IsSupervisor]
    search_fields = ["registration_number", "user__first_name", "user__last_name"]
    ordering = ["registration_number"]

    def get_queryset(self):
        user = self.request.user
        if user.role != User.Role.SUPERVISOR:
            return StudentProfile.objects.none()
        return (
            StudentProfile.objects.filter(placements__supervisor__user=user)
            .select_related("user")
            .distinct()
        )
