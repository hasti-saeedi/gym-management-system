from django.shortcuts import get_object_or_404

from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import NotFound

from accounts.models import CustomUser
from gyms.models import Gym, GymMembership


# ============================================================
# Helper: Can Actor Manage Target Membership?
# ============================================================

def can_manage_membership(actor, membership):
    """
    Check whether the authenticated actor can manage
    the target gym membership.

    This function implements the gym membership management
    permission hierarchy at the service/business-logic layer.

    Role hierarchy:

        Superuser
            ↓
          Owner
            ↓
         Manager
            ↓
      Staff / Trainer / Member

    Rules:

        Superuser:
            Can manage every membership.

        Owner:
            Can manage Manager, Staff, Trainer, and Member.
            Cannot manage another Owner.

        Manager:
            Can manage Staff, Trainer, and Member.
            Cannot manage Owner or Manager.

        Staff:
            Cannot manage memberships.

        Trainer:
            Cannot manage memberships.

        Member:
            Cannot manage memberships.

    Args:
        actor:
            The user performing the operation.

        membership:
            The GymMembership object that the actor wants
            to manage.

    Returns:
        bool:
            Returns True when the actor is allowed to manage
            the target membership.

    Raises:
        ValidationError:
            If the actor is not an active member of the gym
            or does not have sufficient privileges.
    """

    # --------------------------------------------------------
    # Superuser
    # --------------------------------------------------------

    if actor.is_superuser:
        return True

    # --------------------------------------------------------
    # Get actor's active membership in the target gym
    # --------------------------------------------------------

    actor_membership = GymMembership.objects.filter(
        gym=membership.gym,
        user=actor,
        is_active=True,
    ).first()

    if actor_membership is None:
        raise ValidationError(
            "You are not an active member of this gym."
        )

    # --------------------------------------------------------
    # Owner
    # --------------------------------------------------------

    if actor_membership.role == GymMembership.Role.OWNER:

        if membership.role == GymMembership.Role.OWNER:
            raise ValidationError(
                "Owner cannot manage another Owner."
            )

        return True

    # --------------------------------------------------------
    # Manager
    # --------------------------------------------------------

    if actor_membership.role == GymMembership.Role.MANAGER:

        if membership.role in [
            GymMembership.Role.STAFF,
            GymMembership.Role.TRAINER,
            GymMembership.Role.MEMBER,
        ]:
            return True

        raise ValidationError(
            "Manager cannot manage Owner or Manager."
        )

    # --------------------------------------------------------
    # Staff / Trainer / Member
    # --------------------------------------------------------

    raise ValidationError(
        "You do not have permission to manage "
        "this membership."
    )


# ============================================================
# Helper: Can Actor Assign New Role?
# ============================================================

def can_assign_role(actor, membership, new_role):
    """
    Check whether the actor is allowed to assign a new role
    to the target membership.

    This function is responsible only for validating whether
    the actor has permission to assign the requested role.
    It does not modify the membership.

    Rules:

        Superuser:
            Can assign any role.

        Owner:
            Can assign:
                - Manager
                - Staff
                - Trainer
                - Member

            Cannot assign:
                - Owner

        Manager:
            Can assign:
                - Staff
                - Trainer
                - Member

            Cannot assign:
                - Owner
                - Manager

        Staff / Trainer / Member:
            Cannot assign roles.

    Args:
        actor:
            The user performing the operation.

        membership:
            The GymMembership whose role will be changed.

        new_role:
            The role that the actor wants to assign.

    Returns:
        bool:
            Returns True when the actor can assign the role.

    Raises:
        ValidationError:
            If the actor is not an active member of the gym
            or does not have permission to assign the requested role.
    """

    # --------------------------------------------------------
    # Superuser
    # --------------------------------------------------------

    if actor.is_superuser:
        return True

    # --------------------------------------------------------
    # Get actor's active membership
    # --------------------------------------------------------

    actor_membership = GymMembership.objects.filter(
        gym=membership.gym,
        user=actor,
        is_active=True,
    ).first()

    if actor_membership is None:
        raise ValidationError(
            "You are not an active member of this gym."
        )

    # --------------------------------------------------------
    # Owner
    # --------------------------------------------------------

    if actor_membership.role == GymMembership.Role.OWNER:

        if new_role == GymMembership.Role.OWNER:
            raise ValidationError(
                "Owner cannot assign the Owner role."
            )

        return True

    # --------------------------------------------------------
    # Manager
    # --------------------------------------------------------

    if actor_membership.role == GymMembership.Role.MANAGER:

        if new_role in [
            GymMembership.Role.STAFF,
            GymMembership.Role.TRAINER,
            GymMembership.Role.MEMBER,
        ]:
            return True

        raise ValidationError(
            "Manager can only assign Staff, "
            "Trainer, or Member role."
        )

    # --------------------------------------------------------
    # Staff / Trainer / Member
    # --------------------------------------------------------

    raise ValidationError(
        "You do not have permission to assign a role."
    )


# ============================================================
# Add Staff / Membership
# ============================================================

def add_staff(
    actor,
    gym_id,
    user_id,
    role,
    salary,
    share_percentage=None,
):
    """
    Create a new GymMembership for a user in a gym.

    The function performs all business-rule checks required
    before creating a membership.

    Permission rules:

        Superuser:
            Can add any role.

        Owner:
            Can add:
                - Manager
                - Staff
                - Trainer
                - Member

            Cannot add:
                - Owner

        Manager:
            Can add:
                - Staff
                - Trainer
                - Member

            Cannot add:
                - Owner
                - Manager

        Staff / Trainer / Member:
            Cannot add new memberships.

    Additional business rule:

        A user cannot have the same active role more than
        once in the same gym.

    Args:
        actor:
            The authenticated user performing the operation.

        gym_id:
            ID of the gym where the membership will be created.

        user_id:
            ID of the user who will become a gym member.

        role:
            Role assigned to the target user.

        salary:
            Salary associated with the membership.

        share_percentage:
            Optional revenue-share percentage associated
            with the membership.

    Returns:
        GymMembership:
            The newly created membership.

    Raises:
        NotFound:
            If the gym or target user does not exist.

        ValidationError:
            If the actor does not have permission to add
            the membership or the user already has the
            same active role in the gym.
    """

    # --------------------------------------------------------
    # Get Gym
    # --------------------------------------------------------

    gym = get_object_or_404(
        Gym,
        pk=gym_id,
    )

    # --------------------------------------------------------
    # Get target user
    # --------------------------------------------------------

    user = get_object_or_404(
        CustomUser,
        pk=user_id,
    )

    # --------------------------------------------------------
    # Superuser
    # --------------------------------------------------------

    if actor.is_superuser:
        pass

    else:

        # ----------------------------------------------------
        # Get actor's active membership
        # ----------------------------------------------------

        actor_membership = GymMembership.objects.filter(
            gym=gym,
            user=actor,
            is_active=True,
        ).first()

        if actor_membership is None:
            raise ValidationError(
                "You are not an active member of this gym."
            )

        # ----------------------------------------------------
        # Owner
        # ----------------------------------------------------

        if actor_membership.role == GymMembership.Role.OWNER:

            if role == GymMembership.Role.OWNER:
                raise ValidationError(
                    "Owner cannot add another Owner."
                )

        # ----------------------------------------------------
        # Manager
        # ----------------------------------------------------

        elif actor_membership.role == GymMembership.Role.MANAGER:

            if role not in [
                GymMembership.Role.STAFF,
                GymMembership.Role.TRAINER,
                GymMembership.Role.MEMBER,
            ]:
                raise ValidationError(
                    "Manager can only add Staff, "
                    "Trainer, or Member."
                )

        # ----------------------------------------------------
        # Staff / Trainer / Member
        # ----------------------------------------------------

        else:
            raise ValidationError(
                "You do not have permission to add "
                "a member to this gym."
            )

    # --------------------------------------------------------
    # Prevent duplicate active role
    # --------------------------------------------------------

    if GymMembership.objects.filter(
        gym=gym,
        user=user,
        role=role,
        is_active=True,
    ).exists():

        raise ValidationError(
            "This user already has this role "
            "in this gym."
        )

    # --------------------------------------------------------
    # Create Membership
    # --------------------------------------------------------

    membership = GymMembership.objects.create(
        gym=gym,
        user=user,
        role=role,
        salary=salary,
        share_percentage=share_percentage,
    )

    return membership


# ============================================================
# Get Gym Staff
# ============================================================

def get_gym_staff(gym_id):
    """
    Return all active staff memberships of a gym.

    Members whose role is ``MEMBER`` are excluded.
    Therefore, the returned queryset contains only gym
    employees such as:

        - Owner
        - Manager
        - Staff
        - Trainer

    The related user object is loaded using ``select_related``
    to reduce additional database queries when accessing
    membership.user.

    Args:
        gym_id:
            ID of the gym whose staff should be retrieved.

    Returns:
        QuerySet:
            Active non-member GymMembership objects.

    Raises:
        NotFound:
            If the gym has no active staff memberships.
    """

    members = (
        GymMembership.objects
        .filter(
            gym_id=gym_id,
            is_active=True,
        )
        .exclude(
            role=GymMembership.Role.MEMBER,
        )
        .select_related("user")
    )

    if not members.exists():
        raise NotFound(
            "No active staff members found."
        )

    return members


# ============================================================
# Update Membership
# ============================================================

def update_membership(
    actor,
    membership_id,
    role=None,
    salary=None,
    share_percentage=None,
):
    """
    Update an existing GymMembership.

    The function can update the following fields:

        - role
        - salary
        - share_percentage

    Before changing the membership, the actor's permission
    to manage the target membership is checked.

    If a new role is provided, an additional role-assignment
    permission check is performed.

    Business rules:

        - Actor must have permission to manage the membership.
        - Owner cannot assign the Owner role.
        - Manager cannot assign Owner or Manager.
        - Staff / Trainer / Member cannot modify memberships.
        - A user cannot have the same active role twice
          in the same gym.

    Args:
        actor:
            The authenticated user performing the operation.

        membership_id:
            ID of the GymMembership to update.

        role:
            Optional new role for the membership.

        salary:
            Optional new salary.

        share_percentage:
            Optional new revenue-share percentage.

    Returns:
        GymMembership:
            The updated membership.

    Raises:
        NotFound:
            If the membership does not exist.

        ValidationError:
            If the actor does not have permission to update
            the membership or the new role conflicts with
            an existing active membership.
    """

    # --------------------------------------------------------
    # Get Membership
    # --------------------------------------------------------

    membership = get_object_or_404(
        GymMembership,
        pk=membership_id,
    )

    # --------------------------------------------------------
    # Check management permission
    # --------------------------------------------------------

    can_manage_membership(
        actor,
        membership,
    )

    # --------------------------------------------------------
    # Update Role
    # --------------------------------------------------------

    if role is not None:

        can_assign_role(
            actor,
            membership,
            role,
        )

        # Prevent duplicate active role
        if GymMembership.objects.filter(
            gym=membership.gym,
            user=membership.user,
            role=role,
            is_active=True,
        ).exclude(
            pk=membership.pk,
        ).exists():

            raise ValidationError(
                "This user already has this role "
                "in this gym."
            )

        membership.role = role

    # --------------------------------------------------------
    # Update Salary
    # --------------------------------------------------------

    if salary is not None:
        membership.salary = salary

    # --------------------------------------------------------
    # Update Share Percentage
    # --------------------------------------------------------

    if share_percentage is not None:
        membership.share_percentage = share_percentage

    # --------------------------------------------------------
    # Save Changes
    # --------------------------------------------------------

    membership.save()

    return membership


# ============================================================
# Deactivate Membership
# ============================================================

def deactivate_staff(
    actor,
    membership_id,
):
    """
    Deactivate an existing GymMembership.

    Deactivation is implemented as a soft status change.
    The membership record is not deleted from the database.

    Permission hierarchy:

        Superuser:
            Can deactivate everyone.

        Owner:
            Can deactivate Manager, Staff, Trainer, and Member.

        Manager:
            Can deactivate Staff, Trainer, and Member.

        Staff / Trainer / Member:
            Cannot deactivate memberships.

    The function also prevents deactivating a membership that
    is already inactive.

    Args:
        actor:
            The authenticated user performing the operation.

        membership_id:
            ID of the GymMembership to deactivate.

    Returns:
        GymMembership:
            The deactivated membership.

    Raises:
        NotFound:
            If the membership does not exist.

        ValidationError:
            If the actor does not have permission or the
            membership is already inactive.
    """

    # --------------------------------------------------------
    # Get Membership
    # --------------------------------------------------------

    membership = get_object_or_404(
        GymMembership,
        pk=membership_id,
    )

    # --------------------------------------------------------
    # Check Permission
    # --------------------------------------------------------

    can_manage_membership(
        actor,
        membership,
    )

    # --------------------------------------------------------
    # Check Current Status
    # --------------------------------------------------------

    if not membership.is_active:
        raise ValidationError(
            "This membership is already inactive."
        )

    # --------------------------------------------------------
    # Deactivate Membership
    # --------------------------------------------------------

    membership.is_active = False

    membership.save(
        update_fields=["is_active"],
    )

    return membership


# ============================================================
# Activate Membership
# ============================================================

def activate_staff(
    actor,
    membership_id,
):
    """
    Activate an existing GymMembership.

    Activation changes the ``is_active`` field from False
    to True without creating a new membership record.

    The same permission hierarchy used for membership
    management applies:

        Superuser:
            Can activate everyone.

        Owner:
            Can activate Manager, Staff, Trainer, and Member.

        Manager:
            Can activate Staff, Trainer, and Member.

        Staff / Trainer / Member:
            Cannot activate memberships.

    The function prevents activating a membership that is
    already active.

    Args:
        actor:
            The authenticated user performing the operation.

        membership_id:
            ID of the GymMembership to activate.

    Returns:
        GymMembership:
            The activated membership.

    Raises:
        NotFound:
            If the membership does not exist.

        ValidationError:
            If the actor does not have permission or the
            membership is already active.
    """

    # --------------------------------------------------------
    # Get Membership
    # --------------------------------------------------------

    membership = get_object_or_404(
        GymMembership,
        pk=membership_id,
    )

    # --------------------------------------------------------
    # Check Permission
    # --------------------------------------------------------

    can_manage_membership(
        actor,
        membership,
    )

    # --------------------------------------------------------
    # Check Current Status
    # --------------------------------------------------------

    if membership.is_active:
        raise ValidationError(
            "This membership is already active."
        )

    # --------------------------------------------------------
    # Activate Membership
    # --------------------------------------------------------

    membership.is_active = True

    membership.save(
        update_fields=["is_active"],
    )

    return membership