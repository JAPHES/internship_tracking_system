from django.core.exceptions import ValidationError


def validate_date_range(start_date, end_date) -> None:
    if start_date and end_date and end_date < start_date:
        raise ValidationError({"end_date": "End date cannot be earlier than start date."})
