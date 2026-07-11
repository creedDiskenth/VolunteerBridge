from django.contrib import admin

from .models import (
    Activity,
    Participation,
    VolunteerAttendance,
    DailyActivityLog,
)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "organization",
        "category",
        "start_date",
        "end_date",
        "volunteer_limit",
    )
    search_fields = ("title",)
    list_filter = ("category", "organization")


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "activity",
        "status",
        "joined_at",
    )
    search_fields = (
        "user__username",
        "activity__title",
    )
    list_filter = ("status",)


@admin.register(VolunteerAttendance)
class VolunteerAttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "participation",
        "attendance_date",
        "hours",
        "recorded_by",
    )
    list_filter = ("attendance_date",)
    search_fields = (
        "participation__user__username",
    )


@admin.register(DailyActivityLog)
class DailyActivityLogAdmin(admin.ModelAdmin):
    list_display = (
        "activity_type",
        "title",
        "date",
        "created_by",
    )
    list_filter = (
        "activity_type",
        "date",
    )
    search_fields = (
        "title",
        "description",
    )