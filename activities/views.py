from rest_framework import generics
from .models import Activity
from .serializers import ActivitySerializer
from .permissions import IsAdminOrSupervisor
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Activity, Participation, VolunteerAttendance
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Participation
from .serializers import (
    ActivitySerializer,
    ParticipationSerializer,
    VolunteerAttendanceSerializer,
    DailyActivityLogSerializer,
)
from django.db.models import Sum
from .models import DailyActivityLog
from django.db.models import Count
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from organizations.models import Organization


User = get_user_model()


# عرض جميع الأنشطة
class ActivityListView(generics.ListAPIView):

    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]


# إنشاء نشاط
class ActivityCreateView(generics.CreateAPIView):

    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [IsAdminOrSupervisor]


class JoinActivityView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user

        try:
            activity = Activity.objects.get(id=pk)
        except Activity.DoesNotExist:
            return Response(
                {"message": "Activity not found"},
                status=status.HTTP_404_NOT_FOUND
            )


        # منع التسجيل مرتين
        if Participation.objects.filter(
            user=user,
            activity=activity
        ).exists():
            return Response(
                {"message": "Already joined"},
                status=status.HTTP_400_BAD_REQUEST
            )


        # منع تجاوز العدد
        current_participants = Participation.objects.filter(
            activity=activity
        ).count()

        if current_participants >= activity.volunteer_limit:
            return Response(
                {"message": "Activity volunteer limit reached"},
                status=status.HTTP_400_BAD_REQUEST
            )


        # منع التسجيل بعد انتهاء النشاط
        from django.utils import timezone

        if activity.end_date < timezone.now().date():
            return Response(
                {"message": "Activity has already ended"},
                status=status.HTTP_400_BAD_REQUEST
            )


        Participation.objects.create(
            user=user,
            activity=activity
        )

        return Response(
            {"message": "Joined successfully"},
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