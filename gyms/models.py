from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from accounts.models import CustomUser


class Gym(models.Model):
    name = models.CharField(
        max_length=20,
    )

    address = models.TextField()

    phone = models.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                regex=r"^(09\d{9}|\d{10,11})$",
                message=(
                    "Phone number must be either: "
                    "11-digit mobile (09...) or "
                    "10-11-digit landline"
                ),
            ),
        ],
        unique=True,
        blank=True,
        null=True,
        verbose_name="phone number",
    )

    email = models.EmailField(
        null=True,
        blank=True,
        unique=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="date joined",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="last updated",
    )

    def __str__(self):
        return f"{self.name} - is active={self.is_active}"


class GymMembership(models.Model):

    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        MANAGER = "manager", "Manager"
        TRAINER = "trainer", "Trainer"
        STAFF = "staff", "Staff"
        MEMBER = "member", "Member"

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="memberships",
    )

    gym = models.ForeignKey(
        Gym,
        on_delete=models.CASCADE,
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        verbose_name="role",
    )

    share_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="date joined",
    )

    class Meta:
        unique_together = [
            [
                "user",
                "gym",
                "role",
            ]
        ]

    def clean(self):
        # ====================================================
        # Owner
        # ====================================================

        if self.role == self.Role.OWNER:

            if self.share_percentage is None:
                raise ValidationError({
                    "share_percentage": (
                        "Share percentage is required "
                        "for gym owner."
                    )
                })

            if (
                self.share_percentage <= 0
                or self.share_percentage > 100
            ):
                raise ValidationError({
                    "share_percentage": (
                        "Share percentage must be "
                        "between 0 and 100."
                    )
                })

        # ====================================================
        # Member
        # ====================================================

        elif self.role == self.Role.MEMBER:

            if (
                self.salary is not None
                or self.share_percentage is not None
            ):
                raise ValidationError({
                    "salary/share_percentage": (
                        "Members do not receive salary "
                        "or share percentage."
                    )
                })

        # ====================================================
        # Manager / Trainer / Staff
        # ====================================================

        else:

            if self.share_percentage is not None:
                raise ValidationError({
                    "share_percentage": (
                        "Only gym owner can have "
                        "share percentage."
                    )
                })

            if self.salary is None:
                raise ValidationError({
                    "salary": (
                        f"{self.get_role_display()} "
                        "must have a salary."
                    )
                })

            if self.salary <= 0:
                raise ValidationError({
                    "salary": (
                        "Salary cannot be negative or zero."
                    )
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.gym.name} - "
            f"{self.role}"
        )