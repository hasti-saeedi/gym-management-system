from datetime import datetime

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from accounts.models import CustomUser
from classes.models import ClassSession, GymClass
from gyms.models import Gym, GymMembership
from permissions.class_permissions import (
    CanAccessSession,
    CanCreateSession,
    CanDeleteSession,
    CanManageGymClass,
    CanRecordAttendance,
    CanViewSessionStudents,
)


class ClassPermissionsTestCase(TestCase):
    """
    Test suite for class and class-session permissions.

    Covers permissions related to:

    - Managing gym classes
    - Creating class sessions
    - Accessing class sessions
    - Deleting class sessions
    - Viewing session students
    - Recording session attendance

    The tests verify access for different gym roles,
    including Owner, Manager, Staff, Trainer, Member,
    and Superuser where applicable.
    """

    def setUp(self):
        """Create users, gym memberships, class, session, and test views."""

        self.factory = APIRequestFactory()

        # =========================================================
        # Users
        # =========================================================

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

        self.trainer = CustomUser.objects.create_user(
            username="trainer",
            password="Test1234",
        )

        self.superuser = CustomUser.objects.create_superuser(
            username="superuser",
            password="Test1234",
        )

        # =========================================================
        # Gym
        # =========================================================

        self.gym = Gym.objects.create(
            name="Test Gym",
        )

        # =========================================================
        # Gym Memberships
        # =========================================================

        GymMembership.objects.create(
            user=self.owner,
            gym=self.gym,
            role=GymMembership.Role.OWNER,
            share_percentage=100,
            salary=20,
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
            user=self.member,
            gym=self.gym,
            role=GymMembership.Role.MEMBER,
            is_active=True,
        )

        GymMembership.objects.create(
            user=self.trainer,
            gym=self.gym,
            role=GymMembership.Role.TRAINER,
            salary=20,
            is_active=True,
        )

        # =========================================================
        # Gym Class
        # =========================================================

        self.gym_class = GymClass.objects.create(
            name="Test Class",
            gym=self.gym,
            trainer=self.trainer,
            start_date="2026-08-20",
            end_date="2026-09-20",
            start_time="10:00",
            end_time="11:00",
            capacity=20,
            regular_days=["monday"],
            price=100000,
            single_session_price=20000,
        )

        # =========================================================
        # Class Session
        # =========================================================

        self.session = ClassSession.objects.create(
            gym_class=self.gym_class,
            start_time=timezone.make_aware(
                datetime(2026, 8, 20, 10, 0)
            ),
            end_time=timezone.make_aware(
                datetime(2026, 8, 20, 11, 0)
            ),
            trainer=self.trainer,
        )

        # =========================================================
        # Views
        # =========================================================

        # View containing gym_id for GymPermission-based classes.
        self.gym_view = type(
            "View",
            (),
            {
                "kwargs": {
                    "gym_id": self.gym.id,
                }
            },
        )()

        # View used by CanCreateSession.
        self.session_view = type(
            "View",
            (),
            {
                "get_gym_class": lambda view: self.gym_class,
            },
        )()

    # =========================================================
    # CanManageGymClass
    # =========================================================

    def test_manage_gym_class_allows_owner(self):
        """Owner can manage gym classes."""

        request = self.factory.get("/")
        request.user = self.owner

        permission = CanManageGymClass()

        self.assertTrue(
            permission.has_permission(
                request,
                self.gym_view,
            )
        )

    def test_manage_gym_class_allows_manager(self):
        """Manager can manage gym classes."""

        request = self.factory.get("/")
        request.user = self.manager

        permission = CanManageGymClass()

        self.assertTrue(
            permission.has_permission(
                request,
                self.gym_view,
            )
        )

    def test_manage_gym_class_allows_staff(self):
        """Staff can manage gym classes."""

        request = self.factory.get("/")
        request.user = self.staff

        permission = CanManageGymClass()

        self.assertTrue(
            permission.has_permission(
                request,
                self.gym_view,
            )
        )

    def test_manage_gym_class_denies_member(self):
        """Member cannot manage gym classes."""

        request = self.factory.get("/")
        request.user = self.member

        permission = CanManageGymClass()

        self.assertFalse(
            permission.has_permission(
                request,
                self.gym_view,
            )
        )

    def test_manage_gym_class_allows_superuser(self):
        """Superuser can manage gym classes."""

        request = self.factory.get("/")
        request.user = self.superuser

        permission = CanManageGymClass()

        self.assertTrue(
            permission.has_permission(
                request,
                self.gym_view,
            )
        )

    def test_manage_gym_class_object_permission(self):
        """Owner has object-level permission for a gym class."""

        request = self.factory.get("/")
        request.user = self.owner

        permission = CanManageGymClass()

        self.assertTrue(
            permission.has_object_permission(
                request,
                self.gym_view,
                self.gym_class,
            )
        )

    # =========================================================
    # CanCreateSession
    # =========================================================

    def test_create_session_allows_owner(self):
        """Owner can create class sessions."""

        request = self.factory.post("/")
        request.user = self.owner

        permission = CanCreateSession()

        self.assertTrue(
            permission.has_permission(
                request,
                self.session_view,
            )
        )

    def test_create_session_allows_manager(self):
        """Manager can create class sessions."""

        request = self.factory.post("/")
        request.user = self.manager

        permission = CanCreateSession()

        self.assertTrue(
            permission.has_permission(
                request,
                self.session_view,
            )
        )

    def test_create_session_allows_staff(self):
        """Staff can create class sessions."""

        request = self.factory.post("/")
        request.user = self.staff

        permission = CanCreateSession()

        self.assertTrue(
            permission.has_permission(
                request,
                self.session_view,
            )
        )

    def test_create_session_allows_trainer(self):
        """Trainer can create class sessions."""

        request = self.factory.post("/")
        request.user = self.trainer

        permission = CanCreateSession()

        self.assertTrue(
            permission.has_permission(
                request,
                self.session_view,
            )
        )

    def test_create_session_denies_member(self):
        """Member cannot create class sessions."""

        request = self.factory.post("/")
        request.user = self.member

        permission = CanCreateSession()

        self.assertFalse(
            permission.has_permission(
                request,
                self.session_view,
            )
        )

    # =========================================================
    # CanAccessSession
    # =========================================================

    def test_access_session_allows_owner(self):
        """Owner can access a class session."""

        request = self.factory.get("/")
        request.user = self.owner

        permission = CanAccessSession()

        self.assertTrue(
            permission.has_object_permission(
                request,
                None,
                self.session,
            )
        )

    def test_access_session_allows_manager(self):
        """Manager can access a class session."""

        request = self.factory.get("/")
        request.user = self.manager

        permission = CanAccessSession()

        self.assertTrue(
            permission.has_object_permission(
                request,
                None,
                self.session,
            )
        )

    def test_access_session_allows_staff(self):
        """Staff can access a class session."""

        request = self.factory.get("/")
        request.user = self.staff

        permission = CanAccessSession()

        self.assertTrue(
            permission.has_object_permission(
                request,
                None,
                self.session,
            )
        )

    def test_access_session_allows_trainer(self):
        """Trainer can access a class session."""

        request = self.factory.get("/")
        request.user = self.trainer

        permission = CanAccessSession()

        self.assertTrue(
            permission.has_object_permission(
                request,
                None,
                self.session,
            )
        )

    def test_access_session_denies_member(self):
        """Member cannot access a class session."""

        request = self.factory.get("/")
        request.user = self.member

        permission = CanAccessSession()

        self.assertFalse(
            permission.has_object_permission(
                request,
                None,
                self.session,
            )
        )

    # =========================================================
    # CanDeleteSession
    # =========================================================

    def test_delete_session_allows_owner(self):
        """Owner can delete a class session."""

        request = self.factory.delete("/")
        request.user = self.owner

        permission = CanDeleteSession()

        self.assertTrue(
            permission.has_object_permission(
                request,
                None,
                self.session,
            )
        )

    def test_delete_session_allows_manager(self):
        """Manager can delete a class session."""

        request = self.factory.delete("/")
        request.user = self.manager

        permission = CanDeleteSession()

        self.assertTrue(
            permission.has_object_permission(
                request,
                None,
                self.session,
            )
        )

    def test_delete_session_allows_staff(self):
        """Staff can delete a class session."""

        request = self.factory.delete("/")
        request.user = self.staff

        permission = CanDeleteSession()

        self.assertTrue(
            permission.has_object_permission(
                request,
                None,
                self.session,
            )
        )

    def test_delete_session_denies_member(self):
        """Member cannot delete a class session."""

        request = self.factory.delete("/")
        request.user = self.member

        permission = CanDeleteSession()

        self.assertFalse(
            permission.has_object_permission(
                request,
                None,
                self.session,
            )
        )

    # =========================================================
    # CanViewSessionStudents
    # =========================================================

    def test_view_session_students_uses_session_access(self):
        """
        Session-student access follows the session access permission.
        """

        request = self.factory.get("/")
        request.user = self.owner

        permission = CanViewSessionStudents()

        self.assertTrue(
            permission.has_object_permission(
                request,
                None,
                self.session,
            )
        )

    # =========================================================
    # CanRecordAttendance
    # =========================================================

    def test_record_attendance_uses_session_access(self):
        """
        Attendance recording follows the session access permission.
        """

        request = self.factory.patch("/")
        request.user = self.trainer

        permission = CanRecordAttendance()

        self.assertTrue(
            permission.has_object_permission(
                request,
                None,
                self.session,
            )
        )