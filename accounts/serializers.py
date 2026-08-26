from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from accounts.models import CustomUser
from gyms.models import Gym, GymMembership


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serialize basic user profile information.

    Provides the user's account and profile fields, including
    a computed full name.
    """

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "first_name",
            "last_name",
            "full_name",
            "address",
            "is_active",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "date_joined",
        ]

    def get_full_name(self, obj):
        """
        Return the user's full name.

        Args:
            obj (CustomUser): The user instance being serialized.

        Returns:
            str: The user's full name.
        """
        return obj.get_full_name()


class GymUserSerializer(CustomUserSerializer):
    """
    Serialize user information together with their gym-specific role.
    """

    role = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + [
            "role",
        ]

    def get_role(self, obj):
        """
        Return the user's active role within the current gym.

        Args:
            obj (CustomUser): The user instance being serialized.

        Returns:
            str or None: The user's active gym role, if available.
        """
        gym_id = self.context["view"].kwargs.get("gym_id")

        membership = obj.memberships.filter(
            gym_id=gym_id,
            is_active=True,
        ).first()

        if membership:
            return membership.role

        return None


class BaseRegisterSerializer(serializers.ModelSerializer):
    """
    Provide common fields and validation for user registration.
    """

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )

    password2 = serializers.CharField(
        write_only=True,
    )

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "phone",
            "first_name",
            "last_name",
            "address",
            "password",
            "password2",
        ]

    def validate(self, attrs):
        """
        Validate that both password fields contain the same value.

        Args:
            attrs (dict): Validated serializer data.

        Returns:
            dict: Validated serializer data.

        Raises:
            serializers.ValidationError: If the passwords do not match.
        """
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({
                "password2": "Passwords do not match.",
            })

        return attrs


class RegisterSerializer(BaseRegisterSerializer):
    """
    Handle public user registration for active gyms.
    """

    gym = serializers.PrimaryKeyRelatedField(
        queryset=Gym.objects.filter(is_active=True),
    )

    class Meta(BaseRegisterSerializer.Meta):
        fields = BaseRegisterSerializer.Meta.fields + [
            "gym",
        ]


class CreateGymUserSerializer(BaseRegisterSerializer):
    """
    Handle creation of a user and their role within a gym.
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

    class Meta(BaseRegisterSerializer.Meta):
        fields = BaseRegisterSerializer.Meta.fields + [
            "role",
            "salary",
            "share_percentage",
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """
    Validate data required to change a user's password.
    """

    old_password = serializers.CharField(
        write_only=True,
        required=True,
    )

    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )

    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
    )

    def validate(self, attrs):
        """
        Validate that the new password and confirmation match.

        Args:
            attrs (dict): Validated serializer data.

        Returns:
            dict: Validated serializer data.

        Raises:
            serializers.ValidationError: If the passwords do not match.
        """
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match.",
            })

        return attrs


class CurrentUserSerializer(serializers.ModelSerializer):
    """
    Serialize the authenticated user's current profile information.
    """

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "phone",
            "is_superuser",
        ]


class CurrentUserUpdateSerializer(serializers.ModelSerializer):
    """
    Define the fields that an authenticated user can update.
    """

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "email",
        ]


class LoginSerializer(serializers.Serializer):
    """
    Validate credentials required for user authentication.
    """

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class LogoutSerializer(serializers.Serializer):
    """
    Validate the refresh token required for user logout.
    """

    refresh = serializers.CharField()