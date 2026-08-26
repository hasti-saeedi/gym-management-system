from rest_framework import viewsets, status

from .serializers import (
    EnrollmentSerializer,
    EnrollmentUpdateSerializer,
    StaffEnrollmentCreateSerializer,
    MemberEnrollmentCreateSerializer,
    PaymentSerializer,
    ConfirmPaymentSerializer,
)

from drf_spectacular.utils import extend_schema

from .models import Enrollment, Payment
from accounts.models import CustomUser
from gyms.models import Gym

from permissions.permission_helpers import is_gym_employee

from rest_framework.response import Response

from .services.enrollment_services import (
    create_enrollment,
    cancel_enrollment_service,
)

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
    """
    ViewSet for managing gym enrollments.

    Provides endpoints for creating, listing, retrieving, updating,
    deleting, and cancelling enrollments.

    Enrollment creation supports two types of users:

    - Gym employees can create an enrollment for another user.
    - Members can create an enrollment for themselves.

    Business rules related to enrollment creation and cancellation
    are delegated to the enrollment service layer.

    Permissions are handled separately for each action to ensure
    that users can only perform operations allowed by their role
    and relationship with the gym or enrollment.
    """

    def get_queryset(self):
        """
        Return the queryset of enrollments available to the current action.

        For gym-specific list requests, the queryset is restricted to
        enrollments belonging to classes in the requested gym.

        The gym existence is checked before filtering the queryset.
        This prevents a request for a non-existent gym from returning
        an empty result and instead returns HTTP 404.

        The queryset is ordered by registration date, with the newest
        enrollments returned first.

        Returns:
            QuerySet:
                Enrollments matching the requested gym, ordered by
                ``registered_at`` descending.

        Raises:
            NotFound:
                If the requested gym does not exist.
        """

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
        """
        Return the serializer appropriate for the current action.

        Enrollment creation uses different serializers depending on
        whether the authenticated user is a gym employee or a member.

        - Gym employees use ``StaffEnrollmentCreateSerializer`` because
          they can create enrollments for other users.
        - Members use ``MemberEnrollmentCreateSerializer`` because they
          create enrollments for themselves.
        - Update and partial update operations use
          ``EnrollmentUpdateSerializer``.
        - Other operations use ``EnrollmentSerializer``.

        Returns:
            Serializer:
                The serializer class appropriate for the current action.
        """

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
        Return the permissions required for the current enrollment action.

        Permission classes determine which authenticated users are
        allowed to access or modify enrollment resources.

        Permission mapping:

        ``IsAuthenticated``
            Requires the requester to be logged in.

        ``CanViewEnrollment``
            Controls access to the gym-specific enrollment list.
            It determines whether the authenticated user is allowed
            to view enrollments belonging to the requested gym.

        ``CanManageEnrollment``
            Controls management operations on an enrollment, including
            retrieving, updating, partially updating, and deleting it.
            It is responsible for checking whether the requester has
            the required management role or access to that enrollment.

        ``CanCancelEnrollment``
            Controls whether an enrollment can be cancelled.
            Members can cancel their own enrollments, while authorized
            gym employees can cancel enrollments belonging to their gym.

        For the ``my_enrollments`` action, only ``IsAuthenticated`` is
        required because the queryset itself is restricted to the
        authenticated user's own enrollments.

        Returns:
            list:
                Instantiated permission objects for the current action.
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
            permission_classes = [
                IsAuthenticated,
            ]

        return [
            permission()
            for permission in permission_classes
        ]

    def create(self, request, *args, **kwargs):
        """
        Create a new enrollment.

        The request data is first validated by the selected serializer.
        Serializer validation is responsible for validating the input
        structure and field-level requirements.

        After serializer validation, the enrollment service is called
        to execute business rules and create the enrollment.

        User selection works as follows:

        - If ``user_id`` is provided by a gym employee, the enrollment
          is created for that user.
        - If ``user_id`` is not provided, the enrollment is created for
          the authenticated requester.

        Business logic is delegated to ``create_enrollment``.

        The service is responsible for rules such as:

        - Checking whether the gym class exists.
        - Checking whether the class is active.
        - Checking whether the user is an active gym member.
        - Preventing trainers from enrolling in their own class.
        - Preventing duplicate enrollments.
        - Checking class capacity.
        - Validating selected sessions for single-session enrollment.
        - Creating the associated payment.

        Returns:
            Response:
                HTTP 201 containing the created enrollment.

                HTTP 400 when enrollment business validation fails.

        Raises:
            Http404:
                If a provided ``user_id`` does not exist.
        """

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

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
                {
                    "error": e.messages
                },
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
        """
        Return all enrollments belonging to the authenticated user.

        The queryset is explicitly filtered by ``request.user`` so that
        the endpoint only returns enrollments owned by the current user.

        This endpoint does not expose enrollments belonging to other
        users.

        Returns:
            Response:
                HTTP 200 containing the authenticated user's enrollments.
        """

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
        """
        Cancel an existing enrollment.

        The enrollment is first retrieved using the configured queryset.
        Object-level cancellation permission is then checked before
        calling the cancellation service.

        Cancellation is handled by ``cancel_enrollment_service`` rather
        than directly modifying the model in the view.

        The enrollment record is preserved after cancellation and its
        status is changed to ``cancelled``.

        Returns:
            Response:
                HTTP 200 when the enrollment is successfully cancelled.

        Raises:
            ValidationError:
                If the enrollment cannot be cancelled according to the
                business rules implemented by the service.
        """

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
    """
    ViewSet for managing gym payments.

    Provides endpoints for creating, listing, retrieving, updating,
    deleting, and confirming payment records.

    Each payment is associated with an enrollment, and the enrollment
    determines the related user, gym class, and gym.

    Payment access is controlled through dedicated permission classes.

    Permission classes:

    ``IsAuthenticated``
        Ensures that only authenticated users can access payment
        endpoints.

    ``CanViewPayment``
        Controls whether the authenticated user can view payment
        records for a gym or payment object.

    ``CanCreatePayment``
        Controls whether the authenticated user is allowed to create
        a payment.

    ``CanManagePayment``
        Controls whether the authenticated user can update or delete
        an existing payment.

    ``CanConfirmPayment``
        Controls whether the authenticated user can confirm a payment.

    Payment business logic, including payment confirmation and
    enrollment approval, is delegated to the payment service layer.
    """

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
        """
        Return the permissions required for the current payment action.

        Permission mapping:

        ``IsAuthenticated``
            Requires the requester to be authenticated.

        ``CanViewPayment``
            Controls access to payment records when listing or retrieving
            payments.

        ``CanCreatePayment``
            Controls whether the requester is allowed to create a
            payment.

        ``CanManagePayment``
            Controls whether the requester is allowed to update or
            delete an existing payment.

        ``CanConfirmPayment``
            Controls whether the requester is allowed to confirm a
            payment and trigger the related enrollment approval.

        Permission mapping by action:

        - ``my_payments``:
            ``IsAuthenticated``

        - ``list``:
            ``IsAuthenticated`` + ``CanViewPayment``

        - ``create``:
            ``IsAuthenticated`` + ``CanCreatePayment``

        - ``retrieve``:
            ``IsAuthenticated`` + ``CanViewPayment``

        - ``update``:
            ``IsAuthenticated`` + ``CanManagePayment``

        - ``partial_update``:
            ``IsAuthenticated`` + ``CanManagePayment``

        - ``destroy``:
            ``IsAuthenticated`` + ``CanManagePayment``

        - ``confirm``:
            ``IsAuthenticated`` + ``CanConfirmPayment``

        - Other actions:
            ``IsAuthenticated`` only.

        Returns:
            list:
                Instantiated permission objects for the current action.
        """

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

    def get_queryset(self):
        """
        Return the payment queryset available to the current endpoint.

        Related enrollment, user, gym class, and gym objects are loaded
        using ``select_related`` to reduce additional database queries
        when those related objects are accessed.

        For gym-specific endpoints, payments are filtered through the
        related enrollment and gym class so that only payments belonging
        to the requested gym are included.

        The queryset is ordered by creation date with the newest
        payments returned first.

        Returns:
            QuerySet:
                Payments matching the current endpoint and optional
                gym scope.
        """

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

            gym_id = self.kwargs.get(
                "gym_id"
            )

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
        """
        Return all payments belonging to the authenticated user.

        Payments are filtered through the related enrollment, meaning
        only payments whose enrollment belongs to ``request.user`` are
        returned.

        The results are ordered from newest to oldest using
        ``created_at``.

        ``many=True`` is used because the serializer receives a
        collection of payment objects rather than a single payment.

        Returns:
            Response:
                HTTP 200 containing the authenticated user's payment
                history.
        """

        payments = Payment.objects.filter(
            enrollment__user=request.user
        ).order_by(
            "-created_at"
        )

        serializer = PaymentSerializer(
            payments,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        request=ConfirmPaymentSerializer,
        responses={
            200: PaymentSerializer
        },
    )
    @action(
        detail=True,
        methods=["post"]
    )
    def confirm(
        self,
        request,
        pk=None,
        gym_id=None,
    ):
        """
        Confirm an existing payment.

        The payment is first retrieved using the ViewSet queryset.
        Object-level permission is then checked using
        ``CanConfirmPayment``.

        The request body must contain a valid transaction ID, which is
        validated by ``ConfirmPaymentSerializer``.

        After validation, the ``confirm_payment`` service is called to
        perform the payment confirmation and related business logic.

        The payment service is responsible for:

        - Marking the payment as completed.
        - Saving the transaction ID.
        - Approving the related enrollment.
        - Increasing the class enrollment count when applicable.
        - Preventing an already completed payment from being confirmed
          again.

        Returns:
            Response:
                HTTP 200 containing the confirmed payment.

        Raises:
            NotFound:
                If the requested payment does not exist in the current
                queryset.

            ValidationError:
                If the transaction data is invalid or the payment cannot
                be confirmed according to the payment business rules.
        """

        payment = self.get_object()

        self.check_object_permissions(
            request,
            payment,
        )

        serializer = ConfirmPaymentSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        payment = confirm_payment(
            payment_id=pk,
            transaction_id=serializer.validated_data[
                "transaction_id"
            ]
        )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_200_OK
        )