from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):

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
    updated_at = models.DateTimeField(auto_now=True, verbose_name='last updated')


    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return self.get_full_name() or self.username
    
    

