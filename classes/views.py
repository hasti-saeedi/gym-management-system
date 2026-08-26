from rest_framework import viewsets, status

from .serializers import (
    GymClassSerializer,
    ClassSessionSerializer,
    AttendanceSerializer,
    SessionStudentSerializer,
)

from rest_framework.decorators import action
from gyms.models import GymMembership
from .models import GymClass, ClassSession
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema

from .services.attendance_services import (
    record_attendance as record_attendance_service,
    get_enrolled_students,
)

from rest_framework.permissions import IsAuthenticated, AllowAny

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import (
    SearchFilter,
    OrderingFilter,
)

from permissions.class_permissions import (
    CanCreateSession,
    CanAccessSession,
    CanDeleteSession,
    CanViewSessionStudents,
    CanRecordAttendance,
    CanManageGymClass,
)


class GymClassViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing gym classes.

    Provides endpoints for listing, retrieving, creating, updating,
    and deleting gym classes.

    Permissions:

    - AllowAny:
        Allows unauthenticated users to list and retrieve gym classes.

    - CanManageGymClass:
        Controls access to gym class management operations such as
        creating, updating, and deleting classes.

        The exact roles allowed to perform these operations are
        determined by the CanManageGymClass permission class.

    Business logic:
        Request validation is handled by GymClassSerializer.
        Authorization for management operations is handled by
        CanManageGymClass.
    """

    queryset = GymClass.objects.all()
    serializer_class = GymClassSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "name",
        "category",
        "trainer__username",
        "trainer__first_name",
        "trainer__last_name",
        "gym__name",
    ]

    filterset_fields = [
        "category",
        "gym",
        "trainer",
        "is_active",
    ]

    ordering_fields = [
        "created_at",
        "price",
        "capacity",
        "current_enrolled",
        "name",
    ]

    def get_permissions(self):
        """
        Return permission classes required for the current action.

        Permission rules:

        - list:
            Uses AllowAny.
            Both authenticated and unauthenticated users can view
            the list of gym classes.

        - retrieve:
            Uses AllowAny.
            Both authenticated and unauthenticated users can view
            the details of a gym class.

        - create:
            Uses IsAuthenticated and CanManageGymClass.
            The user must be authenticated and must have permission
            to create a gym class.

        - update:
            Uses IsAuthenticated and CanManageGymClass.
            The user must be authenticated and must have permission
            to update a gym class.

        - partial_update:
            Uses IsAuthenticated and CanManageGymClass.
            The user must be authenticated and must have permission
            to partially update a gym class.

        - destroy:
            Uses IsAuthenticated and CanManageGymClass.
            The user must be authenticated and must have permission
            to delete a gym class.

        Returns:
            list:
                Instantiated permission classes for the current action.
        """

        if self.action in [
            "list",
            "retrieve",
        ]:
            permission_classes = [
                AllowAny,
            ]

        elif self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
        ]:
            permission_classes = [
                IsAuthenticated,
                CanManageGymClass,
            ]

        else:
            permission_classes = []

        return [
            permission()
            for permission in permission_classes
        ]


class ClassSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing class sessions.

    A ClassSession belongs to a specific GymClass and is accessed
    through the gym and class hierarchy:

        /gyms/{gym_id}/classes/{class_id}/sessions/

    Permissions:

    - CanAccessSession:
        Controls access to listing, retrieving, updating, and partially
        updating class sessions.

        This permission determines whether the authenticated user is
        allowed to access the requested session.

    - CanCreateSession:
        Controls creation of new class sessions.

        This permission determines whether the authenticated user is
        allowed to create a session for the requested gym class.

    - CanDeleteSession:
        Controls deletion of class sessions.

        This permission determines whether the authenticated user is
        allowed to delete the requested session.

    - CanViewSessionStudents:
        Controls access to the list of students enrolled in a session.

        This permission determines whether the authenticated user is
        allowed to view students associated with the requested session.

    - CanRecordAttendance:
        Controls access to attendance recording.

        This permission determines whether the authenticated user is
        allowed to record attendance for the requested session.

    Queryset access:

    The queryset is additionally restricted according to the user's
    relationship with the gym, class, or session.

    - Superusers can access matching sessions.
    - Gym Owner, Manager, and Staff can access sessions in their gym.
    - The main trainer of the class can access its sessions.
    - The trainer assigned to a session can access that session.
    - Users without access receive an empty queryset.
    """

    serializer_class = ClassSessionSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "gym_class__name",
        "trainer__username",
        "trainer__first_name",
        "trainer__last_name",
    ]

    filterset_fields = [
        "gym_class",
        "trainer",
        "is_cancelled",
    ]

    ordering_fields = [
        "start_time",
        "end_time",
        "created_at",
    ]

    def get_queryset(self):
        """
        Return class sessions accessible to the current user.

        The queryset is restricted by the gym and class specified
        in the URL.

        URL structure:

            /gyms/{gym_id}/classes/{class_id}/sessions/

        Queryset restrictions:

        - The session must belong to the requested gym.
        - The session must belong to the requested class.
        - Superusers can access all matching sessions.
        - Owner, Manager, and Staff can access sessions in their gym.
        - The main trainer of the class can access its sessions.
        - The trainer assigned to a session can access that session.
        - Users without access receive an empty queryset.

        Returns:
            QuerySet:
                Sessions accessible to the current user.
        """

        user = self.request.user

        gym_id = self.kwargs.get("gym_id")
        class_id = self.kwargs.get("class_id")

        queryset = ClassSession.objects.select_related(
            "gym_class",
            "gym_class__gym",
            "trainer",
        ).filter(
            gym_class__gym_id=gym_id,
            gym_class_id=class_id,
        )

        if user.is_superuser:
            return queryset

        # Owner / Manager / Staff
        if user.memberships.filter(
            gym_id=gym_id,
            role__in=[
                GymMembership.Role.OWNER,
                GymMembership.Role.MANAGER,
                GymMembership.Role.STAFF,
            ],
            is_active=True,
        ).exists():
            return queryset.order_by(
                "date",
                "start_time",
            )

        # Main trainer of the class
        if queryset.filter(
            gym_class__trainer=user
        ).exists():
            return queryset.order_by(
                "date",
                "start_time",
            )

        # Trainer assigned to the session
        if queryset.filter(
            trainer=user
        ).exists():
            return queryset.order_by(
                "date",
                "start_time",
            )

        # User has no access
        return queryset.none()

    def get_gym_class(self):
        """
        Return the gym class identified by the URL parameters.

        URL structure:

            /gyms/{gym_id}/classes/{class_id}/sessions/

        The method ensures that the requested class belongs to the
        specified gym.

        Raises:
            Http404:
                If the gym class does not exist or does not belong
                to the requested gym.

        Returns:
            GymClass:
                The gym class associated with the requested session.
        """

        gym_id = self.kwargs.get("gym_id")
        class_id = self.kwargs.get("class_id")

        return get_object_or_404(
            GymClass,
            id=class_id,
            gym_id=gym_id,
        )

    def get_permissions(self):
        """
        Return permission classes required for the current action.

        Permission rules:

        - list:
            Uses IsAuthenticated and CanAccessSession.
            The user must be authenticated and must have permission
            to access sessions belonging to the requested class.

        - retrieve:
            Uses IsAuthenticated and CanAccessSession.
            The user must be authenticated and must have permission
            to access the requested session.

        - update:
            Uses IsAuthenticated and CanAccessSession.
            The user must be authenticated and must have permission
            to update the requested session.

        - partial_update:
            Uses IsAuthenticated and CanAccessSession.
            The user must be authenticated and must have permission
            to partially update the requested session.

        - create:
            Uses IsAuthenticated and CanCreateSession.
            The user must be authenticated and must have permission
            to create a session for the requested gym class.

        - destroy:
            Uses IsAuthenticated and CanDeleteSession.
            The user must be authenticated and must have permission
            to delete the requested session.

        - get_students:
            Uses IsAuthenticated and CanViewSessionStudents.
            The user must be authenticated and must have permission
            to view students enrolled in the requested session.

        - record_attendance:
            Uses IsAuthenticated and CanRecordAttendance.
            The user must be authenticated and must have permission
            to record attendance for the requested session.

        Returns:
            list:
                Instantiated permission classes for the current action.
        """

        if self.action in [
            "list",
            "retrieve",
            "update",
            "partial_update",
        ]:
            permission_classes = [
                IsAuthenticated,
                CanAccessSession,
            ]

        elif self.action == "create":
            permission_classes = [
                IsAuthenticated,
                CanCreateSession,
            ]

        elif self.action == "destroy":
            permission_classes = [
                IsAuthenticated,
                CanDeleteSession,
            ]

        elif self.action == "get_students":
            permission_classes = [
                IsAuthenticated,
                CanViewSessionStudents,
            ]

        elif self.action == "record_attendance":
            permission_classes = [
                IsAuthenticated,
                CanRecordAttendance,
            ]

        else:
            permission_classes = []

        return [
            permission()
            for permission in permission_classes
        ]

    def create(self, request, *args, **kwargs):
        """
        Create a new class session.

        URL:

            /gyms/{gym_id}/classes/{class_id}/sessions/

        Process:

        1. Retrieve and validate the requested GymClass.
        2. Validate request data using ClassSessionSerializer.
        3. Save the new session and associate it with the requested
           GymClass.

        Authorization:
            CanCreateSession determines whether the authenticated user
            is allowed to create the session.

        Returns:
            Response:
                HTTP 201 response containing the created session.
        """

        gym_class = self.get_gym_class()

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save(
            gym_class=gym_class
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        request=AttendanceSerializer,
        responses={200: None},
    )
    @action(
        detail=True,
        methods=["post"],
    )
    def record_attendance(
        self,
        request,
        pk=None,
        **kwargs
    ):
        """
        Record attendance for a student in a class session.

        Permission:
            CanRecordAttendance controls whether the authenticated
            user is allowed to record attendance for the session.

        Validation:
            AttendanceSerializer validates the submitted attendance
            data.

        Business logic:
            The actual attendance operation is delegated to
            record_attendance_service().

        Process:

        1. Retrieve the requested session.
        2. Check object-level permissions for the session.
        3. Validate the attendance request data.
        4. Delegate attendance recording to the service layer.

        Returns:
            Response:
                HTTP 200 response when attendance is recorded
                successfully.
        """

        session = self.get_object()

        self.check_object_permissions(
            request,
            session,
        )

        serializer = AttendanceSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        record_attendance_service(
            session_id=session.id,
            user_id=serializer.validated_data["user_id"],
            attendance_status=serializer.validated_data[
                "attendance_status"
            ],
        )

        return Response(
            {
                "detail": "Attendance recorded successfully."
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["get"],
    )
    def get_students(
        self,
        request,
        pk=None,
        **kwargs
    ):
        """
        Return students enrolled in the requested class session.

        Permission:
            CanViewSessionStudents controls whether the authenticated
            user is allowed to view students of the requested session.

        Business logic:
            Student retrieval is delegated to
            get_enrolled_students().

        Serialization:
            SessionStudentSerializer serializes multiple enrollment
            objects using many=True.

        The current session is passed through serializer context
        so that SessionStudentSerializer can access session-specific
        information such as attendance.

        Process:

        1. Retrieve the requested session.
        2. Check object-level permissions for the session.
        3. Retrieve enrolled students using the service layer.
        4. Serialize the enrollments with session context.
        5. Return the serialized student list.

        Returns:
            Response:
                HTTP 200 response containing students enrolled in
                the requested session.
        """

        session = self.get_object()

        self.check_object_permissions(
            request,
            session,
        )

        enrollments = get_enrolled_students(
            session.id
        )

        serializer = SessionStudentSerializer(
            enrollments,
            many=True,
            context={
                "session": session,
            },
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )