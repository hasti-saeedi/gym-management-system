from rest_framework import serializers
from .models import Gym, GymMembership

class GymSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gym
        fields = [
            'id', 'name', 'address', 'phone', 'email', 'is_active', 'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id','created_at', 'updated_at']

class GymMembershipSerializer(serializers.ModelSerializer):

    user_username = serializers.ReadOnlyField(source = 'user.username')
    gym_name = serializers.ReadOnlyField(source = 'gym.name')
    role_display = serializers.ReadOnlyField(source = 'get_role_display')

    class Meta:
        model = GymMembership
        fields = [
            'id', 'user', 'gym', 'role', 'share_percentage',
            'salary', 'joined_at', 'is_active','user_username','gym_name', 'role_display',
        ]
        read_only_fields = ['id', 'joined_at']

class GymStaffSerializer(serializers.ModelSerializer):

    user_id = serializers.ReadOnlyField(source="user.id")
    username = serializers.ReadOnlyField(source="user.username")
    full_name = serializers.ReadOnlyField(source="user.get_full_name")

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

class AddStaffSerializer(serializers.Serializer):

    user_id = serializers.IntegerField()
    role = serializers.ChoiceField(
        choices=GymMembership.Role.choices,
    )
    salary = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    share_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        allow_null=True,
    )

class ChangeStaffRoleSerializer(serializers.Serializer):

    role = serializers.ChoiceField(
        choices=GymMembership.Role.choices,
    )

    salary = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    share_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        allow_null=True,
    )

# ##### dashboard
# class MemberDashboardSerializer(serializers.Serializer):
#     total = serializers.IntegerField()
#     active = serializers.IntegerField()

# class StaffDashboardSerializer(serializers.Serializer):
#     total = serializers.IntegerField()
#     owners = serializers.IntegerField()
#     managers = serializers.IntegerField()
#     trainers = serializers.IntegerField()
#     cashiers = serializers.IntegerField()
#     staff = serializers.IntegerField()

# class ClassDashboardSerializer(serializers.Serializer):
#     active = serializers.IntegerField()
#     inactive = serializers.IntegerField()

# class SessionDashboardSerializer(serializers.Serializer):
#     today = serializers.IntegerField()
#     cancelled = serializers.IntegerField()
#     running = serializers.IntegerField()
#     finished = serializers.IntegerField()
#     upcoming = serializers.IntegerField()

# class GymDashboardSerializer(serializers.Serializer):

#     gym = GymInfoSerializer()

#     members = MemberDashboardSerializer()

#     staff = StaffDashboardSerializer()

#     classes = ClassDashboardSerializer()

#     sessions = SessionDashboardSerializer()
