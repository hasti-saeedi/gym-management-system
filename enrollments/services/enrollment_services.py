from django.db import transaction

from rest_framework.exceptions import NotFound, ValidationError

from classes.models import ClassSession, GymClass
from enrollments.models import Enrollment
from gyms.models import GymMembership

from .payment_services import create_payment


def create_enrollment(
    user,
    gym_class_id,
    enrollment_type,
    selected_sessions_ids=None,
):
    """
    Create a new enrollment for a user in a gym class.

    Validates the user's gym membership, class availability, enrollment type,
    and selected sessions before creating the enrollment and its payment.

    Args:
        user: The user enrolling in the gym class.
        gym_class_id: The ID of the gym class.
        enrollment_type: The type of enrollment, either semester or single.
        selected_sessions_ids: Optional list of session IDs for single-session
            enrollment.

    Returns:
        Enrollment: The newly created enrollment.

    Raises:
        NotFound: If the gym class does not exist.
        ValidationError: If the class is inactive, the user is not an active
            member, the user is the class trainer, the user is already
            enrolled, or the enrollment data is invalid.
    """

    with transaction.atomic():
        try:
            gym_class = GymClass.objects.select_for_update().get(
                id=gym_class_id
            )
        except GymClass.DoesNotExist:
            raise NotFound("Gym class does not exist.")

        if not gym_class.is_active:
            raise ValidationError("Class is inactive.")

        if not GymMembership.objects.filter(
            user=user,
            gym=gym_class.gym,
            is_active=True,
            role=GymMembership.Role.MEMBER,
        ).exists():
            raise ValidationError(
                "User is not an active member of this gym."
            )

        if gym_class.trainer_id == user.id:
            raise ValidationError(
                "Trainer cannot enroll in his own class."
            )

        if Enrollment.objects.filter(
            user=user,
            gym_class=gym_class,
        ).exists():
            raise ValidationError("Already enrolled.")

        if enrollment_type == "semester":
            if gym_class.current_enrolled >= gym_class.capacity:
                raise ValidationError("Class is full.")

        elif enrollment_type == "single":
            if not selected_sessions_ids:
                raise ValidationError(
                    "Please select at least one session."
                )

            sessions = ClassSession.objects.filter(
                id__in=selected_sessions_ids,
            )

            if sessions.count() != len(selected_sessions_ids):
                raise ValidationError(
                    "One or more sessions do not exist."
                )

            for session in sessions:
                if session.is_cancelled:
                    raise ValidationError(
                        "This session has been cancelled. "
                        "Please select another session."
                    )

                if session.gym_class != gym_class:
                    raise ValidationError(
                        "Session does not belong to this class."
                    )

        else:
            raise ValidationError(
                "Invalid enrollment type."
            )

        enrollment = Enrollment.objects.create(
            user=user,
            gym_class=gym_class,
            enrollment_type=enrollment_type,
            status="pending",
        )

        if enrollment_type == "single":
            enrollment.selected_sessions.set(sessions)

        create_payment(enrollment)

        return enrollment


@transaction.atomic
def cancel_enrollment_service(enrollment):
    """
    Cancel an existing enrollment without deleting it.

    Args:
        enrollment: The enrollment to cancel.

    Returns:
        Enrollment: The updated enrollment with a cancelled status.

    Raises:
        ValidationError: If the provided object is invalid or the enrollment
            has already been cancelled.
        NotFound: If the enrollment does not exist.
    """

    if not isinstance(enrollment, Enrollment):
        raise ValidationError("Invalid enrollment.")

    if not Enrollment.objects.filter(
        id=enrollment.id,
    ).exists():
        raise NotFound("Enrollment not found.")

    if enrollment.status == "cancelled":
        raise ValidationError(
            "Enrollment is already cancelled."
        )

    enrollment.status = "cancelled"

    enrollment.save(
        update_fields=["status"],
    )

    return enrollment