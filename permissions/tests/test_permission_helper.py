from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from classes.models import GymClass
from enrollments.models import Enrollment, Payment
from gyms.models import Gym, GymMembership

from permissions.permission_helpers import (
    can_access_gym_enrollments,
    can_access_gym_payments,
    can_access_session,
    can_cancel_enrollment,
    can_confirm_payment,
    can_create_enrollment,
    can_create_session,
    can_delete_session,
    can_delete_user,
    can_manage_any_gym,
    can_manage_enrollment,
    can_manage_gym,
    can_manage_gym_class,
    can_manage_gym_users,
    can_manage_payment,
    can_update_user,
    can_view_gym_users,
    is_class_member,
    is_class_trainer,
    is_gym_class_trainer,
    is_gym_employee,
    is_gym_owner,
    is_gym_owner_or_manager,
    is_gym_staff,
    is_owner_or_manager,
    is_session_trainer,
    is_staff,
    is_staff_of_gym,
)


User = get_user_model()


class PermissionHelperTest(TestCase):
    """Test permission helper functions across gym roles and resources."""

    def setUp(self):
        """Create gyms, users, memberships, classes, enrollments, and payments."""

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

        self.enrollment = Enrollment.objects.create(
            gym_class=self.gym_class,
            user=self.member,
            status="approved",
            enrollment_type="semester",
        )

        self.payment = Payment.objects.create(
            enrollment=self.enrollment,
            amount=1000,
            status="pending",
        )

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

    # ------------------------------------------------------------------
    # Basic Gym Role Helpers
    # ------------------------------------------------------------------

    def test_is_owner_or_manager(self):
        """Return True for active gym owners and managers only."""
        self.assertTrue(is_owner_or_manager(self.owner, self.gym))
        self.assertTrue(is_owner_or_manager(self.manager, self.gym))
        self.assertFalse(is_owner_or_manager(self.staff, self.gym))
        self.assertFalse(is_owner_or_manager(self.member, self.gym))

    def test_is_owner_or_manager_wrong_gym(self):
        """Return False when the user belongs to a different gym."""
        self.assertFalse(
            is_owner_or_manager(self.owner, self.other_gym)
        )

    def test_is_owner_or_manager_inactive_membership(self):
        """Return False when the user's gym membership is inactive."""
        self.owner_membership.is_active = False
        self.owner_membership.save()

        self.assertFalse(
            is_owner_or_manager(self.owner, self.gym)
        )

    def test_is_staff(self):
        """Return True only for users with the staff role."""
        self.assertTrue(is_staff(self.staff, self.gym))
        self.assertFalse(is_staff(self.owner, self.gym))
        self.assertFalse(is_staff(self.manager, self.gym))
        self.assertFalse(is_staff(self.trainer, self.gym))

    def test_is_gym_owner_or_manager(self):
        """Return True for gym owners and managers."""
        self.assertTrue(
            is_gym_owner_or_manager(self.owner, self.gym)
        )
        self.assertTrue(
            is_gym_owner_or_manager(self.manager, self.gym)
        )
        self.assertFalse(
            is_gym_owner_or_manager(self.staff, self.gym)
        )

    def test_is_gym_owner_or_manager_superuser(self):
        """Allow superusers to manage any gym."""
        self.assertTrue(
            is_gym_owner_or_manager(self.admin, self.other_gym)
        )

    def test_is_gym_staff(self):
        """Return True for owners, managers, and staff members."""
        self.assertTrue(is_gym_staff(self.owner, self.gym))
        self.assertTrue(is_gym_staff(self.manager, self.gym))
        self.assertTrue(is_gym_staff(self.staff, self.gym))
        self.assertFalse(is_gym_staff(self.trainer, self.gym))
        self.assertFalse(is_gym_staff(self.member, self.gym))

    def test_is_gym_staff_superuser(self):
        """Allow superusers to access staff-level gym permissions."""
        self.assertTrue(
            is_gym_staff(self.admin, self.other_gym)
        )

    def test_is_gym_owner(self):
        """Return True only for the gym owner."""
        self.assertTrue(is_gym_owner(self.owner, self.gym))
        self.assertFalse(is_gym_owner(self.manager, self.gym))
        self.assertFalse(is_gym_owner(self.staff, self.gym))

    def test_is_gym_owner_superuser(self):
        """Allow superusers to access owner-level permissions."""
        self.assertTrue(
            is_gym_owner(self.admin, self.other_gym)
        )

    # ------------------------------------------------------------------
    # General Gym Access
    # ------------------------------------------------------------------

    def test_can_manage_any_gym(self):
        """Return True for users allowed to manage at least one gym."""
        self.assertTrue(can_manage_any_gym(self.owner))
        self.assertTrue(can_manage_any_gym(self.manager))
        self.assertTrue(can_manage_any_gym(self.staff))
        self.assertFalse(can_manage_any_gym(self.trainer))
        self.assertFalse(can_manage_any_gym(self.member))

    def test_can_manage_any_gym_superuser(self):
        """Allow superusers to manage any gym."""
        self.assertTrue(can_manage_any_gym(self.admin))

    def test_can_manage_gym(self):
        """Return True for users allowed to manage the specified gym."""
        self.assertTrue(can_manage_gym(self.owner, self.gym))
        self.assertTrue(can_manage_gym(self.manager, self.gym))
        self.assertTrue(can_manage_gym(self.staff, self.gym))
        self.assertFalse(can_manage_gym(self.trainer, self.gym))
        self.assertFalse(can_manage_gym(self.member, self.gym))

    def test_can_manage_gym_superuser(self):
        """Allow superusers to manage any specified gym."""
        self.assertTrue(
            can_manage_gym(self.admin, self.other_gym)
        )

    # ------------------------------------------------------------------
    # Gym User Permissions
    # ------------------------------------------------------------------

    def test_can_view_gym_users(self):
        """Allow owners, managers, and staff to view gym users."""
        self.assertTrue(can_view_gym_users(self.owner, self.gym))
        self.assertTrue(can_view_gym_users(self.manager, self.gym))
        self.assertTrue(can_view_gym_users(self.staff, self.gym))
        self.assertFalse(can_view_gym_users(self.trainer, self.gym))
        self.assertFalse(can_view_gym_users(self.member, self.gym))

    def test_can_manage_gym_users(self):
        """Allow owners and managers to manage gym users."""
        self.assertTrue(can_manage_gym_users(self.owner, self.gym))
        self.assertTrue(can_manage_gym_users(self.manager, self.gym))
        self.assertFalse(can_manage_gym_users(self.staff, self.gym))
        self.assertFalse(can_manage_gym_users(self.member, self.gym))

    # ------------------------------------------------------------------
    # User Update Permissions
    # ------------------------------------------------------------------

    def test_can_update_user_requester_without_membership(self):
        """Deny updates when the requester has no gym membership."""
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
        """Deny updates when the target user has no gym membership."""
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
        """Allow owners to update users with lower-level roles."""
        for target in (
            self.manager,
            self.staff,
            self.trainer,
            self.member,
        ):
            self.assertTrue(
                can_update_user(self.owner, target, self.gym)
            )

    def test_owner_cannot_update_owner(self):
        """Prevent owners from updating another owner."""
        self.assertFalse(
            can_update_user(self.owner, self.owner, self.gym)
        )

    def test_manager_can_update_lower_roles(self):
        """Allow managers to update users with lower-level roles."""
        for target in (
            self.staff,
            self.trainer,
            self.member,
        ):
            self.assertTrue(
                can_update_user(self.manager, target, self.gym)
            )

    def test_manager_cannot_update_owner_or_manager(self):
        """Prevent managers from updating owners or other managers."""
        self.assertFalse(
            can_update_user(self.manager, self.owner, self.gym)
        )
        self.assertFalse(
            can_update_user(self.manager, self.manager, self.gym)
        )

    def test_user_cannot_update_himself(self):
        """Prevent users from updating their own account."""
        self.assertFalse(
            can_update_user(self.member, self.member, self.gym)
        )

    def test_staff_cannot_update_users(self):
        """Prevent staff members from updating gym users."""
        self.assertFalse(
            can_update_user(self.staff, self.member, self.gym)
        )

    def test_cannot_update_user_from_other_gym(self):
        """Prevent users from updating members of another gym."""
        self.assertFalse(
            can_update_user(
                self.owner,
                self.other_member,
                self.gym,
            )
        )

    def test_superuser_can_update_any_user(self):
        """Allow superusers to update users across gyms."""
        self.assertTrue(
            can_update_user(
                self.admin,
                self.other_member,
                self.other_gym,
            )
        )

    # ------------------------------------------------------------------
    # User Delete Permissions
    # ------------------------------------------------------------------

    def test_owner_can_delete_non_owner(self):
        """Allow owners to delete users with lower-level roles."""
        for target in (
            self.manager,
            self.staff,
            self.trainer,
            self.member,
        ):
            self.assertTrue(
                can_delete_user(self.owner, target, self.gym)
            )

    def test_owner_cannot_delete_owner(self):
        """Prevent owners from deleting another owner."""
        self.assertFalse(
            can_delete_user(self.owner, self.owner, self.gym)
        )

    def test_manager_can_delete_lower_roles(self):
        """Allow managers to delete users with lower-level roles."""
        for target in (
            self.staff,
            self.trainer,
            self.member,
        ):
            self.assertTrue(
                can_delete_user(self.manager, target, self.gym)
            )

    def test_manager_cannot_delete_owner_or_manager(self):
        """Prevent managers from deleting owners or other managers."""
        self.assertFalse(
            can_delete_user(self.manager, self.owner, self.gym)
        )
        self.assertFalse(
            can_delete_user(self.manager, self.manager, self.gym)
        )

    def test_staff_cannot_delete_user(self):
        """Prevent staff members from deleting gym users."""
        self.assertFalse(
            can_delete_user(self.staff, self.member, self.gym)
        )

    def test_superuser_can_delete_any_user(self):
        """Allow superusers to delete users across gyms."""
        self.assertTrue(
            can_delete_user(
                self.admin,
                self.other_member,
                self.other_gym,
            )
        )

    # ------------------------------------------------------------------
    # Gym Class Permissions
    # ------------------------------------------------------------------

    def test_can_manage_gym_class(self):
        """Allow owners, managers, and staff to manage gym classes."""
        self.assertTrue(can_manage_gym_class(self.owner, self.gym))
        self.assertTrue(can_manage_gym_class(self.manager, self.gym))
        self.assertTrue(can_manage_gym_class(self.staff, self.gym))
        self.assertFalse(can_manage_gym_class(self.trainer, self.gym))
        self.assertFalse(can_manage_gym_class(self.member, self.gym))

    def test_can_manage_gym_class_superuser(self):
        """Allow superusers to manage classes in any gym."""
        self.assertTrue(
            can_manage_gym_class(self.admin, self.other_gym)
        )

    # ------------------------------------------------------------------
    # Trainer Helpers
    # ------------------------------------------------------------------

    def test_is_staff_of_gym(self):
        """Return True for non-trainer gym staff members."""
        self.assertTrue(is_staff_of_gym(self.owner, self.gym))
        self.assertTrue(is_staff_of_gym(self.manager, self.gym))
        self.assertTrue(is_staff_of_gym(self.staff, self.gym))
        self.assertFalse(is_staff_of_gym(self.trainer, self.gym))

    def test_is_class_trainer(self):
        """Return True only for the assigned class trainer."""
        self.assertTrue(
            is_class_trainer(self.trainer, self.gym_class)
        )
        self.assertFalse(
            is_class_trainer(self.staff, self.gym_class)
        )
        self.assertFalse(
            is_class_trainer(self.member, self.gym_class)
        )

    def test_is_class_trainer_wrong_class_trainer(self):
        """Return False when the user is not the class trainer."""
        self.assertFalse(
            is_class_trainer(self.owner, self.gym_class)
        )

    def test_is_class_trainer_wrong_gym(self):
        """Return False when the class belongs to another gym."""
        self.assertFalse(
            is_class_trainer(
                self.trainer,
                self.other_gym_class,
            )
        )

    def test_is_session_trainer(self):
        """Return True only for the trainer assigned to the session."""
        self.assertTrue(
            is_session_trainer(self.trainer, self.session)
        )
        self.assertFalse(
            is_session_trainer(self.staff, self.session)
        )

    def test_is_gym_class_trainer_alias(self):
        """Ensure the gym class trainer alias matches its source helper."""
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

    # ------------------------------------------------------------------
    # Session Permissions
    # ------------------------------------------------------------------

    def test_can_access_session_staff(self):
        """Allow owners, managers, and staff to access sessions."""
        self.assertTrue(can_access_session(self.owner, self.session))
        self.assertTrue(can_access_session(self.manager, self.session))
        self.assertTrue(can_access_session(self.staff, self.session))

    def test_can_access_session_trainer(self):
        """Allow the assigned trainer to access a session."""
        self.assertTrue(
            can_access_session(self.trainer, self.session)
        )

    def test_member_cannot_access_session(self):
        """Prevent regular members from accessing sessions."""
        self.assertFalse(
            can_access_session(self.member, self.session)
        )

    def test_superuser_can_access_session(self):
        """Allow superusers to access any session."""
        self.assertTrue(
            can_access_session(self.admin, self.session)
        )

    def test_can_create_session(self):
        """Allow authorized gym staff and trainers to create sessions."""
        self.assertTrue(
            can_create_session(self.owner, self.gym_class)
        )
        self.assertTrue(
            can_create_session(self.manager, self.gym_class)
        )
        self.assertTrue(
            can_create_session(self.staff, self.gym_class)
        )
        self.assertTrue(
            can_create_session(self.trainer, self.gym_class)
        )
        self.assertFalse(
            can_create_session(self.member, self.gym_class)
        )

    def test_superuser_can_create_session(self):
        """Allow superusers to create sessions."""
        self.assertTrue(
            can_create_session(self.admin, self.gym_class)
        )

    def test_can_delete_session(self):
        """Allow gym staff to delete sessions but not trainers or members."""
        self.assertTrue(
            can_delete_session(self.owner, self.session)
        )
        self.assertTrue(
            can_delete_session(self.manager, self.session)
        )
        self.assertTrue(
            can_delete_session(self.staff, self.session)
        )
        self.assertFalse(
            can_delete_session(self.trainer, self.session)
        )
        self.assertFalse(
            can_delete_session(self.member, self.session)
        )

    def test_can_access_session_session_trainer_only(self):
        """Allow the trainer assigned directly to the session."""
        self.assertTrue(
            can_access_session(
                self.second_trainer,
                self.session_only_trainer,
            )
        )

    def test_superuser_can_delete_session(self):
        """Allow superusers to delete sessions."""
        self.assertTrue(
            can_delete_session(self.admin, self.session)
        )

    # ------------------------------------------------------------------
    # Enrollment Permissions
    # ------------------------------------------------------------------

    def test_can_access_gym_enrollments(self):
        """Allow owners, managers, and staff to access enrollments."""
        self.assertTrue(
            can_access_gym_enrollments(self.owner, self.gym)
        )
        self.assertTrue(
            can_access_gym_enrollments(self.manager, self.gym)
        )
        self.assertTrue(
            can_access_gym_enrollments(self.staff, self.gym)
        )
        self.assertFalse(
            can_access_gym_enrollments(self.trainer, self.gym)
        )
        self.assertFalse(
            can_access_gym_enrollments(self.member, self.gym)
        )

    def test_superuser_can_access_gym_enrollments(self):
        """Allow superusers to access enrollments in any gym."""
        self.assertTrue(
            can_access_gym_enrollments(
                self.admin,
                self.other_gym,
            )
        )

    def test_can_manage_enrollment(self):
        """Allow gym staff to manage enrollments."""
        self.assertTrue(
            can_manage_enrollment(self.owner, self.enrollment)
        )
        self.assertTrue(
            can_manage_enrollment(self.manager, self.enrollment)
        )
        self.assertTrue(
            can_manage_enrollment(self.staff, self.enrollment)
        )
        self.assertFalse(
            can_manage_enrollment(self.trainer, self.enrollment)
        )
        self.assertFalse(
            can_manage_enrollment(self.member, self.enrollment)
        )

    def test_superuser_can_manage_enrollment(self):
        """Allow superusers to manage enrollments."""
        self.assertTrue(
            can_manage_enrollment(self.admin, self.enrollment)
        )

    def test_can_create_enrollment(self):
        """Allow gym staff to create enrollments for members."""
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
        """Allow members to create enrollments for themselves."""
        self.assertTrue(
            can_create_enrollment(
                self.member,
                self.gym,
                self.member,
            )
        )

    def test_member_cannot_create_enrollment_for_other_user(self):
        """Prevent members from creating enrollments for other users."""
        self.assertFalse(
            can_create_enrollment(
                self.member,
                self.gym,
                self.other_member,
            )
        )

    def test_member_without_target_user_cannot_create_enrollment(self):
        """Prevent members from creating enrollment without a target user."""
        self.assertFalse(
            can_create_enrollment(
                self.member,
                self.gym,
            )
        )

    def test_superuser_can_create_enrollment(self):
        """Allow superusers to create enrollments in any gym."""
        self.assertTrue(
            can_create_enrollment(
                self.admin,
                self.other_gym,
                self.other_member,
            )
        )

    def test_can_cancel_enrollment(self):
        """Allow enrollment owners and gym staff to cancel enrollments."""
        self.assertTrue(
            can_cancel_enrollment(
                self.member,
                self.enrollment,
            )
        )
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
        """Prevent unrelated members from cancelling an enrollment."""
        self.assertFalse(
            can_cancel_enrollment(
                self.other_member,
                self.enrollment,
            )
        )

    def test_superuser_can_cancel_enrollment(self):
        """Allow superusers to cancel enrollments."""
        self.assertTrue(
            can_cancel_enrollment(
                self.admin,
                self.enrollment,
            )
        )

    # ------------------------------------------------------------------
    # Payment Permissions
    # ------------------------------------------------------------------

    def test_can_access_gym_payments(self):
        """Allow owners, managers, and staff to access gym payments."""
        self.assertTrue(
            can_access_gym_payments(self.owner, self.gym)
        )
        self.assertTrue(
            can_access_gym_payments(self.manager, self.gym)
        )
        self.assertTrue(
            can_access_gym_payments(self.staff, self.gym)
        )
        self.assertFalse(
            can_access_gym_payments(self.trainer, self.gym)
        )
        self.assertFalse(
            can_access_gym_payments(self.member, self.gym)
        )

    def test_superuser_can_access_gym_payments(self):
        """Allow superusers to access payments in any gym."""
        self.assertTrue(
            can_access_gym_payments(
                self.admin,
                self.other_gym,
            )
        )

    def test_can_manage_payment(self):
        """Allow gym staff to manage payments."""
        self.assertTrue(
            can_manage_payment(self.owner, self.payment)
        )
        self.assertTrue(
            can_manage_payment(self.manager, self.payment)
        )
        self.assertTrue(
            can_manage_payment(self.staff, self.payment)
        )
        self.assertFalse(
            can_manage_payment(self.trainer, self.payment)
        )
        self.assertFalse(
            can_manage_payment(self.member, self.payment)
        )

    def test_superuser_can_manage_payment(self):
        """Allow superusers to manage payments."""
        self.assertTrue(
            can_manage_payment(self.admin, self.payment)
        )

    def test_can_confirm_payment(self):
        """Allow gym staff to confirm payments."""
        self.assertTrue(
            can_confirm_payment(self.owner, self.payment)
        )
        self.assertTrue(
            can_confirm_payment(self.manager, self.payment)
        )
        self.assertTrue(
            can_confirm_payment(self.staff, self.payment)
        )
        self.assertFalse(
            can_confirm_payment(self.trainer, self.payment)
        )
        self.assertFalse(
            can_confirm_payment(self.member, self.payment)
        )

    def test_superuser_can_confirm_payment(self):
        """Allow superusers to confirm payments."""
        self.assertTrue(
            can_confirm_payment(self.admin, self.payment)
        )

    # ------------------------------------------------------------------
    # Class Membership
    # ------------------------------------------------------------------

    def test_is_class_member(self):
        """Return True for users enrolled in the specified class."""
        self.assertTrue(
            is_class_member(self.member, self.gym_class)
        )
        self.assertFalse(
            is_class_member(self.other_member, self.gym_class)
        )

    def test_is_class_member_wrong_class(self):
        """Return False when the enrollment belongs to another class."""
        self.assertFalse(
            is_class_member(self.member, self.other_gym_class)
        )

    # ------------------------------------------------------------------
    # Gym Employee
    # ------------------------------------------------------------------

    def test_is_gym_employee(self):
        """Return True for owners, managers, and staff members."""
        self.assertTrue(is_gym_employee(self.owner))
        self.assertTrue(is_gym_employee(self.manager))
        self.assertTrue(is_gym_employee(self.staff))
        self.assertFalse(is_gym_employee(self.trainer))
        self.assertFalse(is_gym_employee(self.member))

    def test_is_gym_employee_across_gyms(self):
        """Return True for employees regardless of their gym."""
        self.assertTrue(
            is_gym_employee(self.other_staff)
        )

    # ------------------------------------------------------------------
    # Unauthenticated Users
    # ------------------------------------------------------------------

    def test_unauthenticated_user_is_denied(self):
        """Deny unauthenticated users from protected permission helpers."""
        anonymous = AnonymousUser()

        self.assertFalse(
            is_owner_or_manager(anonymous, self.gym)
        )
        self.assertFalse(
            is_staff(anonymous, self.gym)
        )
        self.assertFalse(
            is_gym_owner_or_manager(anonymous, self.gym)
        )
        self.assertFalse(
            is_gym_staff(anonymous, self.gym)
        )
        self.assertFalse(
            is_gym_owner(anonymous, self.gym)
        )
        self.assertFalse(
            can_manage_any_gym(anonymous)
        )
        self.assertFalse(
            can_manage_gym(anonymous, self.gym)
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