# # from gyms.models import Gym,GymMembership
# # from classes.models import ClassSession, GymClass
# # from rest_framework.exceptions import NotFound
# # from django.shortcuts import get_object_or_404
# # from accounts.models import CustomUser
# # from django.core.exceptions import ValidationError
# # from django.utils import timezone


# # # def add_staff(
# # #     gym_id,
# # #     user_id,
# # #     role,
# # #     salary,
# # #     share_percentage=None,
# # # ):

# # #     gym = get_object_or_404(Gym, pk=gym_id)
# # #     user = get_object_or_404(CustomUser, pk=user_id)

# # #     if GymMembership.objects.filter(
# # #         gym_id=gym_id,
# # #         user_id=user_id,
# # #         role=role,
# # #     ).exists():
# # #         raise ValidationError(
# # #             "This user already has this role in this gym."
        
# # #         )
# # #     membership = GymMembership.objects.create(
# # #         gym=gym,
# # #         user=user,
# # #         role=role,
# # #         salary=salary,
# # #         share_percentage=share_percentage,
# # #     )

# # #     return membership



# # #     #نمایش ممبر های ان جیم اععم از اونر و ترینر و ...

# # from django.shortcuts import get_object_or_404
# # from rest_framework.exceptions import ValidationError

# # from accounts.models import CustomUser
# # from gyms.models import Gym, GymMembership


# # def can_manage_membership(actor, membership):
# #     """
# #     Check whether actor is allowed to manage the target membership.
# #     """

# #     # Superuser can manage everyone
# #     if actor.is_superuser:
# #         return True

# #     actor_membership = GymMembership.objects.filter(
# #         gym=membership.gym,
# #         user=actor,
# #         is_active=True,
# #     ).first()

# #     if actor_membership is None:
# #         raise ValidationError(
# #             "You are not a member of this gym."
# #         )

# #     # Owner can manage everyone except another Owner
# #     if actor_membership.role == GymMembership.Role.OWNER:
# #         if membership.role == GymMembership.Role.OWNER:
# #             raise ValidationError(
# #                 "Owner cannot manage another Owner."
# #             )

# #         return True

# #     # Manager can manage Staff, Trainer and Member
# #     if actor_membership.role == GymMembership.Role.MANAGER:
# #         if membership.role in [
# #             GymMembership.Role.STAFF,
# #             GymMembership.Role.TRAINER,
# #             GymMembership.Role.MEMBER,
# #         ]:
# #             return True

# #         raise ValidationError(
# #             "Manager cannot manage Owner or Manager."
# #         )

# #     # Staff / Trainer / Member
# #     raise ValidationError(
# #         "You do not have permission to manage this member."
# #     )

# # def add_staff(
# #     actor,
# #     gym_id,
# #     user_id,
# #     role,
# #     salary,
# #     share_percentage=None,
# # ):
# #     """
# #     Add a new member to a gym with a specific role.

# #     Parameters:
# #         actor:
# #             The authenticated user who is performing the operation.

# #         gym_id:
# #             ID of the gym where the new membership will be created.

# #         user_id:
# #             ID of the user who will be added to the gym.

# #         role:
# #             Role that will be assigned to the target user.

# #         salary:
# #             Salary associated with the membership.

# #         share_percentage:
# #             Optional percentage of revenue/share for the member.

# #     Business Rules:
# #         - Superuser can add any role.
# #         - Owner can add Manager, Staff, or Trainer.
# #         - Owner cannot add another Owner.
# #         - Manager can add Staff or Trainer.
# #         - Manager cannot add Owner or Manager.
# #         - Staff cannot add anyone.
# #         - Trainer cannot add anyone.
# #         - User must not already have the same role
# #           in the same gym.
# #     """

# #     # -------------------------------------------------
# #     # 1. Get the gym
# #     # -------------------------------------------------

# #     gym = get_object_or_404(
# #         Gym,
# #         pk=gym_id,
# #     )

# #     # -------------------------------------------------
# #     # 2. Get the user who will be added
# #     # -------------------------------------------------

# #     user = get_object_or_404(
# #         CustomUser,
# #         pk=user_id,
# #     )

# #     # -------------------------------------------------
# #     # 3. Find actor's active membership in this gym
# #     # -------------------------------------------------

# #     actor_membership = GymMembership.objects.filter(
# #         gym=gym,
# #         user=actor,
# #         is_active=True,
# #     ).first()

# #     # -------------------------------------------------
# #     # 4. Check actor's permission based on role
# #     # -------------------------------------------------

# #     # Superuser can assign any role.
# #     if actor.is_superuser:
# #         pass

# #     # User has no active membership in this gym.
# #     elif actor_membership is None:
# #         raise ValidationError(
# #             "You are not a member of this gym."
# #         )

# #     # Owner can add Manager, Staff, and Trainer.
# #     # Owner cannot add another Owner.
# #     elif actor_membership.role == GymMembership.Role.OWNER:

# #         if role == GymMembership.Role.OWNER:
# #             raise ValidationError(
# #                 "Owner cannot add another Owner."
# #             )

# #     # Manager can add Staff and Trainer.
# #     elif actor_membership.role == GymMembership.Role.MANAGER:

# #         if role not in [
# #             GymMembership.Role.STAFF,
# #             GymMembership.Role.TRAINER,
# #             GymMembership.Role.MEMBER,
# #         ]:
# #             raise ValidationError(
# #                 "Manager can only add Staff or Trainer."
# #             )

# #     # Staff and Trainer cannot add anyone.
# #     else:
# #         raise ValidationError(
# #             "You do not have permission to add a member."
# #         )

# #     # -------------------------------------------------
# #     # 5. Check duplicate membership
# #     # -------------------------------------------------

# #     if GymMembership.objects.filter(
# #         gym=gym,
# #         user=user,
# #         role=role,
# #     ).exists():

# #         raise ValidationError(
# #             "This user already has this role in this gym."
# #         )

# #     # -------------------------------------------------
# #     # 6. Create membership
# #     # -------------------------------------------------

# #     membership = GymMembership.objects.create(
# #         gym=gym,
# #         user=user,
# #         role=role,
# #         salary=salary,
# #         share_percentage=share_percentage,
# #     )

# #     # -------------------------------------------------
# #     # 7. Return created membership
# #     # -------------------------------------------------

# #     return membership


# # def get_gym_staff(gym_id):

# #     members = GymMembership.objects.filter(
# #         gym_id=gym_id,
# #         is_active=True,
# #     ).exclude(

# #     role=GymMembership.Role.MEMBER

# #     ).select_related("user")

# #     if not members.exists():
# #         raise NotFound("No active members found.")

# #     return members


# # def update_membership(
# #     actor,
# #     membership_id,
# #     role,
# #     salary,
# #     share_percentage=None,
# # ):

# #     membership = get_object_or_404(  #object
# #         GymMembership,
# #         pk=membership_id,
# #     )

# #     # Check whether actor can manage this membership
# #     can_manage_membership(
# #         actor,
# #         membership,
# #     )
        
# #     # -------------------------------------------------
# #     # Check the new role
# #     # -------------------------------------------------

# #     if role == GymMembership.Role.OWNER:
# #         raise ValidationError(
# #             "Owner role cannot be assigned."
# #         )

# #     # -------------------------------------------------
# #     # Prevent duplicate role
# #     # -------------------------------------------------

# #     if GymMembership.objects.filter(
# #         gym=membership.gym,
# #         user=membership.user,
# #         role=role,
# #     ).exclude(
# #         pk=membership.pk
# #     ).exists():
# #         raise ValidationError(
# #             "This user already has this role in this gym."
# #         )

# #         #فقط مقدار داخل آبجکت در حافظه عوض می‌شود.
# #     membership.role = role
# #     membership.salary = salary
# #     membership.share_percentage = share_percentage

# #     membership.save()

# #     return membership

# # def deactivate_staff(
# #         actor,
# #         membership_id,
# #         ):

# #     membership = get_object_or_404(
# #         GymMembership,
# #         pk=membership_id,
# #     )

# #     # Check whether actor can manage this membership
# #     can_manage_membership(
# #         actor,
# #         membership,
# #     )

# #     membership.is_active = False
# #     membership.save()

# #     return membership


# from django.shortcuts import get_object_or_404
# from rest_framework.exceptions import ValidationError, NotFound

# from accounts.models import CustomUser
# from gyms.models import Gym, GymMembership


# # =========================================================
# # Permission / Business Rule Helper
# # =========================================================

# def can_manage_membership(
#     actor,
#     membership,
#     new_role=None,
# ):
#     """
#     Check whether actor is allowed to manage the target membership.

#     Hierarchy:

#         OWNER
#           ↓
#         MANAGER
#           ↓
#         STAFF / TRAINER / MEMBER

#     Rules:

#     - Superuser can manage everyone.
#     - Owner can manage Manager, Staff, Trainer and Member.
#     - Owner cannot manage another Owner.
#     - Owner cannot assign Owner role.
#     - Manager can manage Staff, Trainer and Member.
#     - Manager cannot manage Owner or Manager.
#     - Manager can only assign Staff, Trainer or Member.
#     - Staff, Trainer and Member cannot manage anyone.
#     """

#     # -----------------------------------------------------
#     # Superuser
#     # -----------------------------------------------------

#     if actor.is_superuser:
#         return True

#     # -----------------------------------------------------
#     # Get actor's active membership in target gym
#     # -----------------------------------------------------

#     actor_membership = GymMembership.objects.filter(
#         gym=membership.gym,
#         user=actor,
#         is_active=True,
#     ).first()

#     if actor_membership is None:
#         raise ValidationError(
#             "You are not a member of this gym."
#         )

#     actor_role = actor_membership.role
#     target_role = membership.role

#     # =====================================================
#     # OWNER
#     # =====================================================

#     if actor_role == GymMembership.Role.OWNER:

#         # Owner cannot manage another Owner
#         if target_role == GymMembership.Role.OWNER:
#             raise ValidationError(
#                 "Owner cannot manage another Owner."
#             )

#         # Owner cannot assign Owner role
#         if new_role == GymMembership.Role.OWNER:
#             raise ValidationError(
#                 "Owner cannot assign Owner role."
#             )

#         return True

#     # =====================================================
#     # MANAGER
#     # =====================================================

#     if actor_role == GymMembership.Role.MANAGER:

#         # Manager can only manage:
#         # Staff, Trainer, Member
#         if target_role not in [
#             GymMembership.Role.STAFF,
#             GymMembership.Role.TRAINER,
#             GymMembership.Role.MEMBER,
#         ]:
#             raise ValidationError(
#                 "Manager cannot manage Owner or Manager."
#             )

#         # Manager can only assign:
#         # Staff, Trainer, Member
#         if new_role is not None and new_role not in [
#             GymMembership.Role.STAFF,
#             GymMembership.Role.TRAINER,
#             GymMembership.Role.MEMBER,
#         ]:
#             raise ValidationError(
#                 "Manager can only assign Staff, Trainer or Member."
#             )

#         return True

#     # =====================================================
#     # STAFF / TRAINER / MEMBER
#     # =====================================================

#     raise ValidationError(
#         "You do not have permission to manage members."
#     )


# # =========================================================
# # Add Staff / Member
# # =========================================================

# def add_staff(
#     actor,
#     gym_id,
#     user_id,
#     role,
#     salary,
#     share_percentage=None,
# ):
#     """
#     Add a new membership to a gym.

#     Rules:

#     - Superuser can add any role except restrictions defined
#       by the business rules.
#     - Owner can add Manager, Staff, Trainer and Member.
#     - Owner cannot add Owner.
#     - Manager can add Staff, Trainer and Member.
#     - Manager cannot add Owner or Manager.
#     - Staff, Trainer and Member cannot add anyone.
#     - Same user cannot have duplicate role in same gym.
#     """

#     # -----------------------------------------------------
#     # 1. Get gym
#     # -----------------------------------------------------

#     gym = get_object_or_404(
#         Gym,
#         pk=gym_id,
#     )

#     # -----------------------------------------------------
#     # 2. Get target user
#     # -----------------------------------------------------

#     user = get_object_or_404(
#         CustomUser,
#         pk=user_id,
#     )

#     # -----------------------------------------------------
#     # 3. Get actor's active membership
#     # -----------------------------------------------------

#     actor_membership = GymMembership.objects.filter(
#         gym=gym,
#         user=actor,
#         is_active=True,
#     ).first()

#     # -----------------------------------------------------
#     # 4. Check actor's permission
#     # -----------------------------------------------------

#     if actor.is_superuser:
#         pass

#     elif actor_membership is None:
#         raise ValidationError(
#             "You are not a member of this gym."
#         )

#     # -----------------------------------------------------
#     # Owner
#     # -----------------------------------------------------

#     elif actor_membership.role == GymMembership.Role.OWNER:

#         if role == GymMembership.Role.OWNER:
#             raise ValidationError(
#                 "Owner cannot add another Owner."
#             )

#     # -----------------------------------------------------
#     # Manager
#     # -----------------------------------------------------

#     elif actor_membership.role == GymMembership.Role.MANAGER:

#         if role not in [
#             GymMembership.Role.STAFF,
#             GymMembership.Role.TRAINER,
#             GymMembership.Role.MEMBER,
#         ]:
#             raise ValidationError(
#                 "Manager can only add Staff, Trainer or Member."
#             )

#     # -----------------------------------------------------
#     # Staff / Trainer / Member
#     # -----------------------------------------------------

#     else:
#         raise ValidationError(
#             "You do not have permission to add a member."
#         )

#     # -----------------------------------------------------
#     # 5. Prevent duplicate membership
#     # -----------------------------------------------------

#     if GymMembership.objects.filter(
#         gym=gym,
#         user=user,
#         role=role,
#     ).exists():
#         raise ValidationError(
#             "This user already has this role in this gym."
#         )

#     # -----------------------------------------------------
#     # 6. Create membership
#     # -----------------------------------------------------

#     membership = GymMembership.objects.create(
#         gym=gym,
#         user=user,
#         role=role,
#         salary=salary,
#         share_percentage=share_percentage,
#     )

#     return membership


# # =========================================================
# # Get Gym Staff
# # =========================================================

# def get_gym_staff(gym_id):

#     members = (
#         GymMembership.objects
#         .filter(
#             gym_id=gym_id,
#             is_active=True,
#         )
#         .exclude(
#             role=GymMembership.Role.MEMBER
#         )
#         .select_related("user")
#     )

#     if not members.exists():
#         raise NotFound(
#             "No active members found."
#         )

#     return members


# # =========================================================
# # Change Staff Role, salay, sharepercentage
# # =========================================================

# def update_membership(
#     actor,
#     membership_id,
#     role,
#     salary,
#     share_percentage=None,
# ):
#     """
#     Change the role and financial information of a membership.
#     """

#     # -----------------------------------------------------
#     # 1. Get target membership
#     # -----------------------------------------------------

#     membership = get_object_or_404(
#         GymMembership,
#         pk=membership_id,
#     )

#     # -----------------------------------------------------
#     # 2. Check permission
#     # -----------------------------------------------------

#     can_manage_membership(
#         actor=actor,
#         membership=membership,
#         new_role=role,
#     )

#     # -----------------------------------------------------
#     # 3. Prevent duplicate role
#     # -----------------------------------------------------

#     if GymMembership.objects.filter(
#         gym=membership.gym,
#         user=membership.user,
#         role=role,
#     ).exclude(
#         pk=membership.pk
#     ).exists():

#         raise ValidationError(
#             "This user already has this role in this gym."
#         )

#     # -----------------------------------------------------
#     # 4. Update membership
#     # -----------------------------------------------------

#     membership.role = role
#     membership.salary = salary
#     membership.share_percentage = share_percentage

#     membership.save()

#     return membership


# # =========================================================
# # Deactivate Staff
# # =========================================================

# def deactivate_staff(
#     actor,
#     membership_id,
# ):
#     """
#     Deactivate a gym membership.
#     """

#     # -----------------------------------------------------
#     # 1. Get target membership
#     # -----------------------------------------------------

#     membership = get_object_or_404(
#         GymMembership,
#         pk=membership_id,
#     )

#     # -----------------------------------------------------
#     # 2. Check permission
#     # -----------------------------------------------------

#     can_manage_membership(
#         actor=actor,
#         membership=membership,
#     )

#     # -----------------------------------------------------
#     # 3. Deactivate membership
#     # -----------------------------------------------------

#     membership.is_active = False
#     membership.save()

#     return membership


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
    Check whether actor is allowed to manage
    the target membership.

    Hierarchy:

        Superuser
            ↓
          Owner
            ↓
         Manager
            ↓
      Staff / Trainer / Member

    Rules:

        Superuser:
            Can manage everyone.

        Owner:
            Can manage Manager, Staff, Trainer, Member.
            Cannot manage another Owner.

        Manager:
            Can manage Staff, Trainer, Member.
            Cannot manage Owner or Manager.

        Staff / Trainer / Member:
            Cannot manage anyone.
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
    Check whether actor can assign the new role
    to the target membership.

    Rules:

        Owner:
            Can assign:
                Manager
                Staff
                Trainer
                Member

            Cannot assign:
                Owner

        Manager:
            Can assign:
                Staff
                Trainer
                Member

            Cannot assign:
                Owner
                Manager

        Superuser:
            Can assign any role.
    """

    # --------------------------------------------------------
    # Superuser
    # --------------------------------------------------------

    if actor.is_superuser:
        return True

    # --------------------------------------------------------
    # Get actor membership
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
    Create a new GymMembership.

    Rules:

        Superuser:
            Can add any role.

        Owner:
            Can add Manager, Staff, Trainer, Member.
            Cannot add Owner.

        Manager:
            Can add Staff, Trainer, Member.
            Cannot add Owner or Manager.

        Staff / Trainer / Member:
            Cannot add anyone.
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
        # Get actor membership
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
    Return active non-member staff of a gym.

    Excludes:
        Member
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

    Can change:

        - role
        - salary
        - share_percentage

    Permission hierarchy is checked before update.
    """

    # --------------------------------------------------------
    # Get Membership
    # --------------------------------------------------------

    membership = get_object_or_404(
        GymMembership,
        pk=membership_id,
    )

    # --------------------------------------------------------
    # Check target membership
    # --------------------------------------------------------

    can_manage_membership(
        actor,
        membership,
    )

    # --------------------------------------------------------
    # Role
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
    # Salary
    # --------------------------------------------------------

    if salary is not None:
        membership.salary = salary

    # --------------------------------------------------------
    # Share Percentage
    # --------------------------------------------------------

    if share_percentage is not None:
        membership.share_percentage = share_percentage

    # --------------------------------------------------------
    # Save
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

    Owner:
        Can deactivate Manager / Staff / Trainer / Member.

    Manager:
        Can deactivate Staff / Trainer / Member.

    Superuser:
        Can deactivate everyone.
    """

    membership = get_object_or_404(
        GymMembership,
        pk=membership_id,
    )

    # --------------------------------------------------------
    # Check permission
    # --------------------------------------------------------

    can_manage_membership(
        actor,
        membership,
    )

    # --------------------------------------------------------
    # Already inactive
    # --------------------------------------------------------

    if not membership.is_active:
        raise ValidationError(
            "This membership is already inactive."
        )

    # --------------------------------------------------------
    # Deactivate
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

    Same hierarchy as Deactivate.
    """

    membership = get_object_or_404(
        GymMembership,
        pk=membership_id,
    )

    # --------------------------------------------------------
    # Check permission
    # --------------------------------------------------------

    can_manage_membership(
        actor,
        membership,
    )

    # --------------------------------------------------------
    # Already active
    # --------------------------------------------------------

    if membership.is_active:
        raise ValidationError(
            "This membership is already active."
        )

    # --------------------------------------------------------
    # Activate
    # --------------------------------------------------------

    membership.is_active = True

    membership.save(
        update_fields=["is_active"],
    )

    return membership

