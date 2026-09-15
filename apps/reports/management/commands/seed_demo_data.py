from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.cohorts.models import Cohort
from apps.placements.models import Placement
from apps.reports.models import WeeklyReport
from apps.students.models import StudentProfile
from apps.supervisors.models import SupervisorProfile
from apps.tracks.models import Track

User = get_user_model()


class Command(BaseCommand):
    help = "Create or refresh development-only demonstration data."

    @transaction.atomic
    def handle(self, *args, **options):
        today = timezone.localdate()
        admin = self._user(
            "admin@demo.local", "DemoAdmin123!", "Demo", "Admin", User.Role.ADMIN, is_staff=True
        )
        supervisor_users = [
            self._user(
                f"supervisor{number}@demo.local",
                "DemoSupervisor123!",
                f"Supervisor{number}",
                "Demo",
                User.Role.SUPERVISOR,
            )
            for number in range(1, 3)
        ]
        supervisors = [
            SupervisorProfile.objects.update_or_create(
                user=user,
                defaults={
                    "staff_number": f"DEMO-SUP-{number:03d}",
                    "department": "Computing",
                    "phone_number": f"+25471100000{number}",
                },
            )[0]
            for number, user in enumerate(supervisor_users, start=1)
        ]

        cohort, _ = Cohort.objects.update_or_create(
            name="Demo 2026 Cohort",
            defaults={
                "description": "Development-only demonstration cohort.",
                "start_date": today - timedelta(days=28),
                "end_date": today + timedelta(days=56),
                "is_active": True,
            },
        )
        track_names = [
            "Software Development",
            "Data Science",
            "Machine Learning",
            "Business Intelligence",
        ]
        tracks = [
            Track.objects.update_or_create(
                name=name,
                defaults={"description": f"Demo {name} internship track.", "is_active": True},
            )[0]
            for name in track_names
        ]

        students = []
        for number in range(1, 7):
            user = self._user(
                f"student{number}@demo.local",
                "DemoStudent123!",
                f"Student{number}",
                "Demo",
                User.Role.STUDENT,
            )
            profile, _ = StudentProfile.objects.update_or_create(
                user=user,
                defaults={
                    "registration_number": f"DEMO-{number:03d}",
                    "programme": "BSc Computer Science",
                    "department": "Computing",
                    "phone_number": f"+25470000000{number}",
                },
            )
            students.append(profile)

        for index, student in enumerate(students):
            placement, _ = Placement.objects.update_or_create(
                student=student,
                status=Placement.Status.ACTIVE,
                defaults={
                    "supervisor": supervisors[index % len(supervisors)],
                    "track": tracks[index % len(tracks)],
                    "cohort": cohort,
                    "start_date": cohort.start_date,
                    "end_date": cohort.end_date,
                    "created_by": admin,
                },
            )
            for week_number in range(1, 4):
                week_start = placement.start_date + timedelta(days=7 * (week_number - 1))
                week_end = min(week_start + timedelta(days=6), placement.end_date)
                report_status = (
                    WeeklyReport.Status.REVIEWED
                    if week_number == 1
                    else WeeklyReport.Status.SUBMITTED
                    if week_number == 2
                    else WeeklyReport.Status.DRAFT
                )
                now = timezone.now()
                WeeklyReport.objects.update_or_create(
                    placement=placement,
                    week_number=week_number,
                    defaults={
                        "week_start_date": week_start,
                        "week_end_date": week_end,
                        "activities_completed": f"Demo activities for week {week_number}.",
                        "skills_learned": "Planning, communication, and technical delivery.",
                        "challenges_faced": "Development-only sample challenge.",
                        "status": report_status,
                        "supervisor_feedback": (
                            "Good progress; keep documenting outcomes."
                            if report_status == WeeklyReport.Status.REVIEWED
                            else ""
                        ),
                        "submitted_at": now if report_status != WeeklyReport.Status.DRAFT else None,
                        "reviewed_at": now
                        if report_status == WeeklyReport.Status.REVIEWED
                        else None,
                        "reviewed_by": (
                            placement.supervisor.user
                            if report_status == WeeklyReport.Status.REVIEWED
                            else None
                        ),
                    },
                )

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
        self.stdout.write("Admin: admin@demo.local / DemoAdmin123!")
        self.stdout.write("Supervisor: supervisor1@demo.local / DemoSupervisor123!")
        self.stdout.write("Student: student1@demo.local / DemoStudent123!")
        self.stdout.write(self.style.WARNING("These credentials are for development only."))

    def _user(self, email, password, first_name, last_name, role, *, is_staff=False):
        user, _ = User.objects.update_or_create(
            email=email,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "role": role,
                "is_active": True,
                "is_staff": is_staff,
                "is_superuser": is_staff and role == User.Role.ADMIN,
            },
        )
        user.set_password(password)
        user.save(update_fields=["password", "updated_at"])
        return user
