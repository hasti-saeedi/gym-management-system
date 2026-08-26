from rest_framework import serializers

from enrollments.models import Enrollment

from .models import ClassSession, GymClass
from .services.gym_class_services import generate_sessions


class GymClassSerializer(serializers.ModelSerializer):
    """
    Serialize gym class data and generate its sessions upon creation.
    """

    class Meta:
        model = GymClass
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
        ]

    def create(self, validated_data):
        """
        Create a gym class and automatically generate its sessions.

        Args:
            validated_data (dict): Validated data for creating the gym class.

        Returns:
            GymClass: The newly created gym class instance.
        """
        gym_class = GymClass.objects.create(
            **validated_data
        )

        result = generate_sessions(gym_class)

        gym_class._generation_result = result

        return gym_class


class ClassSessionSerializer(serializers.ModelSerializer):
    """
    Serialize class session data and expose computed session information.

    Includes class details, attendance information, seat availability,
    and other computed session properties.
    """

    class_name = serializers.ReadOnlyField(
        source="gym_class.name"
    )
    available_seats = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    present_count = serializers.ReadOnlyField()
    absent_count = serializers.ReadOnlyField()
    single_session_students = serializers.ReadOnlyField()

    class Meta:
        model = ClassSession
        fields = [
            "id",
            "gym_class",
            "class_name",
            "start_time",
            "end_time",
            "trainer",
            "attendance",
            "is_cancelled",
            "cancel_reason",
            "created_at",
            "available_seats",
            "is_full",
            "present_count",
            "absent_count",
            "single_session_students",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "gym_class",
            "attendance",
            "present_count",
            "absent_count",
            "single_session_students",
        ]


class AttendanceSerializer(serializers.Serializer):
    """
    Validate attendance data for a class session.
    """

    user_id = serializers.IntegerField()
    attendance_status = serializers.BooleanField()


class SessionStudentSerializer(serializers.ModelSerializer):
    """
    Serialize enrollment and attendance information for a session student.
    """

    user_id = serializers.ReadOnlyField(
        source="user.id"
    )
    username = serializers.ReadOnlyField(
        source="user.username"
    )
    attendance = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = [
            "user_id",
            "username",
            "enrollment_type",
            "attendance",
        ]

    def get_attendance(self, obj):
        """
        Return the student's attendance record for the current session.

        Args:
            obj (Enrollment): The student's enrollment instance.

        Returns:
            dict or None: The attendance record for the current session.
        """
        session = self.context.get("session")

        if not session:
            return None

        return session.attendance.get(
            str(obj.user.id)
        )