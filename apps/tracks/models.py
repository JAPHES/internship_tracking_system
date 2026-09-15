from django.db import models
from django.db.models.functions import Lower

from apps.common.models import TimeStampedUUIDModel


class Track(TimeStampedUUIDModel):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(Lower("name"), name="track_name_ci_unique")]
        indexes = [models.Index(fields=["is_active", "name"], name="track_active_name_idx")]

    def __str__(self) -> str:
        return self.name
