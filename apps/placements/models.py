from math import ceil

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q

from apps.common.models import TimeStampedUUIDModel
from apps.common.validators import validate_date_range


class Placement(TimeStampedUUIDModel):
    class Status(models.TextChoices):
        PLACED = "PLACED", "Placed"
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"

    student = models.ForeignKey(
        "students.StudentProfile", on_delete=models.PROTECT, related_name="placements"
    )
    supervisor = models.ForeignKey(
        "supervisors.SupervisorProfile", on_delete=models.PROTECT, related_name="placements"
    )
    track = models.ForeignKey("tracks.Track", on_delete=models.PROTECT, related_name="placements")
    cohort = models.ForeignKey(
        "cohorts.Cohort", on_delete=models.PROTECT, related_name="placements"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLACED)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="placements_created",
    )

    class Meta:
        ordering = ["-start_date", "student__registration_number"]
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__gte=F("start_date")), name="placement_valid_date_range"
            ),
            models.UniqueConstraint(
                fields=["student"],
                condition=~Q(status="COMPLETED"),
                name="one_current_placement_per_student",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "start_date"], name="placement_status_start_idx"),
            models.Index(fields=["supervisor", "status"], name="placement_supervisor_idx"),
            models.Index(fields=["cohort", "status"], name="placement_cohort_idx"),
        ]

    def clean(self):
        super().clean()
        validate_date_range(self.start_date, self.end_date)
        if self.student_id and self.student.user.role != "STUDENT":
            raise ValidationError({"student": "The selected profile is not a student."})
        if self.supervisor_id and self.supervisor.user.role != "SUPERVISOR":
            raise ValidationError({"supervisor": "The selected profile is not a supervisor."})
        if self.student_id and self.status != self.Status.COMPLETED:
            duplicate = Placement.objects.filter(student_id=self.student_id).exclude(
                status=self.Status.COMPLETED
            )
            if self.pk:
                duplicate = duplicate.exclude(pk=self.pk)
            if duplicate.exists():
                raise ValidationError({"student": "This student already has a current placement."})

    @property
    def total_expected_reports(self) -> int:
        return ceil(((self.end_date - self.start_date).days + 1) / 7)

    def __str__(self) -> str:
        return f"{self.student} - {self.track} ({self.status})"
