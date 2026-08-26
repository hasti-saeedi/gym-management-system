from datetime import datetime, timedelta

from django.utils import timezone

from classes.models import ClassSession


def calculate_session_dates(start_date, end_date, regular_days):
    """
    Calculate all dates on which a class session should take place.

    Args:
        start_date (date): The first date of the class schedule.
        end_date (date): The last date of the class schedule.
        regular_days (list): Weekday numbers on which the class is scheduled,
            where Monday is 0 and Sunday is 6.

    Returns:
        list: A list of dates matching the specified regular weekdays.
    """

    if not start_date or not end_date or not regular_days:
        return []

    dates = []
    current_date = start_date

    while current_date <= end_date:
        if current_date.weekday() in regular_days:
            dates.append(current_date)

        current_date += timedelta(days=1)

    return dates


def check_trainer_conflicts(
    trainer,
    start_datetime,
    end_datetime,
):
    """
    Check whether a trainer has another session during the given time range.

    Args:
        trainer (CustomUser): The trainer whose schedule is being checked.
        start_datetime (datetime): The start time of the proposed session.
        end_datetime (datetime): The end time of the proposed session.

    Returns:
        bool: True if the trainer has an overlapping session, otherwise False.
    """

    if trainer is None:
        return False

    return ClassSession.objects.filter(
        trainer=trainer,
        start_time__lt=end_datetime,
        end_time__gt=start_datetime,
    ).exists()


def generate_sessions(gym_class):
    """
    Generate class sessions automatically based on the class schedule.

    Existing sessions prevent duplicate generation. Sessions that conflict
    with the assigned trainer's schedule are skipped and recorded as conflicts.

    Args:
        gym_class (GymClass): The class for which sessions should be generated.

    Returns:
        dict: A dictionary containing:
            created (list): Successfully created ClassSession instances.
            skipped (list): Dates skipped due to trainer conflicts.
            conflicts (list): Details of detected trainer conflicts.
    """

    if gym_class.sessions.exists():
        return {
            "created": [],
            "skipped": [],
            "conflicts": ["Sessions already exist"],
        }

    session_dates = calculate_session_dates(
        gym_class.start_date,
        gym_class.end_date,
        gym_class.regular_days,
    )

    created = []
    skipped = []
    conflicts = []

    for session_date in session_dates:
        start_datetime = timezone.make_aware(
            datetime.combine(
                session_date,
                gym_class.start_time,
            ),
            timezone.get_current_timezone(),
        )

        end_datetime = timezone.make_aware(
            datetime.combine(
                session_date,
                gym_class.end_time,
            ),
            timezone.get_current_timezone(),
        )

        if check_trainer_conflicts(
            gym_class.trainer,
            start_datetime,
            end_datetime,
        ):
            conflicts.append({
                "date": session_date,
                "reason": "trainer conflict",
            })
            skipped.append(session_date)
            continue

        session = ClassSession.objects.create(
            gym_class=gym_class,
            start_time=start_datetime,
            end_time=end_datetime,
            trainer=gym_class.trainer,
        )

        created.append(session)

    return {
        "created": created,
        "skipped": skipped,
        "conflicts": conflicts,
    }