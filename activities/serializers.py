from rest_framework import serializers
from .models import DailyActivityLog
from .models import Activity, Participation, VolunteerAttendance


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'


class ParticipationSerializer(serializers.ModelSerializer):
    activity_title = serializers.CharField(
        source='activity.title',
        read_only=True
    )

    class Meta:
        model = Participation
        fields = '__all__'


class VolunteerAttendanceSerializer(serializers.ModelSerializer):
    volunteer_name = serializers.CharField(
        source='participation.user.username',
        read_only=True
    )

    activity_title = serializers.CharField(
        source='participation.activity.title',
        read_only=True
    )

    recorded_by_name = serializers.CharField(
        source='recorded_by.username',
        read_only=True
    )

    def validate(self, data):
        participation = data["participation"]
        attendance_date = data["attendance_date"]
        hours = data["hours"]

        activity = participation.activity

        # يجب أن تكون الساعات أكبر من صفر
        if hours <= 0:
            raise serializers.ValidationError(
                "Hours must be greater than 0."
            )

        # الحد الأقصى 8 ساعات يومياً
        if hours > 8:
            raise serializers.ValidationError(
                "Maximum allowed hours per day is 8."
            )

        # منع تسجيل الحضور قبل بداية النشاط
        if attendance_date < activity.start_date:
            raise serializers.ValidationError(
                "Attendance date is before the activity starts."
            )

        # منع تسجيل الحضور بعد انتهاء النشاط
        if attendance_date > activity.end_date:
            raise serializers.ValidationError(
                "Attendance date is after the activity ends."
            )

        return data

    class Meta:
        model = VolunteerAttendance
        fields = '__all__'

class DailyActivityLogSerializer(serializers.ModelSerializer):

    created_by_name = serializers.CharField(
        source='created_by.username',
        read_only=True
    )

    organization_name = serializers.CharField(
        source='organization.name',
        read_only=True
    )

    class Meta:
        model = DailyActivityLog
        fields = '__all__'
        read_only_fields = [
            'created_by',
            'created_at'
        ]