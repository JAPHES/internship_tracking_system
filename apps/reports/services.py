from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models import WeeklyReport


@transaction.atomic
def submit_report(*, report_id, user) -> WeeklyReport:
    report = (
        WeeklyReport.objects.select_for_update()
        .select_related("placement__student__user")
        .get(pk=report_id)
    )
    try:
        report.submit(user)
    except DjangoValidationError as exc:
        raise ValidationError(exc.messages) from exc
    report.save(
        update_fields=["status", "submitted_at", "reviewed_at", "reviewed_by", "updated_at"]
    )
    return report


@transaction.atomic
def review_report(*, report_id, user, feedback: str) -> WeeklyReport:
    report = (
        WeeklyReport.objects.select_for_update()
        .select_related("placement__supervisor__user")
        .get(pk=report_id)
    )
    try:
        report.review(user, feedback)
    except DjangoValidationError as exc:
        raise ValidationError(exc.messages) from exc
    report.save(
        update_fields=[
            "status",
            "supervisor_feedback",
            "reviewed_at",
            "reviewed_by",
            "updated_at",
        ]
    )
    return report
