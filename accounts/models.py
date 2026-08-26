from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.

    Adds additional fields for storing the user's phone number,
    address, and last update timestamp.
    """

    phone = models.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                regex=r'^09\d{9}$',
                message="Phone number must start with 09 and be 11 digits"
            )
        ],
        unique=True,
        blank=True,
        null=True,
        verbose_name='phone number'
    )

    address = models.TextField(blank=True)

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='last updated'
    )

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        """
        Return the user's full name or username.

        Returns:
            str: The user's full name if available; otherwise, the username.
        """
        return self.get_full_name() or self.username