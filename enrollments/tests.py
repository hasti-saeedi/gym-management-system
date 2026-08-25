from decimal import Decimal
from datetime import datetime

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.exceptions import NotFound


from accounts.models import CustomUser
from gyms.models import Gym, GymMembership
from classes.models import GymClass, ClassSession
from enrollments.models import Enrollment, Payment

from enrollments.services.enrollment_services import (
    create_enrollment,
    cancel_enrollment_service,
)

from enrollments.services.payment_services import (
    create_payment,
    confirm_payment,
)


# =========================================================
# Enrollment Model Tests
# =========================================================

class EnrollmentModelTest(TestCase):

    def setUp(self):

        self.user = CustomUser.objects.create_user(
            username="member1",
            password="Test1234",
        )

        self.trainer = CustomUser.objects.create_user(
            username="trainer1",
            password="Test1234",
        )

        self.gym = Gym.objects.create(
            name="Test Gym",
            address="Test Address",
        )

        GymMembership.objects.create(
            user=self.trainer,
            gym=self.gym,
            role=GymMembership.Role.TRAINER,
            salary=Decimal("10000.00"),
        )

        self.gym_class = GymClass.objects.create(
            name="Yoga Class",
            category="yoga",
            gym=self.gym,
            trainer=self.trainer,
            capacity=20,
            price=Decimal("500000.00"),
            single_session_price=Decimal("100000.00"),
            regular_days=[],
        )

    def test_create_enrollment(self):

        enrollment = Enrollment.objects.create(
            gym_class=self.gym_class,
            user=self.user,
        )

        self.assertEqual(
            enrollment.gym_class,
            self.gym_class,
        )

        self.assertEqual(
            enrollment.user,
            self.user,
        )

    def test_status_default_is_pending(self):

        enrollment = Enrollment.objects.create(
            gym_class=self.gym_class,
            user=self.user,
        )

        self.assertEqual(
            enrollment.status,
            "pending",
        )

    def test_attended_default_is_false(self):

        enrollment = Enrollment.objects.create(
            gym_class=self.gym_class,
            user=self.user,
        )

        self.assertFalse(
            enrollment.attended
        )

    def test_enrollment_type_default_is_semester(self):

        enrollment = Enrollment.objects.create(
            gym_class=self.gym_class,
            user=self.user,
        )

        self.assertEqual(
            enrollment.enrollment_type,
            "semester",
        )

    def test_enrollment_str(self):

        enrollment = Enrollment.objects.create(
            gym_class=self.gym_class,
            user=self.user,
            status="approved",
        )

        self.assertEqual(
            str(enrollment),
            "member1 - Yoga Class - approved",
        )

    def test_user_cannot_enroll_twice_in_same_class(self):

        Enrollment.objects.create(
            gym_class=self.gym_class,
            user=self.user,
        )

        enrollment = Enrollment(
            gym_class=self.gym_class,
            user=self.user,
        )

        # Model validation
        with self.assertRaises(DjangoValidationError):
            enrollment.full_clean()

    def test_single_session_can_be_selected(self):

        session = ClassSession.objects.create(
            gym_class=self.gym_class,
            start_time=timezone.make_aware(
                datetime(2026, 8, 20, 10, 0)
            ),
            end_time=timezone.make_aware(
                datetime(2026, 8, 20, 11, 0)
            ),
            trainer=self.trainer,
        )

        enrollment = Enrollment.objects.create(
            gym_class=self.gym_class,
            user=self.user,
            enrollment_type="single",
        )

        enrollment.selected_sessions.add(
            session
        )

        self.assertIn(
            session,
            enrollment.selected_sessions.all(),
        )


# =========================================================
# Enrollment Service Tests
# =========================================================

class EnrollmentServiceTest(TestCase):

    def setUp(self):

        self.member = CustomUser.objects.create_user(
            username="member1",
            password="Test1234",
        )

        self.trainer = CustomUser.objects.create_user(
            username="trainer1",
            password="Test1234",
        )

        self.gym = Gym.objects.create(
            name="Test Gym",
            address="Test Address",
        )

        GymMembership.objects.create(
            user=self.member,
            gym=self.gym,
            role=GymMembership.Role.MEMBER,
        )

        GymMembership.objects.create(
            user=self.trainer,
            gym=self.gym,
            role=GymMembership.Role.TRAINER,
            salary=Decimal("10000"),
        )

        self.gym_class = GymClass.objects.create(
            name="Yoga",
            category="yoga",
            gym=self.gym,
            trainer=self.trainer,
            capacity=10,
            current_enrolled=0,
            price=Decimal("500000"),
            single_session_price=Decimal("100000"),
            regular_days=[],
        )

    def test_create_semester_enrollment(self):

        enrollment = create_enrollment(
            user=self.member,
            gym_class_id=self.gym_class.id,
            enrollment_type="semester",
        )

        self.assertEqual(
            enrollment.user,
            self.member,
        )

        self.assertEqual(
            enrollment.gym_class,
            self.gym_class,
        )

        self.assertEqual(
            enrollment.enrollment_type,
            "semester",
        )

        self.assertEqual(
            enrollment.status,
            "pending",
        )

        self.assertTrue(
            Payment.objects.filter(
                enrollment=enrollment
            ).exists()
        )

    def test_create_enrollment_class_not_found(self):

        with self.assertRaises(NotFound):
            create_enrollment(
                user=self.member,
                gym_class_id=99999,
                enrollment_type="semester",
            )

    def test_cannot_enroll_in_inactive_class(self):

        self.gym_class.is_active = False
        self.gym_class.save()

        # Service validation
        with self.assertRaises(DRFValidationError):
            create_enrollment(
                user=self.member,
                gym_class_id=self.gym_class.id,
                enrollment_type="semester",
            )

    def test_non_member_cannot_enroll(self):

        another_user = CustomUser.objects.create_user(
            username="another",
            password="Test1234",
        )

        with self.assertRaises(DRFValidationError):
            create_enrollment(
                user=another_user,
                gym_class_id=self.gym_class.id,
                enrollment_type="semester",
            )

    def test_trainer_cannot_enroll_in_own_class(self):

        with self.assertRaises(DRFValidationError):
            create_enrollment(
                user=self.trainer,
                gym_class_id=self.gym_class.id,
                enrollment_type="semester",
            )

    def test_duplicate_enrollment_is_not_allowed(self):

        create_enrollment(
            user=self.member,
            gym_class_id=self.gym_class.id,
            enrollment_type="semester",
        )

        with self.assertRaises(DRFValidationError):
            create_enrollment(
                user=self.member,
                gym_class_id=self.gym_class.id,
                enrollment_type="semester",
            )

    def test_cannot_enroll_when_class_is_full(self):

        self.gym_class.current_enrolled = self.gym_class.capacity
        self.gym_class.save()

        with self.assertRaises(DRFValidationError):
            create_enrollment(
                user=self.member,
                gym_class_id=self.gym_class.id,
                enrollment_type="semester",
            )

    def create_session(self):

        return ClassSession.objects.create(
            gym_class=self.gym_class,
            start_time=timezone.make_aware(
                datetime(2026, 8, 20, 10, 0)
            ),
            end_time=timezone.make_aware(
                datetime(2026, 8, 20, 11, 0)
            ),
            trainer=self.trainer,
        )

    def test_create_single_enrollment(self):

        session = self.create_session()

        enrollment = create_enrollment(
            user=self.member,
            gym_class_id=self.gym_class.id,
            enrollment_type="single",
            selected_sessions_ids=[session.id],
        )

        self.assertEqual(
            enrollment.enrollment_type,
            "single",
        )

        self.assertIn(
            session,
            enrollment.selected_sessions.all(),
        )

    def test_single_enrollment_requires_session(self):

        with self.assertRaises(DRFValidationError):
            create_enrollment(
                user=self.member,
                gym_class_id=self.gym_class.id,
                enrollment_type="single",
                selected_sessions_ids=[],
            )

    def test_single_enrollment_with_invalid_session(self):

        with self.assertRaises(DRFValidationError):
            create_enrollment(
                user=self.member,
                gym_class_id=self.gym_class.id,
                enrollment_type="single",
                selected_sessions_ids=[99999],
            )

    def test_cancel_enrollment(self):

        enrollment = create_enrollment(
            user=self.member,
            gym_class_id=self.gym_class.id,
            enrollment_type="semester",
        )

        result = cancel_enrollment_service(
            enrollment
        )

        self.assertEqual(
            result.status,
            "cancelled",
        )

    def test_cannot_cancel_already_cancelled_enrollment(self):

        enrollment = create_enrollment(
            user=self.member,
            gym_class_id=self.gym_class.id,
            enrollment_type="semester",
        )

        cancel_enrollment_service(
            enrollment
        )

        with self.assertRaises(DRFValidationError):
            cancel_enrollment_service(
                enrollment
            )


# =========================================================
# Payment Model Tests
# =========================================================

class PaymentModelTest(TestCase):

    def setUp(self):

        self.user = CustomUser.objects.create_user(
            username="member1",
            password="Test1234",
        )

        self.trainer = CustomUser.objects.create_user(
            username="trainer1",
            password="Test1234",
        )

        self.gym = Gym.objects.create(
            name="Test Gym",
            address="Test Address",
        )

        GymMembership.objects.create(
            user=self.trainer,
            gym=self.gym,
            role=GymMembership.Role.TRAINER,
            salary=Decimal("10000.00"),
        )

        self.gym_class = GymClass.objects.create(
            name="Yoga Class",
            category="yoga",
            gym=self.gym,
            trainer=self.trainer,
            capacity=20,
            price=Decimal("500000.00"),
            single_session_price=Decimal("100000.00"),
            regular_days=[],
        )

        self.enrollment = Enrollment.objects.create(
            gym_class=self.gym_class,
            user=self.user,
        )

    def test_create_payment(self):

        payment = Payment.objects.create(
            enrollment=self.enrollment,
            amount=Decimal("500000.00"),
        )

        self.assertEqual(
            payment.amount,
            Decimal("500000.00"),
        )

    def test_payment_status_default_is_pending(self):

        payment = Payment.objects.create(
            enrollment=self.enrollment,
            amount=Decimal("500000.00"),
        )

        self.assertEqual(
            payment.status,
            "pending",
        )

    def test_payment_amount_must_be_greater_than_zero(self):

        payment = Payment(
            enrollment=self.enrollment,
            amount=Decimal("0.00"),
        )

        with self.assertRaises(DjangoValidationError):
            payment.full_clean()

    def test_payment_amount_cannot_be_negative(self):

        payment = Payment(
            enrollment=self.enrollment,
            amount=Decimal("-100.00"),
        )

        with self.assertRaises(DjangoValidationError):
            payment.full_clean()

    def test_completed_payment_requires_transaction_id(self):

        payment = Payment(
            enrollment=self.enrollment,
            amount=Decimal("500000.00"),
            status="completed",
        )

        with self.assertRaises(DjangoValidationError):
            payment.full_clean()

    def test_completed_payment_with_transaction_id_is_valid(self):

        payment = Payment(
            enrollment=self.enrollment,
            amount=Decimal("500000.00"),
            status="completed",
            transaction_id="TX123456",
        )

        payment.full_clean()

        self.assertEqual(
            payment.transaction_id,
            "TX123456",
        )

    def test_payment_str(self):

        payment = Payment.objects.create(
            enrollment=self.enrollment,
            amount=Decimal("500000.00"),
        )

        self.assertEqual(
            str(payment),
            f"Payment {payment.id} - member1 - pending",
        )


# =========================================================
# Payment Service Tests
# =========================================================

class PaymentServiceTest(TestCase):

    def setUp(self):

        self.member = CustomUser.objects.create_user(
            username="member1",
            password="Test1234",
        )

        self.trainer = CustomUser.objects.create_user(
            username="trainer1",
            password="Test1234",
        )

        self.gym = Gym.objects.create(
            name="Test Gym",
            address="Test Address",
        )

        GymMembership.objects.create(
            user=self.member,
            gym=self.gym,
            role=GymMembership.Role.MEMBER,
        )

        GymMembership.objects.create(
            user=self.trainer,
            gym=self.gym,
            role=GymMembership.Role.TRAINER,
            salary=Decimal("10000"),
        )

        self.gym_class = GymClass.objects.create(
            name="Yoga",
            category="yoga",
            gym=self.gym,
            trainer=self.trainer,
            capacity=10,
            current_enrolled=0,
            price=Decimal("500000"),
            single_session_price=Decimal("100000"),
            regular_days=[],
        )

    def test_create_payment_for_semester(self):

        enrollment = Enrollment.objects.create(
            user=self.member,
            gym_class=self.gym_class,
            enrollment_type="semester",
        )

        payment = create_payment(
            enrollment
        )

        self.assertEqual(
            payment.amount,
            Decimal("500000"),
        )

        self.assertEqual(
            payment.status,
            "pending",
        )

    def test_cannot_create_duplicate_payment(self):

        enrollment = Enrollment.objects.create(
            user=self.member,
            gym_class=self.gym_class,
            enrollment_type="semester",
        )

        create_payment(
            enrollment
        )

        with self.assertRaises(DjangoValidationError):
            create_payment(
                enrollment
            )

    def create_session(self):

        return ClassSession.objects.create(
            gym_class=self.gym_class,
            start_time=timezone.make_aware(
                datetime(2026, 8, 20, 10, 0)
            ),
            end_time=timezone.make_aware(
                datetime(2026, 8, 20, 11, 0)
            ),
            trainer=self.trainer,
        )

    def test_create_payment_for_single_enrollment(self):

        session1 = self.create_session()

        enrollment = Enrollment.objects.create(
            user=self.member,
            gym_class=self.gym_class,
            enrollment_type="single",
        )

        enrollment.selected_sessions.add(
            session1
        )

        payment = create_payment(
            enrollment
        )

        self.assertEqual(
            payment.amount,
            Decimal("100000"),
        )

    def test_single_enrollment_payment_depends_on_session_count(self):

        session1 = self.create_session()

        session2 = ClassSession.objects.create(
            gym_class=self.gym_class,
            start_time=timezone.make_aware(
                datetime(2026, 8, 21, 10, 0)
            ),
            end_time=timezone.make_aware(
                datetime(2026, 8, 21, 11, 0)
            ),
            trainer=self.trainer,
        )

        enrollment = Enrollment.objects.create(
            user=self.member,
            gym_class=self.gym_class,
            enrollment_type="single",
        )

        enrollment.selected_sessions.add(
            session1,
            session2,
        )

        payment = create_payment(
            enrollment
        )

        self.assertEqual(
            payment.amount,
            Decimal("200000"),
        )

    def test_single_payment_requires_selected_session(self):

        enrollment = Enrollment.objects.create(
            user=self.member,
            gym_class=self.gym_class,
            enrollment_type="single",
        )

        with self.assertRaises(DjangoValidationError):
            create_payment(
                enrollment
            )

    def test_invalid_enrollment_type(self):

        enrollment = Enrollment.objects.create(
            user=self.member,
            gym_class=self.gym_class,
            enrollment_type="semester",
        )

        enrollment.enrollment_type = "something_invalid"

        with self.assertRaises(DjangoValidationError):
            create_payment(enrollment)

    def test_confirm_payment(self):

        enrollment = Enrollment.objects.create(
            user=self.member,
            gym_class=self.gym_class,
            enrollment_type="semester",
        )

        payment = create_payment(
            enrollment
        )

        result = confirm_payment(
            payment.id,
            "TX123456",
        )

        self.assertEqual(
            result.status,
            "completed",
        )

        enrollment.refresh_from_db()

        self.assertEqual(
            enrollment.status,
            "approved",
        )

    def test_confirm_payment_increases_current_enrolled(self):

        enrollment = Enrollment.objects.create(
            user=self.member,
            gym_class=self.gym_class,
            enrollment_type="semester",
        )

        payment = create_payment(
            enrollment
        )

        confirm_payment(
            payment.id,
            "TX123456",
        )

        self.gym_class.refresh_from_db()

        self.assertEqual(
            self.gym_class.current_enrolled,
            1,
        )

    def test_confirm_nonexistent_payment(self):

        with self.assertRaises(NotFound):
            confirm_payment(
                99999,
                "TX123456",
            )

    def test_cannot_confirm_completed_payment_twice(self):

        enrollment = Enrollment.objects.create(
            user=self.member,
            gym_class=self.gym_class,
            enrollment_type="semester",
        )

        payment = create_payment(
            enrollment
        )

        confirm_payment(
            payment.id,
            "TX123456",
        )

        with self.assertRaises(DjangoValidationError):
            confirm_payment(
                payment.id,
                "TX999999",
            )