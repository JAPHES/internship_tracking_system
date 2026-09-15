from django.db import models
from django.db.models import F, Q

from apps.common.models import TimeStampedUUIDModel
from apps.common.validators import validate_date_range


class Cohort(TimeStampedUUIDModel):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-start_date", "name"]
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__gte=F("start_date")), name="cohort_valid_date_range"
            )
        ]
        indexes = [models.Index(fields=["is_active", "start_date"], name="cohort_active_start_idx")]

    def clean(self):
        super().clean()
        validate_date_range(self.start_date, self.end_date)

    def __str__(self) -> str:
        return self.name
