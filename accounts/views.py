from .models import CustomUser
from gyms.models import Gym

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from django_filters.rest_framework import DjangoFilterBackend

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
)

from permissions.permission_helpers import IsAnonymous

from .serializers import (
    CustomUserSerializer,
    LoginSerializer, 
    CurrentUserSerializer, 
    LogoutSerializer,
    RegisterSerializer,
    CreateGymUserSerializer,
    CurrentUserUpdateSerializer,
    GymUserSerializer,
)

from .services.authentication_services import (
    login_service, 
    logout_service
)

from .services.user_services import (
    register_member, 
    create_gym_user,
    update_current_user,
)

from rest_framework.filters import (
    SearchFilter,
    OrderingFilter,
)



# کلی قدیمی
# class CustomUserViewSet(viewsets.ModelViewSet):
    # queryset = CustomUser.objects.all()
    # serializer_class = CustomUserSerializer

    # filter_backends = [
    #     DjangoFilterBackend,
    #     SearchFilter,
    #     OrderingFilter,
    # ]
    # search_fields = [
    #     "username",
    #     "first_name",
    #     "last_name",
    # ]
    # filterset_fields = [
    #     "is_active",
    # ]

    # ordering_fields = [
    #     "username",
    #     "date_joined",
    #     "first_name",
    #     "last_name",
    # ]


    # def get_permissions(self):

    #     """
    #     Assigns permissions based on DRF ViewSet actions.

    #     Swagger mapping:

    #     GET /api/accounts/users/
    #         Action: list
    #         Permission: CanViewUsers

    #     POST /api/accounts/users/
    #         Action: create
    #         Permission: CanCreateUser

    #     GET /api/accounts/users/{id}/
    #         Action: retrieve
    #         Permission: CanViewUserDetail

    #     PUT /api/accounts/users/{id}/
    #         Action: update
    #         Permission: CanUpdateUser

    #     PATCH /api/accounts/users/{id}/
    #         Action: partial_update
    #         Permission: CanUpdateUser

    #     DELETE /api/accounts/users/{id}/
    #         Action: destroy
    #         Permission: CanDeleteUser
    #     """

    #     if self.action == "list":
    #         permission_classes = [
    #             CanViewUsers
    #         ]

    #     elif self.action == "create":
    #         permission_classes = [
    #             CanCreateUser
    #         ]

    #     elif self.action == "retrieve":
    #         permission_classes = [
    #             CanViewUserDetail
    #         ]

    #     elif self.action in [
    #         "update",
    #         "partial_update",
    #     ]:
    #         permission_classes = [
    #             CanUpdateUser
    #         ]

    #     elif self.action == "destroy":
    #         permission_classes = [
    #             CanDeleteUser
    #         ]

    #     else:
    #         permission_classes = []

    #     return [
    #         permission() #از روی کلاس، یک آبجکت بسازیم.
    #         for permission in permission_classes
    #     ]
    
    # def get_serializer_class(self):

    #     serializer_map = {
    #         "create": CreateGymUserSerializer,
    #         "list": CustomUserSerializer,
    #         "retrieve": CustomUserSerializer,
    #         "update": CustomUserSerializer,
    #         "partial_update": CustomUserSerializer,
    #     }

    #     return serializer_map.get(
    #         self.action,
    #         CustomUserSerializer,
    #     )
        
    # def create(self, request, *args, **kwargs):


    #     serializer = self.get_serializer(
    #         data=request.data
    #     )

    #     serializer.is_valid(
    #         raise_exception=True
    #     )

    #     user = create_gym_user(
    #         creator=request.user,
    #         validated_data=serializer.validated_data,
    #     )

    #     return Response(
    #         CustomUserSerializer(user).data,
    #         status=status.HTTP_201_CREATED,
    #     )

#برای patch/me
class CurrentUserView(APIView):
    """
    APIs:

    GET:
        /api/accounts/me/

    PATCH:
        /api/accounts/me/

    Description:
        Allows authenticated users to
        view and update their own profile.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = CurrentUserSerializer(request.user)

        return Response(serializer.data)

    @extend_schema(
    request=CurrentUserUpdateSerializer,
    responses=CurrentUserSerializer,
    )
    def patch(self, request):

        serializer = CurrentUserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True, #فیلد مخصوص پچ است یعنی لازم نیست همه اطلاعات ارسال شوند
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


# برای یوزر یک جیم خاص
class GymUserViewSet(viewsets.ModelViewSet):

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

        if self.action == "create":
            return CreateGymUserSerializer

        if self.action in [
            "list",
            "retrieve",
        ]:
            return GymUserSerializer
        
        return CustomUserSerializer



    def get_permissions(self):
        from permissions.account_permissions import (
            CanViewGymUsers,
            CanCreateGymUser,
            CanViewGymUserDetail,
            CanUpdateGymUser,
            CanDeleteGymUser,

            )
        """
        Select permission class based on
        current ViewSet action.

        DRF actions:

        list:
            GET collection

        create:
            POST collection

        retrieve:
            GET single object

        update:
            PUT single object

        partial_update:
            PATCH single object

        destroy:
            DELETE single object
        """


        if self.action == "list":
            permission_classes = [
                CanViewGymUsers
            ]

        elif self.action == "create":
            permission_classes = [
                CanCreateGymUser
            ]

        elif self.action == "retrieve":
            permission_classes = [
                CanViewGymUserDetail
            ]

        elif self.action in [
            "update",
            "partial_update"
        ]:
            permission_classes = [
                CanUpdateGymUser
            ]

        elif self.action == "destroy":
            permission_classes = [
                CanDeleteGymUser
            ]

        else:
            permission_classes = []


        return [
            permission()
            for permission in permission_classes
        ]

#GET /gyms/{gym_id}/users/
    def get_queryset(self):

        gym_id = self.kwargs.get("gym_id")

        get_object_or_404(
            Gym,
            id=gym_id
        )


        return CustomUser.objects.filter(
            memberships__gym_id=gym_id,
            memberships__is_active=True,
        ).distinct()

#  POST /gyms/{gym_id}/users/
    def create(self, request, gym_id):


        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        gym = Gym.objects.get(
            id=gym_id
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
    API:

    POST:
        /api/accounts/register/


    Description:

        Creates a new member account.

        User selects a gym and
        becomes a gym member.
    """
            
    permission_classes = [
        IsAnonymous
    ]

    @extend_schema(
        request=RegisterSerializer,
        responses={201: CustomUserSerializer},
    )
    def post(self, request):

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
    API:

    POST:
        /api/accounts/login/


    Description:

        Authenticates user and
        returns JWT tokens.
    """


    permission_classes = [
        AllowAny
    ]

    @extend_schema(
    request=LoginSerializer,
    responses={200: None},
    )
        # Login فقط POST دارد
    def post(self, request):

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = login_service(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )

        return Response(
            {
                "access": result["access"],
                "refresh": result["refresh"],
                "user": CurrentUserSerializer(result["user"]).data,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):

    
    """
    API:

    POST:
        /api/accounts/logout/


    Description:

        Invalidates refresh token
        and logs out authenticated user.
    """


    permission_classes = [
        IsAuthenticated
    ]

    permission_classes = [IsAuthenticated]

    @extend_schema(
    request=LogoutSerializer,
    responses={200: None},
    )
    def post(self, request):

        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        logout_service(
            serializer.validated_data["refresh"]
        )

        return Response(
            {"detail": "Logged out successfully."},
            status=status.HTTP_200_OK,
        )