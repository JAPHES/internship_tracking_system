from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.placements.models import Placement

from .models import WeeklyReport


class WeeklyReportSerializer(serializers.ModelSerializer):
    placement = serializers.PrimaryKeyRelatedField(queryset=Placement.objects.all())
    student_name = serializers.CharField(source="placement.student.user.full_name", read_only=True)
    registration_number = serializers.CharField(
        source="placement.student.registration_number", read_only=True
    )
    supervisor_name = serializers.CharField(
        source="placement.supervisor.user.full_name", read_only=True
    )
    reviewed_by = serializers.UUIDField(source="reviewed_by_id", read_only=True)

    class Meta:
        model = WeeklyReport
        fields = [
            "id",
            "placement",
            "student_name",
            "registration_number",
            "supervisor_name",
            "week_number",
            "week_start_date",
            "week_end_date",
            "activities_completed",
            "skills_learned",
            "challenges_faced",
            "status",
            "supervisor_feedback",
            "submitted_at",
            "reviewed_at",
            "reviewed_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "supervisor_feedback",
            "submitted_at",
            "reviewed_at",
            "reviewed_by",
            "created_at",
            "updated_at",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated and request.user.role == "STUDENT":
            self.fields["placement"].queryset = Placement.objects.filter(student__user=request.user)

    def validate(self, attrs):
        placement = attrs.get("placement", getattr(self.instance, "placement", None))
        request = self.context.get("request")
        if self.instance is None:
            if not request or placement.student.user_id != request.user.id:
                raise serializers.ValidationError(
                    {"placement": "Students can only report against their own placement."}
                )
            if placement.status != Placement.Status.ACTIVE:
                raise serializers.ValidationError(
                    {"placement": "Reports can only be created for an active placement."}
                )

        candidate = WeeklyReport(
            placement=placement,
            week_number=attrs.get("week_number", getattr(self.instance, "week_number", None)),
            week_start_date=attrs.get(
                "week_start_date", getattr(self.instance, "week_start_date", None)
            ),
            week_end_date=attrs.get("week_end_date", getattr(self.instance, "week_end_date", None)),
            activities_completed=attrs.get(
                "activities_completed", getattr(self.instance, "activities_completed", "")
            ),
            skills_learned=attrs.get(
                "skills_learned", getattr(self.instance, "skills_learned", "")
            ),
        )
        if self.instance:
            candidate.pk = self.instance.pk
        try:
            candidate.clean()
        except (DjangoValidationError, TypeError) as exc:
            details = getattr(exc, "message_dict", {"detail": str(exc)})
            raise serializers.ValidationError(details) from exc

        week_number = candidate.week_number
        duplicate = WeeklyReport.objects.filter(placement=placement, week_number=week_number)
        if self.instance:
            duplicate = duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise serializers.ValidationError(
                {"week_number": "A report already exists for this placement week."}
            )
        return attrs


class ReviewReportSerializer(serializers.Serializer):
    supervisor_feedback = serializers.CharField(allow_blank=False)
