from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from permissions.base_permissions import IsAnonymous

from .models import CustomUser
from .serializers import (
    CreateGymUserSerializer,
    CurrentUserSerializer,
    CurrentUserUpdateSerializer,
    CustomUserSerializer,
    GymUserSerializer,
    LoginSerializer,
    LogoutSerializer,
    RegisterSerializer,
)
from .services.authentication_services import login_service, logout_service
from .services.user_services import (
    create_gym_user,
    register_member,
    update_current_user,
)
from gyms.models import Gym


class CurrentUserView(APIView):
    """
    Retrieve and update the authenticated user's profile.

    Endpoints:
        GET: Retrieve the current user's profile.
        PATCH: Partially update the current user's profile.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Return the authenticated user's profile.

        Args:
            request: The HTTP request containing the authenticated user.

        Returns:
            Response: The serialized user profile.
        """
        serializer = CurrentUserSerializer(request.user)

        return Response(serializer.data)

    @extend_schema(
        request=CurrentUserUpdateSerializer,
        responses=CurrentUserSerializer,
    )
    def patch(self, request):
        """
        Partially update the authenticated user's profile.

        Args:
            request: The HTTP request containing the updated profile data.

        Returns:
            Response: The updated user profile.
        """
        serializer = CurrentUserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)

        user = update_current_user(
            user=request.user,
            validated_data=serializer.validated_data,
        )

        return Response(
            CurrentUserSerializer(user).data,
            status=status.HTTP_200_OK,
        )


class GymUserViewSet(viewsets.ModelViewSet):
    """
    Manage users belonging to a specific gym.

    Provides endpoints for listing, creating, retrieving, updating,
    and deleting users associated with the requested gym.

    Users are limited to active memberships in the requested gym.
    Permissions and serializers are selected according to the
    current ViewSet action.
    """

    queryset = CustomUser.objects.all()

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "username",
        "first_name",
        "last_name",
    ]

    filterset_fields = [
        "is_active",
    ]

    ordering_fields = [
        "username",
        "date_joined",
        "first_name",
        "last_name",
    ]

    def get_serializer_class(self):
        """
        Return the serializer appropriate for the current action.

        Returns:
            type: The serializer class associated with the current action.
        """
        if self.action == "create":
            return CreateGymUserSerializer

        if self.action in ["list", "retrieve"]:
            return GymUserSerializer

        return CustomUserSerializer

    def get_permissions(self):
        """
        Select the permission class based on the current action.

        Returns:
            list: Permission instances required for the current action.
        """
        from permissions.account_permissions import (
            CanCreateGymUser,
            CanDeleteGymUser,
            CanUpdateGymUser,
            CanViewGymUserDetail,
            CanViewGymUsers,
        )

        permission_map = {
            "list": [CanViewGymUsers],
            "create": [CanCreateGymUser],
            "retrieve": [CanViewGymUserDetail],
            "update": [CanUpdateGymUser],
            "partial_update": [CanUpdateGymUser],
            "destroy": [CanDeleteGymUser],
        }

        permission_classes = permission_map.get(self.action, [])

        return [
            permission()
            for permission in permission_classes
        ]

    def get_queryset(self):
        """
        Return active users who are members of the requested gym.

        Returns:
            QuerySet: Active users with an active membership in the gym.

        Raises:
            Http404: If the requested gym does not exist.
        """
        gym_id = self.kwargs.get("gym_id")

        get_object_or_404(
            Gym,
            pk=gym_id,
        )

        return (
            CustomUser.objects.filter(
                memberships__gym_id=gym_id,
                memberships__is_active=True,
            )
            .distinct()
        )

    def create(self, request, gym_id):
        """
        Create a new user and assign them to the requested gym.

        Args:
            request: The HTTP request containing the user data.
            gym_id: The ID of the gym where the user will be assigned.

        Returns:
            Response: The newly created user's serialized data.
        """
        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        gym = get_object_or_404(
            Gym,
            pk=gym_id,
        )

        user = create_gym_user(
            creator=request.user,
            gym=gym,
            validated_data=serializer.validated_data,
        )

        return Response(
            CustomUserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class RegisterView(APIView):
    """
    Register a new gym member.

    The user selects an active gym during registration and is
    automatically assigned the MEMBER role.
    """

    permission_classes = [IsAnonymous]

    @extend_schema(
        request=RegisterSerializer,
        responses={201: CustomUserSerializer},
    )
    def post(self, request):
        """
        Create a new member account.

        Args:
            request: The HTTP request containing registration data.

        Returns:
            Response: The newly created member's serialized data.
        """
        serializer = RegisterSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        user = register_member(
            validated_data=serializer.validated_data,
        )

        return Response(
            CustomUserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    Authenticate a user and issue JWT tokens.

    Returns access and refresh tokens together with the
    authenticated user's basic information.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={200: None},
    )
    def post(self, request):
        """
        Authenticate the user and return JWT tokens.

        Args:
            request: The HTTP request containing login credentials.

        Returns:
            Response: Access and refresh tokens with user information.
        """
        serializer = LoginSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        result = login_service(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )

        return Response(
            {
                "access": result["access"],
                "refresh": result["refresh"],
                "user": CurrentUserSerializer(
                    result["user"]
                ).data,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    Log out an authenticated user by invalidating their refresh token.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LogoutSerializer,
        responses={200: None},
    )
    def post(self, request):
        """
        Invalidate the provided refresh token.

        Args:
            request: The HTTP request containing the refresh token.

        Returns:
            Response: A confirmation that the user has been logged out.
        """
        serializer = LogoutSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        logout_service(
            serializer.validated_data["refresh"],
        )

        return Response(
            {"detail": "Logged out successfully."},
            status=status.HTTP_200_OK,
        )