from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import NotAuthenticated

from accounts.models import CustomUser
from gyms.models import Gym, GymMembership

from permissions.gym_permissions import (
    CanViewGym,
    CanCreateGym,
    CanManageGym,
    CanAddStaff,
    CanViewGymMembers,
    CanViewGymMembership,
    CanCreateGymMembership,
    CanManageGymMembership,
)


class GymPermissionsTestCase(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

        # =====================================================
        # Users
        # =====================================================

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

        self.trainer = CustomUser.objects.create_user(
            username="trainer",
            password="Test1234",
        )

        self.member = CustomUser.objects.create_user(
            username="member",
            password="Test1234",
        )

        self.superuser = CustomUser.objects.create_superuser(
            username="superuser",
            password="Test1234",
        )

        # =====================================================
        # Gym
        # =====================================================

        self.gym = Gym.objects.create(
            name="Test Gym",
            address="Tehran",
        )

        self.other_gym = Gym.objects.create(
            name="Other Gym",
            address="Other Address",
        )

        # =====================================================
        # Memberships
        # =====================================================

        GymMembership.objects.create(
            user=self.owner,
            gym=self.gym,
            role=GymMembership.Role.OWNER,
            share_percentage=100,
            is_active=True,
        )

        GymMembership.objects.create(
            user=self.manager,
            gym=self.gym,
            role=GymMembership.Role.MANAGER,
            salary=20,
            is_active=True,
        )

        GymMembership.objects.create(
            user=self.staff,
            gym=self.gym,
            role=GymMembership.Role.STAFF,
            salary=20,
            is_active=True,
        )

        GymMembership.objects.create(
            user=self.trainer,
            gym=self.gym,
            role=GymMembership.Role.TRAINER,
            salary=20,
            is_active=True,
        )

        GymMembership.objects.create(
            user=self.member,
            gym=self.gym,
            role=GymMembership.Role.MEMBER,
            is_active=True,
        )

        # =====================================================
        # Views
        # =====================================================

        self.view = type(
            "View",
            (),
            {
                "kwargs": {
                    "gym_id": self.gym.id,
                }
            },
        )()

        self.other_gym_view = type(
            "View",
            (),
            {
                "kwargs": {
                    "gym_id": self.other_gym.id,
                }
            },
        )()

    # =========================================================
    # CanViewGym
    # =========================================================

    def test_view_gym_allows_unauthenticated(self):
        request = self.factory.get("/")

        permission = CanViewGym()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_view_gym_allows_authenticated(self):
        request = self.factory.get("/")
        request.user = self.member

        permission = CanViewGym()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    # =========================================================
    # CanCreateGym
    # =========================================================

    def test_create_gym_allows_superuser(self):
        request = self.factory.post("/")
        request.user = self.superuser

        permission = CanCreateGym()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_create_gym_denies_owner(self):
        request = self.factory.post("/")
        request.user = self.owner

        permission = CanCreateGym()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_create_gym_denies_manager(self):
        request = self.factory.post("/")
        request.user = self.manager

        permission = CanCreateGym()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_create_gym_denies_member(self):
        request = self.factory.post("/")
        request.user = self.member

        permission = CanCreateGym()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    # =========================================================
    # CanManageGym
    # =========================================================

    def test_manage_gym_allows_superuser(self):
        request = self.factory.patch("/")
        request.user = self.superuser

        permission = CanManageGym()

        self.assertTrue(
            permission.has_object_permission(
                request,
                self.view,
                self.gym,
            )
        )

    def test_manage_gym_allows_owner(self):
        request = self.factory.patch("/")
        request.user = self.owner

        permission = CanManageGym()

        self.assertTrue(
            permission.has_object_permission(
                request,
                self.view,
                self.gym,
            )
        )

    def test_manage_gym_allows_manager(self):
        request = self.factory.patch("/")
        request.user = self.manager

        permission = CanManageGym()

        self.assertTrue(
            permission.has_object_permission(
                request,
                self.view,
                self.gym,
            )
        )

    def test_manage_gym_denies_staff(self):
        request = self.factory.patch("/")
        request.user = self.staff

        permission = CanManageGym()

        self.assertFalse(
            permission.has_object_permission(
                request,
                self.view,
                self.gym,
            )
        )

    def test_manage_gym_denies_trainer(self):
        request = self.factory.patch("/")
        request.user = self.trainer

        permission = CanManageGym()

        self.assertFalse(
            permission.has_object_permission(
                request,
                self.view,
                self.gym,
            )
        )

    def test_manage_gym_denies_member(self):
        request = self.factory.patch("/")
        request.user = self.member

        permission = CanManageGym()

        self.assertFalse(
            permission.has_object_permission(
                request,
                self.view,
                self.gym,
            )
        )

    def test_manage_gym_denies_user_from_other_gym(self):
        request = self.factory.patch("/")
        request.user = self.owner

        permission = CanManageGym()

        self.assertFalse(
            permission.has_object_permission(
                request,
                self.other_gym_view,
                self.other_gym,
            )
        )

    # =========================================================
    # CanAddStaff
    # =========================================================

    def test_add_staff_allows_superuser(self):
        request = self.factory.post("/")
        request.user = self.superuser

        permission = CanAddStaff()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_add_staff_allows_owner(self):
        request = self.factory.post("/")
        request.user = self.owner

        permission = CanAddStaff()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_add_staff_allows_manager(self):
        request = self.factory.post("/")
        request.user = self.manager

        permission = CanAddStaff()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_add_staff_denies_staff(self):
        request = self.factory.post("/")
        request.user = self.staff

        permission = CanAddStaff()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_add_staff_denies_trainer(self):
        request = self.factory.post("/")
        request.user = self.trainer

        permission = CanAddStaff()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_add_staff_denies_member(self):
        request = self.factory.post("/")
        request.user = self.member

        permission = CanAddStaff()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    # =========================================================
    # CanViewGymMembers
    # =========================================================

    def test_view_gym_members_allows_superuser(self):
        request = self.factory.get("/")
        request.user = self.superuser

        permission = CanViewGymMembers()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_view_gym_members_allows_owner(self):
        request = self.factory.get("/")
        request.user = self.owner

        permission = CanViewGymMembers()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_view_gym_members_allows_manager(self):
        request = self.factory.get("/")
        request.user = self.manager

        permission = CanViewGymMembers()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_view_gym_members_allows_staff(self):
        request = self.factory.get("/")
        request.user = self.staff

        permission = CanViewGymMembers()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_view_gym_members_denies_trainer(self):
        request = self.factory.get("/")
        request.user = self.trainer

        permission = CanViewGymMembers()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_view_gym_members_denies_member(self):
        request = self.factory.get("/")
        request.user = self.member

        permission = CanViewGymMembers()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    # =========================================================
    # CanViewGymMembership
    # =========================================================

    def test_view_membership_allows_superuser(self):
        request = self.factory.get("/")
        request.user = self.superuser

        permission = CanViewGymMembership()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_view_membership_allows_owner(self):
        request = self.factory.get("/")
        request.user = self.owner

        permission = CanViewGymMembership()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_view_membership_allows_manager(self):
        request = self.factory.get("/")
        request.user = self.manager

        permission = CanViewGymMembership()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_view_membership_denies_staff(self):
        request = self.factory.get("/")
        request.user = self.staff

        permission = CanViewGymMembership()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_view_membership_denies_member(self):
        request = self.factory.get("/")
        request.user = self.member

        permission = CanViewGymMembership()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    # =========================================================
    # CanCreateGymMembership
    # =========================================================

    def test_create_membership_allows_superuser(self):
        request = self.factory.post("/")
        request.user = self.superuser

        permission = CanCreateGymMembership()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_create_membership_allows_owner(self):
        request = self.factory.post("/")
        request.user = self.owner

        permission = CanCreateGymMembership()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_create_membership_allows_manager(self):
        request = self.factory.post("/")
        request.user = self.manager

        permission = CanCreateGymMembership()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_create_membership_denies_staff(self):
        request = self.factory.post("/")
        request.user = self.staff

        permission = CanCreateGymMembership()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_create_membership_denies_member(self):
        request = self.factory.post("/")
        request.user = self.member

        permission = CanCreateGymMembership()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    # =========================================================
    # CanManageGymMembership
    # =========================================================

    def test_manage_membership_allows_superuser(self):
        membership = GymMembership.objects.get(
            user=self.member,
            gym=self.gym,
        )

        request = self.factory.patch("/")
        request.user = self.superuser

        permission = CanManageGymMembership()

        self.assertTrue(
            permission.has_object_permission(
                request,
                self.view,
                membership,
            )
        )

    def test_manage_membership_allows_owner(self):
        membership = GymMembership.objects.get(
            user=self.member,
            gym=self.gym,
        )

        request = self.factory.patch("/")
        request.user = self.owner

        permission = CanManageGymMembership()

        self.assertTrue(
            permission.has_object_permission(
                request,
                self.view,
                membership,
            )
        )

    def test_manage_membership_allows_manager(self):
        membership = GymMembership.objects.get(
            user=self.member,
            gym=self.gym,
        )

        request = self.factory.patch("/")
        request.user = self.manager

        permission = CanManageGymMembership()

        self.assertTrue(
            permission.has_object_permission(
                request,
                self.view,
                membership,
            )
        )

    def test_manage_membership_denies_staff(self):
        membership = GymMembership.objects.get(
            user=self.member,
            gym=self.gym,
        )

        request = self.factory.patch("/")
        request.user = self.staff

        permission = CanManageGymMembership()

        self.assertFalse(
            permission.has_object_permission(
                request,
                self.view,
                membership,
            )
        )

    def test_manage_membership_denies_trainer(self):
        membership = GymMembership.objects.get(
            user=self.member,
            gym=self.gym,
        )

        request = self.factory.patch("/")
        request.user = self.trainer

        permission = CanManageGymMembership()

        self.assertFalse(
            permission.has_object_permission(
                request,
                self.view,
                membership,
            )
        )

    def test_manage_membership_denies_member(self):
        membership = GymMembership.objects.get(
            user=self.member,
            gym=self.gym,
        )

        request = self.factory.patch("/")
        request.user = self.member

        permission = CanManageGymMembership()

        self.assertFalse(
            permission.has_object_permission(
                request,
                self.view,
                membership,
            )
        )

    def test_manage_membership_denies_membership_from_other_gym(self):
        other_membership = GymMembership.objects.create(
            user=self.member,
            gym=self.other_gym,
            role=GymMembership.Role.MEMBER,
            is_active=True,
        )

        request = self.factory.patch("/")
        request.user = self.owner

        permission = CanManageGymMembership()

        self.assertFalse(
            permission.has_object_permission(
                request,
                self.other_gym_view,
                other_membership,
            )
        )