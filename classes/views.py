from rest_framework import viewsets, status
from .serializers import (
    GymClassSerializer, 
    ClassSessionSerializer, 
    AttendanceSerializer, 
    SessionStudentSerializer
)
from rest_framework.decorators import action
from gyms.models import GymMembership
from .models import GymClass, ClassSession
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema
from .services.attendance_services import (
    record_attendance as record_attendance_service, get_enrolled_students
)

from rest_framework.permissions import IsAuthenticated, AllowAny

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import (
    SearchFilter,
    OrderingFilter,
)


from django.shortcuts import get_object_or_404

from permissions.class_permissions import (
    CanCreateSession,
    CanAccessSession,
    CanDeleteSession,
    CanViewSessionStudents,
    CanRecordAttendance,
    CanManageGymClass,
)

class GymClassViewSet(viewsets.ModelViewSet):
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
        Assign permissions based on actions.

        Public:

            GET /gym-classes/
            GET /gym-classes/{id}/


        Management:

            POST
            PUT
            PATCH
            DELETE

        Requires:

            Owner
            Manager
            Staff
        """

        if self.action in [
            "list",
            "retrieve",
        ]:
            permission_classes = [
                AllowAny
            ]

        elif self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
        ]:
            permission_classes = [
                IsAuthenticated,
                CanManageGymClass
            ]

        else:
            permission_classes = []


        return [
            permission()
            for permission in permission_classes
        ]


class ClassSessionViewSet(viewsets.ModelViewSet):

    # queryset = ClassSession.objects.all()
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
        Limits sessions based on URL hierarchy.

        URL structure:

        /gyms/{gym_id}/classes/{class_id}/sessions/

        Ensures:
            - Gym exists through relation
            - Class belongs to the selected gym
            - Session belongs to the selected class
        """
        user = self.request.user

        # if not user.is_authenticated:
        #     return ClassSession.objects.none()

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


###
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

            return queryset.order_by("date", "start_time")


        # Trainer اصلی کلاس
        if queryset.filter(
            gym_class__trainer=user
        ).exists():

            return queryset.order_by("date", "start_time")


        # Trainer همان Session
        if queryset.filter(
            trainer=user
        ).exists():

            return queryset.order_by("date", "start_time")


        # هیچ دسترسی ندارد
        return queryset.none()
        ##؟؟ این باید باه ؟
   
    def get_gym_class(self):
        """
        Returns the GymClass related to the URL.

        URL:
            /gyms/{gym_id}/classes/{class_id}/sessions/

        Checks:
            - Class exists
            - Class belongs to selected gym
        """

        gym_id = self.kwargs.get("gym_id")
        class_id = self.kwargs.get("class_id")

        return get_object_or_404(
            GymClass,
            id=class_id,
            gym_id=gym_id,
        )
   
   
    def get_permissions(self):

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
                CanCreateSession
                ]


        elif self.action == "destroy":
            permission_classes = [
                IsAuthenticated,
                CanDeleteSession
            ]

        elif self.action == "get_students":
            permission_classes = [
                IsAuthenticated,
                CanViewSessionStudents
            ]

        elif self.action == "record_attendance":
            permission_classes = [
                IsAuthenticated,
                CanRecordAttendance
            ]

        else:
            permission_classes = []


        return [
            permission()
            for permission in permission_classes
        ]
    
    def create(self, request, *args, **kwargs):
        """
        Create a new session for a specific class.

        URL:
            /gyms/{gym_id}/classes/{class_id}/sessions/

        Validates:
            - Gym and Class relationship
            - User permission to create session
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
    @action(detail=True, methods=['post'])
    def record_attendance(self, request, pk=None, **kwargs):

        session = self.get_object() 

            #برو تمام پرمیشن هایی که برای این ویو تعریف شدند رو  روی این ابجکت بررسی کن                   
        self.check_object_permissions(request, session)

        serializer = AttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        record_attendance_service(
            session_id=session.id,
            user_id=serializer.validated_data["user_id"],
            attendance_status=serializer.validated_data["attendance_status"],
        )

        return Response(
            {"detail": "Attendance recorded successfully."},
            status=status.HTTP_200_OK,
        )
        #نمایش اسامی شاگردان جلسه مورد نظر
   

    @action(detail=True, methods=["get"])
    def get_students(self, request, pk=None, **kwargs):


        session = self.get_object()  #session = ClassSession.objects.get(id=pk)#object

        self.check_object_permissions(
        request,
        session,
        )
        enrollments = get_enrolled_students(session.id)
        serializer = SessionStudentSerializer(
            enrollments,#تمام شاگردان enrollment
            many=True,#چون فقط یک Enrollment نداریم.
                 #اگر این را ننویسی، Serializer فکر می‌کند فقط یک آبجکت دریافت کرده است و خطا می‌دهد.
            
                #در سریالایزری که داری متدی داریم به اسم گت اتندنس که درش از سشن استفاده شده 
                #پس ما اطلاعات سشن رو هم همراهش میفرستیم
                #session = self.context.get("session")
                #اگه:
                #self.context = {}
                # session = self.context.get("session")=>null
                #attendance = session.attendance =>error

            context={"session": session},
                
            )

        return Response(serializer.data)
            #response انرا به صورت پاسخ http درمیاورد و میفرستد