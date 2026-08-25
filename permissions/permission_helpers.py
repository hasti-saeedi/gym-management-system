from enrollments.models import Enrollment
from gyms.models import GymMembership


# ============================================================
# Basic Gym Role Helpers
# ============================================================


def is_owner_or_manager(user, gym):
    """
    Return True if the user is an active Owner or Manager
    of the specified gym.
    """

    if not user.is_authenticated:
        return False

    return user.memberships.filter(
        gym=gym,
        role__in=[
            GymMembership.Role.OWNER,
            GymMembership.Role.MANAGER,
        ],
        is_active=True,
    ).exists()


def is_staff(user, gym):
    """
    Return True if the user is an active Staff member
    of the specified gym.
    """

    if not user.is_authenticated:
        return False

    return user.memberships.filter(
        gym=gym,
        role=GymMembership.Role.STAFF,
        is_active=True,
    ).exists()


def is_gym_owner_or_manager(user, gym):
    """
    Return True if the user is an active Owner or Manager
    of the specified gym.

    Superuser always has access.
    """

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return is_owner_or_manager(
        user,
        gym,
    )


def is_gym_staff(user, gym):
    """
    Return True if the user is an active
    Owner, Manager, or Staff member
    of the specified gym.

    Superuser always has access.
    """

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return user.memberships.filter(
        gym=gym,
        role__in=[
            GymMembership.Role.OWNER,
            GymMembership.Role.MANAGER,
            GymMembership.Role.STAFF,
        ],
        is_active=True,
    ).exists()


def is_gym_owner(user, gym):
    """
    Return True if the user is an active Owner
    of the specified gym.

    Superuser always has access.
    """

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return user.memberships.filter(
        gym=gym,
        role=GymMembership.Role.OWNER,
        is_active=True,
    ).exists()


# ============================================================
# General Gym Access
# ============================================================


def can_manage_any_gym(user):
    """
    Return True if the user has an active
    Owner, Manager, or Staff membership in any gym.
    """

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return user.memberships.filter(
        role__in=[
            GymMembership.Role.OWNER,
            GymMembership.Role.MANAGER,
            GymMembership.Role.STAFF,
        ],
        is_active=True,
    ).exists()


def can_manage_gym(user, gym):
    """
    Return True if the user can manage resources
    inside the specified gym.

    Allowed:
        - Superuser
        - Owner
        - Manager
        - Staff
    """

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return is_gym_staff(
        user,
        gym,
    )


# ============================================================
# Gym User Permissions
# ============================================================


def can_view_gym_users(user, gym):
    """
    Owner, Manager and Staff can view users
    belonging to their gym.
    """

    return is_gym_staff(
        user,
        gym,
    )


def can_manage_gym_users(user, gym):
    """
    Owner and Manager can create/manage users
    belonging to their gym.
    """

    return is_gym_owner_or_manager(
        user,
        gym,
    )


def can_update_user(user, target_user, gym):
    """
    Determine whether a user can update another user
    inside a specific gym.

    Rules:

    Owner:
        Can update Manager, Staff, Trainer and Member.
        Cannot update Owner.

    Manager:
        Can update Staff, Trainer and Member.
        Cannot update Owner or Manager.

    Users cannot update themselves through this API.
    """

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if user == target_user:
        return False

    requester_membership = user.memberships.filter(
        gym=gym,
        is_active=True,
    ).first()

    target_membership = target_user.memberships.filter(
        gym=gym,
        is_active=True,
    ).first()

    if not requester_membership or not target_membership:
        return False

    requester_role = requester_membership.role
    target_role = target_membership.role

    if requester_role == GymMembership.Role.OWNER:
        return target_role in [
            GymMembership.Role.MANAGER,
            GymMembership.Role.STAFF,
            GymMembership.Role.TRAINER,
            GymMembership.Role.MEMBER,
        ]

    if requester_role == GymMembership.Role.MANAGER:
        return target_role in [
            GymMembership.Role.STAFF,
            GymMembership.Role.TRAINER,
            GymMembership.Role.MEMBER,
        ]

    return False


def can_delete_user(user, target_user, gym):
    """
    Determine whether a user can delete another user
    from a specific gym.

    Rules:

    Owner:
        Can delete Manager, Staff, Trainer and Member.
        Cannot delete Owner.

    Manager:
        Can delete Staff, Trainer and Member.
        Cannot delete Owner or Manager.

    Users cannot delete themselves.
    """

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if user == target_user:
        return False

    requester_membership = user.memberships.filter(
        gym=gym,
        is_active=True,
    ).first()

    target_membership = target_user.memberships.filter(
        gym=gym,
        is_active=True,
    ).first()

    if not requester_membership or not target_membership:
        return False

    requester_role = requester_membership.role
    target_role = target_membership.role

    if requester_role == GymMembership.Role.OWNER:
        return target_role != GymMembership.Role.OWNER

    if requester_role == GymMembership.Role.MANAGER:
        return target_role in [
            GymMembership.Role.STAFF,
            GymMembership.Role.TRAINER,
            GymMembership.Role.MEMBER,
        ]

    return False


# ============================================================
# Gym Class Permissions
# ============================================================


def can_manage_gym_class(user, gym):
    """
    Determine whether a user can manage classes
    in the specified gym.

    Allowed:
        - Superuser
        - Owner
        - Manager
        - Staff
    """

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return is_gym_staff(
        user,
        gym,
    )


# ============================================================
# Class Session Permissions
# ============================================================


def is_staff_of_gym(user, gym):
    """
    Return True if the user is an active
    Owner, Manager or Staff member of the gym.

    This helper is kept as a semantic alias for
    session/enrollment permission logic.
    """

    return is_gym_staff(
        user,
        gym,
    )


def is_class_trainer(user, gym_class):
    """
    Return True if the user is the active Trainer
    assigned to the specified GymClass.
    """

    if not user.is_authenticated:
        return False

    return (
        user.memberships.filter(
            gym=gym_class.gym,
            role=GymMembership.Role.TRAINER,
            is_active=True,
        ).exists()
        and gym_class.trainer == user
    )


def is_session_trainer(user, session):
    """
    Return True if the user is the trainer directly
    assigned to the specified ClassSession.
    """

    if not user.is_authenticated:
        return False

    return (
        user.memberships.filter(
            gym=session.gym_class.gym,
            role=GymMembership.Role.TRAINER,
            is_active=True,
        ).exists()
        and session.trainer == user
    )


def is_gym_class_trainer(user, gym_class):
    """
    Alias for checking whether the user is the
    assigned trainer of a GymClass.
    """

    return is_class_trainer(
        user,
        gym_class,
    )


def can_access_session(user, session):
    """
    Determine whether a user can access a ClassSession.

    Allowed:
        - Superuser
        - Owner
        - Manager
        - Staff
        - Primary class trainer
        - Session trainer

    Members are not allowed.
    """

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    gym = session.gym_class.gym

    if is_staff_of_gym(user, gym):
        return True

    if is_class_trainer(user, session.gym_class):
        return True

    if is_session_trainer(user, session):
        return True

    return False


def can_create_session(user, gym_class):
    """
    Determine whether a user can create a ClassSession.

    Allowed:
        - Superuser
        - Owner
        - Manager
        - Staff
        - Primary class trainer
    """

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    gym = gym_class.gym

    if is_staff_of_gym(user, gym):
        return True

    return is_class_trainer(
        user,
        gym_class,
    )


def can_delete_session(user, session):
    """
    Determine whether a user can delete a ClassSession.

    Allowed:
        - Superuser
        - Owner
        - Manager
        - Staff

    Trainers cannot delete sessions.
    """

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    gym = session.gym_class.gym

    return is_staff_of_gym(
        user,
        gym,
    )


# ============================================================
# Enrollment Permissions
# ============================================================


def can_access_gym_enrollments(user, gym):
    """
    Determine whether a user can access enrollments
    belonging to a gym.

    Allowed:
        - Superuser
        - Owner
        - Manager
        - Staff
    """

    return is_gym_staff(
        user,
        gym,
    )


def can_manage_enrollment(user, enrollment):
    """
    Determine whether a user can view, update,
    or delete an existing enrollment.

    Allowed:
        - Superuser
        - Owner
        - Manager
        - Staff of the same gym
    """

    if not user.is_authenticated:
        return False

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
    Determine whether a user can create an enrollment.

    Rules:

    Superuser:
        Always allowed.

    Owner / Manager / Staff:
        Can create enrollment for users
        inside their gym.

    Member:
        Can create enrollment only for himself.

    target_user should be a User object.
    """

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if is_staff_of_gym(user, gym):
        return True

    return target_user == user


def can_cancel_enrollment(user, enrollment):
    """
    Determine whether a user can cancel an enrollment.

    Allowed:
        - Superuser
        - Enrollment owner
        - Owner / Manager / Staff of the gym
    """

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if enrollment.user == user:
        return True

    gym = enrollment.gym_class.gym

    return is_staff_of_gym(
        user,
        gym,
    )


# ============================================================
# Payment Permissions
# ============================================================


def can_access_gym_payments(user, gym):
    """
    Determine whether a user can access payments
    belonging to a gym.

    Allowed:
        - Superuser
        - Owner
        - Manager
        - Staff
    """

    return is_gym_staff(
        user,
        gym,
    )


def can_manage_payment(user, payment):
    """
    Determine whether a user can manage
    an existing payment.

    Allowed:
        - Superuser
        - Owner
        - Manager
        - Staff of the same gym
    """

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    gym = payment.enrollment.gym_class.gym

    return is_staff_of_gym(
        user,
        gym,
    )


def can_confirm_payment(user, payment):
    """
    Determine whether a user can confirm
    an existing payment.

    Allowed:
        - Superuser
        - Owner
        - Manager
        - Staff of the same gym
    """

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    gym = payment.enrollment.gym_class.gym

    return is_staff_of_gym(
        user,
        gym,
    )


# ============================================================
# Miscellaneous Helpers
# ============================================================


def is_class_member(user, gym_class):
    """
    Return True if the user has an approved enrollment
    in the specified GymClass.
    """

    if not user.is_authenticated:
        return False

    return Enrollment.objects.filter(
        user=user,
        gym_class=gym_class,
        status="approved",
    ).exists()

from gyms.models import GymMembership


def is_gym_employee(user):
    """
    Return True if user has an active
    Owner, Manager, or Staff role in any gym.
    """

    if not user.is_authenticated:
        return False

    return GymMembership.objects.filter(
        user=user,
        role__in=[
            GymMembership.Role.OWNER,
            GymMembership.Role.MANAGER,
            GymMembership.Role.STAFF,
        ],
        is_active=True,
    ).exists()