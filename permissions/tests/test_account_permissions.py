from django.test import TestCase
from rest_framework.test import APIRequestFactory

from accounts.models import CustomUser
from gyms.models import Gym, GymMembership

from permissions.account_permissions import (
    CanViewGymUsers,
    CanCreateGymUser,
    CanViewGymUserDetail,
    CanUpdateGymUser,
    CanDeleteGymUser,
    CanViewMe,
    CanUpdateMe,
)


class AccountPermissionTestCase(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

        # -----------------------------
        # Users
        # -----------------------------

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

        # -----------------------------
        # Gyms
        # -----------------------------

        self.gym = Gym.objects.create(
            name="Test Gym",
        )

        self.other_gym = Gym.objects.create(
            name="Other Gym",
        )

        # -----------------------------
        # Memberships
        # -----------------------------

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

        # -----------------------------
        # View
        # -----------------------------

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
        request = self.factory.get("/")

        request.user = type(
            "AnonymousUser",
            (),
            {
                "is_authenticated": False,
            },
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
        request = self.factory.get("/")

        request.user = type(
            "AnonymousUser",
            (),
            {
                "is_authenticated": False,
            },
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
        request = self.factory.patch("/")

        request.user = type(
            "AnonymousUser",
            (),
            {
                "is_authenticated": False,
            },
        )()

        permission = CanUpdateMe()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )