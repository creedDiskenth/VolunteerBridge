from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.utils import timezone
from .models import ActivitySettings
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import (
    ActivitySerializer,
    ParticipationSerializer,
    VolunteerAttendanceSerializer,
    DailyActivityLogSerializer,
    ActivitySettingsSerializer,
)
from organizations.authentication import OrganizationJWTAuthentication
from organizations.models import Organization

from .models import (
    Activity,
    Participation,
    VolunteerAttendance,
    DailyActivityLog,
)

from .permissions import (
    IsAdminOrSupervisor,
    IsAdminOrSupervisorOrOrganization,
)

from .serializers import (
    ActivitySerializer,
    ParticipationSerializer,
    VolunteerAttendanceSerializer,
    DailyActivityLogSerializer,
)

User = get_user_model()

def get_activity_settings():
    settings = ActivitySettings.objects.first()

    if not settings:
        settings = ActivitySettings.objects.create(
            minimum_hours=60,
            maximum_hours=120
        )

    return settings



class ActivitySettingsView(generics.RetrieveUpdateAPIView):

    serializer_class = ActivitySettingsSerializer
    permission_classes = [IsAdminOrSupervisor]

    def get_object(self):
        return get_activity_settings()



class MyOrganizationActivitiesView(ListAPIView):

    serializer_class = ActivitySerializer

    authentication_classes = [
        OrganizationJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        organization_id = self.request.auth.get(
            "organization_id"
        )

        return Activity.objects.filter(
            organization_id=organization_id
        ).order_by("-created_at")



class ActivityApplicationsView(ListAPIView):

    serializer_class = ParticipationSerializer

    authentication_classes = [
        OrganizationJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        organization_id = self.request.auth.get(
            "organization_id"
        )

        activity_id = self.kwargs["pk"]

        return Participation.objects.filter(
            activity_id=activity_id,
            activity__organization_id=organization_id
        ).order_by("-joined_at")



class MyOrganizationApplicationsView(ListAPIView):

    serializer_class = ParticipationSerializer

    authentication_classes = [
        OrganizationJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        organization_id = self.request.auth.get(
            "organization_id"
        )

        return Participation.objects.filter(
            activity__organization_id=organization_id
        ).order_by("-joined_at")



class ActivityDetailView(APIView):

    authentication_classes = [
        OrganizationJWTAuthentication,
        JWTAuthentication,
    ]

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        today = timezone.now().date()

        # إغلاق النشاط إذا انتهت مدته
        Activity.objects.filter(
            id=pk,
            end_date__lt=today,
            status="active"
        ).update(
            status="closed"
        )

        try:
            activity = Activity.objects.get(id=pk)

        except Activity.DoesNotExist:
            return Response(
                {"message": "Activity not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ActivitySerializer(activity)

        return Response(serializer.data)


# عرض جميع الأنشطة
class ActivityListView(generics.ListAPIView):

    serializer_class = ActivitySerializer

    authentication_classes = [
        OrganizationJWTAuthentication,
        JWTAuthentication,
    ]

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        today = timezone.now().date()

        # إغلاق الأنشطة التي انتهت مدتها
        Activity.objects.filter(
            end_date__lt=today,
            status="active"
        ).update(
            status="closed"
        )

        queryset = Activity.objects.all()

        status_filter = self.request.query_params.get("status")
        category = self.request.query_params.get("category")
        org_type = self.request.query_params.get("type")

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if category:
            queryset = queryset.filter(category=category)

        if org_type:
            queryset = queryset.filter(
                organization__category=org_type
            )

        return queryset.order_by("-created_at")




class ActivityCreateView(generics.CreateAPIView):

    serializer_class = ActivitySerializer

    authentication_classes = [
        OrganizationJWTAuthentication,
        JWTAuthentication,
    ]

    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):

        user = request.user
        user_role = getattr(user, "role", None)

        # =========================================
        # Admin / Supervisor
        # =========================================

        if (
            user.is_authenticated
            and user_role in ["admin", "supervisor"]
        ):
            serializer = self.get_serializer(
                data=request.data
            )

            serializer.is_valid(raise_exception=True)

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        # =========================================
        # Organization
        # =========================================

        if request.auth:

            organization_id = request.auth.get(
                "organization_id"
            )

            if organization_id:

                serializer = self.get_serializer(
                    data=request.data
                )

                serializer.is_valid(raise_exception=True)

                # المؤسسة تصبح مالكة للفرصة تلقائيًا
                serializer.save(
                    organization_id=organization_id
                )

                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

        # =========================================
        # Unauthorized
        # =========================================

        return Response(
            {
                "detail": (
                    "Only admin, supervisor, or "
                    "organization can create activities."
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )


class JoinActivityView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        user = request.user

        try:
            activity = Activity.objects.get(id=pk)

        except Activity.DoesNotExist:
            return Response(
                {
                    "message": "Activity not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        today = timezone.now().date()

        # =====================================================
        # 1. تحديث حالة الفرصة بناءً على موعد التسجيل
        # =====================================================

        if (
            activity.registration_deadline
            and activity.registration_deadline < today
        ):
            if activity.status != "closed":
                activity.status = "closed"
                activity.save(update_fields=["status"])

            return Response(
                {
                    "message": "Registration deadline has passed."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # =====================================================
        # 2. إذا تم تمديد موعد التسجيل
        #    وكانت الفرصة Closed بسبب انتهاء الموعد
        # =====================================================

        if (
            activity.status == "closed"
            and activity.registration_deadline
            and activity.registration_deadline >= today
        ):
            activity.status = "active"
            activity.save(update_fields=["status"])

        # =====================================================
        # 3. منع التسجيل إذا كانت الفرصة مغلقة
        #    لسبب آخر
        # =====================================================

        if activity.status == "closed":
            return Response(
                {
                    "message": "This activity is closed."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # =====================================================
        # 4. منع التسجيل بعد انتهاء النشاط
        # =====================================================

        if activity.end_date < today:
            return Response(
                {
                    "message": "Activity has already ended"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # =====================================================
        # 5. منع التسجيل مرتين
        # =====================================================

        existing_participation = Participation.objects.filter(
            user=user,
            activity=activity
        ).first()

        if existing_participation:
            return Response(
                {
                    "message": "Already joined",
                    "status": existing_participation.status
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # =====================================================
        # 6. التأكد من وجود مقاعد
        # =====================================================

        if activity.applicants_count >= activity.volunteer_limit:

            activity.status = "closed"
            activity.save(update_fields=["status"])

            return Response(
                {
                    "message": "Activity volunteer limit reached"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # =====================================================
        # 7. إنشاء طلب Pending
        # =====================================================

        Participation.objects.create(
            user=user,
            activity=activity,
            status="pending"
        )

        return Response(
            {
                "message": "Join request submitted successfully",
                "status": "pending",
                "applicants_count": activity.applicants_count,
                "activity_status": activity.status
            },
            status=status.HTTP_201_CREATED
        )


class MyParticipationsView(ListAPIView):

    serializer_class = ParticipationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Participation.objects.filter(
            user=self.request.user
        )

class AttendanceListCreateView(generics.ListCreateAPIView):

    queryset = VolunteerAttendance.objects.all()
    serializer_class = VolunteerAttendanceSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)



class MyTotalHoursView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        total_hours = VolunteerAttendance.objects.filter(
            participation__user=request.user
        ).aggregate(
            total=Sum("hours")
        )["total"] or 0

        required_hours = 60

        remaining_hours = max(0, required_hours - total_hours)

        return Response({
            "student": request.user.username,
            "total_hours": total_hours,
            "required_hours": required_hours,
            "remaining_hours": remaining_hours,
            "completed": total_hours >= required_hours
        })

class DailyActivityLogListCreateView(generics.ListCreateAPIView):

    serializer_class = DailyActivityLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DailyActivityLog.objects.all().order_by('-date')

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user
        )

class DailyActivityStatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        today = timezone.now().date()

        statistics = (
            DailyActivityLog.objects
            .filter(date=today)
            .values("activity_type")
            .annotate(total=Count("id"))
            .order_by("activity_type")
        )

        return Response({
            "date": today,
            "statistics": statistics
        })

class DailyActivityReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if not start_date or not end_date:
            raise ValidationError(
                "Both start_date and end_date are required."
            )

        logs = DailyActivityLog.objects.filter(
            date__range=[start_date, end_date]
        )

        statistics = (
            logs.values("activity_type")
            .annotate(total=Count("id"))
            .order_by("activity_type")
        )

        return Response({
            "start_date": start_date,
            "end_date": end_date,
            "total_logs": logs.count(),
            "statistics": statistics
        })

class VolunteerHoursReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        required_hours = 60
        report = []

        users = User.objects.all()

        for user in users:
            total_hours = (
                VolunteerAttendance.objects.filter(
                    participation__user=user
                ).aggregate(
                    total=Sum("hours")
                )["total"] or 0
            )

            report.append({
                "student": user.username,
                "total_hours": total_hours,
                "required_hours": required_hours,
                "remaining_hours": max(0, required_hours - total_hours),
                "completed": total_hours >= required_hours
            })

        return Response(report)

class DashboardStatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        required_hours = 60

        total_organizations = Organization.objects.count()

        total_activities = Activity.objects.count()

        total_volunteers = User.objects.count()

        total_participations = Participation.objects.count()

        total_attendance_records = VolunteerAttendance.objects.count()

        total_daily_logs = DailyActivityLog.objects.count()

        completed_volunteers = 0

        for user in User.objects.all():

            total_hours = (
                VolunteerAttendance.objects.filter(
                    participation__user=user
                ).aggregate(
                    total=Sum("hours")
                )["total"] or 0
            )

            if total_hours >= required_hours:
                completed_volunteers += 1

        activity_type_chart = (
            DailyActivityLog.objects
            .values("activity_type")
            .annotate(total=Count("id"))
            .order_by("activity_type")
        )

        return Response({

            "total_organizations": total_organizations,

            "total_activities": total_activities,

            "total_volunteers": total_volunteers,

            "total_participations": total_participations,

            "total_attendance_records": total_attendance_records,

            "total_daily_logs": total_daily_logs,

            "completed_volunteers": completed_volunteers,

            "activity_type_chart": activity_type_chart

        })

class OrganizationsReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        report = []

        organizations = Organization.objects.all()

        for organization in organizations:

            activities_count = Activity.objects.filter(
                organization=organization
            ).count()

            participants_count = Participation.objects.filter(
                activity__organization=organization
            ).count()

            report.append({
                "organization": organization.name,
                "category": organization.get_category_display(),
                "activities": activities_count,
                "participants": participants_count
            })

        return Response(report)






class ApproveParticipationView(APIView):

    authentication_classes = [
        OrganizationJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        organization_id = request.auth.get("organization_id")

        try:
            participation = Participation.objects.select_related(
                "activity"
            ).get(
                id=pk,
                activity__organization_id=organization_id
            )

        except Participation.DoesNotExist:
            return Response(
                {"message": "Participation not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        activity = participation.activity

        # ==========================================
        # منع قبول الطلب أكثر من مرة
        # ==========================================

        if participation.status == "approved":
            return Response(
                {
                    "message": "Participation is already approved.",
                    "applicants_count": activity.applicants_count
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==========================================
        # التأكد من وجود مقعد
        # ==========================================

        if activity.applicants_count >= activity.volunteer_limit:

            activity.status = "closed"
            activity.save(update_fields=["status"])

            return Response(
                {
                    "message": "Activity volunteer limit reached.",
                    "applicants_count": activity.applicants_count,
                    "volunteer_limit": activity.volunteer_limit
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==========================================
        # قبول الطالب
        # ==========================================

        participation.status = "approved"
        participation.save(update_fields=["status"])

        # ==========================================
        # حجز مقعد للطالب
        # ==========================================

        activity.applicants_count += 1

        # إذا امتلأت المقاعد تغلق الفرصة
        if activity.applicants_count >= activity.volunteer_limit:
            activity.status = "closed"

        activity.save(
            update_fields=[
                "applicants_count",
                "status"
            ]
        )

        return Response(
            {
                "message": "Participation approved successfully.",
                "participation_id": participation.id,
                "status": participation.status,
                "applicants_count": activity.applicants_count,
                "volunteer_limit": activity.volunteer_limit,
                "activity_status": activity.status
            },
            status=status.HTTP_200_OK
        )

class RejectParticipationView(APIView):

    authentication_classes = [
        OrganizationJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        organization_id = request.auth.get("organization_id")

        try:
            participation = Participation.objects.get(
                id=pk,
                activity__organization_id=organization_id
            )

        except Participation.DoesNotExist:
            return Response(
                {"message": "Participation not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        participation.status = "rejected"
        participation.save()

        return Response({
            "message": "Participation rejected successfully."
        })



class ActivityUpdateView(generics.UpdateAPIView):

    serializer_class = ActivitySerializer

    authentication_classes = [
        OrganizationJWTAuthentication,
        JWTAuthentication,
    ]

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user = self.request.user
        user_role = getattr(user, "role", None)

        # Admin / Supervisor
        if (
            user.is_authenticated
            and user_role in ["admin", "supervisor"]
        ):
            return Activity.objects.all()

        # Organization
        if self.request.auth:

            organization_id = self.request.auth.get(
                "organization_id"
            )

            if organization_id:
                return Activity.objects.filter(
                    organization_id=organization_id
                )

        return Activity.objects.none()

    def update(self, request, *args, **kwargs):

        # =====================================================
        # 1. التحقق من عدد الساعات
        # المسموح من 60 إلى maximum_hours
        # =====================================================

        if "hours" in request.data:

            try:
                hours = int(request.data["hours"])

            except (TypeError, ValueError):
                return Response(
                    {
                        "detail": "Hours must be a valid number."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            settings = ActivitySettings.objects.first()

            if settings:

                # الحد الأدنى
                if hours < 60:
                    return Response(
                        {
                            "detail": (
                                "Activity hours cannot be less than 60."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # الحد الأقصى
                if hours > settings.maximum_hours:
                    return Response(
                        {
                            "detail": (
                                f"Activity hours cannot exceed "
                                f"{settings.maximum_hours} hours."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

        # =====================================================
        # 2. تمديد موعد التسجيل
        # إذا كانت الفرصة Closed وتم تمديد الموعد
        # ترجع Active تلقائيًا
        # =====================================================

        if "registration_deadline" in request.data:

            new_deadline = request.data.get(
                "registration_deadline"
            )

            if new_deadline:

                try:
                    new_deadline = datetime.strptime(
                        new_deadline,
                        "%Y-%m-%d"
                    ).date()

                except (TypeError, ValueError):
                    return Response(
                        {
                            "detail": (
                                "registration_deadline must be "
                                "in YYYY-MM-DD format."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                today = timezone.now().date()

                # إذا الموعد الجديد ما زال صالحًا
                # نعيد الفرصة إلى Active
                if new_deadline >= today:

                    request.data._mutable = True

                    request.data["status"] = "active"

                    request.data._mutable = False

        return super().update(
            request,
            *args,
            **kwargs
        )



class CancelParticipationView(APIView):

    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        user = request.user

        try:
            participation = Participation.objects.select_related(
                "activity"
            ).get(
                id=pk,
                user=user
            )

        except Participation.DoesNotExist:
            return Response(
                {
                    "message": "Participation not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        activity = participation.activity

        # ==========================================
        # لا يمكن إلغاء طلب ملغي مسبقاً
        # ==========================================

        if participation.status == "cancelled":
            return Response(
                {
                    "message": "Participation is already cancelled."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==========================================
        # إذا كان الطالب مقبولاً
        # نرجع المقعد للفرصة
        # ==========================================

        if participation.status == "approved":

            if activity.applicants_count > 0:
                activity.applicants_count -= 1

            # إذا كانت الفرصة أغلقت بسبب امتلاء المقاعد
            # وكان موعد التسجيل ما زال صالحاً، نعيدها Active
            today = timezone.now().date()

            if (
                activity.registration_deadline
                and activity.registration_deadline >= today
                and activity.end_date >= today
            ):
                activity.status = "active"

            activity.save(
                update_fields=[
                    "applicants_count",
                    "status"
                ]
            )

        # ==========================================
        # إلغاء الطلب
        # ==========================================

        participation.status = "cancelled"
        participation.save(update_fields=["status"])

        return Response(
            {
                "message": "Participation cancelled successfully.",
                "participation_id": participation.id,
                "status": participation.status,
                "applicants_count": activity.applicants_count,
                "activity_status": activity.status
            },
            status=status.HTTP_200_OK
        )