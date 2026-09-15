from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from apps.common.models import TimeStampedUUIDModel
from apps.common.validators import validate_date_range


class WeeklyReport(TimeStampedUUIDModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        REVIEWED = "REVIEWED", "Reviewed"

    placement = models.ForeignKey(
        "placements.Placement", on_delete=models.CASCADE, related_name="reports"
    )
    week_number = models.PositiveIntegerField()
    week_start_date = models.DateField()
    week_end_date = models.DateField()
    activities_completed = models.TextField()
    skills_learned = models.TextField()
    challenges_faced = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    supervisor_feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="reports_reviewed",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-week_start_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["placement", "week_number"], name="unique_report_placement_week"
            ),
            models.CheckConstraint(condition=Q(week_number__gte=1), name="report_week_positive"),
            models.CheckConstraint(
                condition=Q(week_end_date__gte=F("week_start_date")),
                name="report_valid_date_range",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "submitted_at"], name="report_status_submitted_idx"),
            models.Index(fields=["placement", "week_number"], name="report_placement_week_idx"),
        ]

    def clean(self):
        super().clean()
        validate_date_range(self.week_start_date, self.week_end_date)
        if not self.placement_id:
            return
        expected_start = self.placement.start_date + timedelta(days=7 * (self.week_number - 1))
        expected_end = min(expected_start + timedelta(days=6), self.placement.end_date)
        if expected_start > self.placement.end_date:
            raise ValidationError({"week_number": "This week falls after the placement ends."})
        if self.week_start_date != expected_start or self.week_end_date != expected_end:
            raise ValidationError(
                {
                    "week_start_date": f"Week {self.week_number} must start on {expected_start}.",
                    "week_end_date": f"Week {self.week_number} must end on {expected_end}.",
                }
            )

    def submit(self, user) -> None:
        """Move a draft/reviewed report to submitted and retain prior feedback."""

        if self.placement.student.user_id != user.id:
            raise ValidationError("Only the placement student can submit this report.")
        if self.placement.status != "ACTIVE":
            raise ValidationError("Reports can only be submitted for an active placement.")
        if self.status not in {self.Status.DRAFT, self.Status.REVIEWED, self.Status.SUBMITTED}:
            raise ValidationError("This report cannot be submitted in its current state.")
        self.status = self.Status.SUBMITTED
        self.submitted_at = timezone.now()
        self.reviewed_at = None
        self.reviewed_by = None

    def review(self, user, feedback: str) -> None:
        """Review a submitted report as its assigned supervisor."""

        if self.placement.supervisor.user_id != user.id:
            raise ValidationError("Only the assigned supervisor can review this report.")
        if self.status != self.Status.SUBMITTED:
            raise ValidationError("Only submitted reports can be reviewed.")
        self.status = self.Status.REVIEWED
        self.supervisor_feedback = feedback
        self.reviewed_at = timezone.now()
        self.reviewed_by = user

    def __str__(self) -> str:
        return f"{self.placement.student} - week {self.week_number}"
