from django.core.exceptions import ValidationError
from django.db import models

from accounts.models import CustomUser
from classes.models import ClassSession, GymClass


class Enrollment(models.Model):
    """
    Represents a user's enrollment in a gym class.

    Supports both full-semester and single-session enrollment types.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
    ]

    ENROLLMENT_TYPE = [
        ("semester", "Full Semester"),
        ("single", "Single Session"),
    ]

    gym_class = models.ForeignKey(
        GymClass,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)

    enrollment_type = models.CharField(
        max_length=20,
        choices=ENROLLMENT_TYPE,
        default="semester",
    )
    selected_sessions = models.ManyToManyField(
        ClassSession,
        blank=True,
        related_name="single_enrollments",
    )

    class Meta:
        unique_together = [["gym_class", "user"]]

    def clean(self):
        """
        Validate the enrollment data.
        """
        pass

    def save(self, *args, **kwargs):
        """
        Validate and save the enrollment instance.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Return a human-readable representation of the enrollment.
        """
        return f"{self.user.username} - {self.gym_class.name} - {self.status}"


class Payment(models.Model):
    """
    Represents a payment associated with an enrollment.
    """

    PAYMENT_STATUS = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="payment",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="pending",
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """
        Validate payment amount and transaction information.
        """

        if self.amount <= 0:
            raise ValidationError({
                "amount": "Amount must be greater than zero.",
            })

        if self.status == "completed" and not self.transaction_id:
            raise ValidationError({
                "transaction_id": (
                    "Transaction ID is required for completed payments."
                ),
            })

    def save(self, *args, **kwargs):
        """
        Validate and save the payment instance.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Return a human-readable representation of the payment.
        """
        return (
            f"Payment {self.id} - "
            f"{self.enrollment.user.username} - "
            f"{self.status}"
        )