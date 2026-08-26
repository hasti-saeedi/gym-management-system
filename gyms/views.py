from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import (
    OrderingFilter,
    SearchFilter,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from .models import Gym, GymMembership
from .serializers import (
    AddStaffSerializer,
    ChangeStaffRoleSerializer,
    GymMembershipSerializer,
    GymSerializer,
    GymStaffSerializer,
)
from .services.gym_membership_services import (
    activate_staff,
    add_staff,
    deactivate_staff,
    get_gym_staff,
    update_membership,
)
from permissions.gym_permissions import (
    CanAddStaff,
    CanCreateGym,
    CanCreateGymMembership,
    CanManageGym,
    CanManageGymMembership,
    CanViewGymMembers,
    CanViewGymMembership,
)


class GymViewSet(viewsets.ModelViewSet):
    """ViewSet for managing gyms and gym staff."""

    queryset = Gym.objects.all()
    serializer_class = GymSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "name",
        "address",
        "phone",
        "email",
    ]

    filterset_fields = [
        "is_active",
    ]

    ordering_fields = [
        "name",
        "created_at",
    ]

    def get_permissions(self):
        """Return permissions based on the current action."""

        if self.action in ["list", "retrieve"]:
            permission_classes = [
                AllowAny,
            ]

        elif self.action == "create":
            permission_classes = [
                IsAuthenticated,
                CanCreateGym,
            ]

        elif self.action in [
            "update",
            "partial_update",
            "destroy",
        ]:
            permission_classes = [
                IsAuthenticated,
                CanManageGym,
            ]

        elif self.action == "add_staff":
            permission_classes = [
                IsAuthenticated,
                CanAddStaff,
            ]

        elif self.action == "members":
            permission_classes = [
                IsAuthenticated,
                CanViewGymMembers,
            ]

        else:
            permission_classes = [
                IsAuthenticated,
            ]

        return [
            permission()
            for permission in permission_classes
        ]

    @action(
        detail=True,
        methods=["get"],
    )
    def members(self, request, pk=None):
        """Return staff members belonging to the specified gym."""

        members = get_gym_staff(pk)

        serializer = GymStaffSerializer(
            members,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=AddStaffSerializer,
        responses={
            201: GymStaffSerializer,
        },
    )
    @action(
        detail=True,
        methods=["post"],
    )
    def add_staff(self, request, pk=None):
        """Add a staff member to the specified gym."""

        serializer = AddStaffSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        membership = add_staff(
            actor=request.user,
            gym_id=pk,
            user_id=serializer.validated_data["user_id"],
            role=serializer.validated_data["role"],
            salary=serializer.validated_data["salary"],
            share_percentage=serializer.validated_data.get(
                "share_percentage",
            ),
        )

        return Response(
            GymStaffSerializer(
                membership,
            ).data,
            status=status.HTTP_201_CREATED,
        )


class GymMembershipViewSet(viewsets.ModelViewSet):
    """ViewSet for managing gym memberships."""

    queryset = GymMembership.objects.all()
    serializer_class = GymMembershipSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "gym__name",
    ]

    filterset_fields = [
        "role",
        "user",
        "is_active",
    ]

    ordering_fields = [
        "joined_at",
        "salary",
    ]

    def get_serializer_class(self):
        """Return the appropriate serializer for the current action."""

        if self.action == "update_membership":
            return ChangeStaffRoleSerializer

        if self.action in [
            "deactivate",
            "activate",
        ]:
            return None

        return self.serializer_class

    def get_queryset(self):
        """Return memberships belonging to the gym specified in the URL."""

        gym_id = self.kwargs.get("gym_id")

        return (
            GymMembership.objects
            .filter(
                gym_id=gym_id,
            )
            .select_related(
                "user",
                "gym",
            )
        )

    def get_permissions(self):
        """Return permissions based on the current action."""

        if self.action in [
            "list",
            "retrieve",
        ]:
            permission_classes = [
                IsAuthenticated,
                CanViewGymMembership,
            ]

        elif self.action == "create":
            permission_classes = [
                IsAuthenticated,
                CanCreateGymMembership,
            ]

        elif self.action in [
            "update_membership",
            "deactivate",
            "activate",
        ]:
            permission_classes = [
                IsAuthenticated,
                CanManageGymMembership,
            ]

        else:
            permission_classes = [
                IsAuthenticated,
                CanViewGymMembership,
            ]

        return [
            permission()
            for permission in permission_classes
        ]

    def create(self, request, *args, **kwargs):
        """Create a new gym membership."""

        serializer = AddStaffSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        membership = add_staff(
            actor=request.user,
            gym_id=kwargs["gym_id"],
            user_id=serializer.validated_data["user_id"],
            role=serializer.validated_data["role"],
            salary=serializer.validated_data["salary"],
            share_percentage=serializer.validated_data.get(
                "share_percentage",
            ),
        )

        return Response(
            GymStaffSerializer(
                membership,
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        request=ChangeStaffRoleSerializer,
        responses={
            200: GymStaffSerializer,
        },
    )
    @action(
        detail=True,
        methods=["patch"],
        url_path="update_membership",
    )
    def update_membership(
        self,
        request,
        pk=None,
        gym_id=None,
    ):
        """Update the role, salary, or share percentage of a membership."""

        serializer = ChangeStaffRoleSerializer(
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        membership = update_membership(
            actor=request.user,
            membership_id=pk,
            role=serializer.validated_data.get("role"),
            salary=serializer.validated_data.get("salary"),
            share_percentage=serializer.validated_data.get(
                "share_percentage",
            ),
        )

        return Response(
            GymStaffSerializer(
                membership,
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
    )
    def deactivate(
        self,
        request,
        pk=None,
        gym_id=None,
    ):
        """Deactivate a gym membership."""

        membership = deactivate_staff(
            actor=request.user,
            membership_id=pk,
        )

        return Response(
            GymStaffSerializer(
                membership,
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
    )
    def activate(
        self,
        request,
        pk=None,
        gym_id=None,
    ):
        """Activate a gym membership."""

        membership = activate_staff(
            actor=request.user,
            membership_id=pk,
        )

        return Response(
            GymStaffSerializer(
                membership,
            ).data,
            status=status.HTTP_200_OK,
        )