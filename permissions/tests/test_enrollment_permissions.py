from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from classes.models import GymClass
from enrollments.models import Enrollment, Payment
from gyms.models import Gym, GymMembership

from permissions.enrollment_permissions import (
    CanCancelEnrollment,
    CanCreateEnrollment,
    CanManageEnrollment,
    CanViewEnrollment,
    CanConfirmPayment,
    CanCreatePayment,
    CanManagePayment,
    CanViewPayment,
)


User = get_user_model()


class EnrollmentPermissionTest(TestCase):
    """Test permissions related to gym class enrollments."""

    def setUp(self):
        """Create users, memberships, gym class, and enrollment fixtures."""
        self.factory = APIRequestFactory()

        # --------------------------------------------------
        # Gyms
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Users
        # --------------------------------------------------

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

        self.member = User.objects.create_user(
            username="member",
            password="Test1234",
        )

        self.other_member = User.objects.create_user(
            username="other_member",
            password="Test1234",
        )

        self.superuser = User.objects.create_superuser(
            username="admin",
            password="Test1234",
        )

        # --------------------------------------------------
        # Memberships
        # --------------------------------------------------

        GymMembership.objects.create(
            user=self.owner,
            gym=self.gym,
            role=GymMembership.Role.OWNER,
            share_percentage=50,
        )

        GymMembership.objects.create(
            user=self.manager,
            gym=self.gym,
            role=GymMembership.Role.MANAGER,
            salary=1000,
        )

        GymMembership.objects.create(
            user=self.staff,
            gym=self.gym,
            role=GymMembership.Role.STAFF,
            salary=800,
        )

        GymMembership.objects.create(
            user=self.trainer,
            gym=self.gym,
            role=GymMembership.Role.TRAINER,
            salary=900,
        )

        GymMembership.objects.create(
            user=self.member,
            gym=self.gym,
            role=GymMembership.Role.MEMBER,
        )

        GymMembership.objects.create(
            user=self.other_member,
            gym=self.other_gym,
            role=GymMembership.Role.MEMBER,
        )

        # --------------------------------------------------
        # Gym Class
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Enrollment
        # --------------------------------------------------

        self.enrollment = Enrollment.objects.create(
            gym_class=self.gym_class,
            user=self.member,
            status="approved",
            enrollment_type="semester",
        )

    def make_request(self, user, method="get", data=None):
        """
        Create a basic Django test request for permission testing.

        Args:
            user: User assigned to the request.
            method: HTTP method used to create the request.
            data: Optional request payload.

        Returns:
            HttpRequest: Configured test request.
        """
        request = getattr(self.factory, method)(
            f"/api/gyms/{self.gym.id}/enrollments/",
            data=data or {},
            format="json",
        )

        request.user = user

        return request

    def make_drf_request(self, user, method="post", data=None):
        """
        Create a DRF Request object with JSON parsing support.

        This helper is useful when the permission class accesses
        request.data directly.
        """
        request = getattr(self.factory, method)(
            f"/api/gyms/{self.gym.id}/enrollments/",
            data=data or {},
            format="json",
        )

        request = Request(
            request,
            parsers=[JSONParser()],
        )

        request.user = user

        return request

    def make_view(self, gym_id=None):
        """
        Create a minimal mock view containing the requested gym ID.

        Args:
            gym_id: Gym ID that should be available in view.kwargs.

        Returns:
            MockView: Minimal view object for permission testing.
        """

        class MockView:
            """Minimal view object used by permission tests."""

            pass

        view = MockView()

        view.kwargs = {
            "gym_id": gym_id or self.gym.id,
        }

        return view

    # ==================================================
    # CanViewEnrollment
    # ==================================================

    def test_owner_can_view_enrollments(self):
        """Owners can view enrollments of their gym."""
        request = self.make_request(self.owner)
        view = self.make_view()

        self.assertTrue(
            CanViewEnrollment().has_permission(
                request,
                view,
            )
        )

    def test_manager_can_view_enrollments(self):
        """Managers can view enrollments of their gym."""
        request = self.make_request(self.manager)
        view = self.make_view()

        self.assertTrue(
            CanViewEnrollment().has_permission(
                request,
                view,
            )
        )

    def test_staff_can_view_enrollments(self):
        """Staff members can view enrollments of their gym."""
        request = self.make_request(self.staff)
        view = self.make_view()

        self.assertTrue(
            CanViewEnrollment().has_permission(
                request,
                view,
            )
        )

    def test_trainer_cannot_view_enrollments(self):
        """Trainers cannot view gym enrollments."""
        request = self.make_request(self.trainer)
        view = self.make_view()

        self.assertFalse(
            CanViewEnrollment().has_permission(
                request,
                view,
            )
        )

    def test_member_cannot_view_enrollments(self):
        """Members cannot view all gym enrollments."""
        request = self.make_request(self.member)
        view = self.make_view()

        self.assertFalse(
            CanViewEnrollment().has_permission(
                request,
                view,
            )
        )

    def test_unauthenticated_user_cannot_view_enrollments(self):
        """Unauthenticated users cannot view gym enrollments."""
        request = self.make_request(self.member)
        request.user = AnonymousUser()

        view = self.make_view()

        self.assertFalse(
            CanViewEnrollment().has_permission(
                request,
                view,
            )
        )

    def test_superuser_can_view_enrollments(self):
        """Superusers can view enrollments regardless of gym membership."""
        request = self.make_request(self.superuser)
        view = self.make_view()

        self.assertTrue(
            CanViewEnrollment().has_permission(
                request,
                view,
            )
        )

    def test_user_cannot_view_enrollments_of_other_gym(self):
        """Users cannot view enrollments belonging to another gym."""
        request = self.make_request(self.owner)

        view = self.make_view(
            gym_id=self.other_gym.id,
        )

        self.assertFalse(
            CanViewEnrollment().has_permission(
                request,
                view,
            )
        )

    # ==================================================
    # CanCreateEnrollment
    # ==================================================

    def test_owner_can_create_enrollment_for_user(self):
        """Owners can create enrollments for gym users."""
        request = self.make_drf_request(
            self.owner,
            data={"user_id": self.member.id},
        )

        view = self.make_view()

        self.assertTrue(
            CanCreateEnrollment().has_permission(
                request,
                view,
            )
        )

    def test_manager_can_create_enrollment(self):
        """Managers can create enrollments."""
        request = self.make_drf_request(
            self.manager,
            data={"user_id": self.member.id},
        )

        view = self.make_view()

        self.assertTrue(
            CanCreateEnrollment().has_permission(
                request,
                view,
            )
        )

    def test_staff_can_create_enrollment(self):
        """Staff members can create enrollments."""
        request = self.make_drf_request(
            self.staff,
            data={"user_id": self.member.id},
        )

        view = self.make_view()

        self.assertTrue(
            CanCreateEnrollment().has_permission(
                request,
                view,
            )
        )

    def test_member_can_create_enrollment_for_himself(self):
        """Members can create an enrollment for themselves."""
        request = self.make_drf_request(
            self.member,
            data={"user_id": self.member.id},
        )

        view = self.make_view()

        self.assertTrue(
            CanCreateEnrollment().has_permission(
                request,
                view,
            )
        )

    def test_member_can_create_enrollment_without_user_id(self):
        """Members can create an enrollment without specifying a user ID."""
        request = self.make_drf_request(
            self.member,
            data={},
        )

        view = self.make_view()

        self.assertTrue(
            CanCreateEnrollment().has_permission(
                request,
                view,
            )
        )

    def test_member_cannot_create_enrollment_for_other_user(self):
        """Members cannot create enrollments for other users."""
        request = self.make_drf_request(
            self.member,
            data={"user_id": self.other_member.id},
        )

        view = self.make_view()

        self.assertFalse(
            CanCreateEnrollment().has_permission(
                request,
                view,
            )
        )

    def test_trainer_cannot_create_enrollment(self):
        """Trainers cannot create enrollments."""
        request = self.make_drf_request(
            self.trainer,
            data={"user_id": self.member.id},
        )

        view = self.make_view()

        self.assertFalse(
            CanCreateEnrollment().has_permission(
                request,
                view,
            )
        )

    def test_superuser_can_create_enrollment(self):
        """Superusers can create enrollments."""
        request = self.make_drf_request(
            self.superuser,
            data={"user_id": self.member.id},
        )

        view = self.make_view()

        self.assertTrue(
            CanCreateEnrollment().has_permission(
                request,
                view,
            )
        )

    def test_create_enrollment_fails_for_nonexistent_user(self):
        """Enrollment creation is denied for a nonexistent user."""
        request = self.make_drf_request(
            self.owner,
            data={"user_id": 999999},
        )

        view = self.make_view()

        self.assertFalse(
            CanCreateEnrollment().has_permission(
                request,
                view,
            )
        )

    # ==================================================
    # CanManageEnrollment
    # ==================================================

    def test_owner_can_manage_enrollment(self):
        """Owners can manage enrollments."""
        request = self.make_request(self.owner)
        view = self.make_view()

        self.assertTrue(
            CanManageEnrollment().has_object_permission(
                request,
                view,
                self.enrollment,
            )
        )

    def test_manager_can_manage_enrollment(self):
        """Managers can manage enrollments."""
        request = self.make_request(self.manager)
        view = self.make_view()

        self.assertTrue(
            CanManageEnrollment().has_object_permission(
                request,
                view,
                self.enrollment,
            )
        )

    def test_staff_can_manage_enrollment(self):
        """Staff members can manage enrollments."""
        request = self.make_request(self.staff)
        view = self.make_view()

        self.assertTrue(
            CanManageEnrollment().has_object_permission(
                request,
                view,
                self.enrollment,
            )
        )

    def test_trainer_cannot_manage_enrollment(self):
        """Trainers cannot manage enrollments."""
        request = self.make_request(self.trainer)
        view = self.make_view()

        self.assertFalse(
            CanManageEnrollment().has_object_permission(
                request,
                view,
                self.enrollment,
            )
        )

    def test_member_cannot_manage_enrollment(self):
        """Members cannot manage enrollments."""
        request = self.make_request(self.member)
        view = self.make_view()

        self.assertFalse(
            CanManageEnrollment().has_object_permission(
                request,
                view,
                self.enrollment,
            )
        )

    def test_superuser_can_manage_enrollment(self):
        """Superusers can manage enrollments."""
        request = self.make_request(self.superuser)
        view = self.make_view()

        self.assertTrue(
            CanManageEnrollment().has_object_permission(
                request,
                view,
                self.enrollment,
            )
        )

    # ==================================================
    # CanCancelEnrollment
    # ==================================================

    def test_owner_can_cancel_enrollment(self):
        """Owners can cancel enrollments."""
        request = self.make_request(self.owner)
        view = self.make_view()

        self.assertTrue(
            CanCancelEnrollment().has_object_permission(
                request,
                view,
                self.enrollment,
            )
        )

    def test_manager_can_cancel_enrollment(self):
        """Managers can cancel enrollments."""
        request = self.make_request(self.manager)
        view = self.make_view()

        self.assertTrue(
            CanCancelEnrollment().has_object_permission(
                request,
                view,
                self.enrollment,
            )
        )

    def test_staff_can_cancel_enrollment(self):
        """Staff members can cancel enrollments."""
        request = self.make_request(self.staff)
        view = self.make_view()

        self.assertTrue(
            CanCancelEnrollment().has_object_permission(
                request,
                view,
                self.enrollment,
            )
        )

    def test_member_can_cancel_his_own_enrollment(self):
        """Members can cancel their own enrollments."""
        request = self.make_request(self.member)
        view = self.make_view()

        self.assertTrue(
            CanCancelEnrollment().has_object_permission(
                request,
                view,
                self.enrollment,
            )
        )

    def test_trainer_cannot_cancel_enrollment(self):
        """Trainers cannot cancel enrollments."""
        request = self.make_request(self.trainer)
        view = self.make_view()

        self.assertFalse(
            CanCancelEnrollment().has_object_permission(
                request,
                view,
                self.enrollment,
            )
        )

    def test_superuser_can_cancel_enrollment(self):
        """Superusers can cancel enrollments."""
        request = self.make_request(self.superuser)
        view = self.make_view()

        self.assertTrue(
            CanCancelEnrollment().has_object_permission(
                request,
                view,
                self.enrollment,
            )
        )


class PaymentPermissionTest(TestCase):
    """Test permissions related to payment management."""

    def setUp(self):
        """Create users, memberships, enrollment, and payment fixtures."""
        self.factory = APIRequestFactory()

        # --------------------------------------------------
        # Gyms
        # --------------------------------------------------

        self.gym = Gym.objects.create(
            name="Payment Gym",
            address="Tehran",
            phone="09223456789",
            email="payment@gym.com",
        )

        self.other_gym = Gym.objects.create(
            name="Other Payment Gym",
            address="Tehran",
            phone="09223456788",
            email="otherpayment@gym.com",
        )

        # --------------------------------------------------
        # Users
        # --------------------------------------------------

        self.owner = User.objects.create_user(
            username="payment_owner",
            password="Test1234",
        )

        self.manager = User.objects.create_user(
            username="payment_manager",
            password="Test1234",
        )

        self.staff = User.objects.create_user(
            username="payment_staff",
            password="Test1234",
        )

        self.trainer = User.objects.create_user(
            username="payment_trainer",
            password="Test1234",
        )

        self.member = User.objects.create_user(
            username="payment_member",
            password="Test1234",
        )

        self.superuser = User.objects.create_superuser(
            username="payment_admin",
            password="Test1234",
        )

        # --------------------------------------------------
        # Memberships
        # --------------------------------------------------

        GymMembership.objects.create(
            user=self.owner,
            gym=self.gym,
            role=GymMembership.Role.OWNER,
            share_percentage=50,
        )

        GymMembership.objects.create(
            user=self.manager,
            gym=self.gym,
            role=GymMembership.Role.MANAGER,
            salary=1000,
        )

        GymMembership.objects.create(
            user=self.staff,
            gym=self.gym,
            role=GymMembership.Role.STAFF,
            salary=800,
        )

        GymMembership.objects.create(
            user=self.trainer,
            gym=self.gym,
            role=GymMembership.Role.TRAINER,
            salary=900,
        )

        GymMembership.objects.create(
            user=self.member,
            gym=self.gym,
            role=GymMembership.Role.MEMBER,
        )

        # --------------------------------------------------
        # Gym Class
        # --------------------------------------------------

        self.gym_class = GymClass.objects.create(
            name="Payment Class",
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

        # --------------------------------------------------
        # Enrollment
        # --------------------------------------------------

        self.enrollment = Enrollment.objects.create(
            gym_class=self.gym_class,
            user=self.member,
            status="approved",
            enrollment_type="semester",
        )

        # --------------------------------------------------
        # Payment
        # --------------------------------------------------

        self.payment = Payment.objects.create(
            enrollment=self.enrollment,
            amount=1000,
            status="pending",
        )

    def make_request(self, user):
        """Create a GET request for payment permission tests."""
        request = self.factory.get(
            f"/api/gyms/{self.gym.id}/payments/",
        )

        request.user = user

        return request

    def make_view(self, gym_id=None):
        """
        Create a minimal mock view containing the requested gym ID.

        Args:
            gym_id: Gym ID that should be available in view.kwargs.

        Returns:
            MockView: Minimal view object for permission testing.
        """

        class MockView:
            """Minimal view object used by payment permission tests."""

            pass

        view = MockView()

        view.kwargs = {
            "gym_id": gym_id or self.gym.id,
        }

        return view

    # ==================================================
    # CanViewPayment
    # ==================================================

    def test_owner_can_view_payment(self):
        """Owners can view payments of their gym."""
        request = self.make_request(self.owner)
        view = self.make_view()

        self.assertTrue(
            CanViewPayment().has_permission(
                request,
                view,
            )
        )

    def test_manager_can_view_payment(self):
        """Managers can view payments of their gym."""
        request = self.make_request(self.manager)
        view = self.make_view()

        self.assertTrue(
            CanViewPayment().has_permission(
                request,
                view,
            )
        )

    def test_staff_can_view_payment(self):
        """Staff members can view payments of their gym."""
        request = self.make_request(self.staff)
        view = self.make_view()

        self.assertTrue(
            CanViewPayment().has_permission(
                request,
                view,
            )
        )

    def test_trainer_cannot_view_payment(self):
        """Trainers cannot view gym payments."""
        request = self.make_request(self.trainer)
        view = self.make_view()

        self.assertFalse(
            CanViewPayment().has_permission(
                request,
                view,
            )
        )

    def test_member_cannot_view_payment(self):
        """Members cannot view gym payments."""
        request = self.make_request(self.member)
        view = self.make_view()

        self.assertFalse(
            CanViewPayment().has_permission(
                request,
                view,
            )
        )

    def test_superuser_can_view_payment(self):
        """Superusers can view payments."""
        request = self.make_request(self.superuser)
        view = self.make_view()

        self.assertTrue(
            CanViewPayment().has_permission(
                request,
                view,
            )
        )

    # ==================================================
    # CanCreatePayment
    # ==================================================

    def test_owner_can_create_payment(self):
        """Owners can create payments."""
        request = self.make_request(self.owner)
        view = self.make_view()

        self.assertTrue(
            CanCreatePayment().has_permission(
                request,
                view,
            )
        )

    def test_manager_can_create_payment(self):
        """Managers can create payments."""
        request = self.make_request(self.manager)
        view = self.make_view()

        self.assertTrue(
            CanCreatePayment().has_permission(
                request,
                view,
            )
        )

    def test_staff_can_create_payment(self):
        """Staff members can create payments."""
        request = self.make_request(self.staff)
        view = self.make_view()

        self.assertTrue(
            CanCreatePayment().has_permission(
                request,
                view,
            )
        )

    def test_trainer_cannot_create_payment(self):
        """Trainers cannot create payments."""
        request = self.make_request(self.trainer)
        view = self.make_view()

        self.assertFalse(
            CanCreatePayment().has_permission(
                request,
                view,
            )
        )

    def test_member_cannot_create_payment(self):
        """Members cannot create payments."""
        request = self.make_request(self.member)
        view = self.make_view()

        self.assertFalse(
            CanCreatePayment().has_permission(
                request,
                view,
            )
        )

    def test_superuser_can_create_payment(self):
        """Superusers can create payments."""
        request = self.make_request(self.superuser)
        view = self.make_view()

        self.assertTrue(
            CanCreatePayment().has_permission(
                request,
                view,
            )
        )

    # ==================================================
    # CanManagePayment
    # ==================================================

    def test_owner_can_manage_payment(self):
        """Owners can manage payments."""
        request = self.make_request(self.owner)
        view = self.make_view()

        self.assertTrue(
            CanManagePayment().has_object_permission(
                request,
                view,
                self.payment,
            )
        )

    def test_manager_can_manage_payment(self):
        """Managers can manage payments."""
        request = self.make_request(self.manager)
        view = self.make_view()

        self.assertTrue(
            CanManagePayment().has_object_permission(
                request,
                view,
                self.payment,
            )
        )

    def test_staff_can_manage_payment(self):
        """Staff members can manage payments."""
        request = self.make_request(self.staff)
        view = self.make_view()

        self.assertTrue(
            CanManagePayment().has_object_permission(
                request,
                view,
                self.payment,
            )
        )

    def test_trainer_cannot_manage_payment(self):
        """Trainers cannot manage payments."""
        request = self.make_request(self.trainer)
        view = self.make_view()

        self.assertFalse(
            CanManagePayment().has_object_permission(
                request,
                view,
                self.payment,
            )
        )

    def test_member_cannot_manage_payment(self):
        """Members cannot manage payments."""
        request = self.make_request(self.member)
        view = self.make_view()

        self.assertFalse(
            CanManagePayment().has_object_permission(
                request,
                view,
                self.payment,
            )
        )

    def test_superuser_can_manage_payment(self):
        """Superusers can manage payments."""
        request = self.make_request(self.superuser)
        view = self.make_view()

        self.assertTrue(
            CanManagePayment().has_object_permission(
                request,
                view,
                self.payment,
            )
        )

    # ==================================================
    # CanConfirmPayment
    # ==================================================

    def test_owner_can_confirm_payment(self):
        """Owners can confirm payments."""
        request = self.make_request(self.owner)
        view = self.make_view()

        self.assertTrue(
            CanConfirmPayment().has_object_permission(
                request,
                view,
                self.payment,
            )
        )

    def test_manager_can_confirm_payment(self):
        """Managers can confirm payments."""
        request = self.make_request(self.manager)
        view = self.make_view()

        self.assertTrue(
            CanConfirmPayment().has_object_permission(
                request,
                view,
                self.payment,
            )
        )

    def test_staff_can_confirm_payment(self):
        """Staff members can confirm payments."""
        request = self.make_request(self.staff)
        view = self.make_view()

        self.assertTrue(
            CanConfirmPayment().has_object_permission(
                request,
                view,
                self.payment,
            )
        )

    def test_trainer_cannot_confirm_payment(self):
        """Trainers cannot confirm payments."""
        request = self.make_request(self.trainer)
        view = self.make_view()

        self.assertFalse(
            CanConfirmPayment().has_object_permission(
                request,
                view,
                self.payment,
            )
        )

    def test_member_cannot_confirm_payment(self):
        """Members cannot confirm payments."""
        request = self.make_request(self.member)
        view = self.make_view()

        self.assertFalse(
            CanConfirmPayment().has_object_permission(
                request,
                view,
                self.payment,
            )
        )

    def test_superuser_can_confirm_payment(self):
        """Superusers can confirm payments."""
        request = self.make_request(self.superuser)
        view = self.make_view()

        self.assertTrue(
            CanConfirmPayment().has_object_permission(
                request,
                view,
                self.payment,
            )
        )