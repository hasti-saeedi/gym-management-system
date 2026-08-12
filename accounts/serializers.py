from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from accounts.models import CustomUser
from gyms.models import Gym, GymMembership


class CustomUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'phone', 'first_name', 'last_name',
            'full_name','address', 
            'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined',]

    def get_full_name(self, obj):
        return obj.get_full_name()

class GymUserSerializer(CustomUserSerializer):

    role = serializers.SerializerMethodField()


    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + [
            "role",
        ]


    def get_role(self, obj):

        gym_id = self.context["view"].kwargs.get(
            "gym_id"
        )

        membership = obj.memberships.filter(
            gym_id=gym_id,
            is_active=True,
        ).first()


        if membership:
            return membership.role

        return None

class BaseRegisterSerializer(serializers.ModelSerializer):

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

        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({
                "password2": "Passwords do not match."
            })

        return attrs


class RegisterSerializer(BaseRegisterSerializer):
    """
    Public register

    Always creates MEMBER
    """

    gym = serializers.PrimaryKeyRelatedField(
        queryset=Gym.objects.filter(is_active=True)
    )

    class Meta(BaseRegisterSerializer.Meta):
        fields = BaseRegisterSerializer.Meta.fields + [
            "gym",
        ]



class CreateGymUserSerializer(BaseRegisterSerializer):

    role = serializers.ChoiceField(
        choices=GymMembership.Role.choices
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
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password] 
    )
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "رمزهای عبور مطابقت ندارند"})
        return attrs

class CurrentUserSerializer(serializers.ModelSerializer):

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

    class Meta:
        model = CustomUser

        fields = [
            "first_name",
            "last_name",
            "email",
        ]

class LoginSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()