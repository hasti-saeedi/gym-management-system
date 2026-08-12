from django.db import models
from django.core.exceptions import ValidationError
from classes.models import ClassSession, GymClass
from accounts.models import CustomUser


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    ENROLLMENT_TYPE = [
        ('semester', 'Full Semester'),
        ('single', 'Single Session'),
    ]
    
    gym_class = models.ForeignKey(
        GymClass, 
        on_delete=models.CASCADE, 
        related_name='enrollments'
    )
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='enrollments'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    
    # فیلدهای جدید برای نوع ثبت‌نام
    enrollment_type = models.CharField(max_length=20, choices=ENROLLMENT_TYPE, default='semester')
    selected_sessions = models.ManyToManyField(
        ClassSession, 
        blank=True, 
        related_name='single_enrollments'
    )
    
    class Meta:
        unique_together = [['gym_class', 'user']]
    
    def clean(self):
        pass
     
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.user.username} - {self.gym_class.name} - {self.status}"

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    enrollment = models.OneToOneField(
        Enrollment, 
        on_delete=models.CASCADE, 
        related_name='payment'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        if self.amount <= 0:
            raise ValidationError({'amount': 'Amount must be greater than zero.'})
        
        if self.status == 'completed' and not self.transaction_id:
            raise ValidationError({'transaction_id': 'Transaction ID is required for completed payments.'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Payment {self.id} - {self.enrollment.user.username} - {self.status}"