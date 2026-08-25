# from decimal import Decimal

# from rest_framework.exceptions import ValidationError, NotFound

# from django.test import TestCase

# from accounts.models import CustomUser
# from gyms.models import Gym, GymMembership

# from gyms.models import Gym, GymMembership

# from gyms.services.gym_membership_services import (
#     can_manage_membership,
#     can_assign_role,
#     add_staff,
#     get_gym_staff,
#     update_membership,
#     deactivate_staff,
#     activate_staff,
# )

# class GymMembershipModelTest(TestCase):

#     def setUp(self):
#         self.user = CustomUser.objects.create_user(
#             username="testuser",
#             password="Test1234",
#         )

#         self.gym = Gym.objects.create(
#             name="Test Gym",
#             address="Test Address",
#         )

#     def test_create_owner_with_valid_share_percentage(self):
#         membership = GymMembership(
#             user=self.user,
#             gym=self.gym,
#             role=GymMembership.Role.OWNER,
#             share_percentage=Decimal("50.00"),
#         )

#         membership.full_clean()

#         self.assertEqual(membership.role, GymMembership.Role.OWNER)
#         self.assertEqual(
#             membership.share_percentage,
#             Decimal("50.00")
#         )

#     def test_owner_requires_share_percentage(self):
#         membership = GymMembership(
#             user=self.user,
#             gym=self.gym,
#             role=GymMembership.Role.OWNER,
#         )

#         with self.assertRaises(ValidationError):
#             membership.full_clean()

#     def test_owner_share_percentage_cannot_be_zero(self):
#         membership = GymMembership(
#             user=self.user,
#             gym=self.gym,
#             role=GymMembership.Role.OWNER,
#             share_percentage=Decimal("0.00"),
#         )

#         with self.assertRaises(ValidationError):
#             membership.full_clean()

#     def test_owner_share_percentage_cannot_exceed_100(self):
#         membership = GymMembership(
#             user=self.user,
#             gym=self.gym,
#             role=GymMembership.Role.OWNER,
#             share_percentage=Decimal("100.01"),
#         )

#         with self.assertRaises(ValidationError):
#             membership.full_clean()

#     def test_member_cannot_have_salary(self):
#         membership = GymMembership(
#             user=self.user,
#             gym=self.gym,
#             role=GymMembership.Role.MEMBER,
#             salary=Decimal("1000.00"),
#         )

#         with self.assertRaises(ValidationError):
#             membership.full_clean()

#     def test_member_cannot_have_share_percentage(self):
#         membership = GymMembership(
#             user=self.user,
#             gym=self.gym,
#             role=GymMembership.Role.MEMBER,
#             share_percentage=Decimal("10.00"),
#         )

#         with self.assertRaises(ValidationError):
#             membership.full_clean()

#     def test_member_with_no_salary_or_share_is_valid(self):
#         membership = GymMembership(
#             user=self.user,
#             gym=self.gym,
#             role=GymMembership.Role.MEMBER,
#         )

#         membership.full_clean()

#         self.assertEqual(membership.role, GymMembership.Role.MEMBER)

#     def test_staff_requires_salary(self):
#         membership = GymMembership(
#             user=self.user,
#             gym=self.gym,
#             role=GymMembership.Role.STAFF,
#         )

#         with self.assertRaises(ValidationError):
#             membership.full_clean()

#     def test_staff_with_salary_is_valid(self):
#         membership = GymMembership(
#             user=self.user,
#             gym=self.gym,
#             role=GymMembership.Role.STAFF,
#             salary=Decimal("10000.00"),
#         )

#         membership.full_clean()

#         self.assertEqual(
#             membership.salary,
#             Decimal("10000.00")
#         )

#     def test_salary_cannot_be_zero(self):
#         membership = GymMembership(
#             user=self.user,
#             gym=self.gym,
#             role=GymMembership.Role.TRAINER,
#             salary=Decimal("0.00"),
#         )

#         with self.assertRaises(ValidationError):
#             membership.full_clean()

#     def test_salary_cannot_be_negative(self):
#         membership = GymMembership(
#             user=self.user,
#             gym=self.gym,
#             role=GymMembership.Role.TRAINER,
#             salary=Decimal("-100.00"),
#         )

#         with self.assertRaises(ValidationError):
#             membership.full_clean()

#     def test_non_owner_cannot_have_share_percentage(self):
#         membership = GymMembership(
#             user=self.user,
#             gym=self.gym,
#             role=GymMembership.Role.MANAGER,
#             salary=Decimal("10000.00"),
#             share_percentage=Decimal("20.00"),
#         )

#         with self.assertRaises(ValidationError):
#             membership.full_clean()

#     def test_membership_str(self):
#         membership = GymMembership(
#             user=self.user,
#             gym=self.gym,
#             role=GymMembership.Role.MEMBER,
#         )

#         self.assertEqual(
#             str(membership),
#             "testuser - Test Gym - member"
#         )


# class GymMembershipHelpersTest(TestCase):

#     def setUp(self):
#         self.gym = Gym.objects.create(
#             name="Test Gym",
#             address="Test Address",
#         )

#         self.owner = CustomUser.objects.create_user(
#             username="owner",
#             password="Test1234",
#         )

#         self.manager = CustomUser.objects.create_user(
#             username="manager",
#             password="Test1234",
#         )

#         self.member = CustomUser.objects.create_user(
#             username="member",
#             password="Test1234",
#         )

#         self.owner_membership = GymMembership.objects.create(
#             user=self.owner,
#             gym=self.gym,
#             role=GymMembership.Role.OWNER,
#             share_percentage=50,
#         )

#         self.manager_membership = GymMembership.objects.create(
#             user=self.manager,
#             gym=self.gym,
#             role=GymMembership.Role.MANAGER,
#             salary=10000,
#         )

#         self.member_membership = GymMembership.objects.create(
#             user=self.member,
#             gym=self.gym,
#             role=GymMembership.Role.MEMBER,
#         )

#     # =====================================================
#     # can_manage_membership
#     # =====================================================

#     def test_owner_can_manage_manager(self):
#         result = can_manage_membership(
#             self.owner,
#             self.manager_membership,
#         )

#         self.assertTrue(result)

#     def test_manager_can_manage_member(self):
#         result = can_manage_membership(
#             self.manager,
#             self.member_membership,
#         )

#         self.assertTrue(result)

#     def test_owner_cannot_manage_owner(self):
#         another_owner = CustomUser.objects.create_user(
#             username="owner2",
#             password="Test1234",
#         )

#         another_owner_membership = GymMembership.objects.create(
#             user=another_owner,
#             gym=self.gym,
#             role=GymMembership.Role.OWNER,
#             share_percentage=50,
#         )

#         with self.assertRaises(ValidationError):
#             can_manage_membership(
#                 self.owner,
#                 another_owner_membership,
#             )

#     def test_member_cannot_manage_member(self):
#         with self.assertRaises(ValidationError):
#             can_manage_membership(
#                 self.member,
#                 self.member_membership,
#             )

#     # =====================================================
#     # can_assign_role
#     # =====================================================

#     def test_owner_can_assign_member_role(self):
#         result = can_assign_role(
#             self.owner,
#             self.member_membership,
#             GymMembership.Role.MEMBER,
#         )

#         self.assertTrue(result)

#     def test_owner_cannot_assign_owner_role(self):
#         with self.assertRaises(ValidationError):
#             can_assign_role(
#                 self.owner,
#                 self.member_membership,
#                 GymMembership.Role.OWNER,
#             )

#     def test_manager_can_assign_staff_role(self):
#         result = can_assign_role(
#             self.manager,
#             self.member_membership,
#             GymMembership.Role.STAFF,
#         )

#         self.assertTrue(result)

#     def test_manager_can_assign_trainer_role(self):
#         result = can_assign_role(
#             self.manager,
#             self.member_membership,
#             GymMembership.Role.TRAINER,
#         )

#         self.assertTrue(result)

#     def test_manager_cannot_assign_owner_role(self):
#         with self.assertRaises(ValidationError):
#             can_assign_role(
#                 self.manager,
#                 self.member_membership,
#                 GymMembership.Role.OWNER,
#             )

#     def test_member_cannot_assign_role(self):
#         with self.assertRaises(ValidationError):
#             can_assign_role(
#                 self.member,
#                 self.member_membership,
#                 GymMembership.Role.STAFF,
#             )

#     def test_non_member_cannot_assign_role(self):
#         outsider = CustomUser.objects.create_user(
#             username="outsider",
#             password="Test1234",
#         )

#         with self.assertRaises(ValidationError):
#             can_assign_role(
#                 outsider,
#                 self.member_membership,
#                 GymMembership.Role.STAFF,
#             )

#     def test_superuser_can_assign_any_role(self):
#         superuser = CustomUser.objects.create_superuser(
#             username="admin",
#             password="Test1234",
#         )

#         result = can_assign_role(
#             superuser,
#             self.member_membership,
#             GymMembership.Role.OWNER,
#         )

#         self.assertTrue(result)



# class GymMembershipServicesTest(TestCase):

#     def setUp(self):

#         self.gym = Gym.objects.create(
#             name="Test Gym",
#             address="Test Address",
#         )

#         self.owner = CustomUser.objects.create_user(
#             username="owner",
#             password="Test1234",
#         )

#         self.manager = CustomUser.objects.create_user(
#             username="manager",
#             password="Test1234",
#         )

#         self.member = CustomUser.objects.create_user(
#             username="member",
#             password="Test1234",
#         )

#         self.new_user = CustomUser.objects.create_user(
#             username="newuser",
#             password="Test1234",
#         )

#         self.owner_membership = GymMembership.objects.create(
#             user=self.owner,
#             gym=self.gym,
#             role=GymMembership.Role.OWNER,
#             share_percentage=50,
#         )

#         self.manager_membership = GymMembership.objects.create(
#             user=self.manager,
#             gym=self.gym,
#             role=GymMembership.Role.MANAGER,
#             salary=10000,
#         )

#         self.member_membership = GymMembership.objects.create(
#             user=self.member,
#             gym=self.gym,
#             role=GymMembership.Role.MEMBER,
#         )

#     # =====================================================
#     # add_staff
#     # =====================================================

#     def test_owner_can_add_staff(self):

#         membership = add_staff(
#             actor=self.owner,
#             gym_id=self.gym.id,
#             user_id=self.new_user.id,
#             role=GymMembership.Role.STAFF,
#             salary=5000,
#         )

#         self.assertEqual(
#             membership.user,
#             self.new_user,
#         )

#         self.assertEqual(
#             membership.role,
#             GymMembership.Role.STAFF,
#         )

#     def test_manager_can_add_member(self):

#         membership = add_staff(
#             actor=self.manager,
#             gym_id=self.gym.id,
#             user_id=self.new_user.id,
#             role=GymMembership.Role.MEMBER,
#             salary=None,
#         )

#         self.assertEqual(
#             membership.role,
#             GymMembership.Role.MEMBER,
#         )

#     def test_owner_cannot_add_owner(self):

#         with self.assertRaises(ValidationError):
#             add_staff(
#                 actor=self.owner,
#                 gym_id=self.gym.id,
#                 user_id=self.new_user.id,
#                 role=GymMembership.Role.OWNER,
#                 salary=None,
#                 share_percentage=50,
#             )

#     def test_manager_cannot_add_manager(self):

#         with self.assertRaises(ValidationError):
#             add_staff(
#                 actor=self.manager,
#                 gym_id=self.gym.id,
#                 user_id=self.new_user.id,
#                 role=GymMembership.Role.MANAGER,
#                 salary=10000,
#             )

#     def test_member_cannot_add_staff(self):

#         with self.assertRaises(ValidationError):
#             add_staff(
#                 actor=self.member,
#                 gym_id=self.gym.id,
#                 user_id=self.new_user.id,
#                 role=GymMembership.Role.STAFF,
#                 salary=5000,
#             )

#     def test_cannot_add_duplicate_active_role(self):

#         with self.assertRaises(ValidationError):
#             add_staff(
#                 actor=self.owner,
#                 gym_id=self.gym.id,
#                 user_id=self.manager.id,
#                 role=GymMembership.Role.MANAGER,
#                 salary=10000,
#             )

#     # =====================================================
#     # get_gym_staff
#     # =====================================================

#     def test_get_gym_staff_returns_non_members(self):

#         result = get_gym_staff(
#             self.gym.id
#         )

#         self.assertEqual(
#             result.count(),
#             2,
#         )

#         self.assertIn(
#             self.owner_membership,
#             result,
#         )

#         self.assertIn(
#             self.manager_membership,
#             result,
#         )

#         self.assertNotIn(
#             self.member_membership,
#             result,
#         )

#     def test_get_gym_staff_raises_when_no_staff_exists(self):

#         GymMembership.objects.all().delete()

#         with self.assertRaises(NotFound):
#             get_gym_staff(
#                 self.gym.id
#             )

#     # =====================================================
#     # update_membership
#     # =====================================================

#     def test_owner_can_update_manager_role(self):

#         updated = update_membership(
#             actor=self.owner,
#             membership_id=self.manager_membership.id,
#             role=GymMembership.Role.STAFF,
#         )

#         self.assertEqual(
#             updated.role,
#             GymMembership.Role.STAFF,
#         )

#     def test_manager_can_update_member_role(self):

#         updated = update_membership(
#             actor=self.manager,
#             membership_id=self.member_membership.id,
#             role=GymMembership.Role.STAFF,
#             salary=5000,
#         )

#         self.assertEqual(
#             updated.role,
#             GymMembership.Role.STAFF,
#         )

#         self.assertEqual(
#             updated.salary,
#             5000,
#         )

#     def test_member_cannot_update_membership(self):

#         with self.assertRaises(ValidationError):
#             update_membership(
#                 actor=self.member,
#                 membership_id=self.member_membership.id,
#                 role=GymMembership.Role.STAFF,
#             )

#     def test_owner_cannot_change_role_to_owner(self):

#         with self.assertRaises(ValidationError):
#             update_membership(
#                 actor=self.owner,
#                 membership_id=self.manager_membership.id,
#                 role=GymMembership.Role.OWNER,
#             )

#     # =====================================================
#     # deactivate_staff
#     # =====================================================

#     def test_owner_can_deactivate_manager(self):

#         result = deactivate_staff(
#             actor=self.owner,
#             membership_id=self.manager_membership.id,
#         )

#         self.assertFalse(
#             result.is_active
#         )

#         self.manager_membership.refresh_from_db()

#         self.assertFalse(
#             self.manager_membership.is_active
#         )

#     def test_manager_can_deactivate_member(self):

#         result = deactivate_staff(
#             actor=self.manager,
#             membership_id=self.member_membership.id,
#         )

#         self.assertFalse(
#             result.is_active
#         )

#     def test_member_cannot_deactivate_membership(self):

#         with self.assertRaises(ValidationError):
#             deactivate_staff(
#                 actor=self.member,
#                 membership_id=self.member_membership.id,
#             )

#     def test_cannot_deactivate_already_inactive_membership(self):

#         self.manager_membership.is_active = False
#         self.manager_membership.save()

#         with self.assertRaises(ValidationError):
#             deactivate_staff(
#                 actor=self.owner,
#                 membership_id=self.manager_membership.id,
#             )

#     # =====================================================
#     # activate_staff
#     # =====================================================

#     def test_owner_can_activate_manager(self):

#         self.manager_membership.is_active = False
#         self.manager_membership.save()

#         result = activate_staff(
#             actor=self.owner,
#             membership_id=self.manager_membership.id,
#         )

#         self.assertTrue(
#             result.is_active
#         )

#         self.manager_membership.refresh_from_db()

#         self.assertTrue(
#             self.manager_membership.is_active
#         )

#     def test_manager_can_activate_member(self):

#         self.member_membership.is_active = False
#         self.member_membership.save()

#         result = activate_staff(
#             actor=self.manager,
#             membership_id=self.member_membership.id,
#         )

#         self.assertTrue(
#             result.is_active
#         )

#     def test_member_cannot_activate_membership(self):

#         self.member_membership.is_active = False
#         self.member_membership.save()

#         with self.assertRaises(ValidationError):
#             activate_staff(
#                 actor=self.member,
#                 membership_id=self.member_membership.id,
#             )

#     def test_cannot_activate_already_active_membership(self):

#         with self.assertRaises(ValidationError):
#             activate_staff(
#                 actor=self.owner,
#                 membership_id=self.manager_membership.id,
#             )

# class GymModelTest(TestCase):

#     def test_create_gym(self):
#         gym = Gym.objects.create(
#             name="Test Gym",
#             address="Test Address",
#         )

#         self.assertEqual(gym.name, "Test Gym")
#         self.assertEqual(gym.address, "Test Address")

#     def test_gym_str(self):
#         gym = Gym.objects.create(
#             name="Test Gym",
#             address="Test Address",
#         )

#         self.assertEqual(
#             str(gym),
#             "Test Gym - is active=True"
#         )

#     def test_gym_is_active_by_default(self):
#         gym = Gym.objects.create(
#             name="Test Gym",
#             address="Test Address",
#         )

#         self.assertTrue(gym.is_active)

#     def test_gym_can_be_deactivated(self):
#         gym = Gym.objects.create(
#             name="Test Gym",
#             address="Test Address",
#             is_active=False,
#         )

#         self.assertFalse(gym.is_active)

#     def test_valid_mobile_phone(self):
#         gym = Gym(
#             name="Test Gym",
#             address="Test Address",
#             phone="09123456789",
#         )

#         gym.full_clean()

#         self.assertEqual(gym.phone, "09123456789")

#     def test_valid_landline_phone(self):
#         gym = Gym(
#             name="Test Gym",
#             address="Test Address",
#             phone="02112345678",
#         )

#         gym.full_clean() 

#         self.assertEqual(gym.phone, "02112345678")

#     def test_invalid_phone(self):
#         gym = Gym(
#             name="Test Gym",
#             address="Test Address",
#             phone="123456789",
#         )

#         with self.assertRaises(ValidationError):
#             gym.full_clean()

#     def test_duplicate_phone(self):
#         Gym.objects.create(
#             name="Gym One",
#             address="Address One",
#             phone="09123456789",
#         )

#         gym = Gym(
#             name="Gym Two",
#             address="Address Two",
#             phone="09123456789",
#         )

#         with self.assertRaises(ValidationError):
#             gym.full_clean()

#     def test_valid_email(self):
#         gym = Gym(
#             name="Test Gym",
#             address="Test Address",
#             email="testgym@example.com",
#         )

#         gym.full_clean()

#         self.assertEqual(
#             gym.email,
#             "testgym@example.com"
#         )

#     def test_invalid_email(self):
#         gym = Gym(
#             name="Test Gym",
#             address="Test Address",
#             email="invalid-email",
#         )

#         with self.assertRaises(ValidationError):
#             gym.full_clean()

#     def test_duplicate_email(self):
#         Gym.objects.create(
#             name="Gym One",
#             address="Address One",
#             email="gym@example.com",
#         )

#         gym = Gym(
#             name="Gym Two",
#             address="Address Two",
#             email="gym@example.com",
#         )

#         with self.assertRaises(ValidationError):
#             gym.full_clean()


from decimal import Decimal

from django.test import TestCase
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.exceptions import (
    ValidationError as DRFValidationError,
    NotFound,
)

from accounts.models import CustomUser
from gyms.models import Gym, GymMembership

from gyms.services.gym_membership_services import (
    can_manage_membership,
    can_assign_role,
    add_staff,
    get_gym_staff,
    update_membership,
    deactivate_staff,
    activate_staff,
)


# =========================================================
# GymMembership Model Tests
# =========================================================

class GymMembershipModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="Test1234",
        )

        self.gym = Gym.objects.create(
            name="Test Gym",
            address="Test Address",
        )

    def test_create_owner_with_valid_share_percentage(self):

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

        membership = GymMembership(
            user=self.user,
            gym=self.gym,
            role=GymMembership.Role.OWNER,
        )

        with self.assertRaises(DjangoValidationError):
            membership.full_clean()

    def test_owner_share_percentage_cannot_be_zero(self):

        membership = GymMembership(
            user=self.user,
            gym=self.gym,
            role=GymMembership.Role.OWNER,
            share_percentage=Decimal("0.00"),
        )

        with self.assertRaises(DjangoValidationError):
            membership.full_clean()

    def test_owner_share_percentage_cannot_exceed_100(self):

        membership = GymMembership(
            user=self.user,
            gym=self.gym,
            role=GymMembership.Role.OWNER,
            share_percentage=Decimal("100.01"),
        )

        with self.assertRaises(DjangoValidationError):
            membership.full_clean()

    def test_member_cannot_have_salary(self):

        membership = GymMembership(
            user=self.user,
            gym=self.gym,
            role=GymMembership.Role.MEMBER,
            salary=Decimal("1000.00"),
        )

        with self.assertRaises(DjangoValidationError):
            membership.full_clean()

    def test_member_cannot_have_share_percentage(self):

        membership = GymMembership(
            user=self.user,
            gym=self.gym,
            role=GymMembership.Role.MEMBER,
            share_percentage=Decimal("10.00"),
        )

        with self.assertRaises(DjangoValidationError):
            membership.full_clean()

    def test_member_with_no_salary_or_share_is_valid(self):

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

        membership = GymMembership(
            user=self.user,
            gym=self.gym,
            role=GymMembership.Role.STAFF,
        )

        with self.assertRaises(DjangoValidationError):
            membership.full_clean()

    def test_staff_with_salary_is_valid(self):

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

        membership = GymMembership(
            user=self.user,
            gym=self.gym,
            role=GymMembership.Role.TRAINER,
            salary=Decimal("0.00"),
        )

        with self.assertRaises(DjangoValidationError):
            membership.full_clean()

    def test_salary_cannot_be_negative(self):

        membership = GymMembership(
            user=self.user,
            gym=self.gym,
            role=GymMembership.Role.TRAINER,
            salary=Decimal("-100.00"),
        )

        with self.assertRaises(DjangoValidationError):
            membership.full_clean()

    def test_non_owner_cannot_have_share_percentage(self):

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

        membership = GymMembership(
            user=self.user,
            gym=self.gym,
            role=GymMembership.Role.MEMBER,
        )

        self.assertEqual(
            str(membership),
            "testuser - Test Gym - member",
        )


# =========================================================
# GymMembership Helpers Tests
# =========================================================

class GymMembershipHelpersTest(TestCase):

    def setUp(self):

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

    # =====================================================
    # can_manage_membership
    # =====================================================

    def test_owner_can_manage_manager(self):

        result = can_manage_membership(
            self.owner,
            self.manager_membership,
        )

        self.assertTrue(result)

    def test_manager_can_manage_member(self):

        result = can_manage_membership(
            self.manager,
            self.member_membership,
        )

        self.assertTrue(result)

    def test_owner_cannot_manage_owner(self):

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

        with self.assertRaises(DRFValidationError):
            can_manage_membership(
                self.member,
                self.member_membership,
            )

    # =====================================================
    # can_assign_role
    # =====================================================

    def test_owner_can_assign_member_role(self):

        result = can_assign_role(
            self.owner,
            self.member_membership,
            GymMembership.Role.MEMBER,
        )

        self.assertTrue(result)

    def test_owner_cannot_assign_owner_role(self):

        with self.assertRaises(DRFValidationError):
            can_assign_role(
                self.owner,
                self.member_membership,
                GymMembership.Role.OWNER,
            )

    def test_manager_can_assign_staff_role(self):

        result = can_assign_role(
            self.manager,
            self.member_membership,
            GymMembership.Role.STAFF,
        )

        self.assertTrue(result)

    def test_manager_can_assign_trainer_role(self):

        result = can_assign_role(
            self.manager,
            self.member_membership,
            GymMembership.Role.TRAINER,
        )

        self.assertTrue(result)

    def test_manager_cannot_assign_owner_role(self):

        with self.assertRaises(DRFValidationError):
            can_assign_role(
                self.manager,
                self.member_membership,
                GymMembership.Role.OWNER,
            )

    def test_member_cannot_assign_role(self):

        with self.assertRaises(DRFValidationError):
            can_assign_role(
                self.member,
                self.member_membership,
                GymMembership.Role.STAFF,
            )

    def test_non_member_cannot_assign_role(self):

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


# =========================================================
# GymMembership Service Tests
# =========================================================

class GymMembershipServicesTest(TestCase):

    def setUp(self):

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

    # =====================================================
    # add_staff
    # =====================================================

    def test_owner_can_add_staff(self):

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

        with self.assertRaises(DRFValidationError):
            add_staff(
                actor=self.manager,
                gym_id=self.gym.id,
                user_id=self.new_user.id,
                role=GymMembership.Role.MANAGER,
                salary=10000,
            )

    def test_member_cannot_add_staff(self):

        with self.assertRaises(DRFValidationError):
            add_staff(
                actor=self.member,
                gym_id=self.gym.id,
                user_id=self.new_user.id,
                role=GymMembership.Role.STAFF,
                salary=5000,
            )

    def test_cannot_add_duplicate_active_role(self):

        with self.assertRaises(DRFValidationError):
            add_staff(
                actor=self.owner,
                gym_id=self.gym.id,
                user_id=self.manager.id,
                role=GymMembership.Role.MANAGER,
                salary=10000,
            )

    # =====================================================
    # get_gym_staff
    # =====================================================

    def test_get_gym_staff_returns_non_members(self):

        result = get_gym_staff(
            self.gym.id
        )

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

        GymMembership.objects.all().delete()

        with self.assertRaises(NotFound):
            get_gym_staff(
                self.gym.id
            )

    # =====================================================
    # update_membership
    # =====================================================

    def test_owner_can_update_manager_role(self):

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

        with self.assertRaises(DRFValidationError):
            update_membership(
                actor=self.member,
                membership_id=self.member_membership.id,
                role=GymMembership.Role.STAFF,
            )

    def test_owner_cannot_change_role_to_owner(self):

        with self.assertRaises(DRFValidationError):
            update_membership(
                actor=self.owner,
                membership_id=self.manager_membership.id,
                role=GymMembership.Role.OWNER,
            )

    # =====================================================
    # deactivate_staff
    # =====================================================

    def test_owner_can_deactivate_manager(self):

        result = deactivate_staff(
            actor=self.owner,
            membership_id=self.manager_membership.id,
        )

        self.assertFalse(
            result.is_active
        )

        self.manager_membership.refresh_from_db()

        self.assertFalse(
            self.manager_membership.is_active
        )

    def test_manager_can_deactivate_member(self):

        result = deactivate_staff(
            actor=self.manager,
            membership_id=self.member_membership.id,
        )

        self.assertFalse(
            result.is_active
        )

    def test_member_cannot_deactivate_membership(self):

        with self.assertRaises(DRFValidationError):
            deactivate_staff(
                actor=self.member,
                membership_id=self.member_membership.id,
            )

    def test_cannot_deactivate_already_inactive_membership(self):

        self.manager_membership.is_active = False
        self.manager_membership.save()

        with self.assertRaises(DRFValidationError):
            deactivate_staff(
                actor=self.owner,
                membership_id=self.manager_membership.id,
            )

    # =====================================================
    # activate_staff
    # =====================================================

    def test_owner_can_activate_manager(self):

        self.manager_membership.is_active = False
        self.manager_membership.save()

        result = activate_staff(
            actor=self.owner,
            membership_id=self.manager_membership.id,
        )

        self.assertTrue(
            result.is_active
        )

        self.manager_membership.refresh_from_db()

        self.assertTrue(
            self.manager_membership.is_active
        )

    def test_manager_can_activate_member(self):

        self.member_membership.is_active = False
        self.member_membership.save()

        result = activate_staff(
            actor=self.manager,
            membership_id=self.member_membership.id,
        )

        self.assertTrue(
            result.is_active
        )

    def test_member_cannot_activate_membership(self):

        self.member_membership.is_active = False
        self.member_membership.save()

        with self.assertRaises(DRFValidationError):
            activate_staff(
                actor=self.member,
                membership_id=self.member_membership.id,
            )

    def test_cannot_activate_already_active_membership(self):

        with self.assertRaises(DRFValidationError):
            activate_staff(
                actor=self.owner,
                membership_id=self.manager_membership.id,
            )


# =========================================================
# Gym Model Tests
# =========================================================

class GymModelTest(TestCase):

    def test_create_gym(self):

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

        gym = Gym.objects.create(
            name="Test Gym",
            address="Test Address",
        )

        self.assertEqual(
            str(gym),
            "Test Gym - is active=True",
        )

    def test_gym_is_active_by_default(self):

        gym = Gym.objects.create(
            name="Test Gym",
            address="Test Address",
        )

        self.assertTrue(
            gym.is_active
        )

    def test_gym_can_be_deactivated(self):

        gym = Gym.objects.create(
            name="Test Gym",
            address="Test Address",
            is_active=False,
        )

        self.assertFalse(
            gym.is_active
        )

    # =====================================================
    # Phone Validation
    # =====================================================

    def test_valid_mobile_phone(self):

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

        gym = Gym(
            name="Test Gym",
            address="Test Address",
            phone="123456789",
        )

        with self.assertRaises(DjangoValidationError):
            gym.full_clean()

    def test_duplicate_phone(self):

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

    # =====================================================
    # Email Validation
    # =====================================================

    def test_valid_email(self):

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

        gym = Gym(
            name="Test Gym",
            address="Test Address",
            email="invalid-email",
        )

        with self.assertRaises(DjangoValidationError):
            gym.full_clean()

    def test_duplicate_email(self):

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