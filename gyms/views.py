# from .models import Gym, GymMembership
# from rest_framework import viewsets, status
# from rest_framework.decorators import action
# from drf_spectacular.utils import extend_schema
# from rest_framework.response import Response
# from .serializers import (
#     ChangeStaffRoleSerializer,
#     GymStaffSerializer,
#     GymSerializer,
#     GymMembershipSerializer,
#     AddStaffSerializer,

# )

# from rest_framework.permissions import AllowAny, IsAuthenticated

# from permissions.gym_permissions import (
#     CanManageGym,
#     CanCreateGym,
#     CanAddStaff,
#     CanViewGymMembers,
#     CanViewGymMembership,
#     CanCreateGymMembership,
#     CanManageGymMembership
# )

# from .services.gym_membership_services import (
#     update_membership,
#     get_gym_staff,
#     add_staff,
#     deactivate_staff,
# )

# from django_filters.rest_framework import DjangoFilterBackend

# from rest_framework.filters import (
#     SearchFilter,
#     OrderingFilter,
# )


# class GymViewSet(viewsets.ModelViewSet):
#     queryset = Gym.objects.all()
#     serializer_class = GymSerializer

#     filter_backends = [
#         DjangoFilterBackend,
#         SearchFilter,
#         OrderingFilter,
#     ]

#     search_fields = [
#         "name",
#         "address",
#         "phone",
#         "email",
#     ]

#     filterset_fields = [
#         "is_active",
#     ]

#     ordering_fields = [
#         "name",
#         "created_at",
#     ]


#     def get_permissions(self):

#         # Public GET
#         if self.action in [
#             "list",
#             "retrieve",
#         ]:
#             permission_classes = [
#                 AllowAny,
#             ]

#         # Create Gym
#         elif self.action == "create":
#             permission_classes = [
#                 IsAuthenticated,
#                 CanCreateGym,
#             ]

#         # Update / Delete Gym
#         elif self.action in [
#             "update",
#             "partial_update",
#             "destroy",
#         ]:
#             permission_classes = [
#                 IsAuthenticated,
#                 CanManageGym,
#             ]

#         # Add Staff
#         elif self.action == "add_staff":
#             permission_classes = [
#                 IsAuthenticated,
#                 CanAddStaff,
#             ]

#         # View Gym Members
#         elif self.action == "members":
#             permission_classes = [
#                 IsAuthenticated,
#                 CanViewGymMembers,
#             ]

#         # Fallback
#         else:
#             permission_classes = [
#                 IsAuthenticated,
#             ]

#         return [
#             permission()
#             for permission in permission_classes
#         ]
        

#     @action(detail=True, methods=["get"])
#     def members(self, request, pk=None):

#         members = get_gym_staff(pk)

#         serializer = GymStaffSerializer(
#             members,
#             many=True, # میخوایم به سریالایزر بگیم این یک لیست از آبجکت‌هاست، نه یک آبجکت 
#     )

#         return Response(serializer.data)



#     @extend_schema(
#     request=AddStaffSerializer,
#     responses={200: GymStaffSerializer},
#     )
#     @action(detail=True, methods=["post"])
#     def add_staff(self, request, pk):  #چون جیم ایدی از یوارال میاد در سریالایزر نمیگیریمش

#         serializer = AddStaffSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         membership = add_staff(
#             actor = request.user,
#             gym_id=pk,
#             user_id=serializer.validated_data["user_id"],
#             role=serializer.validated_data["role"],
#             salary=serializer.validated_data["salary"],
#             share_percentage=serializer.validated_data.get("share_percentage"),
#         )

#         return Response(
#             GymStaffSerializer(membership).data,
#             status=status.HTTP_201_CREATED,
#         )
    

# class GymMembershipViewSet(viewsets.ModelViewSet):
#     queryset = GymMembership.objects.all()


#     def get_serializer_class(self):
#         if self.action == 'deactivate':
#             return None
        
#         elif self.action == "update_membership":
#             return ChangeStaffRoleSerializer
#         return GymMembershipSerializer
        

#     filter_backends = [
#         DjangoFilterBackend,
#         SearchFilter,
#         OrderingFilter,
#     ]

#     search_fields = [
#         "user__username",
#         "user__first_name",
#         "user__last_name",
#         "gym__name",
#     ]

#     filterset_fields = [
#         "role",
#         "user",
#         "is_active",
#     ]

#     ordering_fields = [
#         "joined_at",
#         "salary",
#     ]

#     def get_queryset(self):

#         """ Return only memberships belonging to the Gym specified in the URL.
#         URL: /api/gyms/{gym_id}/gymmembership/ 
#         This prevents users from accessing memberships belonging to 
#         another gym by changing the membership ID. 
        
#         """
#         gym_id = self.kwargs.get("gym_id")

#         return GymMembership.objects.filter( 
#             gym_id=gym_id 
#             ).select_related( 
#                 "user", "gym",
#             )

#     def get_permissions(self):

#         """ 
#             Select the appropriate permission class 
#             based on the current action. 
#             Permissions: list / retrieve: Owner / Manager / Superuser 
#             create: Owner / Manager / Superuser update / partial_update / 
#             destroy: Owner / Superuser update_membership: Owner / 
#             Superuser deactivate: Owner / Superuser 
        
#         """ 

#         if self.action in [ "list", "retrieve", ]: 
#             permission_classes = [
#                 IsAuthenticated, 
#                 CanViewGymMembership,
#                 ] 
        
#         elif self.action == "create": 
#             permission_classes = [
#                 IsAuthenticated, 
#                 CanCreateGymMembership, 
#                 ]

#         elif self.action in [ 
#             "update", 
#             "partial_update", 
#             "destroy", 
#             "update_membership", 
#             "deactivate", 
#             ]: 
#             permission_classes = [
#                 IsAuthenticated, 
#                 CanManageGymMembership, 
#                 ] 

#         else: permission_classes = [
#                 IsAuthenticated, 
#                 CanViewGymMembership, 
#                 ] 

    
#         return [ 
#             permission() 
#             for permission in permission_classes 
#             ]    


#     @extend_schema(
#     request=ChangeStaffRoleSerializer,
#     responses={200: GymStaffSerializer},
#     )
#     @action(detail=True, methods=["patch"])
#     def update_membership(self, request, pk, gym_id=None):

#         # serializer = ChangeStaffRoleSerializer(
#         #     data=request.data
#         # )
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         membership = update_membership(
#             membership_id=pk,
#             role=serializer.validated_data["role"],
#             salary=serializer.validated_data["salary"],
#                 # برای این گت مینویسیم چون فیلد اختیاری هست و اگه خالی بود نان رو قبول کنه
#             share_percentage=serializer.validated_data.get( 
#                 "share_percentage"
#             ),
#         )

#         return Response(
#             GymStaffSerializer(membership).data  # data ===این آبجکت را به دیکشنری پایتون تبدیل کن.
#         )
    

#     @action(detail=True, methods=["post"])
#     def deactivate(self, request, pk, gym_id=None):

#         membership = deactivate_staff(pk)

#         return Response(
#             GymStaffSerializer(membership).data
#         )
    

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import (
    SearchFilter,
    OrderingFilter,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema


from .models import Gym, GymMembership

from .serializers import (
    GymSerializer,
    GymMembershipSerializer,
    GymStaffSerializer,
    AddStaffSerializer,
    ChangeStaffRoleSerializer,
)

from .services.gym_membership_services import (
    add_staff,
    get_gym_staff,
    update_membership,
    deactivate_staff,
    activate_staff,
)

from permissions.gym_permissions import (
    CanManageGym,
    CanCreateGym,
    CanAddStaff,
    CanViewGymMembers,
    CanViewGymMembership,
    CanCreateGymMembership,
    CanManageGymMembership,
)


# ============================================================
# Gym ViewSet
# ============================================================


class GymViewSet(viewsets.ModelViewSet):

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

    # --------------------------------------------------------
    # Permissions
    # --------------------------------------------------------

    def get_permissions(self):

        if self.action in [
            "list",
            "retrieve",
        ]:
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

    # --------------------------------------------------------
    # Members
    # --------------------------------------------------------

    @action(
        detail=True,
        methods=["get"],
    )
    def members(self, request, pk=None):

        members = get_gym_staff(pk)

        serializer = GymStaffSerializer(
            members,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    # --------------------------------------------------------
    # Add Staff
    # --------------------------------------------------------

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

        serializer = AddStaffSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        membership = add_staff(
            actor=request.user,
            gym_id=pk,
            user_id=serializer.validated_data[
                "user_id"
            ],
            role=serializer.validated_data[
                "role"
            ],
            salary=serializer.validated_data[
                "salary"
            ],
            share_percentage=serializer.validated_data.get(
                "share_percentage"
            ),
        )

        return Response(
            GymStaffSerializer(
                membership
            ).data,
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# GymMembership ViewSet
# ============================================================

class GymMembershipViewSet(viewsets.ModelViewSet):

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

    # --------------------------------------------------------
    # Serializer
    # --------------------------------------------------------

    def get_serializer_class(self):

        if self.action == "update_membership":
            return ChangeStaffRoleSerializer
        
        if self.action in [
            'deactivate',
            'activate'
        ]:
            return None

        return self.serializer_class

    # --------------------------------------------------------
    # Queryset
    # --------------------------------------------------------

    def get_queryset(self):

        gym_id = self.kwargs.get(
            "gym_id"
        )

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

    # --------------------------------------------------------
    # Permissions
    # --------------------------------------------------------

    def get_permissions(self):

        # ---------------------------------------------
        # List / Retrieve
        # ---------------------------------------------

        if self.action in [
            "list",
            "retrieve",
        ]:
            permission_classes = [
                IsAuthenticated,
                CanViewGymMembership,
            ]

        # ---------------------------------------------
        # Create
        # ---------------------------------------------

        elif self.action == "create":
            permission_classes = [
                IsAuthenticated,
                CanCreateGymMembership,
            ]

        # ---------------------------------------------
        # Update Membership
        # ---------------------------------------------

        elif self.action in [
            "update_membership",
            "deactivate",
            "activate",
        ]:
            permission_classes = [
                IsAuthenticated,
                CanManageGymMembership,
            ]

        # ---------------------------------------------
        # Fallback
        # ---------------------------------------------

        else:
            permission_classes = [
                IsAuthenticated,
                CanViewGymMembership,
            ]

        return [
            permission()
            for permission in permission_classes
        ]

    # ========================================================
    # Create
    # ========================================================

    def create(self, request, *args, **kwargs):

        serializer = AddStaffSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        membership = add_staff(
            actor=request.user,
            gym_id=kwargs["gym_id"],
            user_id=serializer.validated_data[
                "user_id"
            ],
            role=serializer.validated_data[
                "role"
            ],
            salary=serializer.validated_data[
                "salary"
            ],
            share_percentage=serializer.validated_data.get(
                "share_percentage"
            ),
        )

        return Response(
            GymStaffSerializer(
                membership
            ).data,
            status=status.HTTP_201_CREATED,
        )

    # ========================================================
    # Update Membership
    # ========================================================

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
            role=serializer.validated_data.get(
                "role"
            ),
            salary=serializer.validated_data.get(
                "salary"
            ),
            share_percentage=serializer.validated_data.get(
                "share_percentage"
            ),
        )

        return Response(
            GymStaffSerializer(
                membership
            ).data,
            status=status.HTTP_200_OK,
        )

    # ========================================================
    # Deactivate
    # ========================================================

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

        membership = deactivate_staff(
            actor=request.user,
            membership_id=pk,
        )

        return Response(
            GymStaffSerializer(
                membership
            ).data,
            status=status.HTTP_200_OK,
        )

    # ========================================================
    # Activate
    # ========================================================

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

        membership = activate_staff(
            actor=request.user,
            membership_id=pk,
        )

        return Response(
            GymStaffSerializer(
                membership
            ).data,
            status=status.HTTP_200_OK,
        )

