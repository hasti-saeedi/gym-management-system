from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission

from permissions.base_permissions import GymPermission
from permissions.permission_helpers import (
    can_access_gym_payments,
    can_manage_payment,
    can_confirm_payment,
    can_manage_enrollment,
    can_create_enrollment,
    can_cancel_enrollment,
    can_access_gym_enrollments,
)


User = get_user_model()


class CanViewEnrollment(GymPermission):
    """
    Allows Owner, Manager and Staff to view
    enrollments belonging to a gym.
    """

    message = (
        "You do not have permission to view "
        "enrollments for this gym."
    )

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        gym = self.get_gym(view)

        return can_access_gym_enrollments(
            request.user,
            gym,
        )


class CanCreateEnrollment(GymPermission):
    """
    Allows:

        Superuser:
            Create enrollment for anyone.

        Owner / Manager / Staff:
            Create enrollment for users in their gym.

        Member:
            Create enrollment only for himself.
    """

    message = (
        "You do not have permission to create "
        "an enrollment for this gym."
    )

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        gym = self.get_gym(view)

        target_user_id = request.data.get("user_id")

        # If user_id is not provided,
        # the serializer/service will use request.user.
        if target_user_id is None:
            target_user = request.user

        else:
            try:
                target_user = User.objects.get(
                    pk=target_user_id
                )
            except User.DoesNotExist:
                return False

        return can_create_enrollment(
            request.user,
            gym,
            target_user,
        )


class CanManageEnrollment(BasePermission):
    """
    Allows Owner, Manager and Staff to manage
    an existing enrollment.
    """

    message = (
        "You do not have permission to manage "
        "this enrollment."
    )

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        if not request.user.is_authenticated:
            return False

        return can_manage_enrollment(
            request.user,
            obj,
        )


class CanCancelEnrollment(BasePermission):
    """
    Allows:

        - Superuser
        - Enrollment owner
        - Owner
        - Manager
        - Staff

    to cancel an enrollment.
    """

    message = (
        "You do not have permission to cancel "
        "this enrollment."
    )

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        if not request.user.is_authenticated:
            return False

        return can_cancel_enrollment(
            request.user,
            obj,
        )


class CanViewPayment(GymPermission):
    """
    Allows Owner, Manager and Staff to view
    payments belonging to a gym.
    """

    message = (
        "You do not have permission to view "
        "payments for this gym."
    )

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        gym = self.get_gym(view)

        return can_access_gym_payments(
            request.user,
            gym,
        )


class CanCreatePayment(GymPermission):
    """
    Allows Owner, Manager and Staff to create
    payments inside a gym.
    """

    message = (
        "You do not have permission to create "
        "payments for this gym."
    )

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        gym = self.get_gym(view)

        return can_access_gym_payments(
            request.user,
            gym,
        )


class CanManagePayment(BasePermission):
    """
    Allows Owner, Manager and Staff to manage
    an existing payment.
    """

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
        if not request.user.is_authenticated:
            return False

        return can_manage_payment(
            request.user,
            obj,
        )


class CanConfirmPayment(BasePermission):
    """
    Allows Owner, Manager and Staff to confirm
    an existing payment.
    """

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
        if not request.user.is_authenticated:
            return False

        return can_confirm_payment(
            request.user,
            obj,
        )