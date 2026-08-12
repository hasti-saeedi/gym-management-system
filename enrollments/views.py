from rest_framework import viewsets, status

from .serializers import (
    EnrollmentSerializer,
    EnrollmentUpdateSerializer, 
    StaffEnrollmentCreateSerializer,
    MemberEnrollmentCreateSerializer, 
    PaymentSerializer, 
    ConfirmPaymentSerializer
    )


from drf_spectacular.utils import extend_schema
from .models import Enrollment, Payment
from accounts.models import CustomUser
from gyms.models import Gym
from permissions.bass_permissions import is_gym_employee
from rest_framework.response import Response
from .services.enrollment_services import create_enrollment, cancel_enrollment_service
from .services.payment_services import confirm_payment
from rest_framework.exceptions import NotFound
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action


from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import (
    SearchFilter,
    OrderingFilter,
)

from rest_framework.permissions import IsAuthenticated

from permissions.enrollment_permissions import (
    CanManageEnrollment,
    CanCancelEnrollment,
    CanViewEnrollment,
    CanViewPayment,
    CanCreatePayment,
    CanManagePayment,
    CanConfirmPayment,
)


class EnrollmentViewSet(viewsets.ModelViewSet):
   
    def get_queryset(self):

        queryset = Enrollment.objects.all()

        if self.action == "list":

            gym_id = self.kwargs.get("gym_id")

            if not Gym.objects.filter(id=gym_id).exists():
                raise NotFound(
                    "Gym does not exist."
                )

            queryset = queryset.filter(
                gym_class__gym_id=gym_id
            )

        return queryset.order_by(
            "-registered_at"
        )
   
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "gym_class__name",
    ]
    
    filterset_fields = [
        "status",
        "enrollment_type",
        "gym_class",
        "user",
        "attended",
    ]

    ordering_fields = [
        "registered_at",
        "status",
    ]


    def get_serializer_class(self):
        
        if self.action == "create":

            user = self.request.user

            if is_gym_employee(user):
                return StaffEnrollmentCreateSerializer

            return MemberEnrollmentCreateSerializer


        if self.action in [
            "update",
            "partial_update",
        ]:
            return EnrollmentUpdateSerializer


        return EnrollmentSerializer


    def get_permissions(self):

        """
        ViewSet for managing enrollments.

        APIs:

        1) GET /api/enrollments/enrollments/
            List enrollments.

            Rules:
                - Queryset controls which enrollments are visible.
                - Permission rules are applied based on user role.


        2) POST /api/enrollments/enrollments/
            Create a new enrollment.

            Rules:
                - Member:
                    - Can create enrollment only for himself.
                    - user_id is not required.

                - Owner / Manager / Staff:
                    - Can create enrollment for other users.
                    - user_id is required.

            Business logic:
                - Checked using can_create_enrollment()


        3) GET /api/enrollments/enrollments/{id}/
            Retrieve enrollment detail.

            Permission:
                - CanManageEnrollment


        4) PUT /api/enrollments/enrollments/{id}/
            Update enrollment.

            Permission:
                - CanManageEnrollment


        5) PATCH /api/enrollments/enrollments/{id}/
            Partial update enrollment.

            Permission:
                - CanManageEnrollment


        6) DELETE /api/enrollments/enrollments/{id}/
            Delete enrollment.

            Permission:
                - CanManageEnrollment


        7) GET /api/enrollments/enrollments/my/
            Retrieve current user's enrollments.

            Rules:
                - User can only access his own enrollments.


        8) POST /api/enrollments/enrollments/{id}/cancel/
            Cancel enrollment.

            Permission:
                - CanCancelEnrollment

            Rules:
                - Member can cancel his own enrollment.
                - Owner / Manager / Staff can cancel enrollments
                inside their own gym.
        """

        if self.action == "cancel":

            permission_classes = [
                IsAuthenticated,
                CanCancelEnrollment,
            ]
        
        elif self.action == "list":
            permission_classes = [
                IsAuthenticated,
                CanViewEnrollment,
            ]


        elif self.action in [

            "retrieve",
            "update",
            "partial_update",
            "destroy",
        ]:

            permission_classes = [
                IsAuthenticated,
                CanManageEnrollment,
            ]

        else:
# برای گت می 
            permission_classes = [
                IsAuthenticated,
            ]

        return [
            permission()
            for permission in permission_classes
        ]

        
        #قبل از اینکه Serializer ساخته شود، از من بپرس کدام Serializer را استفاده کنم.
   
    def get_serializer_class(self):

        if self.action == "create":

            user = self.request.user

            if is_gym_employee(user):
                return StaffEnrollmentCreateSerializer

            return MemberEnrollmentCreateSerializer


        if self.action == "cancel":
            return None

        return EnrollmentSerializer
    


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
            #Validation فقط Validation مربوط به Serializer است، نه Business Logic.
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data


        user_id = validated_data.get(
            "user_id"
        )

        if user_id:

            user = get_object_or_404(
                CustomUser,
                id=user_id
            )

        else:

            user = request.user

        try:
            enrollment = create_enrollment(
                user=user,
                gym_class_id=validated_data["gym_class_id"],
                enrollment_type=validated_data["enrollment_type"],
                selected_sessions_ids=validated_data.get(
                    "selected_sessions_ids"
                ),
            )

        except ValidationError as e:
            return Response(
                {"error": e.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            EnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED
        )
   
   
    @action(
    detail=False,
    methods=["get"],
    url_path="my",
    )
    def my_enrollments(self, request):

        enrollments = Enrollment.objects.filter(
            user=request.user
        )

        serializer = EnrollmentSerializer(
            enrollments,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    

    @action(
        detail=True,
        methods=["post"],
    )
    def cancel(
        self,
        request,
        pk=None
    ):

        enrollment = self.get_object()


        self.check_object_permissions(
            request,
            enrollment
        )


        cancel_enrollment_service(
            enrollment=enrollment
        )


        return Response(
            {
                "detail": "Enrollment cancelled successfully."
            },
            status=status.HTTP_200_OK,
        )
            


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "transaction_id",
        "enrollment__user__username",
        "enrollment__user__first_name",
        "enrollment__user__last_name",
    ]
    filterset_fields = [
        "status",
    ]
    ordering_fields = [
        "created_at",
        "amount",
    ]

    def get_permissions(self):

        if self.action == "my_payments":

            permission_classes = [
                IsAuthenticated,
            ]

        elif self.action == "list":

            permission_classes = [
                IsAuthenticated,
                CanViewPayment,
            ]

        elif self.action == "create":

            permission_classes = [
                IsAuthenticated,
                CanCreatePayment,
            ]

        elif self.action == "retrieve":

            permission_classes = [
                IsAuthenticated,
                CanViewPayment,
            ]

        elif self.action in [
            "update",
            "partial_update",
            "destroy",
        ]:

            permission_classes = [
                IsAuthenticated,
                CanManagePayment,
            ]

        elif self.action == "confirm":

            permission_classes = [
                IsAuthenticated,
                CanConfirmPayment,
        ]

        else:

            permission_classes = [
                IsAuthenticated,
            ]

        return [
            permission()
            for permission in permission_classes
        ]

    # =====================================================
    # Queryset
    # =====================================================

    def get_queryset(self):

        queryset = Payment.objects.select_related(
            "enrollment",
            "enrollment__user",
            "enrollment__gym_class",
            "enrollment__gym_class__gym",
        )

        if self.action in [
            "list",
            "retrieve",
            "update",
            "partial_update",
            "destroy",
            "confirm",
        ]:

            gym_id = self.kwargs.get("gym_id")

            if gym_id is not None:

                queryset = queryset.filter(
                    enrollment__gym_class__gym_id=gym_id
                )

        return queryset.order_by(
            "-created_at"
        )


    @action(
        detail=False,
        methods=["get"],
        url_path="my",
    )
    def my_payments(self, request):

        payments = Payment.objects.filter(
            enrollment__user=request.user
        ).order_by("-created_at")

        serializer = PaymentSerializer(
            payments,
            many=True #چیزی که بهت دادم یک پیمنت نیست؛ چند پیمنت است.
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
    request=ConfirmPaymentSerializer,
    responses={200: PaymentSerializer},
)
    @action(detail= True, methods=["post"])
    def confirm(self, request, pk=None, gym_id=None,):

        payment = self.get_object()

        self.check_object_permissions(
            request,
            payment,
        )
        serializer =  ConfirmPaymentSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)


        payment = confirm_payment(
            payment_id=pk,
            transaction_id=serializer.validated_data["transaction_id"]
        )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_200_OK
        )

