from datetime import date, timedelta

import factory
from django.contrib.auth import get_user_model

from apps.cohorts.models import Cohort
from apps.placements.models import Placement
from apps.reports.models import WeeklyReport
from apps.students.models import StudentProfile
from apps.supervisors.models import SupervisorProfile
from apps.tracks.models import Track

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda number: f"user{number}@example.com")
    first_name = "Test"
    last_name = factory.Sequence(lambda number: f"User{number}")
    role = User.Role.STUDENT
    password = "StrongPass123!"

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return model_class.objects.create_user(*args, **kwargs)


class AdminFactory(UserFactory):
    role = User.Role.ADMIN
    is_staff = True


class StudentProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StudentProfile

    user = factory.SubFactory(UserFactory, role=User.Role.STUDENT)
    registration_number = factory.Sequence(lambda number: f"REG-{number:04d}")
    programme = "BSc Computer Science"
    department = "Computing"
    phone_number = "+254700000000"


class SupervisorProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SupervisorProfile

    user = factory.SubFactory(UserFactory, role=User.Role.SUPERVISOR)
    staff_number = factory.Sequence(lambda number: f"STAFF-{number:04d}")
    department = "Computing"
    phone_number = "+254711000000"


class CohortFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cohort

    name = factory.Sequence(lambda number: f"Cohort {number}")
    description = "Test cohort"
    start_date = factory.LazyFunction(lambda: date.today() - timedelta(days=28))
    end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=56))
    is_active = True


class TrackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Track

    name = factory.Sequence(lambda number: f"Track {number}")
    description = "Test track"
    is_active = True


class PlacementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Placement

    student = factory.SubFactory(StudentProfileFactory)
    supervisor = factory.SubFactory(SupervisorProfileFactory)
    track = factory.SubFactory(TrackFactory)
    cohort = factory.SubFactory(CohortFactory)
    start_date = factory.LazyFunction(lambda: date.today() - timedelta(days=28))
    end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=56))
    status = Placement.Status.ACTIVE
    created_by = factory.SubFactory(AdminFactory)


class WeeklyReportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WeeklyReport

    placement = factory.SubFactory(PlacementFactory)
    week_number = 1
    week_start_date = factory.LazyAttribute(lambda report: report.placement.start_date)
    week_end_date = factory.LazyAttribute(
        lambda report: min(
            report.placement.start_date + timedelta(days=6), report.placement.end_date
        )
    )
    activities_completed = "Implemented API endpoints."
    skills_learned = "Django REST Framework"
    challenges_faced = "None"
