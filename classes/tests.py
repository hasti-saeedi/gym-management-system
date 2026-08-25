# from datetime import date, time
# from decimal import Decimal

# from rest_framework.exceptions import NotFound
# from django.core.exceptions import ValidationError as DjangoValidationError
# from rest_framework.exceptions import ValidationError as DRFValidationError
# from django.test import TestCase

# from accounts.models import CustomUser
# from gyms.models import Gym, GymMembership
# from classes.models import GymClass
# from datetime import datetime, time
# from decimal import Decimal
# from django.utils import timezone
# from classes.models import GymClass, ClassSession
# from enrollments.models import Enrollment

# from classes.services.attendance_services import (
#     get_enrolled_students,
#     record_attendance,
# )

# from classes.services.gym_class_services import (
#     calculate_session_dates,
#     check_trainer_conflicts,
#     generate_sessions,
# )

# class GymClassModelTest(TestCase):

#     def setUp(self):
#         self.user = CustomUser.objects.create_user(
#             username="trainer1",
#             password="Test1234",
#         )

#         self.gym = Gym.objects.create(
#             name="Test Gym",
#             address="Test Address",
#         )

#         GymMembership.objects.create(
#             user=self.user,
#             gym=self.gym,
#             role=GymMembership.Role.TRAINER,
#             salary=Decimal("10000.00"),
#         )

#     def create_valid_class(self, **kwargs):
#         data = {
#             "name": "Yoga Class",
#             "category": "yoga",
#             "gym": self.gym,
#             "trainer": self.user,
#             "capacity": 20,
#             "regular_days":[0, 2, 4],
#             "start_time":time(10, 0),
#             "end_time":time(11, 0),
#             "start_date":date(2026, 8, 17),
#             "end_date":date(2026, 8, 28),
#             "total_sessions":6,
#             "duration_minutes": 60,
#             "price": Decimal("500000.00"),
#             "single_session_price": Decimal("100000.00"),
#         }

#         data.update(kwargs)# مقدار های قبلی را در صورت وجود ریست میکند و مفدار جدید   کیارگز رو به همه میریزد

#         return GymClass(**data)

#     def test_create_valid_gym_class(self):
#         gym_class = self.create_valid_class()

#         gym_class.full_clean()

#         self.assertEqual(gym_class.name, "Yoga Class")
#         self.assertEqual(gym_class.category, "yoga")
#         self.assertEqual(gym_class.capacity, 20)

#     def test_gym_class_str(self):
#         gym_class = self.create_valid_class()

#         self.assertEqual(
#             str(gym_class),
#             "Yoga Class - Test Gym"
#         )

#     def test_current_enrolled_default_is_zero(self):
#         gym_class = self.create_valid_class()

#         self.assertEqual(gym_class.current_enrolled, 0)

#     def test_is_active_default_is_true(self):
#         gym_class = self.create_valid_class()

#         self.assertTrue(gym_class.is_active)

#     def test_duration_default_is_60_minutes(self):
#         gym_class = self.create_valid_class()

#         self.assertEqual(gym_class.duration_minutes, 60)

#     def test_capacity_cannot_be_zero(self):
#         gym_class = self.create_valid_class(
#             capacity=0
#         )

#         with self.assertRaises(ValidationError):
#             gym_class.full_clean()

#     def test_price_cannot_be_negative(self):
#         gym_class = self.create_valid_class(
#             price=Decimal("-100.00")
#         )

#         with self.assertRaises(ValidationError):
#             gym_class.full_clean()

#     def test_class_name_cannot_be_empty(self):
#         gym_class = self.create_valid_class(
#             name=""
#         )

#         with self.assertRaises(ValidationError):
#             gym_class.full_clean()

#     def test_class_name_cannot_be_only_whitespace(self):
#         gym_class = self.create_valid_class(
#             name="   "
#         )

#         with self.assertRaises(ValidationError):
#             gym_class.full_clean()

#     def test_end_time_must_be_after_start_time(self):
#         gym_class = self.create_valid_class(
#             start_time=time(10, 0),
#             end_time=time(9, 0),
#         )

#         with self.assertRaises(ValidationError):
#             gym_class.full_clean()

#     def test_end_date_must_be_after_start_date(self):
#         gym_class = self.create_valid_class(
#             start_date=date(2026, 8, 20),
#             end_date=date(2026, 8, 19),
#         )

#         with self.assertRaises(ValidationError):
#             gym_class.full_clean()

#     def test_trainer_must_be_active_trainer_of_gym(self):
#         another_user = CustomUser.objects.create_user(
#             username="nottrainer",
#             password="Test1234",
#         )

#         gym_class = self.create_valid_class(
#             trainer=another_user
#         )

#         with self.assertRaises(ValidationError):
#             gym_class.full_clean()


# class ClassSessionModelTest(TestCase):

#     def setUp(self):
#         self.trainer = CustomUser.objects.create_user(
#             username="trainer1",
#             password="Test1234",
#         )

#         self.member = CustomUser.objects.create_user(
#             username="member1",
#             password="Test1234",
#         )

#         self.gym = Gym.objects.create(
#             name="Test Gym",
#             address="Test Address",
#         )

#         GymMembership.objects.create(
#             user=self.trainer,
#             gym=self.gym,
#             role=GymMembership.Role.TRAINER,
#             salary=Decimal("10000.00"),
#         )

#         self.gym_class = GymClass.objects.create(
#             name="Yoga Class",
#             category="yoga",
#             gym=self.gym,
#             trainer=self.trainer,
#             capacity=20,
#             duration_minutes=60,
#             price=Decimal("500000.00"),
#             single_session_price=Decimal("100000.00"),
#             regular_days=[],
#         )

#         self.start_time = timezone.make_aware(
#             datetime(2026, 8, 20, 10, 0)
#         )

#         self.end_time = timezone.make_aware(
#             datetime(2026, 8, 20, 11, 0)
#         )

#     def create_valid_session(self, **kwargs):
#         data = {
#             "gym_class": self.gym_class,
#             "start_time": self.start_time,
#             "end_time": self.end_time,
#             "trainer": self.trainer,
#         }

#         data.update(kwargs)

#         return ClassSession(**data)

#     def test_create_valid_session(self):
#         session = self.create_valid_session()

#         session.full_clean()

#         self.assertEqual(
#             session.gym_class,
#             self.gym_class
#         )

#         self.assertEqual(
#             session.trainer,
#             self.trainer
#         )

#     def test_attendance_default_is_empty_dict(self):
#         session = self.create_valid_session()

#         self.assertEqual(
#             session.attendance,
#             {}
#         )

#     def test_is_cancelled_default_is_false(self):
#         session = self.create_valid_session()

#         self.assertFalse(session.is_cancelled)

#     def test_present_count(self):
#         session = self.create_valid_session(
#             attendance={
#                 "1": {"present": True},
#                 "2": {"present": True},
#                 "3": {"present": False},
#             }
#         )

#         self.assertEqual(
#             session.present_count,
#             2
#         )

#     def test_absent_count(self):
#         session = self.create_valid_session(
#             attendance={
#                 "1": {"present": True},
#                 "2": {"present": False},
#                 "3": {"present": False},
#             }
#         )

#         self.assertEqual(
#             session.absent_count,
#             2
#         )

#     def test_single_session_students(self):
#         session = self.create_valid_session(
#             attendance={
#                 "1": {
#                     "present": True,
#                     "single_session": True,
#                 },
#                 "2": {
#                     "present": True,
#                     "single_session": False,
#                 },
#                 "3": {
#                     "present": False,
#                     "single_session": True,
#                 },
#             }
#         )

#         self.assertEqual(
#             session.single_session_students,
#             ["1", "3"]
#         )

#     def test_end_time_must_be_after_start_time(self):
#         session = self.create_valid_session(
#             start_time=timezone.make_aware(
#                 datetime(2026, 8, 20, 11, 0)
#             ),
#             end_time=timezone.make_aware(
#                 datetime(2026, 8, 20, 10, 0)
#             ),
#         )

#         with self.assertRaises(ValidationError):
#             session.full_clean()

#     def test_trainer_must_be_active_trainer_of_gym(self):
#         another_user = CustomUser.objects.create_user(
#             username="nottrainer",
#             password="Test1234",
#         )

#         session = self.create_valid_session(
#             trainer=another_user
#         )

#         with self.assertRaises(ValidationError):
#             session.full_clean()

#     def test_trainer_cannot_have_overlapping_sessions(self):
#         first_session = self.create_valid_session()

#         first_session.save()

#         overlapping_session = self.create_valid_session(
#             start_time=timezone.make_aware(
#                 datetime(2026, 8, 20, 10, 30)
#             ),
#             end_time=timezone.make_aware(
#                 datetime(2026, 8, 20, 11, 30)
#             ),
#         )

#         with self.assertRaises(ValidationError):
#             overlapping_session.save()

#     def test_trainer_can_have_non_overlapping_sessions(self):
#         first_session = self.create_valid_session()

#         first_session.save()

#         second_session = self.create_valid_session(
#             start_time=timezone.make_aware(
#                 datetime(2026, 8, 20, 11, 0)
#             ),
#             end_time=timezone.make_aware(
#                 datetime(2026, 8, 20, 12, 0)
#             ),
#         )

#         second_session.save()

#         self.assertEqual(
#             ClassSession.objects.count(),
#             2
#         )

#     def test_str(self):
#         session = self.create_valid_session()

#         expected = f"{self.gym_class.name} - {self.start_time}"

#         self.assertEqual(
#             str(session),
#             expected
#         )



# class ClassesServicesTest(TestCase):

#     def setUp(self):

#         # =========================
#         # Users
#         # =========================

#         self.member = CustomUser.objects.create_user(
#             username="member",
#             password="Test1234",
#         )

#         self.member2 = CustomUser.objects.create_user(
#             username="member2",
#             password="Test1234",
#         )

#         self.trainer = CustomUser.objects.create_user(
#             username="trainer",
#             password="Test1234",
#         )

#         self.trainer2 = CustomUser.objects.create_user(
#             username="trainer2",
#             password="Test1234",
#         )

#         # =========================
#         # Gym
#         # =========================

#         self.gym = Gym.objects.create(
#             name="Test Gym",
#             address="Test Address",
#         )

#         # =========================
#         # Memberships
#         # =========================

#         GymMembership.objects.create(
#             user=self.member,
#             gym=self.gym,
#             role=GymMembership.Role.MEMBER,
#         )

#         GymMembership.objects.create(
#             user=self.member2,
#             gym=self.gym,
#             role=GymMembership.Role.MEMBER,
#         )

#         GymMembership.objects.create(
#             user=self.trainer,
#             gym=self.gym,
#             role=GymMembership.Role.TRAINER,
#             salary=10000,
#         )

#         GymMembership.objects.create(
#             user=self.trainer2,
#             gym=self.gym,
#             role=GymMembership.Role.TRAINER,
#             salary=10000,
#         )

#         # =========================
#         # Gym Class
#         # =========================

#         self.gym_class = GymClass.objects.create(
#             name="Yoga",
#             category="yoga",
#             gym=self.gym,
#             trainer=self.trainer,
#             capacity=10,
#             duration_minutes=60,
#             price=100000,
#             single_session_price=20000,
#             regular_days=[0],
#             start_time=time(10, 0),
#             end_time=time(11, 0),
#             start_date=date(2026, 8, 17),
#             end_date=date(2026, 8, 31),
#             total_sessions=3,
#         )

#     # =====================================================
#     # calculate_session_dates
#     # =====================================================

#     def test_calculate_session_dates(self):

#         result = calculate_session_dates(
#             date(2026, 8, 17),
#             date(2026, 8, 31),
#             [0],
#         )

#         self.assertEqual(
#             result,
#             [
#                 date(2026, 8, 17),
#                 date(2026, 8, 24),
#                 date(2026, 8, 31),
#             ],
#         )

#     def test_calculate_session_dates_empty_values(self):

#         result = calculate_session_dates(
#             None,
#             date(2026, 8, 31),
#             [0],
#         )

#         self.assertEqual(
#             result,
#             [],
#         )

#     # =====================================================
#     # check_trainer_conflicts
#     # =====================================================

#     def test_check_trainer_conflicts_none_trainer(self):

#         start = timezone.make_aware(
#             datetime(2026, 8, 20, 10, 0)
#         )

#         end = timezone.make_aware(
#             datetime(2026, 8, 20, 11, 0)
#         )

#         result = check_trainer_conflicts(
#             None,
#             start,
#             end,
#         )

#         self.assertFalse(result)

#     def test_check_trainer_conflicts_exists(self):

#         ClassSession.objects.create(
#             gym_class=self.gym_class,
#             trainer=self.trainer,
#             start_time=timezone.make_aware(
#                 datetime(2026, 8, 20, 10, 0)
#             ),
#             end_time=timezone.make_aware(
#                 datetime(2026, 8, 20, 11, 0)
#             ),
#         )

#         result = check_trainer_conflicts(
#             self.trainer,
#             timezone.make_aware(
#                 datetime(2026, 8, 20, 10, 30)
#             ),
#             timezone.make_aware(
#                 datetime(2026, 8, 20, 11, 30)
#             ),
#         )

#         self.assertTrue(result)

#     def test_check_trainer_conflicts_no_conflict(self):

#         ClassSession.objects.create(
#             gym_class=self.gym_class,
#             trainer=self.trainer,
#             start_time=timezone.make_aware(
#                 datetime(2026, 8, 20, 10, 0)
#             ),
#             end_time=timezone.make_aware(
#                 datetime(2026, 8, 20, 11, 0)
#             ),
#         )

#         result = check_trainer_conflicts(
#             self.trainer,
#             timezone.make_aware(
#                 datetime(2026, 8, 20, 11, 0)
#             ),
#             timezone.make_aware(
#                 datetime(2026, 8, 20, 12, 0)
#             ),
#         )

#         self.assertFalse(result)

#     # =====================================================
#     # generate_sessions
#     # =====================================================

#     def test_generate_sessions_creates_sessions(self):

#         result = generate_sessions(
#             self.gym_class
#         )

#         self.assertEqual(
#             len(result["created"]),
#             3,
#         )

#         self.assertEqual(
#             ClassSession.objects.filter(
#                 gym_class=self.gym_class
#             ).count(),
#             3,
#         )

#     def test_generate_sessions_does_not_duplicate(self):

#         generate_sessions(
#             self.gym_class
#         )

#         result = generate_sessions(
#             self.gym_class
#         )

#         self.assertEqual(
#             result["created"],
#             [],
#         )

#         self.assertEqual(
#             result["conflicts"],
#             ["Sessions already exist"],
#         )

#         self.assertEqual(
#             ClassSession.objects.filter(
#                 gym_class=self.gym_class
#             ).count(),
#             3,
#         )

#     def test_generate_sessions_skips_trainer_conflict(self):

#         conflict_date = date(2026, 8, 17)

#         conflict_start = timezone.make_aware(
#             datetime.combine(
#                 conflict_date,
#                 time(10, 0)
#             )
#         )

#         conflict_end = timezone.make_aware(
#             datetime.combine(
#                 conflict_date,
#                 time(11, 0)
#             )
#         )

#         # کلاس دیگری که همان مربی را دارد
#         conflict_class = GymClass.objects.create(
#             name="Pilates",
#             category="yoga",
#             gym=self.gym,
#             trainer=self.trainer,
#             capacity=10,
#             duration_minutes=60,
#             price=100000,
#             single_session_price=20000,
#             regular_days=[0],
#             start_time=time(10, 0),
#             end_time=time(11, 0),
#             start_date=conflict_date,
#             end_date=conflict_date,
#             total_sessions=1,
#         )

#         # جلسه قبلی برای همان مربی،
#         # اما مربوط به کلاس دیگری
#         ClassSession.objects.create(
#             gym_class=conflict_class,
#             trainer=self.trainer,
#             start_time=conflict_start,
#             end_time=conflict_end,
#         )

#         result = generate_sessions(
#             self.gym_class
#         )

#         self.assertIn(
#             conflict_date,
#             result["skipped"],
#         )

#         self.assertEqual(
#             len(result["conflicts"]),
#             1,
#         )

#         self.assertEqual(
#             result["conflicts"][0]["reason"],
#             "trainer conflict",
#         )

#     # =====================================================
#     # get_enrolled_students
#     # =====================================================

#     def test_get_enrolled_students_semester(self):

#         session = ClassSession.objects.create(
#             gym_class=self.gym_class,
#             trainer=self.trainer,
#             start_time=timezone.make_aware(
#                 datetime(2026, 8, 20, 10, 0)
#             ),
#             end_time=timezone.make_aware(
#                 datetime(2026, 8, 20, 11, 0)
#             ),
#         )

#         enrollment = Enrollment.objects.create(
#             gym_class=self.gym_class,
#             user=self.member,
#             enrollment_type="semester",
#             status="approved",
#         )

#         result = get_enrolled_students(
#             session.id
#         )

#         self.assertIn(
#             enrollment,
#             result,
#         )

#     def test_get_enrolled_students_single_session(self):

#         session = ClassSession.objects.create(
#             gym_class=self.gym_class,
#             trainer=self.trainer,
#             start_time=timezone.make_aware(
#                 datetime(2026, 8, 20, 10, 0)
#             ),
#             end_time=timezone.make_aware(
#                 datetime(2026, 8, 20, 11, 0)
#             ),
#         )

#         enrollment = Enrollment.objects.create(
#             gym_class=self.gym_class,
#             user=self.member,
#             enrollment_type="single",
#             status="approved",
#         )

#         enrollment.selected_sessions.add(
#             session
#         )

#         result = get_enrolled_students(
#             session.id
#         )

#         self.assertIn(
#             enrollment,
#             result,
#         )

#     def test_get_enrolled_students_returns_both_types(self):

#         session = ClassSession.objects.create(
#             gym_class=self.gym_class,
#             trainer=self.trainer,
#             start_time=timezone.make_aware(
#                 datetime(2026, 8, 20, 10, 0)
#             ),
#             end_time=timezone.make_aware(
#                 datetime(2026, 8, 20, 11, 0)
#             ),
#         )

#         semester_enrollment = Enrollment.objects.create(
#             gym_class=self.gym_class,
#             user=self.member,
#             enrollment_type="semester",
#             status="approved",
#         )

#         single_enrollment = Enrollment.objects.create(
#             gym_class=self.gym_class,
#             user=self.member2,
#             enrollment_type="single",
#             status="approved",
#         )

#         single_enrollment.selected_sessions.add(
#             session
#         )

#         result = get_enrolled_students(
#             session.id
#         )

#         self.assertIn(
#             semester_enrollment,
#             result,
#         )

#         self.assertIn(
#             single_enrollment,
#             result,
#         )

#     def test_get_enrolled_students_session_not_found(self):

#         with self.assertRaises(NotFound):
#             get_enrolled_students(
#                 99999
#             )

#     # =====================================================
#     # record_attendance
#     # =====================================================

#     def test_record_attendance_present(self):

#         session = ClassSession.objects.create(
#             gym_class=self.gym_class,
#             trainer=self.trainer,
#             start_time=timezone.make_aware(
#                 datetime(2026, 8, 20, 10, 0)
#             ),
#             end_time=timezone.make_aware(
#                 datetime(2026, 8, 20, 11, 0)
#             ),
#         )

#         Enrollment.objects.create(
#             gym_class=self.gym_class,
#             user=self.member,
#             enrollment_type="semester",
#             status="approved",
#         )

#         record_attendance(
#             session.id,
#             self.member.id,
#             True,
#         )

#         session.refresh_from_db()

#         self.assertTrue(
#             session.attendance[
#                 str(self.member.id)
#             ]["present"]
#         )

#     def test_record_attendance_absent(self):

#         session = ClassSession.objects.create(
#             gym_class=self.gym_class,
#             trainer=self.trainer,
#             start_time=timezone.make_aware(
#                 datetime(2026, 8, 20, 10, 0)
#             ),
#             end_time=timezone.make_aware(
#                 datetime(2026, 8, 20, 11, 0)
#             ),
#         )

#         Enrollment.objects.create(
#             gym_class=self.gym_class,
#             user=self.member,
#             enrollment_type="semester",
#             status="approved",
#         )

#         record_attendance(
#             session.id,
#             self.member.id,
#             False,
#         )

#         session.refresh_from_db()

#         self.assertFalse(
#             session.attendance[
#                 str(self.member.id)
#             ]["present"]
#         )

#     def test_record_attendance_user_not_enrolled(self):

#         session = ClassSession.objects.create(
#             gym_class=self.gym_class,
#             trainer=self.trainer,
#             start_time=timezone.make_aware(
#                 datetime(2026, 8, 20, 10, 0)
#             ),
#             end_time=timezone.make_aware(
#                 datetime(2026, 8, 20, 11, 0)
#             ),
#         )

#         with self.assertRaises(ValidationError):
#             record_attendance(
#                 session.id,
#                 self.member.id,
#                 True,
#             )

#     def test_record_attendance_session_not_found(self):


#         with self.assertRaises(NotFound):

#             record_attendance(
#                 99999,
#                 self.member.id,
#                 True,
#             )


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
from gyms.models import Gym, GymMembership
from classes.models import GymClass, ClassSession
from enrollments.models import Enrollment

from classes.services.attendance_services import (
    get_enrolled_students,
    record_attendance,
)

from classes.services.gym_class_services import (
    calculate_session_dates,
    check_trainer_conflicts,
    generate_sessions,
)


# =========================================================
# GymClass Model Tests
# =========================================================

class GymClassModelTest(TestCase):

    def setUp(self):

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

        gym_class = self.create_valid_class()

        gym_class.full_clean()

        self.assertEqual(
            gym_class.name,
            "Yoga Class",
        )

        self.assertEqual(
            gym_class.category,
            "yoga",
        )

        self.assertEqual(
            gym_class.capacity,
            20,
        )

    def test_gym_class_str(self):

        gym_class = self.create_valid_class()

        self.assertEqual(
            str(gym_class),
            "Yoga Class - Test Gym",
        )

    def test_current_enrolled_default_is_zero(self):

        gym_class = self.create_valid_class()

        self.assertEqual(
            gym_class.current_enrolled,
            0,
        )

    def test_is_active_default_is_true(self):

        gym_class = self.create_valid_class()

        self.assertTrue(
            gym_class.is_active,
        )

    def test_duration_default_is_60_minutes(self):

        gym_class = self.create_valid_class()

        self.assertEqual(
            gym_class.duration_minutes,
            60,
        )

    def test_capacity_cannot_be_zero(self):

        gym_class = self.create_valid_class(
            capacity=0,
        )

        with self.assertRaises(DjangoValidationError):
            gym_class.full_clean()

    def test_price_cannot_be_negative(self):

        gym_class = self.create_valid_class(
            price=Decimal("-100.00"),
        )

        with self.assertRaises(DjangoValidationError):
            gym_class.full_clean()

    def test_class_name_cannot_be_empty(self):

        gym_class = self.create_valid_class(
            name="",
        )

        with self.assertRaises(DjangoValidationError):
            gym_class.full_clean()

    def test_class_name_cannot_be_only_whitespace(self):

        gym_class = self.create_valid_class(
            name="   ",
        )

        with self.assertRaises(DjangoValidationError):
            gym_class.full_clean()

    def test_end_time_must_be_after_start_time(self):

        gym_class = self.create_valid_class(
            start_time=time(10, 0),
            end_time=time(9, 0),
        )

        with self.assertRaises(DjangoValidationError):
            gym_class.full_clean()

    def test_end_date_must_be_after_start_date(self):

        gym_class = self.create_valid_class(
            start_date=date(2026, 8, 20),
            end_date=date(2026, 8, 19),
        )

        with self.assertRaises(DjangoValidationError):
            gym_class.full_clean()

    def test_trainer_must_be_active_trainer_of_gym(self):

        another_user = CustomUser.objects.create_user(
            username="nottrainer",
            password="Test1234",
        )

        gym_class = self.create_valid_class(
            trainer=another_user,
        )

        with self.assertRaises(DjangoValidationError):
            gym_class.full_clean()


# =========================================================
# ClassSession Model Tests
# =========================================================

class ClassSessionModelTest(TestCase):

    def setUp(self):

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
            datetime(2026, 8, 20, 10, 0)
        )

        self.end_time = timezone.make_aware(
            datetime(2026, 8, 20, 11, 0)
        )

    def create_valid_session(self, **kwargs):

        data = {
            "gym_class": self.gym_class,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "trainer": self.trainer,
        }

        data.update(kwargs)

        return ClassSession(**data)

    def test_create_valid_session(self):

        session = self.create_valid_session()

        session.full_clean()

        self.assertEqual(
            session.gym_class,
            self.gym_class,
        )

        self.assertEqual(
            session.trainer,
            self.trainer,
        )

    def test_attendance_default_is_empty_dict(self):

        session = self.create_valid_session()

        self.assertEqual(
            session.attendance,
            {},
        )

    def test_is_cancelled_default_is_false(self):

        session = self.create_valid_session()

        self.assertFalse(
            session.is_cancelled,
        )

    def test_present_count(self):

        session = self.create_valid_session(
            attendance={
                "1": {"present": True},
                "2": {"present": True},
                "3": {"present": False},
            }
        )

        self.assertEqual(
            session.present_count,
            2,
        )

    def test_absent_count(self):

        session = self.create_valid_session(
            attendance={
                "1": {"present": True},
                "2": {"present": False},
                "3": {"present": False},
            }
        )

        self.assertEqual(
            session.absent_count,
            2,
        )

    def test_single_session_students(self):

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

        session = self.create_valid_session(
            start_time=timezone.make_aware(
                datetime(2026, 8, 20, 11, 0)
            ),
            end_time=timezone.make_aware(
                datetime(2026, 8, 20, 10, 0)
            ),
        )

        with self.assertRaises(DjangoValidationError):
            session.full_clean()

    def test_trainer_must_be_active_trainer_of_gym(self):

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

        first_session = self.create_valid_session()

        first_session.save()

        overlapping_session = self.create_valid_session(
            start_time=timezone.make_aware(
                datetime(2026, 8, 20, 10, 30)
            ),
            end_time=timezone.make_aware(
                datetime(2026, 8, 20, 11, 30)
            ),
        )

        with self.assertRaises(DjangoValidationError):
            overlapping_session.save()

    def test_trainer_can_have_non_overlapping_sessions(self):

        first_session = self.create_valid_session()

        first_session.save()

        second_session = self.create_valid_session(
            start_time=timezone.make_aware(
                datetime(2026, 8, 20, 11, 0)
            ),
            end_time=timezone.make_aware(
                datetime(2026, 8, 20, 12, 0)
            ),
        )

        second_session.save()

        self.assertEqual(
            ClassSession.objects.count(),
            2,
        )

    def test_str(self):

        session = self.create_valid_session()

        expected = (
            f"{self.gym_class.name} - {self.start_time}"
        )

        self.assertEqual(
            str(session),
            expected,
        )


# =========================================================
# Classes Services Tests
# =========================================================

class ClassesServicesTest(TestCase):

    def setUp(self):

        # =========================
        # Users
        # =========================

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

        # =========================
        # Gym
        # =========================

        self.gym = Gym.objects.create(
            name="Test Gym",
            address="Test Address",
        )

        # =========================
        # Memberships
        # =========================

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

        # =========================
        # Gym Class
        # =========================

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

    # =====================================================
    # calculate_session_dates
    # =====================================================

    def test_calculate_session_dates(self):

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

        result = calculate_session_dates(
            None,
            date(2026, 8, 31),
            [0],
        )

        self.assertEqual(
            result,
            [],
        )

    # =====================================================
    # check_trainer_conflicts
    # =====================================================

    def test_check_trainer_conflicts_none_trainer(self):

        start = timezone.make_aware(
            datetime(2026, 8, 20, 10, 0)
        )

        end = timezone.make_aware(
            datetime(2026, 8, 20, 11, 0)
        )

        result = check_trainer_conflicts(
            None,
            start,
            end,
        )

        self.assertFalse(
            result,
        )

    def test_check_trainer_conflicts_exists(self):

        ClassSession.objects.create(
            gym_class=self.gym_class,
            trainer=self.trainer,
            start_time=timezone.make_aware(
                datetime(2026, 8, 20, 10, 0)
            ),
            end_time=timezone.make_aware(
                datetime(2026, 8, 20, 11, 0)
            ),
        )

        result = check_trainer_conflicts(
            self.trainer,
            timezone.make_aware(
                datetime(2026, 8, 20, 10, 30)
            ),
            timezone.make_aware(
                datetime(2026, 8, 20, 11, 30)
            ),
        )

        self.assertTrue(
            result,
        )

    def test_check_trainer_conflicts_no_conflict(self):

        ClassSession.objects.create(
            gym_class=self.gym_class,
            trainer=self.trainer,
            start_time=timezone.make_aware(
                datetime(2026, 8, 20, 10, 0)
            ),
            end_time=timezone.make_aware(
                datetime(2026, 8, 20, 11, 0)
            ),
        )

        result = check_trainer_conflicts(
            self.trainer,
            timezone.make_aware(
                datetime(2026, 8, 20, 11, 0)
            ),
            timezone.make_aware(
                datetime(2026, 8, 20, 12, 0)
            ),
        )

        self.assertFalse(
            result,
        )

    # =====================================================
    # generate_sessions
    # =====================================================

    def test_generate_sessions_creates_sessions(self):

        result = generate_sessions(
            self.gym_class
        )

        self.assertEqual(
            len(result["created"]),
            3,
        )

        self.assertEqual(
            ClassSession.objects.filter(
                gym_class=self.gym_class
            ).count(),
            3,
        )

    def test_generate_sessions_does_not_duplicate(self):

        generate_sessions(
            self.gym_class
        )

        result = generate_sessions(
            self.gym_class
        )

        self.assertEqual(
            result["created"],
            [],
        )

        self.assertEqual(
            result["conflicts"],
            ["Sessions already exist"],
        )

        self.assertEqual(
            ClassSession.objects.filter(
                gym_class=self.gym_class
            ).count(),
            3,
        )

    def test_generate_sessions_skips_trainer_conflict(self):

        conflict_date = date(2026, 8, 17)

        conflict_start = timezone.make_aware(
            datetime.combine(
                conflict_date,
                time(10, 0),
            )
        )

        conflict_end = timezone.make_aware(
            datetime.combine(
                conflict_date,
                time(11, 0),
            )
        )

        # کلاس دیگری که همان مربی را دارد
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

        # جلسه قبلی برای همان مربی،
        # اما مربوط به کلاس دیگری
        ClassSession.objects.create(
            gym_class=conflict_class,
            trainer=self.trainer,
            start_time=conflict_start,
            end_time=conflict_end,
        )

        result = generate_sessions(
            self.gym_class,
        )

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

    # =====================================================
    # get_enrolled_students
    # =====================================================

    def test_get_enrolled_students_semester(self):

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

        result = get_enrolled_students(
            session.id,
        )

        self.assertIn(
            enrollment,
            result,
        )

    def test_get_enrolled_students_single_session(self):

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

        enrollment.selected_sessions.add(
            session,
        )

        result = get_enrolled_students(
            session.id,
        )

        self.assertIn(
            enrollment,
            result,
        )

    def test_get_enrolled_students_returns_both_types(self):

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

        single_enrollment.selected_sessions.add(
            session,
        )

        result = get_enrolled_students(
            session.id,
        )

        self.assertIn(
            semester_enrollment,
            result,
        )

        self.assertIn(
            single_enrollment,
            result,
        )

    def test_get_enrolled_students_session_not_found(self):

        with self.assertRaises(NotFound):
            get_enrolled_students(
                99999,
            )

    # =====================================================
    # record_attendance
    # =====================================================

    def test_record_attendance_present(self):

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

        with self.assertRaises(NotFound):
            record_attendance(
                99999,
                self.member.id,
                True,
            )
            