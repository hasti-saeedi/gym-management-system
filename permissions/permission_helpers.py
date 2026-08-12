from enrollments.models import Enrollment
from gyms.models import GymMembership
from rest_framework.permissions import BasePermission

def is_owner_or_manager(user, gym):
    """
    Checks whether the given user is an active Owner or Manager
    of the specified gym.

    Returns:
        bool: True if the user has Owner or Manager role
        in the given gym, otherwise False.
    """

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
    Checks whether the given user is an active Staff
    member of the specified gym.

    Returns:
        bool: True if the user has Staff role
        in the given gym, otherwise False.
    """

    return user.memberships.filter(
        gym=gym,
        role=GymMembership.Role.STAFF,
        is_active=True,
    ).exists()

#owner and manager of any gym at all
def can_manage_any_gym(user):

    return user.memberships.filter(
        role__in=[
            GymMembership.Role.OWNER,
            GymMembership.Role.MANAGER,
            GymMembership.Role.STAFF,
        ],
        is_active=True,
    ).exists()

#owner and manager of specific gym
def can_manage_gym(user, gym):

    return (
        is_owner_or_manager(user, gym)
        or
        is_staff(user, gym)
    )

    #ممکن است بعداً (در توسعه‌های بعدی) مدرس متفاوتی داشته باشد
    # به خاطر همنی با سشن چک کردیم

def is_class_trainer(user, session): 
    """
    Checks whether the given user is the assigned Trainer
    of the specified class session.

    Conditions:
        - User must have Trainer role in the gym.
        - User must be the assigned trainer of the session.

    Returns:
        bool: True if both conditions are met,
        otherwise False.
    """

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
    Checks whether the given user is the assigned trainer
    of the specified gym class.

    Conditions:
        - User must have Trainer role in the gym.
        - User must be the assigned trainer of the gym class.

    Returns:
        bool: True if both conditions are met,
        otherwise False.
    """

    return (
        user.memberships.filter(
            gym=gym_class.gym,
            role=GymMembership.Role.TRAINER,
            is_active=True,
        ).exists()
        and gym_class.trainer == user
    )

def is_class_member(user, gym_class):
    """
    Checks whether the given user is enrolled
    in the specified gym class.

    Conditions:
        - Enrollment must belong to the user.
        - Enrollment must belong to the given class.
        - Enrollment status must be approved.

    Returns:
        bool: True if the user has an approved
        enrollment in the class, otherwise False.
    """

    return Enrollment.objects.filter(
        user=user,
        gym_class=gym_class,
        status=Enrollment.STATUS_CHOICES.approved,
    ).exists()


class IsAnonymous(BasePermission):
    """
    Allows access only for users who are not authenticated.
    """

    def has_permission(self, request, view):
        return not request.user.is_authenticated

def can_view_gym_users(user, gym):
    """
    Permission:
    Owner, Manager, Staff can view users of their gym.
    """
    return user.memberships.filter(
        gym=gym,
        role__in=[
            GymMembership.Role.OWNER,
            GymMembership.Role.MANAGER,
            GymMembership.Role.STAFF,
        ],
        is_active=True,
    ).exists()

def can_manage_gym_users(user, gym):
    """
    Permission:
    Owner and Manager can manage users of their gym.
    """

    return user.memberships.filter(
        gym=gym,
        role__in=[
            GymMembership.Role.OWNER,
            GymMembership.Role.MANAGER,
        ],
        is_active=True,
    ).exists()

def can_update_user(user, target_user, gym):
    """
    Determines whether a user can update another user
    within a specific gym.

    Rules:

    Superuser:
        - Can update everyone.

    Owner:
        - Can update Manager, Staff,
          Trainer and Member.
        - Cannot update another Owner.

    Manager:
        - Can update Staff,
          Trainer and Member.
        - Cannot update Owner
          or another Manager.

    Notes:
        - Users cannot update themselves
          from this API.
        - Self update must be done
          via PATCH /accounts/me/.
    """

    # Self update is not allowed here.
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

    # Owner
    if requester_role == GymMembership.Role.OWNER:

        return target_role in [
            GymMembership.Role.MANAGER,
            GymMembership.Role.STAFF,
            GymMembership.Role.TRAINER,
            GymMembership.Role.MEMBER,
        ]

    # Manager
    if requester_role == GymMembership.Role.MANAGER:

        return target_role in [
            GymMembership.Role.STAFF,
            GymMembership.Role.TRAINER,
            GymMembership.Role.MEMBER,
        ]

    return False

def can_delete_user(user, target_user, gym):

    #اگر کسی بخواهد خودش را حذف کند، اجازه نده.
    if user == target_user:
        return False

#"این کسی که درخواست Delete داده در این Gym چه نقشی دارد
    requester_membership = user.memberships.filter(
        gym=gym,
        is_active=True,
    ).first()
    print("REQUEST USER:", user)
    print("REQUESTER MEMBERSHIP:", requester_membership)


    target_membership = target_user.memberships.filter(
        gym=gym,
        is_active=True,
    ).first()


# اگر یکی از این دو نفر در این Gym Membership نداشتند:
# درخواست‌دهنده عضو این Gym نیست
# فرد هدف عضو این Gym نیست
    if not requester_membership or not target_membership:
        return False


    requester_role = requester_membership.role
    target_role = target_membership.role
    


    # Owner
    if requester_role == GymMembership.Role.OWNER:

        return target_role != GymMembership.Role.OWNER


    # Manager
    if requester_role == GymMembership.Role.MANAGER:

        return target_role in [
            GymMembership.Role.STAFF,
            GymMembership.Role.TRAINER,
            GymMembership.Role.MEMBER,
        ]


    return False