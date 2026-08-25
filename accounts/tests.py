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
    update_current_user,
    register_member,
    create_gym_user,
)

from gyms.models import (
    Gym,
    GymMembership,
)


# =========================================================
# CustomUser Model Tests
# =========================================================

class CustomUserModelTest(TestCase):

    def test_create_user(self):

        user = CustomUser.objects.create_user(
            username="testuser",
            password="Test1234",
            phone="09123456789",
        )

        self.assertEqual(
            user.username,
            "testuser",
        )

        self.assertEqual(
            user.phone,
            "09123456789",
        )

    def test_password_is_hashed(self):

        user = CustomUser.objects.create_user(
            username="testuser",
            password="Test1234",
        )

        self.assertNotEqual(
            user.password,
            "Test1234",
        )

        self.assertTrue(
            user.check_password("Test1234")
        )

    def test_user_str_returns_full_name(self):

        user = CustomUser.objects.create_user(
            username="testuser",
            password="Test1234",
            first_name="Hasti",
            last_name="Saeedi",
        )

        self.assertEqual(
            str(user),
            "Hasti Saeedi",
        )

    def test_user_str_returns_username_when_name_is_empty(self):

        user = CustomUser.objects.create_user(
            username="testuser",
            password="Test1234",
        )

        self.assertEqual(
            str(user),
            "testuser",
        )

    def test_valid_phone_number(self):

        user = CustomUser(
            username="testuser",
            password="Test1234",
            phone="09123456789",
        )

        user.full_clean()

        self.assertEqual(
            user.phone,
            "09123456789",
        )

    def test_invalid_phone_number(self):

        user = CustomUser(
            username="testuser",
            password="Test1234",
            phone="123456789",
        )

        with self.assertRaises(DjangoValidationError):
            user.full_clean()

    def test_phone_number_must_be_unique(self):

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


# =========================================================
# Accounts Services Tests
# =========================================================

class AccountsServicesTest(TestCase):

    def setUp(self):

        # =========================
        # Users
        # =========================

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

        # =========================
        # Gym
        # =========================

        self.gym = Gym.objects.create(
            name="Test Gym",
            address="Test Address",
        )

        # Manager must have salary
        GymMembership.objects.create(
            user=self.creator,
            gym=self.gym,
            role=GymMembership.Role.MANAGER,
            salary=Decimal("15000.00"),
        )

    # =====================================================
    # login_service
    # =====================================================

    def test_login_service_success(self):

        result = login_service(
            "hasti",
            "Test1234",
        )

        self.assertEqual(
            result["user"],
            self.user,
        )

        self.assertIn(
            "access",
            result,
        )

        self.assertIn(
            "refresh",
            result,
        )

        self.assertTrue(
            result["access"],
        )

        self.assertTrue(
            result["refresh"],
        )

    def test_login_service_invalid_username(self):

        with self.assertRaises(AuthenticationFailed):

            login_service(
                "wrong_username",
                "Test1234",
            )

    def test_login_service_invalid_password(self):

        with self.assertRaises(AuthenticationFailed):

            login_service(
                "hasti",
                "WrongPassword",
            )

    # =====================================================
    # logout_service
    # =====================================================

    def test_logout_service_success(self):

        refresh = RefreshToken.for_user(
            self.user
        )

        refresh_token = str(refresh)

        result = logout_service(
            refresh_token
        )

        self.assertIsNone(
            result
        )

    def test_logout_service_invalid_token(self):

        with self.assertRaises(DRFValidationError):

            logout_service(
                "invalid-refresh-token"
            )

    # =====================================================
    # update_current_user
    # =====================================================

    def test_update_current_user(self):

        result = update_current_user(
            user=self.user,
            validated_data={
                "first_name": "NewFirstName",
                "last_name": "NewLastName",
                "email": "new@example.com",
            },
        )

        self.assertEqual(
            result,
            self.user,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.first_name,
            "NewFirstName",
        )

        self.assertEqual(
            self.user.last_name,
            "NewLastName",
        )

        self.assertEqual(
            self.user.email,
            "new@example.com",
        )

    def test_update_current_user_partial_update(self):

        result = update_current_user(
            user=self.user,
            validated_data={
                "first_name": "NewFirstName",
            },
        )

        self.assertEqual(
            result.first_name,
            "NewFirstName",
        )

        self.assertEqual(
            result.last_name,
            "Saeedi",
        )

        self.assertEqual(
            result.email,
            "hasti@example.com",
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.first_name,
            "NewFirstName",
        )

        self.assertEqual(
            self.user.last_name,
            "Saeedi",
        )

        self.assertEqual(
            self.user.email,
            "hasti@example.com",
        )

    # =====================================================
    # register_member
    # =====================================================

    def test_register_member_success(self):

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

        self.assertIsInstance(
            result,
            CustomUser,
        )

        self.assertEqual(
            result.username,
            "newmember",
        )

        self.assertTrue(
            result.check_password("Test1234")
        )

        self.assertTrue(
            GymMembership.objects.filter(
                user=result,
                gym=self.gym,
                role=GymMembership.Role.MEMBER,
            ).exists()
        )

    def test_register_member_creates_only_member_role(self):

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

    # =====================================================
    # create_gym_user
    # =====================================================

    def test_create_gym_user_success(self):

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

        self.assertIsInstance(
            result,
            CustomUser,
        )

        self.assertEqual(
            result.username,
            "trainer1",
        )

        self.assertTrue(
            result.check_password("Test1234")
        )

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

        self.assertIsInstance(
            result,
            CustomUser,
        )

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

        self.assertIsInstance(
            result,
            CustomUser,
        )

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

    # =====================================================
    # Transaction / Validation
    # =====================================================

    def test_register_member_rolls_back_user_when_membership_fails(self):

        initial_user_count = CustomUser.objects.count()

        with patch(
            "accounts.services.user_services.GymMembership.save"
        ) as mock_save:

            mock_save.side_effect = DjangoValidationError(
                {
                    "gym": [
                        "Membership creation failed."
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
                username="invalidmember"
            ).exists()
        )