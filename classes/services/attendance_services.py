from classes.models import ClassSession
from enrollments.models import Enrollment
from rest_framework.exceptions import NotFound, ValidationError
from django.db import transaction

    #برگرداندن ردیف اینرولمنت همه ثبت نام های ان جلسه 
# خروجی == QuerySet<Enrollment>  ینی یعنی یک مجموعه از Enrollmentها.
def get_enrolled_students(session_id):

    try:
        session = ClassSession.objects.get(id=session_id)#object
    except ClassSession.DoesNotExist:
        raise NotFound("Session not found.")
    gym_class = session.gym_class
    enrollments_semester = Enrollment.objects.filter(  #"queryset"
        status = 'approved',
        gym_class = gym_class,
        enrollment_type = 'semester'
    )

    enrollments_single  = Enrollment.objects.filter( #"queryset"
        status = 'approved',
        gym_class = gym_class,
        enrollment_type = 'single',
        selected_sessions = session
    )
    enrollments = enrollments_semester | enrollments_single #"queryset"

    return enrollments #"queryset"

    #ثبت حضورو غیاب جلسه

def record_attendance(session_id, user_id, attendance_status):
    
    with transaction.atomic():

        try:
            session = ClassSession.objects.get( #object
                id = session_id
            )# خروجی یک یک آبجکت از سشنی که میخواهیم یعنی ستونی از ان جلسه مورد نظر
                #<ClassSession: Yoga Session 1>
        except ClassSession.DoesNotExist:
            raise NotFound("session not found")
        
        enrollments = get_enrolled_students(session_id) #queryset
        
        # خروجی == ستونی از اینرولمنت هایی که به این کلاس یا جلسه مربوط اند
                # خروجی == QuerySet<Enrollment>  همان یعنی یک مجموعه از Enrollmentها.
        if not enrollments.filter(
            user__id = user_id
            ).exists(): # اگه در اون اینرولمنت ها ایدی یوزری که میدهد وجود نداشت 
            raise ValidationError(
        "User is not enrolled in this session."
    )

        # session.attendance[str(user_id)] = attendance_status
        session.attendance[str(user_id)] = {
            "present": attendance_status # چون در گت اتندنس در مدل که داریم تعداد پرسنت:ترو رو چک میکنه
        }
        session.save(update_fields=["attendance"])
        
        return session
            
        
        
    

    

