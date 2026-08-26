from django.test import TestCase
from rest_framework.test import APIRequestFactory

from accounts.models import CustomUser
from gyms.models import Gym, GymMembership

from permissions.account_permissions import (
    CanCreateGymUser,
    CanDeleteGymUser,
    CanUpdateGymUser,
    CanUpdateMe,
    CanViewGymUserDetail,
    CanViewGymUsers,
    CanViewMe,
)


class AccountPermissionTestCase(TestCase):
    """
    Test permission classes related to account management.

    The tests verify access for different gym roles, including:

    - Owner
    - Manager
    - Staff
    - Member
    - Superuser
    - Unauthenticated users

    The tests also verify that users belonging to another gym
    cannot access resources of the current gym.
    """

    def setUp(self):
        """Create users, gyms, memberships, and a mock view."""

        self.factory = APIRequestFactory()

        # Users
        self.owner = CustomUser.objects.create_user(
            username="owner",
            password="Test1234",
        )

        self.manager = CustomUser.objects.create_user(
            username="manager",
            password="Test1234",
        )

        self.staff = CustomUser.objects.create_user(
            username="staff",
            password="Test1234",
        )

        self.member = CustomUser.objects.create_user(
            username="member",
            password="Test1234",
        )

        self.other_owner = CustomUser.objects.create_user(
            username="other_owner",
            password="Test1234",
        )

        self.superuser = CustomUser.objects.create_superuser(
            username="superuser",
            password="Test1234",
        )

        # Gyms
        self.gym = Gym.objects.create(
            name="Test Gym",
        )

        self.other_gym = Gym.objects.create(
            name="Other Gym",
        )

        # Memberships
        GymMembership.objects.create(
            user=self.owner,
            gym=self.gym,
            role=GymMembership.Role.OWNER,
            salary=20,
            share_percentage=30,
        )

        GymMembership.objects.create(
            user=self.manager,
            gym=self.gym,
            role=GymMembership.Role.MANAGER,
            salary=20,
        )

        GymMembership.objects.create(
            user=self.staff,
            gym=self.gym,
            role=GymMembership.Role.STAFF,
            salary=20,
        )

        GymMembership.objects.create(
            user=self.member,
            gym=self.gym,
            role=GymMembership.Role.MEMBER,
        )

        GymMembership.objects.create(
            user=self.other_owner,
            gym=self.other_gym,
            role=GymMembership.Role.OWNER,
            salary=20,
            share_percentage=10,
        )

        # Mock view containing gym_id in URL kwargs
        self.view = type(
            "View",
            (),
            {
                "kwargs": {
                    "gym_id": self.gym.id,
                }
            },
        )()

    # =========================================================
    # CanViewGymUsers
    # =========================================================

    def test_can_view_gym_users_owner(self):
        """Owner can view users of their gym."""

        request = self.factory.get("/")
        request.user = self.owner

        permission = CanViewGymUsers()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_can_view_gym_users_manager(self):
        """Manager can view users of their gym."""

        request = self.factory.get("/")
        request.user = self.manager

        permission = CanViewGymUsers()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_can_view_gym_users_staff(self):
        """Staff can view users of their gym."""

        request = self.factory.get("/")
        request.user = self.staff

        permission = CanViewGymUsers()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_can_view_gym_users_member_denied(self):
        """Member cannot view users of their gym."""

        request = self.factory.get("/")
        request.user = self.member

        permission = CanViewGymUsers()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_can_view_gym_users_other_gym_denied(self):
        """User from another gym cannot view this gym's users."""

        request = self.factory.get("/")
        request.user = self.other_owner

        permission = CanViewGymUsers()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_can_view_gym_users_superuser(self):
        """Superuser can view users of any gym."""

        request = self.factory.get("/")
        request.user = self.superuser

        permission = CanViewGymUsers()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_can_view_gym_users_unauthenticated(self):
        """Unauthenticated users cannot view gym users."""

        request = self.factory.get("/")
        request.user = type(
            "AnonymousUser",
            (),
            {"is_authenticated": False},
        )()

        permission = CanViewGymUsers()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    # =========================================================
    # CanCreateGymUser
    # =========================================================

    def test_can_create_gym_user_owner(self):
        """Owner can create users in their gym."""

        request = self.factory.post("/")
        request.user = self.owner

        permission = CanCreateGymUser()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_can_create_gym_user_manager(self):
        """Manager can create users in their gym."""

        request = self.factory.post("/")
        request.user = self.manager

        permission = CanCreateGymUser()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_can_create_gym_user_staff_denied(self):
        """Staff cannot create users in the gym."""

        request = self.factory.post("/")
        request.user = self.staff

        permission = CanCreateGymUser()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_can_create_gym_user_member_denied(self):
        """Member cannot create users in the gym."""

        request = self.factory.post("/")
        request.user = self.member

        permission = CanCreateGymUser()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_can_create_gym_user_superuser(self):
        """Superuser can create users in any gym."""

        request = self.factory.post("/")
        request.user = self.superuser

        permission = CanCreateGymUser()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    # =========================================================
    # CanViewGymUserDetail
    # =========================================================

    def test_can_view_gym_user_detail_owner(self):
        """Owner can view a user's details in their gym."""

        request = self.factory.get("/")
        request.user = self.owner

        permission = CanViewGymUserDetail()

        self.assertTrue(
            permission.has_object_permission(
                request,
                self.view,
                self.member,
            )
        )

    def test_can_view_gym_user_detail_manager(self):
        """Manager can view a user's details in their gym."""

        request = self.factory.get("/")
        request.user = self.manager

        permission = CanViewGymUserDetail()

        self.assertTrue(
            permission.has_object_permission(
                request,
                self.view,
                self.member,
            )
        )

    def test_can_view_gym_user_detail_staff(self):
        """Staff can view a user's details in their gym."""

        request = self.factory.get("/")
        request.user = self.staff

        permission = CanViewGymUserDetail()

        self.assertTrue(
            permission.has_object_permission(
                request,
                self.view,
                self.member,
            )
        )

    def test_can_view_gym_user_detail_member_denied(self):
        """Member cannot view another user's details."""

        request = self.factory.get("/")
        request.user = self.member

        permission = CanViewGymUserDetail()

        self.assertFalse(
            permission.has_object_permission(
                request,
                self.view,
                self.member,
            )
        )

    def test_can_view_gym_user_detail_superuser(self):
        """Superuser can view user details."""

        request = self.factory.get("/")
        request.user = self.superuser

        permission = CanViewGymUserDetail()

        self.assertTrue(
            permission.has_object_permission(
                request,
                self.view,
                self.member,
            )
        )

    # =========================================================
    # CanUpdateGymUser
    # =========================================================

    def test_can_update_gym_user_owner(self):
        """Owner can update users in their gym."""

        request = self.factory.patch("/")
        request.user = self.owner

        permission = CanUpdateGymUser()

        self.assertTrue(
            permission.has_object_permission(
                request,
                self.view,
                self.member,
            )
        )

    def test_can_update_gym_user_manager(self):
        """Manager can update users in their gym."""

        request = self.factory.patch("/")
        request.user = self.manager

        permission = CanUpdateGymUser()

        self.assertTrue(
            permission.has_object_permission(
                request,
                self.view,
                self.member,
            )
        )

    def test_can_update_gym_user_member_denied(self):
        """Member cannot update another user's account."""

        request = self.factory.patch("/")
        request.user = self.member

        permission = CanUpdateGymUser()

        self.assertFalse(
            permission.has_object_permission(
                request,
                self.view,
                self.staff,
            )
        )

    def test_can_update_gym_user_superuser(self):
        """Superuser can update users."""

        request = self.factory.patch("/")
        request.user = self.superuser

        permission = CanUpdateGymUser()

        self.assertTrue(
            permission.has_object_permission(
                request,
                self.view,
                self.member,
            )
        )

    # =========================================================
    # CanDeleteGymUser
    # =========================================================

    def test_can_delete_gym_user_owner(self):
        """Owner can delete users in their gym."""

        request = self.factory.delete("/")
        request.user = self.owner

        permission = CanDeleteGymUser()

        self.assertTrue(
            permission.has_object_permission(
                request,
                self.view,
                self.member,
            )
        )

    def test_can_delete_gym_user_manager(self):
        """Manager can delete users in their gym."""

        request = self.factory.delete("/")
        request.user = self.manager

        permission = CanDeleteGymUser()

        self.assertTrue(
            permission.has_object_permission(
                request,
                self.view,
                self.member,
            )
        )

    def test_can_delete_gym_user_member_denied(self):
        """Member cannot delete another user's account."""

        request = self.factory.delete("/")
        request.user = self.member

        permission = CanDeleteGymUser()

        self.assertFalse(
            permission.has_object_permission(
                request,
                self.view,
                self.staff,
            )
        )

    def test_can_delete_gym_user_superuser(self):
        """Superuser can delete users."""

        request = self.factory.delete("/")
        request.user = self.superuser

        permission = CanDeleteGymUser()

        self.assertTrue(
            permission.has_object_permission(
                request,
                self.view,
                self.member,
            )
        )

    # =========================================================
    # CanViewMe
    # =========================================================

    def test_can_view_me_authenticated(self):
        """Authenticated users can view their own profile."""

        request = self.factory.get("/")
        request.user = self.member

        permission = CanViewMe()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_can_view_me_unauthenticated(self):
        """Unauthenticated users cannot view their profile."""

        request = self.factory.get("/")
        request.user = type(
            "AnonymousUser",
            (),
            {"is_authenticated": False},
        )()

        permission = CanViewMe()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    # =========================================================
    # CanUpdateMe
    # =========================================================

    def test_can_update_me_authenticated(self):
        """Authenticated users can update their own profile."""

        request = self.factory.patch("/")
        request.user = self.member

        permission = CanUpdateMe()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_can_update_me_unauthenticated(self):
        """Unauthenticated users cannot update their profile."""

        request = self.factory.patch("/")
        request.user = type(
            "AnonymousUser",
            (),
            {"is_authenticated": False},
        )()

        permission = CanUpdateMe()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )