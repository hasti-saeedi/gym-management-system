from rest_framework import serializers
from .models import Enrollment, Payment
from classes.models import ClassSession
from classes.serializers import ClassSessionSerializer

class ClassSessionSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClassSession
        fields = [
            'id',
            'start_time',
            'end_time',
            'gym_class'
        ]


class EnrollmentSerializer(serializers.ModelSerializer):

    user_username = serializers.ReadOnlyField(
        source='user.username'
    )

    gym_class_name = serializers.ReadOnlyField(
        source='gym_class.name'
    )

    selected_sessions_details = ClassSessionSimpleSerializer(
        many=True,
        read_only=True,
        source='selected_sessions'
    )

    class Meta:
        model = Enrollment

        fields = [
            'id',
            'gym_class',
            'user',
            'status',
            'registered_at',
            # 'attended',
            'enrollment_type',
            'selected_sessions',
            'selected_sessions_details',
            'user_username',
            'gym_class_name',
        ]

        read_only_fields = [
            'id',
            'registered_at',
        ]


class EnrollmentUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Enrollment

        fields = [
            "status",
            "attended",
            "enrollment_type",
            "selected_sessions",
        ]


class MemberEnrollmentCreateSerializer(serializers.Serializer):

    gym_class_id = serializers.IntegerField()

    enrollment_type = serializers.ChoiceField(
        choices=Enrollment.ENROLLMENT_TYPE
    )

    selected_sessions_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )


class StaffEnrollmentCreateSerializer(serializers.Serializer):

    user_id = serializers.IntegerField(
        required=True
    )
    gym_class_id = serializers.IntegerField()

    enrollment_type = serializers.ChoiceField(
        choices=Enrollment.ENROLLMENT_TYPE
    )

    selected_sessions_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )
    

class PaymentSerializer(serializers.ModelSerializer):

    enrollment_user = serializers.ReadOnlyField(
        source='enrollment.user.username'
    )


    enrollment_user_id = serializers.ReadOnlyField(
        source='enrollment.user.id'
    )


    enrollment_class = serializers.ReadOnlyField(
        source='enrollment.gym_class.name'
    )

    enrollment_type = serializers.ReadOnlyField(
        source = 'enrollment.enrollment_type'
    )

    selected_sessions_details = ClassSessionSerializer(
    source="enrollment.selected_sessions",
    many=True,
    read_only=True
    )

    enrollment_status = serializers.ReadOnlyField(
        source='enrollment.status'
    )

    class Meta:
        model = Payment

        fields = [
            'id',
            'enrollment',
            'enrollment_user',
            'enrollment_user_id',
            'enrollment_class',
            'enrollment_status',
            'enrollment_type',
            'amount',
            'status',
            'transaction_id',
            'selected_sessions_details',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]

    #سریالایزر برای درآوردن حضورو یاب
    #الان اینجا ما اینرولمنت رو داتمی حالا اون رو میاریم و چون ستون کلس سشنز هم داشتیم اونم میاریم 
        #خروجی اخر میشه اسم همه شاگردان 


class ConfirmPaymentSerializer(serializers.Serializer):
    transaction_id = serializers.CharField()