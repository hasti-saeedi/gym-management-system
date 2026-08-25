from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.test import TestCase

from gyms.models import Gym, GymMembership
from classes.models import GymClass
from enrollments.models import Enrollment, Payment

from permissions.permission_helpers import (
    is_owner_or_manager,
    is_staff,
    is_gym_owner_or_manager,
    is_gym_staff,
    is_gym_owner,
    can_manage_any_gym,
    can_manage_gym,
    can_view_gym_users,
    can_manage_gym_users,
    can_update_user,
    can_delete_user,
    can_manage_gym_class,
    is_staff_of_gym,
    is_class_trainer,
    is_session_trainer,
    is_gym_class_trainer,
    can_access_session,
    can_create_session,
    can_delete_session,
    can_access_gym_enrollments,
    can_manage_enrollment,
    can_create_enrollment,
    can_cancel_enrollment,
    can_access_gym_payments,
    can_manage_payment,
    can_confirm_payment,
    is_class_member,
    is_gym_employee,
)


User = get_user_model()


class PermissionHelperTest(TestCase):

    def setUp(self):
        # =====================================================
        # Gyms
        # =====================================================

        self.gym = Gym.objects.create(
            name="Test Gym",
            address="Tehran",
            phone="09123456789",
            email="gym@test.com",
        )

        self.other_gym = Gym.objects.create(
            name="Other Gym",
            address="Tehran",
            phone="09123456788",
            email="other@test.com",
        )

        # =====================================================
        # Users
        # =====================================================

        self.owner = User.objects.create_user(
            username="owner",
            password="Test1234",
        )

        self.manager = User.objects.create_user(
            username="manager",
            password="Test1234",
        )

        self.staff = User.objects.create_user(
            username="staff",
            password="Test1234",
        )

        self.trainer = User.objects.create_user(
            username="trainer",
            password="Test1234",
        )

        self.second_trainer = User.objects.create_user(
        username="second_trainer",
        password="Test1234",
        )

        self.member = User.objects.create_user(
            username="member",
            password="Test1234",
        )

        self.other_member = User.objects.create_user(
            username="other_member",
            password="Test1234",
        )

        self.other_staff = User.objects.create_user(
            username="other_staff",
            password="Test1234",
        )

        self.admin = User.objects.create_superuser(
            username="admin",
            password="Test1234",
        )

        # =====================================================
        # Memberships - Main Gym
        # =====================================================

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
            salary=1000,
        )

        self.staff_membership = GymMembership.objects.create(
            user=self.staff,
            gym=self.gym,
            role=GymMembership.Role.STAFF,
            salary=800,
        )

        self.trainer_membership = GymMembership.objects.create(
            user=self.trainer,
            gym=self.gym,
            role=GymMembership.Role.TRAINER,
            salary=900,
        )
        self.second_trainer_membership = GymMembership.objects.create(
            user=self.second_trainer,
            gym=self.gym,
            role=GymMembership.Role.TRAINER,
            salary=900,
        )

        self.member_membership = GymMembership.objects.create(
            user=self.member,
            gym=self.gym,
            role=GymMembership.Role.MEMBER,
        )

        # =====================================================
        # Memberships - Other Gym
        # =====================================================

        self.other_member_membership = GymMembership.objects.create(
            user=self.other_member,
            gym=self.other_gym,
            role=GymMembership.Role.MEMBER,
        )

        self.other_staff_membership = GymMembership.objects.create(
            user=self.other_staff,
            gym=self.other_gym,
            role=GymMembership.Role.STAFF,
            salary=700,
        )

        # =====================================================
        # Gym Class
        # =====================================================

        self.gym_class = GymClass.objects.create(
            name="Python Class",
            gym=self.gym,
            trainer=self.trainer,
            start_date="2026-08-20",
            end_date="2026-09-20",
            start_time="10:00",
            end_time="11:00",
            capacity=20,
            regular_days=["monday"],
            price=1000,
            single_session_price=100,
        )

        self.other_gym_class = GymClass.objects.create(
            name="Other Class",
            gym=self.other_gym,
            trainer=self.trainer,
            start_date="2026-08-20",
            end_date="2026-09-20",
            start_time="10:00",
            end_time="11:00",
            capacity=20,
            regular_days=["monday"],
            price=1000,
            single_session_price=100,
        )

        # =====================================================
        # Enrollment
        # =====================================================

        self.enrollment = Enrollment.objects.create(
            gym_class=self.gym_class,
            user=self.member,
            status="approved",
            enrollment_type="semester",
        )

        # =====================================================
        # Payment
        # =====================================================

        self.payment = Payment.objects.create(
            enrollment=self.enrollment,
            amount=1000,
            status="pending",
        )

        # =====================================================
        # Fake Session objects
        #
        # We only need the attributes used by helpers.
        # =====================================================

        self.session = SimpleNamespace(
            gym_class=self.gym_class,
            trainer=self.trainer,
        )

        self.other_session = SimpleNamespace(
            gym_class=self.other_gym_class,
            trainer=self.trainer,
        )

        self.session_only_trainer = SimpleNamespace(
            gym_class=self.gym_class,
            trainer=self.second_trainer,
        )

    # =========================================================
    # Basic Gym Role Helpers
    # =========================================================

    def test_is_owner_or_manager(self):
        self.assertTrue(
            is_owner_or_manager(self.owner, self.gym)
        )

        self.assertTrue(
            is_owner_or_manager(self.manager, self.gym)
        )

        self.assertFalse(
            is_owner_or_manager(self.staff, self.gym)
        )

        self.assertFalse(
            is_owner_or_manager(self.member, self.gym)
        )

    def test_is_owner_or_manager_wrong_gym(self):
        self.assertFalse(
            is_owner_or_manager(
                self.owner,
                self.other_gym,
            )
        )

    def test_is_owner_or_manager_inactive_membership(self):
        self.owner_membership.is_active = False
        self.owner_membership.save()

        self.assertFalse(
            is_owner_or_manager(
                self.owner,
                self.gym,
            )
        )

    def test_is_staff(self):
        self.assertTrue(
            is_staff(self.staff, self.gym)
        )

        self.assertFalse(
            is_staff(self.owner, self.gym)
        )

        self.assertFalse(
            is_staff(self.manager, self.gym)
        )

        self.assertFalse(
            is_staff(self.trainer, self.gym)
        )

    def test_is_gym_owner_or_manager(self):
        self.assertTrue(
            is_gym_owner_or_manager(
                self.owner,
                self.gym,
            )
        )

        self.assertTrue(
            is_gym_owner_or_manager(
                self.manager,
                self.gym,
            )
        )

        self.assertFalse(
            is_gym_owner_or_manager(
                self.staff,
                self.gym,
            )
        )

    def test_is_gym_owner_or_manager_superuser(self):
        self.assertTrue(
            is_gym_owner_or_manager(
                self.admin,
                self.other_gym,
            )
        )

    def test_is_gym_staff(self):
        self.assertTrue(
            is_gym_staff(self.owner, self.gym)
        )

        self.assertTrue(
            is_gym_staff(self.manager, self.gym)
        )

        self.assertTrue(
            is_gym_staff(self.staff, self.gym)
        )

        self.assertFalse(
            is_gym_staff(self.trainer, self.gym)
        )

        self.assertFalse(
            is_gym_staff(self.member, self.gym)
        )

    def test_is_gym_staff_superuser(self):
        self.assertTrue(
            is_gym_staff(
                self.admin,
                self.other_gym,
            )
        )

    def test_is_gym_owner(self):
        self.assertTrue(
            is_gym_owner(
                self.owner,
                self.gym,
            )
        )

        self.assertFalse(
            is_gym_owner(
                self.manager,
                self.gym,
            )
        )

        self.assertFalse(
            is_gym_owner(
                self.staff,
                self.gym,
            )
        )

    def test_is_gym_owner_superuser(self):
        self.assertTrue(
            is_gym_owner(
                self.admin,
                self.other_gym,
            )
        )

    # =========================================================
    # General Gym Access
    # =========================================================

    def test_can_manage_any_gym(self):
        self.assertTrue(
            can_manage_any_gym(self.owner)
        )

        self.assertTrue(
            can_manage_any_gym(self.manager)
        )

        self.assertTrue(
            can_manage_any_gym(self.staff)
        )

        self.assertFalse(
            can_manage_any_gym(self.trainer)
        )

        self.assertFalse(
            can_manage_any_gym(self.member)
        )

    def test_can_manage_any_gym_superuser(self):
        self.assertTrue(
            can_manage_any_gym(self.admin)
        )

    def test_can_manage_gym(self):
        self.assertTrue(
            can_manage_gym(
                self.owner,
                self.gym,
            )
        )

        self.assertTrue(
            can_manage_gym(
                self.manager,
                self.gym,
            )
        )

        self.assertTrue(
            can_manage_gym(
                self.staff,
                self.gym,
            )
        )

        self.assertFalse(
            can_manage_gym(
                self.trainer,
                self.gym,
            )
        )

        self.assertFalse(
            can_manage_gym(
                self.member,
                self.gym,
            )
        )

    def test_can_manage_gym_superuser(self):
        self.assertTrue(
            can_manage_gym(
                self.admin,
                self.other_gym,
            )
        )

    # =========================================================
    # Gym User Permissions
    # =========================================================

    def test_can_view_gym_users(self):
        self.assertTrue(
            can_view_gym_users(
                self.owner,
                self.gym,
            )
        )

        self.assertTrue(
            can_view_gym_users(
                self.manager,
                self.gym,
            )
        )

        self.assertTrue(
            can_view_gym_users(
                self.staff,
                self.gym,
            )
        )

        self.assertFalse(
            can_view_gym_users(
                self.trainer,
                self.gym,
            )
        )

        self.assertFalse(
            can_view_gym_users(
                self.member,
                self.gym,
            )
        )

    def test_can_manage_gym_users(self):
        self.assertTrue(
            can_manage_gym_users(
                self.owner,
                self.gym,
            )
        )

        self.assertTrue(
            can_manage_gym_users(
                self.manager,
                self.gym,
            )
        )

        self.assertFalse(
            can_manage_gym_users(
                self.staff,
                self.gym,
            )
        )

        self.assertFalse(
            can_manage_gym_users(
                self.member,
                self.gym,
            )
        )

    # =========================================================
    # Update User
    # =========================================================
    def test_can_update_user_requester_without_membership(self):
        user_without_membership = User.objects.create_user(
            username="no_membership_user",
            password="Test1234",
        )

        self.assertFalse(
            can_update_user(
                user_without_membership,
                self.member,
                self.gym,
            )
        )

    def test_can_update_user_target_without_membership(self):
        user_without_membership = User.objects.create_user(
            username="target_without_membership",
            password="Test1234",
        )

        self.assertFalse(
            can_update_user(
                self.owner,
                user_without_membership,
                self.gym,
            )
        )

    def test_owner_can_update_lower_roles(self):
        for target in [
            self.manager,
            self.staff,
            self.trainer,
            self.member,
        ]:
            self.assertTrue(
                can_update_user(
                    self.owner,
                    target,
                    self.gym,
                )
            )

    def test_owner_cannot_update_owner(self):
        self.assertFalse(
            can_update_user(
                self.owner,
                self.owner,
                self.gym,
            )
        )

    def test_manager_can_update_lower_roles(self):
        for target in [
            self.staff,
            self.trainer,
            self.member,
        ]:
            self.assertTrue(
                can_update_user(
                    self.manager,
                    target,
                    self.gym,
                )
            )

    def test_manager_cannot_update_owner_or_manager(self):
        self.assertFalse(
            can_update_user(
                self.manager,
                self.owner,
                self.gym,
            )
        )

        self.assertFalse(
            can_update_user(
                self.manager,
                self.manager,
                self.gym,
            )
        )

    def test_user_cannot_update_himself(self):
        self.assertFalse(
            can_update_user(
                self.member,
                self.member,
                self.gym,
            )
        )

    def test_staff_cannot_update_users(self):
        self.assertFalse(
            can_update_user(
                self.staff,
                self.member,
                self.gym,
            )
        )

    def test_cannot_update_user_from_other_gym(self):
        self.assertFalse(
            can_update_user(
                self.owner,
                self.other_member,
                self.gym,
            )
        )

    def test_superuser_can_update_any_user(self):
        self.assertTrue(
            can_update_user(
                self.admin,
                self.other_member,
                self.other_gym,
            )
        )

    # =========================================================
    # Delete User
    # =========================================================

    def test_owner_can_delete_non_owner(self):
        for target in [
            self.manager,
            self.staff,
            self.trainer,
            self.member,
        ]:
            self.assertTrue(
                can_delete_user(
                    self.owner,
                    target,
                    self.gym,
                )
            )

    def test_owner_cannot_delete_owner(self):
        self.assertFalse(
            can_delete_user(
                self.owner,
                self.owner,
                self.gym,
            )
        )

    def test_manager_can_delete_lower_roles(self):
        for target in [
            self.staff,
            self.trainer,
            self.member,
        ]:
            self.assertTrue(
                can_delete_user(
                    self.manager,
                    target,
                    self.gym,
                )
            )

    def test_manager_cannot_delete_owner_or_manager(self):
        self.assertFalse(
            can_delete_user(
                self.manager,
                self.owner,
                self.gym,
            )
        )

        self.assertFalse(
            can_delete_user(
                self.manager,
                self.manager,
                self.gym,
            )
        )

    def test_staff_cannot_delete_user(self):
        self.assertFalse(
            can_delete_user(
                self.staff,
                self.member,
                self.gym,
            )
        )

    def test_superuser_can_delete_any_user(self):
        self.assertTrue(
            can_delete_user(
                self.admin,
                self.other_member,
                self.other_gym,
            )
        )

    # =========================================================
    # Gym Class Permissions
    # =========================================================

    def test_can_manage_gym_class(self):
        self.assertTrue(
            can_manage_gym_class(
                self.owner,
                self.gym,
            )
        )

        self.assertTrue(
            can_manage_gym_class(
                self.manager,
                self.gym,
            )
        )

        self.assertTrue(
            can_manage_gym_class(
                self.staff,
                self.gym,
            )
        )

        self.assertFalse(
            can_manage_gym_class(
                self.trainer,
                self.gym,
            )
        )

        self.assertFalse(
            can_manage_gym_class(
                self.member,
                self.gym,
            )
        )

    def test_can_manage_gym_class_superuser(self):
        self.assertTrue(
            can_manage_gym_class(
                self.admin,
                self.other_gym,
            )
        )

    # =========================================================
    # Trainer Helpers
    # =========================================================

    def test_is_staff_of_gym(self):
        self.assertTrue(
            is_staff_of_gym(
                self.owner,
                self.gym,
            )
        )

        self.assertTrue(
            is_staff_of_gym(
                self.manager,
                self.gym,
            )
        )

        self.assertTrue(
            is_staff_of_gym(
                self.staff,
                self.gym,
            )
        )

        self.assertFalse(
            is_staff_of_gym(
                self.trainer,
                self.gym,
            )
        )

    def test_is_class_trainer(self):
        self.assertTrue(
            is_class_trainer(
                self.trainer,
                self.gym_class,
            )
        )

        self.assertFalse(
            is_class_trainer(
                self.staff,
                self.gym_class,
            )
        )

        self.assertFalse(
            is_class_trainer(
                self.member,
                self.gym_class,
            )
        )

    def test_is_class_trainer_wrong_class_trainer(self):
        self.assertFalse(
            is_class_trainer(
                self.owner,
                self.gym_class,
            )
        )

    def test_is_class_trainer_wrong_gym(self):
        self.assertFalse(
            is_class_trainer(
                self.trainer,
                self.other_gym_class,
            )
        )

    def test_is_session_trainer(self):
        self.assertTrue(
            is_session_trainer(
                self.trainer,
                self.session,
            )
        )

        self.assertFalse(
            is_session_trainer(
                self.staff,
                self.session,
            )
        )

    def test_is_gym_class_trainer_alias(self):
        self.assertEqual(
            is_gym_class_trainer(
                self.trainer,
                self.gym_class,
            ),
            is_class_trainer(
                self.trainer,
                self.gym_class,
            ),
        )

    # =========================================================
    # Session Permissions
    # =========================================================

    def test_can_access_session_staff(self):
        self.assertTrue(
            can_access_session(
                self.owner,
                self.session,
            )
        )

        self.assertTrue(
            can_access_session(
                self.manager,
                self.session,
            )
        )

        self.assertTrue(
            can_access_session(
                self.staff,
                self.session,
            )
        )

    def test_can_access_session_trainer(self):
        self.assertTrue(
            can_access_session(
                self.trainer,
                self.session,
            )
        )

    def test_member_cannot_access_session(self):
        self.assertFalse(
            can_access_session(
                self.member,
                self.session,
            )
        )

    def test_superuser_can_access_session(self):
        self.assertTrue(
            can_access_session(
                self.admin,
                self.session,
            )
        )

    def test_can_create_session(self):
        self.assertTrue(
            can_create_session(
                self.owner,
                self.gym_class,
            )
        )

        self.assertTrue(
            can_create_session(
                self.manager,
                self.gym_class,
            )
        )

        self.assertTrue(
            can_create_session(
                self.staff,
                self.gym_class,
            )
        )

        self.assertTrue(
            can_create_session(
                self.trainer,
                self.gym_class,
            )
        )

        self.assertFalse(
            can_create_session(
                self.member,
                self.gym_class,
            )
        )

    def test_superuser_can_create_session(self):
        self.assertTrue(
            can_create_session(
                self.admin,
                self.gym_class,
            )
        )

    def test_can_delete_session(self):
        self.assertTrue(
            can_delete_session(
                self.owner,
                self.session,
            )
        )

        self.assertTrue(
            can_delete_session(
                self.manager,
                self.session,
            )
        )

        self.assertTrue(
            can_delete_session(
                self.staff,
                self.session,
            )
        )

        self.assertFalse(
            can_delete_session(
                self.trainer,
                self.session,
            )
        )

        self.assertFalse(
            can_delete_session(
                self.member,
                self.session,
            )
        )


    def test_can_access_session_session_trainer_only(self):
        self.assertTrue(
            can_access_session(
                self.second_trainer,
                self.session_only_trainer,
            )
        )

    def test_superuser_can_delete_session(self):
        self.assertTrue(
            can_delete_session(
                self.admin,
                self.session,
            )
        )

    # =========================================================
    # Enrollment Permissions
    # =========================================================

    def test_can_access_gym_enrollments(self):
        self.assertTrue(
            can_access_gym_enrollments(
                self.owner,
                self.gym,
            )
        )

        self.assertTrue(
            can_access_gym_enrollments(
                self.manager,
                self.gym,
            )
        )

        self.assertTrue(
            can_access_gym_enrollments(
                self.staff,
                self.gym,
            )
        )

        self.assertFalse(
            can_access_gym_enrollments(
                self.trainer,
                self.gym,
            )
        )

        self.assertFalse(
            can_access_gym_enrollments(
                self.member,
                self.gym,
            )
        )

    def test_superuser_can_access_gym_enrollments(self):
        self.assertTrue(
            can_access_gym_enrollments(
                self.admin,
                self.other_gym,
            )
        )

    def test_can_manage_enrollment(self):
        self.assertTrue(
            can_manage_enrollment(
                self.owner,
                self.enrollment,
            )
        )

        self.assertTrue(
            can_manage_enrollment(
                self.manager,
                self.enrollment,
            )
        )

        self.assertTrue(
            can_manage_enrollment(
                self.staff,
                self.enrollment,
            )
        )

        self.assertFalse(
            can_manage_enrollment(
                self.trainer,
                self.enrollment,
            )
        )

        self.assertFalse(
            can_manage_enrollment(
                self.member,
                self.enrollment,
            )
        )

    def test_superuser_can_manage_enrollment(self):
        self.assertTrue(
            can_manage_enrollment(
                self.admin,
                self.enrollment,
            )
        )

    def test_can_create_enrollment(self):
        self.assertTrue(
            can_create_enrollment(
                self.owner,
                self.gym,
                self.member,
            )
        )

        self.assertTrue(
            can_create_enrollment(
                self.manager,
                self.gym,
                self.member,
            )
        )

        self.assertTrue(
            can_create_enrollment(
                self.staff,
                self.gym,
                self.member,
            )
        )

    def test_member_can_create_enrollment_for_himself(self):
        self.assertTrue(
            can_create_enrollment(
                self.member,
                self.gym,
                self.member,
            )
        )

    def test_member_cannot_create_enrollment_for_other_user(self):
        self.assertFalse(
            can_create_enrollment(
                self.member,
                self.gym,
                self.other_member,
            )
        )

    def test_member_without_target_user_cannot_create_enrollment(self):
        self.assertFalse(
            can_create_enrollment(
                self.member,
                self.gym,
            )
        )

    def test_superuser_can_create_enrollment(self):
        self.assertTrue(
            can_create_enrollment(
                self.admin,
                self.other_gym,
                self.other_member,
            )
        )

    def test_can_cancel_enrollment(self):
        # Enrollment owner
        self.assertTrue(
            can_cancel_enrollment(
                self.member,
                self.enrollment,
            )
        )

        # Gym staff
        self.assertTrue(
            can_cancel_enrollment(
                self.owner,
                self.enrollment,
            )
        )

        self.assertTrue(
            can_cancel_enrollment(
                self.manager,
                self.enrollment,
            )
        )

        self.assertTrue(
            can_cancel_enrollment(
                self.staff,
                self.enrollment,
            )
        )

    def test_other_member_cannot_cancel_enrollment(self):
        self.assertFalse(
            can_cancel_enrollment(
                self.other_member,
                self.enrollment,
            )
        )

    def test_superuser_can_cancel_enrollment(self):
        self.assertTrue(
            can_cancel_enrollment(
                self.admin,
                self.enrollment,
            )
        )

    # =========================================================
    # Payment Permissions
    # =========================================================

    def test_can_access_gym_payments(self):
        self.assertTrue(
            can_access_gym_payments(
                self.owner,
                self.gym,
            )
        )

        self.assertTrue(
            can_access_gym_payments(
                self.manager,
                self.gym,
            )
        )

        self.assertTrue(
            can_access_gym_payments(
                self.staff,
                self.gym,
            )
        )

        self.assertFalse(
            can_access_gym_payments(
                self.trainer,
                self.gym,
            )
        )

        self.assertFalse(
            can_access_gym_payments(
                self.member,
                self.gym,
            )
        )

    def test_superuser_can_access_gym_payments(self):
        self.assertTrue(
            can_access_gym_payments(
                self.admin,
                self.other_gym,
            )
        )

    def test_can_manage_payment(self):
        self.assertTrue(
            can_manage_payment(
                self.owner,
                self.payment,
            )
        )

        self.assertTrue(
            can_manage_payment(
                self.manager,
                self.payment,
            )
        )

        self.assertTrue(
            can_manage_payment(
                self.staff,
                self.payment,
            )
        )

        self.assertFalse(
            can_manage_payment(
                self.trainer,
                self.payment,
            )
        )

        self.assertFalse(
            can_manage_payment(
                self.member,
                self.payment,
            )
        )

    def test_superuser_can_manage_payment(self):
        self.assertTrue(
            can_manage_payment(
                self.admin,
                self.payment,
            )
        )

    def test_can_confirm_payment(self):
        self.assertTrue(
            can_confirm_payment(
                self.owner,
                self.payment,
            )
        )

        self.assertTrue(
            can_confirm_payment(
                self.manager,
                self.payment,
            )
        )

        self.assertTrue(
            can_confirm_payment(
                self.staff,
                self.payment,
            )
        )

        self.assertFalse(
            can_confirm_payment(
                self.trainer,
                self.payment,
            )
        )

        self.assertFalse(
            can_confirm_payment(
                self.member,
                self.payment,
            )
        )

    def test_superuser_can_confirm_payment(self):
        self.assertTrue(
            can_confirm_payment(
                self.admin,
                self.payment,
            )
        )

    # =========================================================
    # Class Member
    # =========================================================

    def test_is_class_member(self):
        self.assertTrue(
            is_class_member(
                self.member,
                self.gym_class,
            )
        )

        self.assertFalse(
            is_class_member(
                self.other_member,
                self.gym_class,
            )
        )

    def test_is_class_member_wrong_class(self):
        self.assertFalse(
            is_class_member(
                self.member,
                self.other_gym_class,
            )
        )

    # =========================================================
    # Gym Employee
    # =========================================================

    def test_is_gym_employee(self):
        self.assertTrue(
            is_gym_employee(self.owner)
        )

        self.assertTrue(
            is_gym_employee(self.manager)
        )

        self.assertTrue(
            is_gym_employee(self.staff)
        )

        self.assertFalse(
            is_gym_employee(self.trainer)
        )

        self.assertFalse(
            is_gym_employee(self.member)
        )

    def test_is_gym_employee_across_gyms(self):
        self.assertTrue(
            is_gym_employee(self.other_staff)
        )

    # =========================================================
    # Unauthenticated
    # =========================================================

    def test_unauthenticated_user_is_denied(self):
        from django.contrib.auth.models import AnonymousUser

        anonymous = AnonymousUser()

        self.assertFalse(
            is_owner_or_manager(
                anonymous,
                self.gym,
            )
        )

        self.assertFalse(
            is_staff(
                anonymous,
                self.gym,
            )
        )

        self.assertFalse(
            is_gym_owner_or_manager(
                anonymous,
                self.gym,
            )
        )

        self.assertFalse(
            is_gym_staff(
                anonymous,
                self.gym,
            )
        )

        self.assertFalse(
            is_gym_owner(
                anonymous,
                self.gym,
            )
        )

        self.assertFalse(
            can_manage_any_gym(anonymous)
        )

        self.assertFalse(
            can_manage_gym(
                anonymous,
                self.gym,
            )
        )

        self.assertFalse(
            can_update_user(
                anonymous,
                self.member,
                self.gym,
            )
        )

        self.assertFalse(
            can_delete_user(
                anonymous,
                self.member,
                self.gym,
            )
        )

        self.assertFalse(
            can_manage_gym_class(
                anonymous,
                self.gym,
            )
        )

        self.assertFalse(
            is_class_trainer(
                anonymous,
                self.gym_class,
            )
        )

        self.assertFalse(
            is_session_trainer(
                anonymous,
                self.session,
            )
        )

        self.assertFalse(
            can_access_session(
                anonymous,
                self.session,
            )
        )

        self.assertFalse(
            can_create_session(
                anonymous,
                self.gym_class,
            )
        )

        self.assertFalse(
            can_delete_session(
                anonymous,
                self.session,
            )
        )

        self.assertFalse(
            can_manage_enrollment(
                anonymous,
                self.enrollment,
            )
        )

        self.assertFalse(
            can_create_enrollment(
                anonymous,
                self.gym,
                self.member,
            )
        )

        self.assertFalse(
            can_cancel_enrollment(
                anonymous,
                self.enrollment,
            )
        )

        self.assertFalse(
            can_manage_payment(
                anonymous,
                self.payment,
            )
        )

        self.assertFalse(
            can_confirm_payment(
                anonymous,
                self.payment,
            )
        )

        self.assertFalse(
            is_class_member(
                anonymous,
                self.gym_class,
            )
        )

        self.assertFalse(
            is_gym_employee(anonymous)
        )