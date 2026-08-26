from rest_framework import serializers

from classes.models import ClassSession
from classes.serializers import ClassSessionSerializer

from .models import Enrollment, Payment


class ClassSessionSimpleSerializer(serializers.ModelSerializer):
    """
    Serialize basic information about a class session.
    """

    class Meta:
        model = ClassSession
        fields = [
            "id",
            "start_time",
            "end_time",
            "gym_class",
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Serialize enrollment information and selected session details.
    """

    user_username = serializers.ReadOnlyField(
        source="user.username",
    )

    gym_class_name = serializers.ReadOnlyField(
        source="gym_class.name",
    )

    selected_sessions_details = ClassSessionSimpleSerializer(
        many=True,
        read_only=True,
        source="selected_sessions",
    )

    class Meta:
        model = Enrollment

        fields = [
            "id",
            "gym_class",
            "user",
            "status",
            "registered_at",
            "enrollment_type",
            "selected_sessions",
            "selected_sessions_details",
            "user_username",
            "gym_class_name",
        ]

        read_only_fields = [
            "id",
            "registered_at",
        ]


class EnrollmentUpdateSerializer(serializers.ModelSerializer):
    """
    Serialize fields that can be updated for an enrollment.
    """

    class Meta:
        model = Enrollment

        fields = [
            "status",
            "attended",
            "enrollment_type",
            "selected_sessions",
        ]


class MemberEnrollmentCreateSerializer(serializers.Serializer):
    """
    Validate data required for a member to create an enrollment.
    """

    gym_class_id = serializers.IntegerField()

    enrollment_type = serializers.ChoiceField(
        choices=Enrollment.ENROLLMENT_TYPE,
    )

    selected_sessions_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )


class StaffEnrollmentCreateSerializer(serializers.Serializer):
    """
    Validate data required for staff to create an enrollment for a user.
    """

    user_id = serializers.IntegerField(
        required=True,
    )

    gym_class_id = serializers.IntegerField()

    enrollment_type = serializers.ChoiceField(
        choices=Enrollment.ENROLLMENT_TYPE,
    )

    selected_sessions_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serialize payment information with related enrollment details.
    """

    enrollment_user = serializers.ReadOnlyField(
        source="enrollment.user.username",
    )

    enrollment_user_id = serializers.ReadOnlyField(
        source="enrollment.user.id",
    )

    enrollment_class = serializers.ReadOnlyField(
        source="enrollment.gym_class.name",
    )

    enrollment_type = serializers.ReadOnlyField(
        source="enrollment.enrollment_type",
    )

    selected_sessions_details = ClassSessionSerializer(
        source="enrollment.selected_sessions",
        many=True,
        read_only=True,
    )

    enrollment_status = serializers.ReadOnlyField(
        source="enrollment.status",
    )

    class Meta:
        model = Payment

        fields = [
            "id",
            "enrollment",
            "enrollment_user",
            "enrollment_user_id",
            "enrollment_class",
            "enrollment_status",
            "enrollment_type",
            "amount",
            "status",
            "transaction_id",
            "selected_sessions_details",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class ConfirmPaymentSerializer(serializers.Serializer):
    """
    Validate the transaction ID required to confirm a payment.
    """

    transaction_id = serializers.CharField()