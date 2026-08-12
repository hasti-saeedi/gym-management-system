from django.shortcuts import get_object_or_404
from django.shortcuts import get_object_or_404

from rest_framework.permissions import BasePermission

from gyms.models import (
    Gym,
    GymMembership,
    )

#GymClass
#POST /api/classes/gyms/{gym_id}/classes/

def can_manage_gym_class(user, gym):
    """
    Determines whether a user can manage classes
    in the specified gym.

    Allowed roles:
        - Owner
        - Manager
        - Staff

    Superusers always have access.
    """

    if user.is_superuser:
        return True

    membership = user.memberships.filter(
        gym=gym,
        is_active=True,
    ).first()

    if not membership:
        return False

    return membership.role in [
        GymMembership.Role.OWNER,
        GymMembership.Role.MANAGER,
        GymMembership.Role.STAFF,
    ]

class CanManageGymClass(BasePermission):
    """
    Permission for GymClass management.

    APIs:

        POST
        /api/classes/gyms/{gym_id}/classes/

        PUT
        /api/classes/gyms/{gym_id}/classes/{id}/

        PATCH
        /api/classes/gyms/{gym_id}/classes/{id}/

        DELETE
        /api/classes/gyms/{gym_id}/classes/{id}/

    Allowed roles:
        - Owner
        - Manager
        - Staff
    """

    message = (
        "You do not have permission to manage classes in this gym."
    )

    def has_permission(self, request, view):
        """
        Used for create actions.
        """

        # if not request.user.is_authenticated:
        #     return False 

        if request.user.is_superuser:
            return True

        gym_id = view.kwargs.get("gym_id")

        gym = get_object_or_404(
            Gym,
            id=gym_id,
        )

        return can_manage_gym_class(
            request.user,
            gym,
        )

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        """
        Used for update, partial_update and destroy actions.
        """

        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        return can_manage_gym_class(
            request.user,
            obj.gym,
        )
  
 # helper of classsessions 

# classsessions

def is_staff_of_gym(user, gym):
    """
    Return True if the user is an active Owner,
    Manager, or Staff member of the given gym.
    """
    # if not user.is_authenticated:
    #     return False

    if not user.is_authenticated:
        return False
    
    return GymMembership.objects.filter(
        user=user,
        gym=gym,
        role__in=[
            GymMembership.Role.OWNER,
            GymMembership.Role.MANAGER,
            GymMembership.Role.STAFF,
        ],
        is_active=True,
    ).exists()

def is_class_trainer(user, gym_class):
    """
    Return True if the user is the primary trainer
    assigned to the given class.
    """
    # if not user.is_authenticated:
    #     return False
    
    return gym_class.trainer == user

def is_session_trainer(user, session):
    """
    Return True if the user is the trainer assigned
    directly to the given session.
    """
    
    # if not user.is_authenticated:
    #     return False
    
    return session.trainer == user

def can_access_session(user, session):
    """
    Determine whether the user is allowed to access
    the given class session.

    Access is granted if the user is:

    - Superuser
    - Owner of the gym
    - Manager of the gym
    - Staff of the gym
    - Primary trainer of the class
    - Trainer assigned directly to this session

    Members are not allowed.

    Returns:
        bool
    """
    # if not user.is_authenticated:
    #     return False
    
    if user.is_superuser:
        return True
    

    gym = session.gym_class.gym
    gym_class = session.gym_class

    if is_staff_of_gym(user, gym):
        return True
    
    if is_class_trainer(user, gym_class):
        return True

    if is_session_trainer(user, session):
        return True

    return False

def can_create_session(user, gym_class):
    """
    Check whether user can create a session
    for the given class.

    Allowed:
        - Superuser
        - Owner
        - Manager
        - Staff
        - Primary class trainer

    Not allowed:
        - Session trainer
        - Member
    """
    # if not user.is_authenticated:
    #     return False
    
    if user.is_superuser:
        return True


    gym = gym_class.gym


    if is_staff_of_gym(user, gym):
        return True


    if gym_class.trainer == user:
        return True


    return False

def can_delete_session(user, session):
    """
    Determine whether the user is allowed to delete
    the given class session.

    Access is granted if the user is:

    - Superuser
    - Owner of the gym
    - Manager of the gym
    - Staff of the gym

    Trainers are NOT allowed to delete sessions.

    Members are not allowed.

    Returns:
        bool
    # """
    # if not user.is_authenticated:
    #     return False
    
    if user.is_superuser:
        return True

    gym = session.gym_class.gym

    if is_staff_of_gym(user, gym):
        return True

    return False
 

class CanCreateSession(BasePermission):

    def has_permission(self, request, view):

        gym_class = view.get_gym_class()

        if not gym_class:
            return False

        return can_create_session(
            request.user,
            gym_class,
        )


class CanAccessSession(BasePermission):
    """
    Allows access to an existing session.

    Allowed:
        - Superuser
        - Owner
        - Manager
        - Staff
        - Class trainer
        - Session trainer
    """

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        return can_access_session(
            request.user,
            obj,
        )


class CanDeleteSession(BasePermission):
    """
    Allows deleting sessions.

    Allowed:
        - Superuser
        - Owner
        - Manager
        - Staff

    Trainers cannot delete sessions.
    """

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        return can_delete_session(
            request.user,
            obj,
        )
    

class CanViewSessionStudents(CanAccessSession):
    """
    Allows viewing students enrolled in a session.
    Uses the same access rule as session access.
    """
    pass


class CanRecordAttendance(CanAccessSession):
    """
    Allows recording attendance for a session.
    Uses the same access rule as session access.
    """
    pass


class CanRecordAttendance(CanAccessSession):
    """
    Allows recording attendance for a session.

    Uses the same access rules as session access.
    """
    pass