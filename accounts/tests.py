from decimal import Decimal
from unittest.mock import patch

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.test import TestCase
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import CustomUser
from accounts.services.authentication_services import (
    login_service,
    logout_service,
)
from accounts.services.user_services import (
    create_gym_user,
    register_member,
    update_current_user,
)
from gyms.models import Gym, GymMembership


class CustomUserModelTest(TestCase):
    """Test the behavior and validation of the CustomUser model."""

    def test_create_user(self):
        """Test that a user can be created with valid credentials."""
        user = CustomUser.objects.create_user(
            username="testuser",
            password="Test1234",
            phone="09123456789",
        )

        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.phone, "09123456789")

    def test_password_is_hashed(self):
        """Test that the user's password is stored as a hash."""
        user = CustomUser.objects.create_user(
            username="testuser",
            password="Test1234",
        )

        self.assertNotEqual(user.password, "Test1234")
        self.assertTrue(user.check_password("Test1234"))

    def test_user_str_returns_full_name(self):
        """Test that the string representation returns the user's full name."""
        user = CustomUser.objects.create_user(
            username="testuser",
            password="Test1234",
            first_name="Hasti",
            last_name="Saeedi",
        )

        self.assertEqual(str(user), "Hasti Saeedi")

    def test_user_str_returns_username_when_name_is_empty(self):
        """Test that the username is returned when the full name is empty."""
        user = CustomUser.objects.create_user(
            username="testuser",
            password="Test1234",
        )

        self.assertEqual(str(user), "testuser")

    def test_valid_phone_number(self):
        """Test that a valid phone number passes model validation."""
        user = CustomUser(
            username="testuser",
            password="Test1234",
            phone="09123456789",
        )

        user.full_clean()

        self.assertEqual(user.phone, "09123456789")

    def test_invalid_phone_number(self):
        """Test that an invalid phone number raises a validation error."""
        user = CustomUser(
            username="testuser",
            password="Test1234",
            phone="123456789",
        )

        with self.assertRaises(DjangoValidationError):
            user.full_clean()

    def test_phone_number_must_be_unique(self):
        """Test that duplicate phone numbers are rejected."""
        CustomUser.objects.create_user(
            username="user1",
            password="Test1234",
            phone="09123456789",
        )

        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                username="user2",
                password="Test1234",
                phone="09123456789",
            )


class AccountsServicesTest(TestCase):
    """Test authentication and user management services."""

    def setUp(self):
        """Set up users, a gym, and gym membership data for service tests."""
        self.user = CustomUser.objects.create_user(
            username="hasti",
            password="Test1234",
            first_name="Hasti",
            last_name="Saeedi",
            email="hasti@example.com",
        )

        self.creator = CustomUser.objects.create_user(
            username="creator",
            password="Test1234",
        )

        self.gym = Gym.objects.create(
            name="Test Gym",
            address="Test Address",
        )

        GymMembership.objects.create(
            user=self.creator,
            gym=self.gym,
            role=GymMembership.Role.MANAGER,
            salary=Decimal("15000.00"),
        )

    def test_login_service_success(self):
        """Test that valid credentials return user and authentication tokens."""
        result = login_service(
            "hasti",
            "Test1234",
        )

        self.assertEqual(result["user"], self.user)
        self.assertIn("access", result)
        self.assertIn("refresh", result)
        self.assertTrue(result["access"])
        self.assertTrue(result["refresh"])

    def test_login_service_invalid_username(self):
        """Test that an invalid username raises an authentication error."""
        with self.assertRaises(AuthenticationFailed):
            login_service(
                "wrong_username",
                "Test1234",
            )

    def test_login_service_invalid_password(self):
        """Test that an invalid password raises an authentication error."""
        with self.assertRaises(AuthenticationFailed):
            login_service(
                "hasti",
                "WrongPassword",
            )

    def test_logout_service_success(self):
        """Test that a valid refresh token can be used to log out."""
        refresh = RefreshToken.for_user(self.user)
        refresh_token = str(refresh)

        result = logout_service(refresh_token)

        self.assertIsNone(result)

    def test_logout_service_invalid_token(self):
        """Test that an invalid refresh token raises a validation error."""
        with self.assertRaises(DRFValidationError):
            logout_service("invalid-refresh-token")

    def test_update_current_user(self):
        """Test that the current user's profile can be updated."""
        result = update_current_user(
            user=self.user,
            validated_data={
                "first_name": "NewFirstName",
                "last_name": "NewLastName",
                "email": "new@example.com",
            },
        )

        self.assertEqual(result, self.user)

        self.user.refresh_from_db()

        self.assertEqual(self.user.first_name, "NewFirstName")
        self.assertEqual(self.user.last_name, "NewLastName")
        self.assertEqual(self.user.email, "new@example.com")

    def test_update_current_user_partial_update(self):
        """Test that only provided profile fields are updated."""
        result = update_current_user(
            user=self.user,
            validated_data={
                "first_name": "NewFirstName",
            },
        )

        self.assertEqual(result.first_name, "NewFirstName")
        self.assertEqual(result.last_name, "Saeedi")
        self.assertEqual(result.email, "hasti@example.com")

        self.user.refresh_from_db()

        self.assertEqual(self.user.first_name, "NewFirstName")
        self.assertEqual(self.user.last_name, "Saeedi")
        self.assertEqual(self.user.email, "hasti@example.com")

    def test_register_member_success(self):
        """Test that a new member is registered successfully."""
        result = register_member(
            validated_data={
                "username": "newmember",
                "password": "Test1234",
                "password2": "Test1234",
                "first_name": "New",
                "last_name": "Member",
                "email": "member@example.com",
                "gym": self.gym,
            }
        )

        self.assertIsInstance(result, CustomUser)
        self.assertEqual(result.username, "newmember")
        self.assertTrue(result.check_password("Test1234"))

        self.assertTrue(
            GymMembership.objects.filter(
                user=result,
                gym=self.gym,
                role=GymMembership.Role.MEMBER,
            ).exists()
        )

    def test_register_member_creates_only_member_role(self):
        """Test that public registration creates only a member role."""
        user = register_member(
            validated_data={
                "username": "member2",
                "password": "Test1234",
                "password2": "Test1234",
                "first_name": "Member",
                "last_name": "Two",
                "email": "member2@example.com",
                "gym": self.gym,
            }
        )

        membership = GymMembership.objects.get(
            user=user,
            gym=self.gym,
        )

        self.assertEqual(
            membership.role,
            GymMembership.Role.MEMBER,
        )

    def test_create_gym_user_success(self):
        """Test that a gym user is created with the specified role and salary."""
        result = create_gym_user(
            creator=self.creator,
            gym=self.gym,
            validated_data={
                "username": "trainer1",
                "password": "Test1234",
                "password2": "Test1234",
                "first_name": "Trainer",
                "last_name": "One",
                "email": "trainer@example.com",
                "role": GymMembership.Role.TRAINER,
                "salary": Decimal("10000.00"),
            },
        )

        self.assertIsInstance(result, CustomUser)
        self.assertEqual(result.username, "trainer1")
        self.assertTrue(result.check_password("Test1234"))

        membership = GymMembership.objects.get(
            user=result,
            gym=self.gym,
        )

        self.assertEqual(
            membership.role,
            GymMembership.Role.TRAINER,
        )
        self.assertEqual(
            membership.salary,
            Decimal("10000.00"),
        )

    def test_create_gym_user_with_share_percentage(self):
        """Test that a gym user can be created with a share percentage."""
        result = create_gym_user(
            creator=self.creator,
            gym=self.gym,
            validated_data={
                "username": "owner1",
                "password": "Test1234",
                "password2": "Test1234",
                "first_name": "Owner",
                "last_name": "One",
                "email": "owner@example.com",
                "role": GymMembership.Role.OWNER,
                "share_percentage": Decimal("20.00"),
            },
        )

        self.assertIsInstance(result, CustomUser)

        membership = GymMembership.objects.get(
            user=result,
            gym=self.gym,
        )

        self.assertEqual(
            membership.role,
            GymMembership.Role.OWNER,
        )
        self.assertEqual(
            membership.share_percentage,
            Decimal("20.00"),
        )

    def test_create_gym_user_staff_with_salary(self):
        """Test that a staff user can be created with a salary."""
        result = create_gym_user(
            creator=self.creator,
            gym=self.gym,
            validated_data={
                "username": "staff1",
                "password": "Test1234",
                "password2": "Test1234",
                "first_name": "Staff",
                "last_name": "One",
                "email": "staff@example.com",
                "role": GymMembership.Role.STAFF,
                "salary": Decimal("10000.00"),
            },
        )

        self.assertIsInstance(result, CustomUser)

        membership = GymMembership.objects.get(
            user=result,
            gym=self.gym,
        )

        self.assertEqual(
            membership.role,
            GymMembership.Role.STAFF,
        )
        self.assertEqual(
            membership.salary,
            Decimal("10000.00"),
        )

    def test_register_member_rolls_back_user_when_membership_fails(self):
        """
        Test that user creation is rolled back when membership creation fails.
        """
        initial_user_count = CustomUser.objects.count()

        with patch(
            "accounts.services.user_services.GymMembership.save"
        ) as mock_save:
            mock_save.side_effect = DjangoValidationError(
                {
                    "gym": [
                        "Membership creation failed.",
                    ]
                }
            )

            with self.assertRaises(DRFValidationError):
                register_member(
                    validated_data={
                        "username": "invalidmember",
                        "password": "Test1234",
                        "password2": "Test1234",
                        "first_name": "Invalid",
                        "last_name": "Member",
                        "email": "invalid@example.com",
                        "gym": self.gym,
                    }
                )

        self.assertEqual(
            CustomUser.objects.count(),
            initial_user_count,
        )

        self.assertFalse(
            CustomUser.objects.filter(
                username="invalidmember",
            ).exists()
        )