from rest_framework import serializers

from .models import Gym, GymMembership


class GymSerializer(serializers.ModelSerializer):
    """
    Serializer for Gym model.

    Used for creating, retrieving, and updating gym information.

    Read-only fields:
        - id
        - created_at
        - updated_at
    """

    class Meta:
        model = Gym

        fields = [
            "id",
            "name",
            "address",
            "phone",
            "email",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class GymMembershipSerializer(serializers.ModelSerializer):
    """
    Serializer for GymMembership model.

    Provides membership information together with
    read-only user, gym, and role display information.

    Read-only fields:
        - id
        - joined_at
        - user_username
        - gym_name
        - role_display
    """

    user_username = serializers.ReadOnlyField(
        source="user.username"
    )

    gym_name = serializers.ReadOnlyField(
        source="gym.name"
    )

    role_display = serializers.ReadOnlyField(
        source="get_role_display"
    )

    class Meta:
        model = GymMembership

        fields = [
            "id",
            "user",
            "gym",
            "role",
            "share_percentage",
            "salary",
            "joined_at",
            "is_active",
            "user_username",
            "gym_name",
            "role_display",
        ]

        read_only_fields = [
            "id",
            "joined_at",
            "user_username",
            "gym_name",
            "role_display",
        ]


class GymStaffSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying gym staff information.

    User information is exposed through read-only fields.

    Fields:
        - user_id
        - username
        - full_name
        - role
        - salary
        - share_percentage
        - is_active
        - joined_at
    """

    user_id = serializers.ReadOnlyField(
        source="user.id"
    )

    username = serializers.ReadOnlyField(
        source="user.username"
    )

    full_name = serializers.ReadOnlyField(
        source="user.get_full_name"
    )

    class Meta:
        model = GymMembership

        fields = [
            "id",
            "user_id",
            "username",
            "full_name",
            "role",
            "salary",
            "share_percentage",
            "is_active",
            "joined_at",
        ]

        read_only_fields = [
            "id",
            "user_id",
            "username",
            "full_name",
            "joined_at",
        ]


class AddStaffSerializer(serializers.Serializer):
    """
    Validate input required to create a new GymMembership.

    Business permission rules such as who can add which role
    are handled by the service layer.

    This serializer is responsible only for validating
    the structure and basic validity of request data.
    """

    user_id = serializers.IntegerField()

    role = serializers.ChoiceField(
        choices=GymMembership.Role.choices,
    )

    salary = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
    )

    share_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        allow_null=True,
    )


class ChangeStaffRoleSerializer(serializers.Serializer):
    """
    Validate input required to update a GymMembership.

    The service layer is responsible for checking whether
    the authenticated user is allowed to perform the update.

    Supported fields:
        - role
        - salary
        - share_percentage
    """

    role = serializers.ChoiceField(
        choices=GymMembership.Role.choices,
    )

    salary = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
    )

    share_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        allow_null=True,
    )