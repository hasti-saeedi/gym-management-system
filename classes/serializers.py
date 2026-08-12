from rest_framework import serializers
from .models import GymClass, ClassSession
from enrollments.models import Enrollment
from .services.gym_class_services import generate_sessions



class GymClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymClass
        fields = "__all__"
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        gym_class = GymClass.objects.create(**validated_data)

        result = generate_sessions(gym_class)

        gym_class._generation_result = result

        return gym_class


class ClassSessionSerializer(serializers.ModelSerializer):
    class_name = serializers.ReadOnlyField(source='gym_class.name')
    available_seats = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    present_count = serializers.ReadOnlyField()
    absent_count = serializers.ReadOnlyField()
    single_session_students = serializers.ReadOnlyField()
    
    class Meta:
        model = ClassSession
        fields = [
            'id', 'gym_class', 'class_name', 'start_time', 'end_time',
            'trainer', 'attendance', 'is_cancelled', 'cancel_reason',
            'created_at', 'available_seats', 'is_full',
            'present_count', 'absent_count', 'single_session_students'
        ]
        read_only_fields = [
            'id',
            'created_at',
            'gym_class',
            'attendance',
            'present_count',
            'absent_count',
            'single_session_students'
        ]

class AttendanceSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    attendance_status = serializers.BooleanField()

class SessionStudentSerializer(serializers.ModelSerializer):

    user_id = serializers.ReadOnlyField(source="user.id")
    username = serializers.ReadOnlyField(source="user.username")

    attendance = serializers.SerializerMethodField()#اینجا خودش دنبال تابعی بع اسم get_attendace میگرده

    class Meta:
        model = Enrollment
        fields = [
            "user_id",
            "username",
            "enrollment_type",
            "attendance",
        ]

    def get_attendance(self, obj):
        session = self.context.get("session")

        # if not session:
        #     return None
            #session = ClassSession.objects.get(id=session_id)
            # پس سشنی که داره الان یک ردیف از کلس سشن هست
        attendance = session.attendance

        return attendance.get(str(obj.user.id))