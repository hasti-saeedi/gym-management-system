from django.core.exceptions import ValidationError
from enrollments.models import Payment
from rest_framework.exceptions import NotFound
from django.db import transaction

    #اونی که اینرولمنت  اوردتش رو الان قیمت گذاری و چک دوباره میکنه
def create_payment(enrollment):
        #پیمنت قبا ساخته نشده باشه
    if Payment.objects.filter(enrollment=enrollment).exists():
        raise ValidationError("Payment already exists.")
    
        #تمام ترم
    if enrollment.enrollment_type == 'semester':

        final_price = enrollment.gym_class.price
        
        # تک جلسه
    elif enrollment.enrollment_type == 'single' :
        sessions_count = enrollment.selected_sessions.count()
        if sessions_count<=0 :
            raise ValidationError("there is no selected session")
        
        final_price = enrollment.gym_class.single_session_price * sessions_count

    else:
        raise ValidationError("Invalid enrollment type.")

    payment = Payment.objects.create(
        enrollment = enrollment,
        amount = final_price,
        status = 'pending'
        )
        
    return payment

def confirm_payment(payment_id, transaction_id):

    with transaction.atomic():
        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            raise NotFound("Payment not found.")  
        
        if payment.status == 'completed':
            raise ValidationError(" seccessed before")
        
        
        payment.status = 'completed'
        payment.transaction_id = transaction_id
        payment.save(update_fields= ["status", "transaction_id"])

        payment.enrollment.status = 'approved'
        payment.enrollment.save(update_fields= ["status"])

        if payment.enrollment.enrollment_type == 'semester':
            gym_class = payment.enrollment.gym_class
            gym_class.current_enrolled += 1
            gym_class.save(update_fields=["current_enrolled"])
        
                    
    return payment



    

