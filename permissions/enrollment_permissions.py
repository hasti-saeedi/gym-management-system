from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from gyms.models import Gym
from enrollments.models import Enrollment

from permissions.class_permissions import is_staff_of_gym


# =========================================================
# Helper Functions
# =========================================================


def can_manage_enrollment(user, enrollment):
    """
    Check if user can view, update, or delete an enrollment.

    Allowed:
        - Superuser
        - Owner
        - Manager
        - Staff of the same gym

    Not allowed:
        - Member
        - Trainer
        - Users from another gym
    """

    if user.is_superuser:
        return True

    gym = enrollment.gym_class.gym

    return is_staff_of_gym(
        user,
        gym,
    )


def can_create_enrollment(
    user,
    gym,
    target_user=None,
):
    """
    Check if user can create an enrollment inside a gym.

    Rules:

    Member:
        - Can create enrollment only for himself.

    Owner / Manager / Staff:
        - Can create enrollment for other users.
        - Only inside their own gym.

    Superuser:
        - Always allowed.
    """

    if user.is_superuser:
        return True

    # Owner / Manager / Staff
    if is_staff_of_gym(
        user,
        gym,
    ):
        return True

    # Member can only enroll himself
    return target_user == user


def can_cancel_enrollment(user, enrollment):
    """
    Check if user can cancel an enrollment.

    Allowed:
        - Superuser
        - Enrollment owner
        - Owner of the gym
        - Manager of the gym
        - Staff of the gym

    Not allowed:
        - Other members
        - Trainers
        - Users from another gym
    """

    if user.is_superuser:
        return True

    # Member can cancel his own enrollment
    if enrollment.user == user:
        return True

    gym = enrollment.gym_class.gym

    # Owner / Manager / Staff of the same gym
    return is_staff_of_gym(
        user,
        gym,
    )


# =========================================================
# Enrollment Permissions
# =========================================================


class CanViewEnrollment(BasePermission):

    """
    Permission for viewing enrollments of a specific gym.

    API:

        GET
        /api/enrollments/gyms/{gym_id}/enrollments/

    Allowed:
        - Superuser
        - Owner
        - Manager
        - Staff of the same gym

    Not allowed:
        - Member
        - Trainer
        - Users from another gym
    """

    message = (
        "You do not have permission to view enrollments for this gym."
    )

    def has_permission(self, request, view):

        gym_id = view.kwargs.get("gym_id")

        # Gym must exist.
        # If it does not exist -> 404
        gym = get_object_or_404(
            Gym,
            id=gym_id,
        )

        if request.user.is_superuser:
            return True

        return is_staff_of_gym(
            request.user,
            gym,
        )


class CanCreateEnrollment(BasePermission):

    """
    Permission for creating an enrollment.

    API:

        POST
        /api/enrollments/gyms/{gym_id}/enrollments/

    Allowed:

        Superuser:
            - Always allowed.

        Owner / Manager / Staff:
            - Can create enrollment for other users.
            - Only inside their own gym.

        Member:
            - Can create enrollment only for himself.
    """

    message = (
        "You do not have permission to create an enrollment "
        "for this gym."
    )

    def has_permission(self, request, view):

        gym_id = view.kwargs.get("gym_id")

        # Gym must exist.
        # Invalid gym_id -> 404
        gym = get_object_or_404(
            Gym,
            id=gym_id,
        )

        user = request.user

        if user.is_superuser:
            return True

        # Owner / Manager / Staff
        if is_staff_of_gym(
            user,
            gym,
        ):
            return True

        # Member:
        # If user_id is not sent, View will use request.user.
        target_user_id = request.data.get("user_id")

        if target_user_id is None:
            return True

        # If user_id is provided, Member can only
        # create enrollment for himself.
        return str(target_user_id) == str(user.id)


class CanManageEnrollment(BasePermission):

    """
    Permission for managing an existing enrollment.

    APIs:

        GET
        /api/enrollments/gyms/{gym_id}/enrollments/{id}/

        PUT
        /api/enrollments/gyms/{gym_id}/enrollments/{id}/

        PATCH
        /api/enrollments/gyms/{gym_id}/enrollments/{id}/

        DELETE
        /api/enrollments/gyms/{gym_id}/enrollments/{id}/

    Allowed:
        - Superuser
        - Owner of the gym
        - Manager of the gym
        - Staff of the gym

    Not allowed:
        - Member
        - Trainer
        - Users from another gym
    """

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        return can_manage_enrollment(
            request.user,
            obj,
        )


class CanCancelEnrollment(BasePermission):

    """
    Permission for cancelling an enrollment.

    API:

        POST
        /api/enrollments/gyms/{gym_id}/enrollments/{id}/cancel/

    Allowed:
        - Superuser
        - Enrollment owner
        - Owner of the gym
        - Manager of the gym
        - Staff of the gym

    Not allowed:
        - Other members
        - Trainers
        - Users from another gym
    """

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        return can_cancel_enrollment(
            request.user,
            obj,
        )
    
from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from gyms.models import Gym
from permissions.class_permissions import is_staff_of_gym


# =========================================================
# Helper Functions
# =========================================================


def can_access_gym_payments(user, gym):
    """
    Check if user can access payments of a gym.

    Allowed:
    - Superuser
    - Owner
    - Manager
    - Staff of the same gym
    """

    if user.is_superuser:
        return True

    return is_staff_of_gym(
        user,
        gym,
    )


def can_manage_payment(user, payment):
    """
    Check if user can retrieve, update, or delete a payment.

    Allowed:
    - Superuser
    - Owner
    - Manager
    - Staff of the same gym

    Not allowed:
    - Member
    - Trainer
    - Users from another gym
    """

    if user.is_superuser:
        return True

    gym = payment.enrollment.gym_class.gym

    return is_staff_of_gym(
        user,
        gym,
    )


def can_confirm_payment(user, payment):
    """
    Check if user can confirm a payment.

    Allowed:
    - Superuser
    - Owner
    - Manager
    - Staff of the same gym
    """

    if user.is_superuser:
        return True

    gym = payment.enrollment.gym_class.gym

    return is_staff_of_gym(
        user,
        gym,
    )


# =========================================================
# Base Permission
# =========================================================


class CanAccessGymPayment(BasePermission):
    """
    Base permission for payment APIs that use gym_id
    in the URL.
    """

    def has_permission(self, request, view):

        gym_id = view.kwargs.get("gym_id")

        gym = get_object_or_404(
            Gym,
            id=gym_id,
        )

        return can_access_gym_payments(
            request.user,
            gym,
        )


# =========================================================
# Payment Permissions
# =========================================================


class CanViewPayment(CanAccessGymPayment):

    message = (
        "You do not have permission to view payments "
        "for this gym."
    )


class CanCreatePayment(CanAccessGymPayment):

    message = (
        "You do not have permission to create payments "
        "for this gym."
    )


class CanManagePayment(BasePermission):

    message = (
        "You do not have permission to manage "
        "this payment."
    )

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):

        return can_manage_payment(
            request.user,
            obj,
        )


class CanConfirmPayment(BasePermission):

    message = (
        "You do not have permission to confirm "
        "this payment."
    )

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):

        return can_confirm_payment(
            request.user,
            obj,
        )