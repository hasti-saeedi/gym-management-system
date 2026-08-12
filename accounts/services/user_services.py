from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.exceptions import ValidationError

from accounts.models import CustomUser
from gyms.models import GymMembership


def update_current_user(
    *,
    user,
    validated_data,
):
    # for field, value in validated_data.items():
    #     setattr(user, field, value)
    user.first_name = validated_data.get("first_name", user.first_name)
    user.last_name = validated_data.get("last_name", user.last_name)
    user.email = validated_data.get("email", user.email)
#حلقه دو بار اجرا می‌شود.
 #1
 #field = first_name
# value = Hasti
        
 #2
#field = last_name
# value = Saeedi
        
    user.save()

# تا اینجا فقط آبجکت داخل حافظه تغییر کرده بود.

# با این دستور داخل دیتابیس ذخیره می‌شود.

    return user
# کاربر آپدیت‌شده را برمی‌گرداند تا View آن را Serialize کند.

@transaction.atomic
def register_member(
    *,
    validated_data,
):

    gym = validated_data.pop("gym")

    validated_data.pop("password2")

    password = validated_data.pop("password")

    user = CustomUser.objects.create_user(
        password=password,
        **validated_data,
    )

    membership = GymMembership(
        user=user,
        gym=gym,
        role=GymMembership.Role.MEMBER,
    )

    try:
        membership.save()

    except DjangoValidationError as e:
        raise ValidationError(e.message_dict)

    return user


@transaction.atomic
def create_gym_user(
    *,
    creator,
    gym,
    validated_data,
):


    role = validated_data.pop("role")

    salary = validated_data.pop(
        "salary",
        None,
    )

    share_percentage = validated_data.pop(
        "share_percentage",
        None,
    )

    validated_data.pop("password2")

    password = validated_data.pop("password")

    user = CustomUser.objects.create_user(
        password=password,
        **validated_data,
    )

    membership = GymMembership(
        user=user,
        gym=gym,
        role=role,
        salary=salary,
        share_percentage=share_percentage,
    )

    try:
        membership.save()

    except DjangoValidationError as e:
        raise ValidationError(e.message_dict)

    return user
