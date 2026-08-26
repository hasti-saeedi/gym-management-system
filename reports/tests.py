from datetime import time, timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from accounts.models import CustomUser
from classes.models import ClassSession, GymClass
from enrollments.models import Enrollment
from gyms.models import Gym, GymMembership
from reports.models import Report

from reports.services.attendance_report_service import (
    get_attendance_statistics,
    get_cancelled_sessions,
    get_today_sessions,
)
from reports.services.class_report_service import get_class_statistics
from reports.services.dashboard_service import (
    get_dashboard,
    get_gym_info,
    get_member_statistics,
    get_session_statistics,
    get_staff_statistics,
)
from reports.services.member_report_service import (
    get_member_statistics as get_member_report_statistics,
    get_members_by_month,
    get_new_members,
)
from reports.services.staff_report_service import (
    get_staff_statistics as get_staff_report_statistics,
)
from reports.services.trainer_report_service import get_trainers_workload


class ReportModelTest(TestCase):
    """Test the Report model."""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="reporter",
            password="Test1234",
        )

    def test_create_report(self):
        report = Report.objects.create(
            title="Monthly Report",
            report_type="monthly",
            generated_by=self.user,
            data={"members": 10},
        )

        self.assertEqual(report.title, "Monthly Report")
        self.assertEqual(report.report_type, "monthly")
        self.assertEqual(report.generated_by, self.user)
        self.assertEqual(report.data["members"], 10)

    def test_report_created_at_is_set(self):
        report = Report.objects.create(
            title="Daily Report",
            report_type="daily",
            generated_by=self.user,
        )

        self.assertIsNotNone(report.created_at)

    def test_report_string_representation(self):
        report = Report.objects.create(
            title="Monthly Report",
            report_type="monthly",
            generated_by=self.user,
        )

        expected = (
            f"Monthly Report - "
            f"{report.created_at.strftime('%Y-%m-%d')}"
        )

        self.assertEqual(str(report), expected)

    def test_report_ordering(self):
        now = timezone.now()

        first = Report.objects.create(
            title="First",
            report_type="daily",
            generated_by=self.user,
            created_at=now - timedelta(minutes=1),
        )

        second = Report.objects.create(
            title="Second",
            report_type="daily",
            generated_by=self.user,
            created_at=now,
        )

        reports = list(Report.objects.all())

        self.assertEqual(reports[0], second)
        self.assertEqual(reports[1], first)

    def test_report_can_be_created_without_generated_by(self):
        report = Report.objects.create(
            title="System Report",
            report_type="custom",
            generated_by=None,
        )

        self.assertIsNone(report.generated_by)


class ReportsTestMixin:
    """Provide reusable factory methods for report tests."""

    def create_user(self, username, password="Test1234"):
        return CustomUser.objects.create_user(
            username=username,
            password=password,
        )

    def create_gym(self, name="Test Gym"):
        return Gym.objects.create(
            name=name,
            address="Tehran",
        )

    def create_membership(
        self,
        user,
        gym,
        role,
        is_active=True,
        salary=None,
        share_percentage=None,
    ):
        return GymMembership.objects.create(
            user=user,
            gym=gym,
            role=role,
            is_active=is_active,
            salary=salary,
            share_percentage=share_percentage,
        )

    def create_class(
        self,
        gym,
        name="Yoga",
        trainer=None,
        capacity=10,
        current_enrolled=0,
        is_active=True,
    ):
        return GymClass.objects.create(
            name=name,
            category="yoga",
            gym=gym,
            trainer=trainer,
            capacity=capacity,
            current_enrolled=current_enrolled,
            duration_minutes=60,
            price=Decimal("100000"),
            single_session_price=Decimal("15000"),
            regular_days=[],
            is_active=is_active,
        )

    def create_session(
        self,
        gym_class,
        start_time,
        end_time,
        trainer=None,
        is_cancelled=False,
    ):
        return ClassSession.objects.create(
            gym_class=gym_class,
            start_time=start_time,
            end_time=end_time,
            trainer=trainer,
            is_cancelled=is_cancelled,
        )


class AttendanceReportServiceTest(ReportsTestMixin, TestCase):
    """Test attendance report services."""

    def setUp(self):
        self.gym = self.create_gym()

        self.user = self.create_user("trainer")

        self.create_membership(
            self.user,
            self.gym,
            GymMembership.Role.TRAINER,
            salary=Decimal("5000000"),
        )

        self.gym_class = self.create_class(
            gym=self.gym,
            trainer=self.user,
        )

    def test_get_attendance_statistics(self):
        now = timezone.now()

        self.create_session(
            self.gym_class,
            now + timedelta(hours=1),
            now + timedelta(hours=2),
        )

        self.create_session(
            self.gym_class,
            now + timedelta(hours=3),
            now + timedelta(hours=4),
            is_cancelled=True,
        )

        result = get_attendance_statistics(self.gym.id)

        self.assertEqual(result["total_sessions"], 2)
        self.assertEqual(result["active_sessions"], 1)
        self.assertEqual(result["cancelled_sessions"], 1)

    def test_get_attendance_statistics_empty_gym(self):
        result = get_attendance_statistics(self.gym.id)

        self.assertEqual(result["total_sessions"], 0)
        self.assertEqual(result["active_sessions"], 0)
        self.assertEqual(result["cancelled_sessions"], 0)

    def test_get_today_sessions(self):
        today = timezone.localdate()

        start = timezone.make_aware(
            timezone.datetime.combine(
                today,
                time(10, 0),
            )
        )

        end = timezone.make_aware(
            timezone.datetime.combine(
                today,
                time(11, 0),
            )
        )

        session = self.create_session(
            self.gym_class,
            start,
            end,
        )

        result = list(
            get_today_sessions(self.gym.id)
        )

        self.assertIn(session, result)

    def test_get_today_sessions_excludes_other_days(self):
        today = timezone.localdate()
        tomorrow = today + timedelta(days=1)

        start = timezone.make_aware(
            timezone.datetime.combine(
                tomorrow,
                time(10, 0),
            )
        )

        end = timezone.make_aware(
            timezone.datetime.combine(
                tomorrow,
                time(11, 0),
            )
        )

        session = self.create_session(
            self.gym_class,
            start,
            end,
        )

        result = list(
            get_today_sessions(self.gym.id)
        )

        self.assertNotIn(session, result)

    def test_get_cancelled_sessions(self):
        now = timezone.now()

        cancelled = self.create_session(
            self.gym_class,
            now + timedelta(hours=1),
            now + timedelta(hours=2),
            is_cancelled=True,
        )

        active = self.create_session(
            self.gym_class,
            now + timedelta(hours=3),
            now + timedelta(hours=4),
            is_cancelled=False,
        )

        result = list(
            get_cancelled_sessions(self.gym.id)
        )

        self.assertIn(cancelled, result)
        self.assertNotIn(active, result)


class ClassReportServiceTest(ReportsTestMixin, TestCase):
    """Test class report services."""

    def setUp(self):
        self.gym = self.create_gym()

    def test_get_class_statistics(self):
        self.create_class(
            self.gym,
            name="Active Class",
            is_active=True,
            capacity=10,
            current_enrolled=5,
        )

        self.create_class(
            self.gym,
            name="Inactive Class",
            is_active=False,
            capacity=10,
            current_enrolled=2,
        )

        self.create_class(
            self.gym,
            name="Full Class",
            is_active=True,
            capacity=10,
            current_enrolled=10,
        )

        result = get_class_statistics(self.gym.id)

        self.assertEqual(result["total"], 3)
        self.assertEqual(result["active"], 2)
        self.assertEqual(result["inactive"], 1)
        self.assertEqual(result["full"], 1)
        self.assertEqual(result["available"], 2)

    def test_get_class_statistics_empty(self):
        result = get_class_statistics(self.gym.id)

        self.assertEqual(result["total"], 0)
        self.assertEqual(result["active"], 0)
        self.assertEqual(result["inactive"], 0)
        self.assertEqual(result["full"], 0)
        self.assertEqual(result["available"], 0)


class DashboardServiceTest(ReportsTestMixin, TestCase):
    """Test dashboard report services."""

    def setUp(self):
        self.gym = self.create_gym()

        self.member = self.create_user("member")
        self.manager = self.create_user("manager")
        self.trainer = self.create_user("trainer")
        self.staff = self.create_user("staff")

        self.create_membership(
            self.member,
            self.gym,
            GymMembership.Role.MEMBER,
        )

        self.create_membership(
            self.manager,
            self.gym,
            GymMembership.Role.MANAGER,
            salary=Decimal("5000000"),
        )

        self.create_membership(
            self.trainer,
            self.gym,
            GymMembership.Role.TRAINER,
            salary=Decimal("4000000"),
        )

        self.create_membership(
            self.staff,
            self.gym,
            GymMembership.Role.STAFF,
            salary=Decimal("3000000"),
        )

    def test_get_member_statistics(self):
        result = get_member_statistics(self.gym.id)

        self.assertEqual(result["total"], 1)
        self.assertEqual(result["active"], 1)
        self.assertEqual(result["inactive"], 0)

    def test_get_staff_statistics(self):
        result = get_staff_statistics(self.gym.id)

        self.assertEqual(result["total"], 3)
        self.assertEqual(result["active"], 3)
        self.assertEqual(result["inactive"], 0)
        self.assertEqual(result["managers"], 1)
        self.assertEqual(result["trainers"], 1)
        self.assertEqual(result["staff"], 1)

    def test_get_gym_info(self):
        result = get_gym_info(self.gym.id)

        self.assertEqual(result["id"], self.gym.id)
        self.assertEqual(result["name"], self.gym.name)
        self.assertTrue(result["is_active"])

    def test_get_session_statistics(self):
        gym_class = self.create_class(
            self.gym,
            trainer=self.trainer,
        )

        now = timezone.now()

        self.create_session(
            gym_class,
            now - timedelta(minutes=30),
            now + timedelta(minutes=30),
        )

        self.create_session(
            gym_class,
            now - timedelta(hours=2),
            now - timedelta(hours=1),
        )

        self.create_session(
            gym_class,
            now + timedelta(hours=1),
            now + timedelta(hours=2),
        )

        self.create_session(
            gym_class,
            now + timedelta(hours=3),
            now + timedelta(hours=4),
            is_cancelled=True,
        )

        result = get_session_statistics(self.gym.id)

        self.assertEqual(result["total"], 4)
        self.assertEqual(result["cancelled"], 1)
        self.assertEqual(result["running"], 1)
        self.assertEqual(result["finished"], 1)
        self.assertEqual(result["upcoming"], 1)

    def test_get_dashboard(self):
        result = get_dashboard(self.gym.id)

        self.assertIn("gym", result)
        self.assertIn("members", result)
        self.assertIn("staff", result)
        self.assertIn("classes", result)
        self.assertIn("sessions", result)

        self.assertEqual(
            result["gym"]["id"],
            self.gym.id,
        )


class MemberReportServiceTest(ReportsTestMixin, TestCase):
    """Test member report services."""

    def setUp(self):
        self.gym = self.create_gym()

        self.member1 = self.create_user("member1")
        self.member2 = self.create_user("member2")
        self.trainer = self.create_user("trainer")

        self.create_membership(
            self.member1,
            self.gym,
            GymMembership.Role.MEMBER,
        )

        self.create_membership(
            self.member2,
            self.gym,
            GymMembership.Role.MEMBER,
        )

        self.create_membership(
            self.trainer,
            self.gym,
            GymMembership.Role.TRAINER,
            salary=Decimal("4000000"),
        )

    def test_get_member_report_statistics(self):
        result = get_member_report_statistics(
            self.gym.id
        )

        self.assertEqual(result["total"], 2)
        self.assertEqual(result["active"], 2)
        self.assertEqual(result["inactive"], 0)

    def test_get_new_members(self):
        result = list(
            get_new_members(self.gym.id)
        )

        self.assertEqual(len(result), 2)

        self.assertIn(
            self.member1,
            [membership.user for membership in result],
        )

        self.assertIn(
            self.member2,
            [membership.user for membership in result],
        )

    def test_get_members_by_month(self):
        result = list(
            get_members_by_month(self.gym.id)
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["total"], 2)


class StaffReportServiceTest(ReportsTestMixin, TestCase):
    """Test staff report services."""

    def setUp(self):
        self.gym = self.create_gym()

        self.owner = self.create_user("owner")
        self.manager = self.create_user("manager")
        self.staff = self.create_user("staff")
        self.member = self.create_user("member")

        self.create_membership(
            self.owner,
            self.gym,
            GymMembership.Role.OWNER,
            share_percentage=20,
            salary=None,
        )

        self.create_membership(
            self.manager,
            self.gym,
            GymMembership.Role.MANAGER,
            salary=Decimal("5000000"),
        )

        self.create_membership(
            self.staff,
            self.gym,
            GymMembership.Role.STAFF,
            salary=Decimal("3000000"),
        )

        self.create_membership(
            self.member,
            self.gym,
            GymMembership.Role.MEMBER,
        )

    def test_get_staff_report_statistics(self):
        result = get_staff_report_statistics(
            self.gym.id
        )

        self.assertEqual(result["owners"], 1)
        self.assertEqual(result["managers"], 1)
        self.assertEqual(result["staff"], 1)
        self.assertEqual(result["total"], 3)
        self.assertEqual(result["active"], 3)
        self.assertEqual(result["inactive"], 0)


class TrainerReportServiceTest(ReportsTestMixin, TestCase):
    """Test trainer report services."""

    def setUp(self):
        self.gym = self.create_gym()

        self.trainer1 = self.create_user("trainer1")
        self.trainer2 = self.create_user("trainer2")

        self.create_membership(
            self.trainer1,
            self.gym,
            GymMembership.Role.TRAINER,
            salary=Decimal("4000000"),
        )

        self.create_membership(
            self.trainer2,
            self.gym,
            GymMembership.Role.TRAINER,
            salary=Decimal("4500000"),
        )

        self.class1 = self.create_class(
            self.gym,
            name="Yoga",
            trainer=self.trainer1,
        )

        self.class2 = self.create_class(
            self.gym,
            name="Crossfit",
            trainer=self.trainer1,
        )

        self.class3 = self.create_class(
            self.gym,
            name="Swimming",
            trainer=self.trainer2,
        )

    def test_get_trainers_workload(self):
        result = list(
            get_trainers_workload(self.gym.id)
        )

        trainer1 = next(
            item
            for item in result
            if item.user == self.trainer1
        )

        trainer2 = next(
            item
            for item in result
            if item.user == self.trainer2
        )

        self.assertEqual(
            trainer1.total_classes,
            2,
        )

        self.assertEqual(
            trainer2.total_classes,
            1,
        )

    def test_get_trainers_workload_only_returns_trainers(self):
        member = self.create_user("member")

        self.create_membership(
            member,
            self.gym,
            GymMembership.Role.MEMBER,
        )

        result = list(
            get_trainers_workload(self.gym.id)
        )

        users = [
            item.user
            for item in result
        ]

        self.assertNotIn(member, users)
        self.assertIn(self.trainer1, users)
        self.assertIn(self.trainer2, users)