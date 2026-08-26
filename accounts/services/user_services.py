from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from rest_framework.exceptions import ValidationError

from accounts.models import CustomUser
from gyms.models import GymMembership


def update_current_user(*, user, validated_data):
    """
    Update the authenticated user's profile information.

    Args:
        user (CustomUser): The user whose profile is being updated.
        validated_data (dict): Validated profile fields to update.

    Returns:
        CustomUser: The updated user instance.
    """

    user.first_name = validated_data.get(
        "first_name",
        user.first_name,
    )
    user.last_name = validated_data.get(
        "last_name",
        user.last_name,
    )
    user.email = validated_data.get(
        "email",
        user.email,
    )

    user.save()

    return user


@transaction.atomic
def register_member(*, validated_data):
    """
    Register a new user as a member of a selected gym.

    Args:
        validated_data (dict): Validated registration data, including
        the selected gym and user credentials.

    Returns:
        CustomUser: The newly registered user.

    Raises:
        ValidationError: If gym membership creation fails.
    """

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
    """
    Create a user and assign them a role within a specific gym.

    Args:
        creator (CustomUser): The user creating the gym user.
        gym (Gym): The gym where the new user will be assigned.
        validated_data (dict): Validated user and membership data,
        including role, salary, and share percentage.

    Returns:
        CustomUser: The newly created user.

    Raises:
        ValidationError: If gym membership creation fails.
    """

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