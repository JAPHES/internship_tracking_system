from django.core.exceptions import ValidationError
from django.db import models

from apps.accounts.models import User
from apps.common.models import TimeStampedUUIDModel


class SupervisorProfile(TimeStampedUUIDModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="supervisor_profile")
    staff_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    department = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["user__last_name", "user__first_name"]
        indexes = [models.Index(fields=["department"], name="supervisor_department_idx")]

    def clean(self):
        super().clean()
        if self.user_id and self.user.role != User.Role.SUPERVISOR:
            raise ValidationError(
                {"user": "Only users with the SUPERVISOR role can have this profile."}
            )

    def save(self, *args, **kwargs):
        self.staff_number = self.staff_number or None
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.user.full_name or self.user.email
