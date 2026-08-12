from rest_framework import serializers


class GymInfoReportSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    name = serializers.CharField()
    is_active = serializers.BooleanField()

class MemberStatisticsReportSerializer(serializers.Serializer):

    total = serializers.IntegerField()
    active = serializers.IntegerField()
    inactive = serializers.IntegerField()

class StaffStatisticsReportSerializer(serializers.Serializer):

    total = serializers.IntegerField()
    active = serializers.IntegerField()
    inactive = serializers.IntegerField()

    owners = serializers.IntegerField()
    managers = serializers.IntegerField()
    trainers = serializers.IntegerField()
    staff = serializers.IntegerField()

class ClassStatisticsReportSerializer(serializers.Serializer):

    total = serializers.IntegerField()
    active = serializers.IntegerField()
    inactive = serializers.IntegerField()

class SessionStatisticsReportSerializer(serializers.Serializer):

    total = serializers.IntegerField()
    today = serializers.IntegerField()

    cancelled = serializers.IntegerField()

    running = serializers.IntegerField()
    finished = serializers.IntegerField()
    upcoming = serializers.IntegerField()

class DashboardReportSerializer(serializers.Serializer):

    gym = GymInfoReportSerializer()

    members = MemberStatisticsReportSerializer()

    staff = StaffStatisticsReportSerializer()

    classes = ClassStatisticsReportSerializer()

    sessions = SessionStatisticsReportSerializer()


###### member

class MemberStatisticsSerializer(serializers.Serializer):

    total = serializers.IntegerField()

    active = serializers.IntegerField()

    inactive = serializers.IntegerField()


class NewMemberReportSerializer(serializers.Serializer):

    id = serializers.IntegerField(source="user.id")

    username = serializers.CharField(source="user.username")

    joined_at = serializers.DateTimeField()


class MemberMonthlyReportSerializer(serializers.Serializer):

    month = serializers.IntegerField()

    total = serializers.IntegerField()


##### attendence

class AttendanceStatisticsReportSerializer(serializers.Serializer):

    total_sessions = serializers.IntegerField()

    active_sessions = serializers.IntegerField()

    cancelled_sessions = serializers.IntegerField()


class SessionReportSerializer(serializers.Serializer):

    id = serializers.IntegerField()

    class_name = serializers.CharField(
        source="gym_class.name"
    )

    trainer = serializers.CharField(
        source="trainer.username",
        allow_null=True,# فرقش با نال ؟
    )

    start_time = serializers.DateTimeField()

    end_time = serializers.DateTimeField()

    is_cancelled = serializers.BooleanField()

####staff
class StaffStatisticsReportSerializer(serializers.Serializer):

    owners = serializers.IntegerField()

    managers = serializers.IntegerField()

    staff = serializers.IntegerField()

    total = serializers.IntegerField()

    active = serializers.IntegerField()

    inactive = serializers.IntegerField()

#### trainer
class TrainerWorkloadReportSerializer(serializers.Serializer):

    trainer_id = serializers.IntegerField(
        source="user.id",
    )

    trainer_name = serializers.CharField(
        source="user.username",
    )

    total_classes = serializers.IntegerField()

### class
class ClassStatisticsReportSerializer(serializers.Serializer):

    total = serializers.IntegerField()

    active = serializers.IntegerField()

    inactive = serializers.IntegerField()

    full = serializers.IntegerField()

    available = serializers.IntegerField()