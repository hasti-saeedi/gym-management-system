from django.db import models
# from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError
from gyms.models import GymMembership

class GymClass(models.Model):
    CATEGORY_CHOICES = [
        ('yoga', 'Yoga'),
        ('gym', 'Gym'),
        ('crossfit', 'Crossfit'),
        ('swim', 'Swimming'),
        ('zumba', 'Zumba'),
        ('pilates', 'Pilates'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    gym = models.ForeignKey('gyms.Gym', on_delete=models.CASCADE, related_name='classes')
    trainer = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='taught_classes'
    )
    
    current_enrolled = models.PositiveIntegerField(default=0)
    capacity = models.PositiveIntegerField()
    duration_minutes = models.PositiveIntegerField(default=60)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    single_session_price = models.DecimalField(max_digits=10, decimal_places=2)

    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # فیلدهای جدید برای زمان‌بندی منظم
    regular_days = models.JSONField(default=list)  # [0,2,4] = شنبه, دوشنبه, چهارشنبه
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    
    # فیلدهای جدید برای ترم
    total_sessions = models.PositiveIntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def clean(self):

        if self.trainer:

            is_trainer = GymMembership.objects.filter(
                gym=self.gym,
                user=self.trainer,
                role=GymMembership.Role.TRAINER,
                is_active=True,
            ).exists()

            if not is_trainer:
                raise ValidationError({
                    "trainer": "Selected user is not an active trainer of this gym."
                })

        if self.capacity is not None and self.capacity <= 0:
            raise ValidationError({
                'capacity': 'Class capacity must be greater than zero.'
            })

        if self.price is not None and self.price < 0:
            raise ValidationError({
                'price': 'Price cannot be negative.'
            })

        if not self.name or not self.name.strip():
            raise ValidationError({
                'name': 'Class name cannot be empty.'
            })

        if (
            self.start_time and
            self.end_time and
            self.start_time >= self.end_time
        ):
            raise ValidationError({
                'end_time': 'End time must be after start time.'
            })

        if (
            self.start_date and
            self.end_date and
            self.start_date > self.end_date
        ):
            raise ValidationError({
                'end_date': 'End date must be after start date.'
            })

        if self.start_date and self.end_date and self.regular_days:
            from .services.gym_class_services import calculate_session_dates

            expected_sessions = len(
                calculate_session_dates(
                    self.start_date,
                    self.end_date,
                    self.regular_days,
                )
            )

            if self.total_sessions != expected_sessions:
                raise ValidationError({
                    "total_sessions":
                        f"Expected {expected_sessions} sessions based on selected dates and days."
                })
            
    def save(self, *args, **kwargs):
        # ذخیره اولیه
        is_new = self.pk is None
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.gym.name}"


class ClassSession(models.Model):
    gym_class = models.ForeignKey(GymClass, on_delete=models.CASCADE, related_name='sessions')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    trainer = models.ForeignKey(
        'accounts.CustomUser', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='session_trainer'
    )
    attendance = models.JSONField(default=dict, blank = True)
    is_cancelled = models.BooleanField(default=False)
    cancel_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def present_count(self):
        return sum(1 for data in self.attendance.values() if data.get('present'))
    
    @property
    def absent_count(self):
        return sum(1 for data in self.attendance.values() if not data.get('present'))
    
    @property
    def single_session_students(self):
        return [uid for uid, data in self.attendance.items() if data.get('single_session')]

    @property
    def available_seats(self):
        from enrollments.models import Enrollment

        enrolled_count = Enrollment.objects.filter(
            gym_class=self.gym_class,
            status='approved'
        ).count()

        return self.gym_class.capacity - enrolled_count
    
    @property
    def is_full(self):
        return self.available_seats <= 0
    
    def clean(self):
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError({
                    'end_time': 'End time must be after start time.'
                })
        
        if self.trainer:

            is_trainer = GymMembership.objects.filter(
                gym=self.gym_class.gym,
                user=self.trainer,
                role=GymMembership.Role.TRAINER,
                is_active=True,
            ).exists()

            if not is_trainer:
                raise ValidationError({
                    "trainer": "Selected user is not an active trainer of this gym."
                })
        if self.trainer:
            
            overlapping = ClassSession.objects.filter(
                trainer=self.trainer,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            ).exclude(pk=self.pk)
            if overlapping.exists():
                raise ValidationError({
                    'trainer': 'Trainer has another session at the same time.'
                })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.gym_class.name} - {self.start_time}"