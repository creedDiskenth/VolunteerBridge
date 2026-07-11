from django.urls import path
from .views import (
    ActivityListView,
    ActivityCreateView,
    JoinActivityView,
    MyParticipationsView,
    AttendanceListCreateView,
    MyTotalHoursView,
    DailyActivityLogListCreateView,
    DailyActivityStatisticsView,
    DailyActivityReportView,
    VolunteerHoursReportView,
    DashboardStatisticsView,
    OrganizationsReportView,

)

urlpatterns = [
    path('', ActivityListView.as_view(), name='activity-list'),
    path('create/', ActivityCreateView.as_view(), name='activity-create'),

    path(
        '<int:pk>/join/',
        JoinActivityView.as_view(),
        name='activity-join'
    ),

    path(
        'my-participations/',
        MyParticipationsView.as_view(),
        name='my-participations'
    ),

    path(
        'attendance/',
        AttendanceListCreateView.as_view(),
        name='attendance-list-create'
    ),

    path(
    "my-total-hours/",
    MyTotalHoursView.as_view(),
    name="my-total-hours",
),
    path(
    'daily-logs/',
    DailyActivityLogListCreateView.as_view(),
    name='daily-logs'
),
    path(
    'daily-logs/statistics/',
    DailyActivityStatisticsView.as_view(),
    name='daily-log-statistics'
),
    path(
    "daily-logs/report/",
    DailyActivityReportView.as_view(),
    name="daily-log-report",
),
    path(
    "volunteer-hours-report/",
    VolunteerHoursReportView.as_view(),
    name="volunteer-hours-report",
),
    path(
    "dashboard/",
    DashboardStatisticsView.as_view(),
    name="dashboard",
),
    path(
    "organizations-report/",
    OrganizationsReportView.as_view(),
    name="organizations-report",
),
]