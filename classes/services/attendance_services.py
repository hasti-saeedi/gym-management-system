from django.db import transaction

from rest_framework.exceptions import NotFound, ValidationError

from classes.models import ClassSession
from enrollments.models import Enrollment


def get_enrolled_students(session_id):
    """
    Retrieve all approved enrollments associated with a class session.

    Semester enrollments are included automatically, while single-session
    enrollments are included only when the requested session is selected.

    Args:
        session_id (int): The ID of the class session.

    Returns:
        QuerySet: A queryset containing approved enrollments for the session.

    Raises:
        NotFound: If the specified class session does not exist.
    """

    try:
        session = ClassSession.objects.get(
            id=session_id,
        )
    except ClassSession.DoesNotExist:
        raise NotFound("Session not found.")

    gym_class = session.gym_class

    enrollments_semester = Enrollment.objects.filter(
        status="approved",
        gym_class=gym_class,
        enrollment_type="semester",
    )

    enrollments_single = Enrollment.objects.filter(
        status="approved",
        gym_class=gym_class,
        enrollment_type="single",
        selected_sessions=session,
    )

    enrollments = enrollments_semester | enrollments_single

    return enrollments


@transaction.atomic
def record_attendance(
    session_id,
    user_id,
    attendance_status,
):
    """
    Record a user's attendance status for a specific class session.

    The user must have an approved enrollment for the session, either
    through a semester enrollment or a selected single-session enrollment.

    Args:
        session_id (int): The ID of the class session.
        user_id (int): The ID of the user whose attendance is being recorded.
        attendance_status (bool): Whether the user attended the session.

    Returns:
        ClassSession: The updated class session instance.

    Raises:
        NotFound: If the specified class session does not exist.
        ValidationError: If the user is not enrolled in the session.
    """

    try:
        session = ClassSession.objects.get(
            id=session_id,
        )
    except ClassSession.DoesNotExist:
        raise NotFound("Session not found.")

    enrollments = get_enrolled_students(session_id)

    if not enrollments.filter(
        user__id=user_id,
    ).exists():
        raise ValidationError(
            "User is not enrolled in this session."
        )

    session.attendance[str(user_id)] = {
        "present": attendance_status,
    }

    session.save(
        update_fields=["attendance"],
    )

    return session
            
        
        
    

    

