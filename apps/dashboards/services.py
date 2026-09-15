from datetime import date, timedelta

from django.db.models import Prefetch

from apps.placements.models import Placement
from apps.reports.models import WeeklyReport


def expected_week_numbers(placement: Placement, as_of: date | None = None) -> list[int]:
    """Return week numbers whose capped week-end date is before `as_of`."""

    as_of = as_of or date.today()
    expected = []
    for week_number in range(1, placement.total_expected_reports + 1):
        week_start = placement.start_date + timedelta(days=7 * (week_number - 1))
        week_end = min(week_start + timedelta(days=6), placement.end_date)
        if week_end < as_of:
            expected.append(week_number)
    return expected


def overdue_week_numbers(placement: Placement, as_of: date | None = None) -> list[int]:
    submitted_weeks = {
        report.week_number
        for report in placement.reports.all()
        if report.status in {WeeklyReport.Status.SUBMITTED, WeeklyReport.Status.REVIEWED}
    }
    return [
        week_number
        for week_number in expected_week_numbers(placement, as_of)
        if week_number not in submitted_weeks
    ]


def placement_progress_percentage(placement: Placement, as_of: date | None = None) -> float:
    as_of = as_of or date.today()
    if as_of < placement.start_date:
        return 0.0
    total_days = (placement.end_date - placement.start_date).days + 1
    elapsed_days = min((as_of - placement.start_date).days + 1, total_days)
    return round((elapsed_days / total_days) * 100, 2)


def active_placements_with_reports():
    return (
        Placement.objects.filter(status=Placement.Status.ACTIVE)
        .select_related("student__user", "supervisor__user", "track", "cohort")
        .prefetch_related(
            Prefetch(
                "reports",
                queryset=WeeklyReport.objects.only("placement_id", "week_number", "status"),
            )
        )
    )
