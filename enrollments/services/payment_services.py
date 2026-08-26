from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.exceptions import NotFound

from enrollments.models import Payment


def create_payment(enrollment):
    """
    Create a pending payment for an enrollment.

    Calculates the payment amount based on the enrollment type.
    Semester enrollments use the class price, while single-session
    enrollments use the single-session price multiplied by the number
    of selected sessions.

    Args:
        enrollment: The enrollment associated with the payment.

    Returns:
        Payment: The newly created pending payment.

    Raises:
        ValidationError: If a payment already exists, no sessions are
            selected for a single-session enrollment, or the enrollment
            type is invalid.
    """

    if Payment.objects.filter(
        enrollment=enrollment,
    ).exists():
        raise ValidationError(
            "Payment already exists."
        )

    if enrollment.enrollment_type == "semester":
        final_price = enrollment.gym_class.price

    elif enrollment.enrollment_type == "single":
        sessions_count = enrollment.selected_sessions.count()

        if sessions_count <= 0:
            raise ValidationError(
                "There are no selected sessions."
            )

        final_price = (
            enrollment.gym_class.single_session_price
            * sessions_count
        )

    else:
        raise ValidationError(
            "Invalid enrollment type."
        )

    payment = Payment.objects.create(
        enrollment=enrollment,
        amount=final_price,
        status="pending",
    )

    return payment


@transaction.atomic
def confirm_payment(
    payment_id,
    transaction_id,
):
    """
    Confirm a pending payment and approve its enrollment.

    Updates the payment status to completed, stores the transaction ID,
    and changes the associated enrollment status to approved. For
    semester enrollments, the class enrollment count is also incremented.

    Args:
        payment_id: The ID of the payment to confirm.
        transaction_id: The transaction ID associated with the payment.

    Returns:
        Payment: The confirmed payment.

    Raises:
        NotFound: If the payment does not exist.
        ValidationError: If the payment has already been completed.
    """

    try:
        payment = Payment.objects.get(
            id=payment_id,
        )
    except Payment.DoesNotExist:
        raise NotFound(
            "Payment not found."
        )

    if payment.status == "completed":
        raise ValidationError(
            "Payment has already been completed."
        )

    payment.status = "completed"
    payment.transaction_id = transaction_id

    payment.save(
        update_fields=[
            "status",
            "transaction_id",
        ],
    )

    enrollment = payment.enrollment
    enrollment.status = "approved"

    enrollment.save(
        update_fields=["status"],
    )

    if enrollment.enrollment_type == "semester":
        gym_class = enrollment.gym_class
        gym_class.current_enrolled += 1

        gym_class.save(
            update_fields=["current_enrolled"],
        )

    return payment