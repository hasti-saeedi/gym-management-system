from django.test import TestCase
from rest_framework.test import APIRequestFactory

from accounts.models import CustomUser
from gyms.models import Gym, GymMembership

from permissions.gym_permissions import (
    CanAddStaff,
    CanCreateGym,
    CanCreateGymMembership,
    CanManageGym,
    CanManageGymMembership,
    CanViewGym,
    CanViewGymMembers,
    CanViewGymMembership,
)


class GymPermissionsTestCase(TestCase):
    """Test permissions related to gyms and gym memberships."""

    def setUp(self):
        """Create users, gyms, memberships, and mock views for testing."""
        self.factory = APIRequestFactory()

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

        self.gym = Gym.objects.create(
            name="Test Gym",
            address="Tehran",
        )

        self.other_gym = Gym.objects.create(
            name="Other Gym",
            address="Other Address",
        )

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

    # CanViewGym

    def test_view_gym_allows_unauthenticated(self):
        """Allow unauthenticated users to view a gym."""
        request = self.factory.get("/")

        permission = CanViewGym()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_view_gym_allows_authenticated(self):
        """Allow authenticated users to view a gym."""
        request = self.factory.get("/")
        request.user = self.member

        permission = CanViewGym()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    # CanCreateGym

    def test_create_gym_allows_superuser(self):
        """Allow superusers to create gyms."""
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
        """Deny gym owners from creating gyms."""
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
        """Deny gym managers from creating gyms."""
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
        """Deny gym members from creating gyms."""
        request = self.factory.post("/")
        request.user = self.member

        permission = CanCreateGym()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    # CanManageGym

    def test_manage_gym_allows_superuser(self):
        """Allow superusers to manage any gym."""
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
        """Allow gym owners to manage their gym."""
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
        """Allow gym managers to manage their gym."""
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
        """Deny staff members from managing a gym."""
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
        """Deny trainers from managing a gym."""
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
        """Deny members from managing a gym."""
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
        """Deny users from managing a gym they do not belong to."""
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

    # CanAddStaff

    def test_add_staff_allows_superuser(self):
        """Allow superusers to add staff to a gym."""
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
        """Allow gym owners to add staff."""
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
        """Allow gym managers to add staff."""
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
        """Deny staff members from adding other staff."""
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
        """Deny trainers from adding staff."""
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
        """Deny members from adding staff."""
        request = self.factory.post("/")
        request.user = self.member

        permission = CanAddStaff()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    # CanViewGymMembers

    def test_view_gym_members_allows_superuser(self):
        """Allow superusers to view gym members."""
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
        """Allow gym owners to view gym members."""
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
        """Allow gym managers to view gym members."""
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
        """Allow staff members to view gym members."""
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
        """Deny trainers from viewing gym members."""
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
        """Deny members from viewing other gym members."""
        request = self.factory.get("/")
        request.user = self.member

        permission = CanViewGymMembers()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    # CanViewGymMembership

    def test_view_membership_allows_superuser(self):
        """Allow superusers to view gym memberships."""
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
        """Allow gym owners to view memberships."""
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
        """Allow gym managers to view memberships."""
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
        """Deny staff members from viewing gym memberships."""
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
        """Deny members from viewing gym memberships."""
        request = self.factory.get("/")
        request.user = self.member

        permission = CanViewGymMembership()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    # CanCreateGymMembership

    def test_create_membership_allows_superuser(self):
        """Allow superusers to create gym memberships."""
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
        """Allow gym owners to create memberships."""
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
        """Allow gym managers to create memberships."""
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
        """Deny staff members from creating gym memberships."""
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
        """Deny members from creating gym memberships."""
        request = self.factory.post("/")
        request.user = self.member

        permission = CanCreateGymMembership()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    # CanManageGymMembership

    def test_manage_membership_allows_superuser(self):
        """Allow superusers to manage gym memberships."""
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
        """Allow gym owners to manage memberships."""
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
        """Allow gym managers to manage memberships."""
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
        """Deny staff members from managing gym memberships."""
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
        """Deny trainers from managing gym memberships."""
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
        """Deny members from managing their own or other memberships."""
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
        """Deny users from managing memberships belonging to another gym."""
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