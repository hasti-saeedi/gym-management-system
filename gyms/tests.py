from decimal import Decimal

from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase
from rest_framework.exceptions import (
    NotFound,
    ValidationError as DRFValidationError,
)

from accounts.models import CustomUser
from gyms.models import Gym, GymMembership
from gyms.services.gym_membership_services import (
    activate_staff,
    add_staff,
    can_assign_role,
    can_manage_membership,
    deactivate_staff,
    get_gym_staff,
    update_membership,
)


class GymMembershipModelTest(TestCase):
    """Test cases for the GymMembership model."""

    def setUp(self):
        """Create common test data."""

        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="Test1234",
        )

        self.gym = Gym.objects.create(
            name="Test Gym",
            address="Test Address",
        )

    def test_create_owner_with_valid_share_percentage(self):
        """An owner can have a valid share percentage."""

        membership = GymMembership(
            user=self.user,
            gym=self.gym,
            role=GymMembership.Role.OWNER,
            share_percentage=Decimal("50.00"),
        )

        membership.full_clean()

        self.assertEqual(
            membership.role,
            GymMembership.Role.OWNER,
        )

        self.assertEqual(
            membership.share_percentage,
            Decimal("50.00"),
        )

    def test_owner_requires_share_percentage(self):
        """An owner must have a share percentage."""

        membership = GymMembership(
            user=self.user,
            gym=self.gym,
            role=GymMembership.Role.OWNER,
        )

        with self.assertRaises(DjangoValidationError):
            membership.full_clean()

    def test_owner_share_percentage_cannot_be_zero(self):
        """An owner's share percentage cannot be zero."""

        membership = GymMembership(
            user=self.user,
            gym=self.gym,
            role=GymMembership.Role.OWNER,
            share_percentage=Decimal("0.00"),
        )

        with self.assertRaises(DjangoValidationError):
            membership.full_clean()

    def test_owner_share_percentage_cannot_exceed_100(self):
        """An owner's share percentage cannot exceed 100."""

        membership = GymMembership(
            user=self.user,
            gym=self.gym,
            role=GymMembership.Role.OWNER,
            share_percentage=Decimal("100.01"),
        )

        with self.assertRaises(DjangoValidationError):
            membership.full_clean()

    def test_member_cannot_have_salary(self):
        """A member cannot have a salary."""

        membership = GymMembership(
            user=self.user,
            gym=self.gym,
            role=GymMembership.Role.MEMBER,
            salary=Decimal("1000.00"),
        )

        with self.assertRaises(DjangoValidationError):
            membership.full_clean()

    def test_member_cannot_have_share_percentage(self):
        """A member cannot have a share percentage."""

        membership = GymMembership(
            user=self.user,
            gym=self.gym,
            role=GymMembership.Role.MEMBER,
            share_percentage=Decimal("10.00"),
        )

        with self.assertRaises(DjangoValidationError):
            membership.full_clean()

    def test_member_with_no_salary_or_share_is_valid(self):
        """A member without salary or share percentage is valid."""

        membership = GymMembership(
            user=self.user,
            gym=self.gym,
            role=GymMembership.Role.MEMBER,
        )

        membership.full_clean()

        self.assertEqual(
            membership.role,
            GymMembership.Role.MEMBER,
        )

    def test_staff_requires_salary(self):
        """A staff member must have a salary."""

        membership = GymMembership(
            user=self.user,
            gym=self.gym,
            role=GymMembership.Role.STAFF,
        )

        with self.assertRaises(DjangoValidationError):
            membership.full_clean()

    def test_staff_with_salary_is_valid(self):
        """A staff member with a valid salary is valid."""

        membership = GymMembership(
            user=self.user,
            gym=self.gym,
            role=GymMembership.Role.STAFF,
            salary=Decimal("10000.00"),
        )

        membership.full_clean()

        self.assertEqual(
            membership.salary,
            Decimal("10000.00"),
        )

    def test_salary_cannot_be_zero(self):
        """Salary cannot be zero."""

        membership = GymMembership(
            user=self.user,
            gym=self.gym,
            role=GymMembership.Role.TRAINER,
            salary=Decimal("0.00"),
        )

        with self.assertRaises(DjangoValidationError):
            membership.full_clean()

    def test_salary_cannot_be_negative(self):
        """Salary cannot be negative."""

        membership = GymMembership(
            user=self.user,
            gym=self.gym,
            role=GymMembership.Role.TRAINER,
            salary=Decimal("-100.00"),
        )

        with self.assertRaises(DjangoValidationError):
            membership.full_clean()

    def test_non_owner_cannot_have_share_percentage(self):
        """Only owners can have a share percentage."""

        membership = GymMembership(
            user=self.user,
            gym=self.gym,
            role=GymMembership.Role.MANAGER,
            salary=Decimal("10000.00"),
            share_percentage=Decimal("20.00"),
        )

        with self.assertRaises(DjangoValidationError):
            membership.full_clean()

    def test_membership_str(self):
        """Membership string representation should contain user, gym, and role."""

        membership = GymMembership(
            user=self.user,
            gym=self.gym,
            role=GymMembership.Role.MEMBER,
        )

        self.assertEqual(
            str(membership),
            "testuser - Test Gym - member",
        )


class GymMembershipHelpersTest(TestCase):
    """Test cases for GymMembership helper functions."""

    def setUp(self):
        """Create common users, gym, and memberships."""

        self.gym = Gym.objects.create(
            name="Test Gym",
            address="Test Address",
        )

        self.owner = CustomUser.objects.create_user(
            username="owner",
            password="Test1234",
        )

        self.manager = CustomUser.objects.create_user(
            username="manager",
            password="Test1234",
        )

        self.member = CustomUser.objects.create_user(
            username="member",
            password="Test1234",
        )

        self.owner_membership = GymMembership.objects.create(
            user=self.owner,
            gym=self.gym,
            role=GymMembership.Role.OWNER,
            share_percentage=50,
        )

        self.manager_membership = GymMembership.objects.create(
            user=self.manager,
            gym=self.gym,
            role=GymMembership.Role.MANAGER,
            salary=10000,
        )

        self.member_membership = GymMembership.objects.create(
            user=self.member,
            gym=self.gym,
            role=GymMembership.Role.MEMBER,
        )

    def test_owner_can_manage_manager(self):
        """An owner can manage a manager membership."""

        result = can_manage_membership(
            self.owner,
            self.manager_membership,
        )

        self.assertTrue(result)

    def test_manager_can_manage_member(self):
        """A manager can manage a member membership."""

        result = can_manage_membership(
            self.manager,
            self.member_membership,
        )

        self.assertTrue(result)

    def test_owner_cannot_manage_owner(self):
        """An owner cannot manage another owner."""

        another_owner = CustomUser.objects.create_user(
            username="owner2",
            password="Test1234",
        )

        another_owner_membership = GymMembership.objects.create(
            user=another_owner,
            gym=self.gym,
            role=GymMembership.Role.OWNER,
            share_percentage=50,
        )

        with self.assertRaises(DRFValidationError):
            can_manage_membership(
                self.owner,
                another_owner_membership,
            )

    def test_member_cannot_manage_member(self):
        """A member cannot manage another membership."""

        with self.assertRaises(DRFValidationError):
            can_manage_membership(
                self.member,
                self.member_membership,
            )

    def test_owner_can_assign_member_role(self):
        """An owner can assign the member role."""

        result = can_assign_role(
            self.owner,
            self.member_membership,
            GymMembership.Role.MEMBER,
        )

        self.assertTrue(result)

    def test_owner_cannot_assign_owner_role(self):
        """An owner cannot assign the owner role."""

        with self.assertRaises(DRFValidationError):
            can_assign_role(
                self.owner,
                self.member_membership,
                GymMembership.Role.OWNER,
            )

    def test_manager_can_assign_staff_role(self):
        """A manager can assign the staff role."""

        result = can_assign_role(
            self.manager,
            self.member_membership,
            GymMembership.Role.STAFF,
        )

        self.assertTrue(result)

    def test_manager_can_assign_trainer_role(self):
        """A manager can assign the trainer role."""

        result = can_assign_role(
            self.manager,
            self.member_membership,
            GymMembership.Role.TRAINER,
        )

        self.assertTrue(result)

    def test_manager_cannot_assign_owner_role(self):
        """A manager cannot assign the owner role."""

        with self.assertRaises(DRFValidationError):
            can_assign_role(
                self.manager,
                self.member_membership,
                GymMembership.Role.OWNER,
            )

    def test_member_cannot_assign_role(self):
        """A member cannot assign roles."""

        with self.assertRaises(DRFValidationError):
            can_assign_role(
                self.member,
                self.member_membership,
                GymMembership.Role.STAFF,
            )

    def test_non_member_cannot_assign_role(self):
        """A user without gym membership cannot assign roles."""

        outsider = CustomUser.objects.create_user(
            username="outsider",
            password="Test1234",
        )

        with self.assertRaises(DRFValidationError):
            can_assign_role(
                outsider,
                self.member_membership,
                GymMembership.Role.STAFF,
            )

    def test_superuser_can_assign_any_role(self):
        """A superuser can assign any role."""

        superuser = CustomUser.objects.create_superuser(
            username="admin",
            password="Test1234",
        )

        result = can_assign_role(
            superuser,
            self.member_membership,
            GymMembership.Role.OWNER,
        )

        self.assertTrue(result)


class GymMembershipServicesTest(TestCase):
    """Test cases for GymMembership service functions."""

    def setUp(self):
        """Create common users, gym, and memberships."""

        self.gym = Gym.objects.create(
            name="Test Gym",
            address="Test Address",
        )

        self.owner = CustomUser.objects.create_user(
            username="owner",
            password="Test1234",
        )

        self.manager = CustomUser.objects.create_user(
            username="manager",
            password="Test1234",
        )

        self.member = CustomUser.objects.create_user(
            username="member",
            password="Test1234",
        )

        self.new_user = CustomUser.objects.create_user(
            username="newuser",
            password="Test1234",
        )

        self.owner_membership = GymMembership.objects.create(
            user=self.owner,
            gym=self.gym,
            role=GymMembership.Role.OWNER,
            share_percentage=50,
        )

        self.manager_membership = GymMembership.objects.create(
            user=self.manager,
            gym=self.gym,
            role=GymMembership.Role.MANAGER,
            salary=10000,
        )

        self.member_membership = GymMembership.objects.create(
            user=self.member,
            gym=self.gym,
            role=GymMembership.Role.MEMBER,
        )

    def test_owner_can_add_staff(self):
        """An owner can add a staff member."""

        membership = add_staff(
            actor=self.owner,
            gym_id=self.gym.id,
            user_id=self.new_user.id,
            role=GymMembership.Role.STAFF,
            salary=5000,
        )

        self.assertEqual(
            membership.user,
            self.new_user,
        )

        self.assertEqual(
            membership.role,
            GymMembership.Role.STAFF,
        )

    def test_manager_can_add_member(self):
        """A manager can add a member."""

        membership = add_staff(
            actor=self.manager,
            gym_id=self.gym.id,
            user_id=self.new_user.id,
            role=GymMembership.Role.MEMBER,
            salary=None,
        )

        self.assertEqual(
            membership.role,
            GymMembership.Role.MEMBER,
        )

    def test_owner_cannot_add_owner(self):
        """An owner cannot add another owner."""

        with self.assertRaises(DRFValidationError):
            add_staff(
                actor=self.owner,
                gym_id=self.gym.id,
                user_id=self.new_user.id,
                role=GymMembership.Role.OWNER,
                salary=None,
                share_percentage=50,
            )

    def test_manager_cannot_add_manager(self):
        """A manager cannot add another manager."""

        with self.assertRaises(DRFValidationError):
            add_staff(
                actor=self.manager,
                gym_id=self.gym.id,
                user_id=self.new_user.id,
                role=GymMembership.Role.MANAGER,
                salary=10000,
            )

    def test_member_cannot_add_staff(self):
        """A member cannot add staff."""

        with self.assertRaises(DRFValidationError):
            add_staff(
                actor=self.member,
                gym_id=self.gym.id,
                user_id=self.new_user.id,
                role=GymMembership.Role.STAFF,
                salary=5000,
            )

    def test_cannot_add_duplicate_active_role(self):
        """A user cannot have duplicate active memberships for the same role."""

        with self.assertRaises(DRFValidationError):
            add_staff(
                actor=self.owner,
                gym_id=self.gym.id,
                user_id=self.manager.id,
                role=GymMembership.Role.MANAGER,
                salary=10000,
            )

    def test_get_gym_staff_returns_non_members(self):
        """Get gym staff should return non-member memberships."""

        result = get_gym_staff(self.gym.id)

        self.assertEqual(
            result.count(),
            2,
        )

        self.assertIn(
            self.owner_membership,
            result,
        )

        self.assertIn(
            self.manager_membership,
            result,
        )

        self.assertNotIn(
            self.member_membership,
            result,
        )

    def test_get_gym_staff_raises_when_no_staff_exists(self):
        """Getting staff should raise NotFound when no staff exists."""

        GymMembership.objects.all().delete()

        with self.assertRaises(NotFound):
            get_gym_staff(self.gym.id)

    def test_owner_can_update_manager_role(self):
        """An owner can update a manager's role."""

        updated = update_membership(
            actor=self.owner,
            membership_id=self.manager_membership.id,
            role=GymMembership.Role.STAFF,
        )

        self.assertEqual(
            updated.role,
            GymMembership.Role.STAFF,
        )

    def test_manager_can_update_member_role(self):
        """A manager can update a member's role and salary."""

        updated = update_membership(
            actor=self.manager,
            membership_id=self.member_membership.id,
            role=GymMembership.Role.STAFF,
            salary=5000,
        )

        self.assertEqual(
            updated.role,
            GymMembership.Role.STAFF,
        )

        self.assertEqual(
            updated.salary,
            5000,
        )

    def test_member_cannot_update_membership(self):
        """A member cannot update a membership."""

        with self.assertRaises(DRFValidationError):
            update_membership(
                actor=self.member,
                membership_id=self.member_membership.id,
                role=GymMembership.Role.STAFF,
            )

    def test_owner_cannot_change_role_to_owner(self):
        """An owner cannot change another membership's role to owner."""

        with self.assertRaises(DRFValidationError):
            update_membership(
                actor=self.owner,
                membership_id=self.manager_membership.id,
                role=GymMembership.Role.OWNER,
            )

    def test_owner_can_deactivate_manager(self):
        """An owner can deactivate a manager."""

        result = deactivate_staff(
            actor=self.owner,
            membership_id=self.manager_membership.id,
        )

        self.assertFalse(result.is_active)

        self.manager_membership.refresh_from_db()

        self.assertFalse(
            self.manager_membership.is_active,
        )

    def test_manager_can_deactivate_member(self):
        """A manager can deactivate a member."""

        result = deactivate_staff(
            actor=self.manager,
            membership_id=self.member_membership.id,
        )

        self.assertFalse(
            result.is_active,
        )

    def test_member_cannot_deactivate_membership(self):
        """A member cannot deactivate a membership."""

        with self.assertRaises(DRFValidationError):
            deactivate_staff(
                actor=self.member,
                membership_id=self.member_membership.id,
            )

    def test_cannot_deactivate_already_inactive_membership(self):
        """An inactive membership cannot be deactivated again."""

        self.manager_membership.is_active = False
        self.manager_membership.save()

        with self.assertRaises(DRFValidationError):
            deactivate_staff(
                actor=self.owner,
                membership_id=self.manager_membership.id,
            )

    def test_owner_can_activate_manager(self):
        """An owner can activate an inactive manager membership."""

        self.manager_membership.is_active = False
        self.manager_membership.save()

        result = activate_staff(
            actor=self.owner,
            membership_id=self.manager_membership.id,
        )

        self.assertTrue(
            result.is_active,
        )

        self.manager_membership.refresh_from_db()

        self.assertTrue(
            self.manager_membership.is_active,
        )

    def test_manager_can_activate_member(self):
        """A manager can activate an inactive member membership."""

        self.member_membership.is_active = False
        self.member_membership.save()

        result = activate_staff(
            actor=self.manager,
            membership_id=self.member_membership.id,
        )

        self.assertTrue(
            result.is_active,
        )

    def test_member_cannot_activate_membership(self):
        """A member cannot activate a membership."""

        self.member_membership.is_active = False
        self.member_membership.save()

        with self.assertRaises(DRFValidationError):
            activate_staff(
                actor=self.member,
                membership_id=self.member_membership.id,
            )

    def test_cannot_activate_already_active_membership(self):
        """An active membership cannot be activated again."""

        with self.assertRaises(DRFValidationError):
            activate_staff(
                actor=self.owner,
                membership_id=self.manager_membership.id,
            )


class GymModelTest(TestCase):
    """Test cases for the Gym model."""

    def test_create_gym(self):
        """A gym can be created with valid data."""

        gym = Gym.objects.create(
            name="Test Gym",
            address="Test Address",
        )

        self.assertEqual(
            gym.name,
            "Test Gym",
        )

        self.assertEqual(
            gym.address,
            "Test Address",
        )

    def test_gym_str(self):
        """Gym string representation should contain its name and status."""

        gym = Gym.objects.create(
            name="Test Gym",
            address="Test Address",
        )

        self.assertEqual(
            str(gym),
            "Test Gym - is active=True",
        )

    def test_gym_is_active_by_default(self):
        """A gym should be active by default."""

        gym = Gym.objects.create(
            name="Test Gym",
            address="Test Address",
        )

        self.assertTrue(
            gym.is_active,
        )

    def test_gym_can_be_deactivated(self):
        """A gym can be created as inactive."""

        gym = Gym.objects.create(
            name="Test Gym",
            address="Test Address",
            is_active=False,
        )

        self.assertFalse(
            gym.is_active,
        )

    def test_valid_mobile_phone(self):
        """A valid Iranian mobile phone number should pass validation."""

        gym = Gym(
            name="Test Gym",
            address="Test Address",
            phone="09123456789",
        )

        gym.full_clean()

        self.assertEqual(
            gym.phone,
            "09123456789",
        )

    def test_valid_landline_phone(self):
        """A valid Iranian landline phone number should pass validation."""

        gym = Gym(
            name="Test Gym",
            address="Test Address",
            phone="02112345678",
        )

        gym.full_clean()

        self.assertEqual(
            gym.phone,
            "02112345678",
        )

    def test_invalid_phone(self):
        """An invalid phone number should raise a validation error."""

        gym = Gym(
            name="Test Gym",
            address="Test Address",
            phone="123456789",
        )

        with self.assertRaises(DjangoValidationError):
            gym.full_clean()

    def test_duplicate_phone(self):
        """A duplicate phone number should raise a validation error."""

        Gym.objects.create(
            name="Gym One",
            address="Address One",
            phone="09123456789",
        )

        gym = Gym(
            name="Gym Two",
            address="Address Two",
            phone="09123456789",
        )

        with self.assertRaises(DjangoValidationError):
            gym.full_clean()

    def test_valid_email(self):
        """A valid email address should pass validation."""

        gym = Gym(
            name="Test Gym",
            address="Test Address",
            email="testgym@example.com",
        )

        gym.full_clean()

        self.assertEqual(
            gym.email,
            "testgym@example.com",
        )

    def test_invalid_email(self):
        """An invalid email address should raise a validation error."""

        gym = Gym(
            name="Test Gym",
            address="Test Address",
            email="invalid-email",
        )

        with self.assertRaises(DjangoValidationError):
            gym.full_clean()

    def test_duplicate_email(self):
        """A duplicate email address should raise a validation error."""

        Gym.objects.create(
            name="Gym One",
            address="Address One",
            email="gym@example.com",
        )

        gym = Gym(
            name="Gym Two",
            address="Address Two",
            email="gym@example.com",
        )

        with self.assertRaises(DjangoValidationError):
            gym.full_clean()