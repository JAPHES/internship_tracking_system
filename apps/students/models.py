from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower

from apps.accounts.models import User
from apps.common.models import TimeStampedUUIDModel


class StudentProfile(TimeStampedUUIDModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    registration_number = models.CharField(max_length=50, unique=True)
    programme = models.CharField(max_length=150)
    department = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["registration_number"]
        constraints = [
            models.UniqueConstraint(
                Lower("registration_number"), name="student_reg_number_ci_unique"
            )
        ]
        indexes = [models.Index(fields=["department"], name="student_department_idx")]

    def clean(self):
        super().clean()
        if self.user_id and self.user.role != User.Role.STUDENT:
            raise ValidationError(
                {"user": "Only users with the STUDENT role can have this profile."}
            )

    def __str__(self) -> str:
        return f"{self.registration_number} - {self.user.full_name}"
