from django.db import transaction
# from django.core.exceptions import ValidationError
from rest_framework.exceptions import NotFound, ValidationError
from enrollments.models import Enrollment
from classes.models import GymClass, ClassSession
from gyms.models import GymMembership
from .payment_services import create_payment

def create_enrollment(user, gym_class_id, enrollment_type, selected_sessions_ids=None):

    with transaction.atomic():

            #  قفل کردن خود کلاس
        # gym_class = GymClass.objects.select_for_update().get(id=gym_class_id)
        try:
            gym_class = GymClass.objects.select_for_update().get(
                id=gym_class_id
            )

        except GymClass.DoesNotExist:
            raise NotFound(
                "Gym class does not exist."
            )

            #چک وجود داشتن و اکتیو بودن
        if not gym_class.is_active:
            raise ValidationError("Class is inactive.")
            # فرد ثبت نام شده ممبر همان جیم باشد
        if not GymMembership.objects.filter(
            user=user,
            gym=gym_class.gym,
            is_active=True,
            role=GymMembership.Role.MEMBER,
        ).exists():

            raise ValidationError(
                "User is not an active member of this gym."
            )

        # Trainer cannot enroll in his own class
        if gym_class.trainer_id == user.id:
            raise ValidationError(
                "Trainer cannot enroll in his own class."
            )
  
            #قبلا ثبت نام نبوده باشه
        if Enrollment.objects.filter(
            user=user,
            gym_class=gym_class
        ).exists():
            raise ValidationError("Already enrolled.")
        

            
        if enrollment_type == 'semester':
            # selected_sessions_semester = selected_sessions
            #تعداد ظرفیت باقی
            if gym_class.current_enrolled >= gym_class.capacity:
                raise ValidationError("Class is full.")
            
        elif enrollment_type == 'single':
            if not selected_sessions_ids:
                raise ValidationError("Please select at least one session.")
            
            sessions = ClassSession.objects.filter(id__in =selected_sessions_ids)

            session_count = sessions.count()
            if session_count!= len(selected_sessions_ids):
                raise ValidationError("One or more sessions do not exist.")
            
            for session in sessions:
                if session.is_cancelled:
                    raise ValidationError(" this session has been cancelled select other session")
                
                if not session.gym_class == gym_class:
                    raise ValidationError ("session is not for the certain class")
            

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
def cancel_enrollment_service(
    enrollment,
):
    """
    Cancel an enrollment.

    Rules:
    - Enrollment must exist.
    - Enrollment will not be deleted.
    - Status will be changed to cancelled.
    """

    if not isinstance(enrollment, Enrollment):
        raise ValidationError(
            "Invalid enrollment."
        )


    if not Enrollment.objects.filter(
        id=enrollment.id
    ).exists():
        raise NotFound(
            "Enrollment not found."
        )
    
    if enrollment.status=='cancelled':
        raise ValidationError(" enrollment is already cancell ")


    enrollment.status = "cancelled"

    enrollment.save(
        update_fields=[
            "status"
        ]
    )


    return enrollment