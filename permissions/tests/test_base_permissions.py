from django.test import TestCase
from rest_framework.test import APIRequestFactory

from accounts.models import CustomUser
from gyms.models import Gym

from permissions.base_permissions import (
    IsAnonymous,
    AuthenticatedPermission,
    GymPermission,
)


class BasePermissionsTestCase(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="Test1234",
        )

        self.superuser = CustomUser.objects.create_superuser(
            username="superuser",
            password="Test1234",
        )

        self.gym = Gym.objects.create(
            name="Test Gym",
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

    # =========================================================
    # IsAnonymous
    # =========================================================

    def test_is_anonymous_allows_unauthenticated_user(self):
        request = self.factory.get("/")

        request.user = type(
            "AnonymousUser",
            (),
            {
                "is_authenticated": False,
            },
        )()

        permission = IsAnonymous()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_is_anonymous_denies_authenticated_user(self):
        request = self.factory.get("/")
        request.user = self.user

        permission = IsAnonymous()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    # =========================================================
    # AuthenticatedPermission
    # =========================================================

    def test_authenticated_permission_allows_authenticated_user(self):
        request = self.factory.get("/")
        request.user = self.user

        permission = AuthenticatedPermission()

        self.assertTrue(
            permission.has_permission(
                request,
                self.view,
            )
        )

    def test_authenticated_permission_denies_unauthenticated_user(self):
        request = self.factory.get("/")

        request.user = type(
            "AnonymousUser",
            (),
            {
                "is_authenticated": False,
            },
        )()

        permission = AuthenticatedPermission()

        self.assertFalse(
            permission.has_permission(
                request,
                self.view,
            )
        )

    # =========================================================
    # GymPermission - get_gym
    # =========================================================

    def test_get_gym_returns_correct_gym(self):
        permission = GymPermission()

        result = permission.get_gym(
            self.view
        )

        self.assertEqual(
            result,
            self.gym,
        )

    def test_get_gym_raises_404_for_invalid_gym_id(self):
        permission = GymPermission()

        self.view.kwargs["gym_id"] = 999999

        with self.assertRaises(Exception) as context:
            permission.get_gym(
                self.view
            )

        self.assertEqual(
            context.exception.__class__.__name__,
            "Http404",
        )

    # =========================================================
    # GymPermission - is_superuser
    # =========================================================

    def test_is_superuser_returns_true_for_superuser(self):
        request = self.factory.get("/")
        request.user = self.superuser

        permission = GymPermission()

        self.assertTrue(
            permission.is_superuser(
                request
            )
        )

    def test_is_superuser_returns_false_for_normal_user(self):
        request = self.factory.get("/")
        request.user = self.user

        permission = GymPermission()

        self.assertFalse(
            permission.is_superuser(
                request
            )
        )

    def test_is_superuser_returns_false_for_unauthenticated_user(self):
        request = self.factory.get("/")

        request.user = type(
            "AnonymousUser",
            (),
            {
                "is_authenticated": False,
                "is_superuser": False,
            },
        )()

        permission = GymPermission()

        self.assertFalse(
            permission.is_superuser(
                request
            )
        )