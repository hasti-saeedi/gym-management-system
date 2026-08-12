from datetime import timedelta, datetime
from django.utils import timezone
from classes.models import ClassSession

    #@admin.action(description="Generate sessions") در ادمین جیم کلس اوردیم که بتونه استفاده کنه
    #این سه تا تابع برای ساختن خودکار جلسات در کلس سشز هست 
#@@@@
def calculate_session_dates(start_date, end_date, regular_days):
    """
    برگرداندن لیست تاریخ‌هایی که کلاس باید برگزار شود
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

def check_trainer_conflicts(trainer, start_datetime, end_datetime):
    """
    بررسی اینکه آیا مربی در این بازه زمانی جلسه دیگری دارد یا نه
    """
    if trainer is None:
        return False

    return ClassSession.objects.filter(
        trainer=trainer,
        start_time__lt=end_datetime,
        end_time__gt=start_datetime
    ).exists()

def generate_sessions(gym_class):
    """
    تولید خودکار جلسات برای یک کلاس
    """

    # جلوگیری از ساخت دوباره
    if gym_class.sessions.exists():
        return {
            "created": [],
            "skipped": [],
            "conflicts": ["Sessions already exist"]
        }

    session_dates = calculate_session_dates(
        gym_class.start_date,
        gym_class.end_date,
        gym_class.regular_days
    )

    created = []
    skipped = []
    conflicts = []

    for session_date in session_dates:

        start_datetime = timezone.make_aware(
            datetime.combine(session_date, gym_class.start_time),
            timezone.get_current_timezone()
        )

        end_datetime = timezone.make_aware(
            datetime.combine(session_date, gym_class.end_time),
            timezone.get_current_timezone()
        )

        # بررسی تداخل مربی
        if check_trainer_conflicts(
            gym_class.trainer,
            start_datetime,
            end_datetime
        ):
            conflicts.append({
                "date": session_date,
                "reason": "trainer conflict"
            })
            skipped.append(session_date)
            continue

        session = ClassSession.objects.create(
            gym_class=gym_class,
            start_time=start_datetime,
            end_time=end_datetime,
            trainer=gym_class.trainer
        )

        created.append(session)

    return {
        "created": created,
        "skipped": skipped,
        "conflicts": conflicts
    }
#@@@@