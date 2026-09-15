from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.cohorts.models import Cohort
from apps.students.models import StudentProfile
from apps.supervisors.models import SupervisorProfile
from apps.tracks.models import Track

from .models import Placement


class PlacementSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects.all())
    supervisor = serializers.PrimaryKeyRelatedField(queryset=SupervisorProfile.objects.all())
    track = serializers.PrimaryKeyRelatedField(queryset=Track.objects.all())
    cohort = serializers.PrimaryKeyRelatedField(queryset=Cohort.objects.all())
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    registration_number = serializers.CharField(
        source="student.registration_number", read_only=True
    )
    supervisor_name = serializers.CharField(source="supervisor.user.full_name", read_only=True)
    track_name = serializers.CharField(source="track.name", read_only=True)
    cohort_name = serializers.CharField(source="cohort.name", read_only=True)
    created_by = serializers.UUIDField(source="created_by_id", read_only=True)
    total_expected_reports = serializers.IntegerField(read_only=True)

    class Meta:
        model = Placement
        fields = [
            "id",
            "student",
            "student_name",
            "registration_number",
            "supervisor",
            "supervisor_name",
            "track",
            "track_name",
            "cohort",
            "cohort_name",
            "start_date",
            "end_date",
            "status",
            "total_expected_reports",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def validate(self, attrs):
        candidate = Placement(
            student=attrs.get("student", getattr(self.instance, "student", None)),
            supervisor=attrs.get("supervisor", getattr(self.instance, "supervisor", None)),
            track=attrs.get("track", getattr(self.instance, "track", None)),
            cohort=attrs.get("cohort", getattr(self.instance, "cohort", None)),
            start_date=attrs.get("start_date", getattr(self.instance, "start_date", None)),
            end_date=attrs.get("end_date", getattr(self.instance, "end_date", None)),
            status=attrs.get("status", getattr(self.instance, "status", Placement.Status.PLACED)),
        )
        if self.instance:
            candidate.pk = self.instance.pk
        try:
            candidate.clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from exc
        return attrs
