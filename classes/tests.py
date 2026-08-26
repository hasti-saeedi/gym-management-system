from datetime import date, datetime, time
from decimal import Decimal

from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase
from django.utils import timezone

from rest_framework.exceptions import (
    NotFound,
    ValidationError as DRFValidationError,
)

from accounts.models import CustomUser
from classes.models import ClassSession, GymClass
from classes.services.attendance_services import (
    get_enrolled_students,
    record_attendance,
)
from classes.services.gym_class_services import (
    calculate_session_dates,
    check_trainer_conflicts,
    generate_sessions,
)
from enrollments.models import Enrollment
from gyms.models import Gym, GymMembership


class GymClassModelTest(TestCase):
    """Test validation, defaults, and behavior of the GymClass model."""

    def setUp(self):
        """Create the trainer, gym, and trainer membership used by the tests."""
        self.user = CustomUser.objects.create_user(
            username="trainer1",
            password="Test1234",
        )

        self.gym = Gym.objects.create(
            name="Test Gym",
            address="Test Address",
        )

        GymMembership.objects.create(
            user=self.user,
            gym=self.gym,
            role=GymMembership.Role.TRAINER,
            salary=Decimal("10000.00"),
        )

    def create_valid_class(self, **kwargs):
        """
        Return a valid GymClass instance with optional overridden fields.

        Args:
            **kwargs: Fields to override in the default class data.

        Returns:
            GymClass: An unsaved valid gym class instance.
        """
        data = {
            "name": "Yoga Class",
            "category": "yoga",
            "gym": self.gym,
            "trainer": self.user,
            "capacity": 20,
            "regular_days": [0, 2, 4],
            "start_time": time(10, 0),
            "end_time": time(11, 0),
            "start_date": date(2026, 8, 17),
            "end_date": date(2026, 8, 28),
            "total_sessions": 6,
            "duration_minutes": 60,
            "price": Decimal("500000.00"),
            "single_session_price": Decimal("100000.00"),
        }

        data.update(kwargs)

        return GymClass(**data)

    def test_create_valid_gym_class(self):
        """Test that a valid gym class passes model validation."""
        gym_class = self.create_valid_class()

        gym_class.full_clean()

        self.assertEqual(gym_class.name, "Yoga Class")
        self.assertEqual(gym_class.category, "yoga")
        self.assertEqual(gym_class.capacity, 20)

    def test_gym_class_str(self):
        """Test the string representation of a gym class."""
        gym_class = self.create_valid_class()

        self.assertEqual(
            str(gym_class),
            "Yoga Class - Test Gym",
        )

    def test_current_enrolled_default_is_zero(self):
        """Test that the default current enrollment count is zero."""
        gym_class = self.create_valid_class()

        self.assertEqual(
            gym_class.current_enrolled,
            0,
        )

    def test_is_active_default_is_true(self):
        """Test that a gym class is active by default."""
        gym_class = self.create_valid_class()

        self.assertTrue(gym_class.is_active)

    def test_duration_default_is_60_minutes(self):
        """Test that the default class duration is 60 minutes."""
        gym_class = self.create_valid_class()

        self.assertEqual(
            gym_class.duration_minutes,
            60,
        )

    def test_capacity_cannot_be_zero(self):
        """Test that class capacity cannot be zero."""
        gym_class = self.create_valid_class(
            capacity=0,
        )

        with self.assertRaises(DjangoValidationError):
            gym_class.full_clean()

    def test_price_cannot_be_negative(self):
        """Test that a gym class price cannot be negative."""
        gym_class = self.create_valid_class(
            price=Decimal("-100.00"),
        )

        with self.assertRaises(DjangoValidationError):
            gym_class.full_clean()

    def test_class_name_cannot_be_empty(self):
        """Test that a gym class name cannot be empty."""
        gym_class = self.create_valid_class(
            name="",
        )

        with self.assertRaises(DjangoValidationError):
            gym_class.full_clean()

    def test_class_name_cannot_be_only_whitespace(self):
        """Test that a gym class name cannot contain only whitespace."""
        gym_class = self.create_valid_class(
            name="   ",
        )

        with self.assertRaises(DjangoValidationError):
            gym_class.full_clean()

    def test_end_time_must_be_after_start_time(self):
        """Test that the class end time must be after the start time."""
        gym_class = self.create_valid_class(
            start_time=time(10, 0),
            end_time=time(9, 0),
        )

        with self.assertRaises(DjangoValidationError):
            gym_class.full_clean()

    def test_end_date_must_be_after_start_date(self):
        """Test that the class end date must not precede the start date."""
        gym_class = self.create_valid_class(
            start_date=date(2026, 8, 20),
            end_date=date(2026, 8, 19),
        )

        with self.assertRaises(DjangoValidationError):
            gym_class.full_clean()

    def test_trainer_must_be_active_trainer_of_gym(self):
        """Test that the assigned trainer must belong to the gym."""
        another_user = CustomUser.objects.create_user(
            username="nottrainer",
            password="Test1234",
        )

        gym_class = self.create_valid_class(
            trainer=another_user,
        )

        with self.assertRaises(DjangoValidationError):
            gym_class.full_clean()


class ClassSessionModelTest(TestCase):
    """Test validation, properties, and behavior of the ClassSession model."""

    def setUp(self):
        """Create the trainer, member, gym, and gym class used by the tests."""
        self.trainer = CustomUser.objects.create_user(
            username="trainer1",
            password="Test1234",
        )

        self.member = CustomUser.objects.create_user(
            username="member1",
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
            duration_minutes=60,
            price=Decimal("500000.00"),
            single_session_price=Decimal("100000.00"),
            regular_days=[],
        )

        self.start_time = timezone.make_aware(
            datetime(2026, 8, 20, 10, 0),
        )

        self.end_time = timezone.make_aware(
            datetime(2026, 8, 20, 11, 0),
        )

    def create_valid_session(self, **kwargs):
        """
        Return a valid ClassSession instance with optional overridden fields.

        Args:
            **kwargs: Fields to override in the default session data.

        Returns:
            ClassSession: An unsaved valid class session instance.
        """
        data = {
            "gym_class": self.gym_class,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "trainer": self.trainer,
        }

        data.update(kwargs)

        return ClassSession(**data)

    def test_create_valid_session(self):
        """Test that a valid class session passes model validation."""
        session = self.create_valid_session()

        session.full_clean()

        self.assertEqual(session.gym_class, self.gym_class)
        self.assertEqual(session.trainer, self.trainer)

    def test_attendance_default_is_empty_dict(self):
        """Test that session attendance defaults to an empty dictionary."""
        session = self.create_valid_session()

        self.assertEqual(session.attendance, {})

    def test_is_cancelled_default_is_false(self):
        """Test that a class session is not cancelled by default."""
        session = self.create_valid_session()

        self.assertFalse(session.is_cancelled)

    def test_present_count(self):
        """Test that the number of present students is calculated correctly."""
        session = self.create_valid_session(
            attendance={
                "1": {"present": True},
                "2": {"present": True},
                "3": {"present": False},
            }
        )

        self.assertEqual(session.present_count, 2)

    def test_absent_count(self):
        """Test that the number of absent students is calculated correctly."""
        session = self.create_valid_session(
            attendance={
                "1": {"present": True},
                "2": {"present": False},
                "3": {"present": False},
            }
        )

        self.assertEqual(session.absent_count, 2)

    def test_single_session_students(self):
        """Test that single-session student IDs are returned correctly."""
        session = self.create_valid_session(
            attendance={
                "1": {
                    "present": True,
                    "single_session": True,
                },
                "2": {
                    "present": True,
                    "single_session": False,
                },
                "3": {
                    "present": False,
                    "single_session": True,
                },
            }
        )

        self.assertEqual(
            session.single_session_students,
            ["1", "3"],
        )

    def test_end_time_must_be_after_start_time(self):
        """Test that the session end time must be after the start time."""
        session = self.create_valid_session(
            start_time=timezone.make_aware(
                datetime(2026, 8, 20, 11, 0),
            ),
            end_time=timezone.make_aware(
                datetime(2026, 8, 20, 10, 0),
            ),
        )

        with self.assertRaises(DjangoValidationError):
            session.full_clean()

    def test_trainer_must_be_active_trainer_of_gym(self):
        """Test that the assigned trainer must belong to the gym."""
        another_user = CustomUser.objects.create_user(
            username="nottrainer",
            password="Test1234",
        )

        session = self.create_valid_session(
            trainer=another_user,
        )

        with self.assertRaises(DjangoValidationError):
            session.full_clean()

    def test_trainer_cannot_have_overlapping_sessions(self):
        """Test that a trainer cannot have overlapping class sessions."""
        first_session = self.create_valid_session()
        first_session.save()

        overlapping_session = self.create_valid_session(
            start_time=timezone.make_aware(
                datetime(2026, 8, 20, 10, 30),
            ),
            end_time=timezone.make_aware(
                datetime(2026, 8, 20, 11, 30),
            ),
        )

        with self.assertRaises(DjangoValidationError):
            overlapping_session.save()

    def test_trainer_can_have_non_overlapping_sessions(self):
        """Test that a trainer can have non-overlapping class sessions."""
        first_session = self.create_valid_session()
        first_session.save()

        second_session = self.create_valid_session(
            start_time=timezone.make_aware(
                datetime(2026, 8, 20, 11, 0),
            ),
            end_time=timezone.make_aware(
                datetime(2026, 8, 20, 12, 0),
            ),
        )

        second_session.save()

        self.assertEqual(
            ClassSession.objects.count(),
            2,
        )

    def test_str(self):
        """Test the string representation of a class session."""
        session = self.create_valid_session()

        expected = f"{self.gym_class.name} - {self.start_time}"

        self.assertEqual(
            str(session),
            expected,
        )


class ClassesServicesTest(TestCase):
    """Test class scheduling, enrollment, and attendance services."""

    def setUp(self):
        """Create the users, gym, memberships, and class used by the tests."""
        self.member = CustomUser.objects.create_user(
            username="member",
            password="Test1234",
        )

        self.member2 = CustomUser.objects.create_user(
            username="member2",
            password="Test1234",
        )

        self.trainer = CustomUser.objects.create_user(
            username="trainer",
            password="Test1234",
        )

        self.trainer2 = CustomUser.objects.create_user(
            username="trainer2",
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
            user=self.member2,
            gym=self.gym,
            role=GymMembership.Role.MEMBER,
        )

        GymMembership.objects.create(
            user=self.trainer,
            gym=self.gym,
            role=GymMembership.Role.TRAINER,
            salary=10000,
        )

        GymMembership.objects.create(
            user=self.trainer2,
            gym=self.gym,
            role=GymMembership.Role.TRAINER,
            salary=10000,
        )

        self.gym_class = GymClass.objects.create(
            name="Yoga",
            category="yoga",
            gym=self.gym,
            trainer=self.trainer,
            capacity=10,
            duration_minutes=60,
            price=100000,
            single_session_price=20000,
            regular_days=[0],
            start_time=time(10, 0),
            end_time=time(11, 0),
            start_date=date(2026, 8, 17),
            end_date=date(2026, 8, 31),
            total_sessions=3,
        )

    def test_calculate_session_dates(self):
        """Test that session dates are calculated from the selected weekdays."""
        result = calculate_session_dates(
            date(2026, 8, 17),
            date(2026, 8, 31),
            [0],
        )

        self.assertEqual(
            result,
            [
                date(2026, 8, 17),
                date(2026, 8, 24),
                date(2026, 8, 31),
            ],
        )

    def test_calculate_session_dates_empty_values(self):
        """Test that missing scheduling values return an empty result."""
        result = calculate_session_dates(
            None,
            date(2026, 8, 31),
            [0],
        )

        self.assertEqual(result, [])

    def test_check_trainer_conflicts_none_trainer(self):
        """Test that no conflict is reported when no trainer is provided."""
        start = timezone.make_aware(
            datetime(2026, 8, 20, 10, 0),
        )

        end = timezone.make_aware(
            datetime(2026, 8, 20, 11, 0),
        )

        result = check_trainer_conflicts(
            None,
            start,
            end,
        )

        self.assertFalse(result)

    def test_check_trainer_conflicts_exists(self):
        """Test that an overlapping trainer session is detected."""
        ClassSession.objects.create(
            gym_class=self.gym_class,
            trainer=self.trainer,
            start_time=timezone.make_aware(
                datetime(2026, 8, 20, 10, 0),
            ),
            end_time=timezone.make_aware(
                datetime(2026, 8, 20, 11, 0),
            ),
        )

        result = check_trainer_conflicts(
            self.trainer,
            timezone.make_aware(
                datetime(2026, 8, 20, 10, 30),
            ),
            timezone.make_aware(
                datetime(2026, 8, 20, 11, 30),
            ),
        )

        self.assertTrue(result)

    def test_check_trainer_conflicts_no_conflict(self):
        """Test that non-overlapping trainer sessions are allowed."""
        ClassSession.objects.create(
            gym_class=self.gym_class,
            trainer=self.trainer,
            start_time=timezone.make_aware(
                datetime(2026, 8, 20, 10, 0),
            ),
            end_time=timezone.make_aware(
                datetime(2026, 8, 20, 11, 0),
            ),
        )

        result = check_trainer_conflicts(
            self.trainer,
            timezone.make_aware(
                datetime(2026, 8, 20, 11, 0),
            ),
            timezone.make_aware(
                datetime(2026, 8, 20, 12, 0),
            ),
        )

        self.assertFalse(result)

    def test_generate_sessions_creates_sessions(self):
        """Test that sessions are generated for all scheduled class dates."""
        result = generate_sessions(self.gym_class)

        self.assertEqual(
            len(result["created"]),
            3,
        )

        self.assertEqual(
            ClassSession.objects.filter(
                gym_class=self.gym_class,
            ).count(),
            3,
        )

    def test_generate_sessions_does_not_duplicate(self):
        """Test that existing sessions are not generated again."""
        generate_sessions(self.gym_class)

        result = generate_sessions(self.gym_class)

        self.assertEqual(result["created"], [])

        self.assertEqual(
            result["conflicts"],
            ["Sessions already exist"],
        )

        self.assertEqual(
            ClassSession.objects.filter(
                gym_class=self.gym_class,
            ).count(),
            3,
        )

    def test_generate_sessions_skips_trainer_conflict(self):
        """Test that session generation skips dates with trainer conflicts."""
        conflict_date = date(2026, 8, 17)

        conflict_start = timezone.make_aware(
            datetime.combine(
                conflict_date,
                time(10, 0),
            ),
        )

        conflict_end = timezone.make_aware(
            datetime.combine(
                conflict_date,
                time(11, 0),
            ),
        )

        conflict_class = GymClass.objects.create(
            name="Pilates",
            category="yoga",
            gym=self.gym,
            trainer=self.trainer,
            capacity=10,
            duration_minutes=60,
            price=100000,
            single_session_price=20000,
            regular_days=[0],
            start_time=time(10, 0),
            end_time=time(11, 0),
            start_date=conflict_date,
            end_date=conflict_date,
            total_sessions=1,
        )

        ClassSession.objects.create(
            gym_class=conflict_class,
            trainer=self.trainer,
            start_time=conflict_start,
            end_time=conflict_end,
        )

        result = generate_sessions(self.gym_class)

        self.assertIn(
            conflict_date,
            result["skipped"],
        )

        self.assertEqual(
            len(result["conflicts"]),
            1,
        )

        self.assertEqual(
            result["conflicts"][0]["reason"],
            "trainer conflict",
        )

    def test_get_enrolled_students_semester(self):
        """Test that semester enrollments are included for a session."""
        session = ClassSession.objects.create(
            gym_class=self.gym_class,
            trainer=self.trainer,
            start_time=timezone.make_aware(
                datetime(2026, 8, 20, 10, 0),
            ),
            end_time=timezone.make_aware(
                datetime(2026, 8, 20, 11, 0),
            ),
        )

        enrollment = Enrollment.objects.create(
            gym_class=self.gym_class,
            user=self.member,
            enrollment_type="semester",
            status="approved",
        )

        result = get_enrolled_students(session.id)

        self.assertIn(enrollment, result)

    def test_get_enrolled_students_single_session(self):
        """Test that selected single-session enrollments are included."""
        session = ClassSession.objects.create(
            gym_class=self.gym_class,
            trainer=self.trainer,
            start_time=timezone.make_aware(
                datetime(2026, 8, 20, 10, 0),
            ),
            end_time=timezone.make_aware(
                datetime(2026, 8, 20, 11, 0),
            ),
        )

        enrollment = Enrollment.objects.create(
            gym_class=self.gym_class,
            user=self.member,
            enrollment_type="single",
            status="approved",
        )

        enrollment.selected_sessions.add(session)

        result = get_enrolled_students(session.id)

        self.assertIn(enrollment, result)

    def test_get_enrolled_students_returns_both_types(self):
        """Test that both semester and single-session enrollments are returned."""
        session = ClassSession.objects.create(
            gym_class=self.gym_class,
            trainer=self.trainer,
            start_time=timezone.make_aware(
                datetime(2026, 8, 20, 10, 0),
            ),
            end_time=timezone.make_aware(
                datetime(2026, 8, 20, 11, 0),
            ),
        )

        semester_enrollment = Enrollment.objects.create(
            gym_class=self.gym_class,
            user=self.member,
            enrollment_type="semester",
            status="approved",
        )

        single_enrollment = Enrollment.objects.create(
            gym_class=self.gym_class,
            user=self.member2,
            enrollment_type="single",
            status="approved",
        )

        single_enrollment.selected_sessions.add(session)

        result = get_enrolled_students(session.id)

        self.assertIn(semester_enrollment, result)
        self.assertIn(single_enrollment, result)

    def test_get_enrolled_students_session_not_found(self):
        """Test that requesting an unknown session raises NotFound."""
        with self.assertRaises(NotFound):
            get_enrolled_students(99999)

    def test_record_attendance_present(self):
        """Test recording a present attendance status."""
        session = ClassSession.objects.create(
            gym_class=self.gym_class,
            trainer=self.trainer,
            start_time=timezone.make_aware(
                datetime(2026, 8, 20, 10, 0),
            ),
            end_time=timezone.make_aware(
                datetime(2026, 8, 20, 11, 0),
            ),
        )

        Enrollment.objects.create(
            gym_class=self.gym_class,
            user=self.member,
            enrollment_type="semester",
            status="approved",
        )

        record_attendance(
            session.id,
            self.member.id,
            True,
        )

        session.refresh_from_db()

        self.assertTrue(
            session.attendance[
                str(self.member.id)
            ]["present"]
        )

    def test_record_attendance_absent(self):
        """Test recording an absent attendance status."""
        session = ClassSession.objects.create(
            gym_class=self.gym_class,
            trainer=self.trainer,
            start_time=timezone.make_aware(
                datetime(2026, 8, 20, 10, 0),
            ),
            end_time=timezone.make_aware(
                datetime(2026, 8, 20, 11, 0),
            ),
        )

        Enrollment.objects.create(
            gym_class=self.gym_class,
            user=self.member,
            enrollment_type="semester",
            status="approved",
        )

        record_attendance(
            session.id,
            self.member.id,
            False,
        )

        session.refresh_from_db()

        self.assertFalse(
            session.attendance[
                str(self.member.id)
            ]["present"]
        )

    def test_record_attendance_user_not_enrolled(self):
        """Test that attendance cannot be recorded for an unenrolled user."""
        session = ClassSession.objects.create(
            gym_class=self.gym_class,
            trainer=self.trainer,
            start_time=timezone.make_aware(
                datetime(2026, 8, 20, 10, 0),
            ),
            end_time=timezone.make_aware(
                datetime(2026, 8, 20, 11, 0),
            ),
        )

        with self.assertRaises(DRFValidationError):
            record_attendance(
                session.id,
                self.member.id,
                True,
            )

    def test_record_attendance_session_not_found(self):
        """Test that recording attendance for an unknown session raises NotFound."""
        with self.assertRaises(NotFound):
            record_attendance(
                99999,
                self.member.id,
                True,
            )