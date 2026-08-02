from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.db.models import Sum

from .models import User
from activities.models import VolunteerAttendance


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    username_field = 'university_id'

    def validate(self, attrs):
        data = super().validate(attrs)

        # نضيف معلومات المستخدم للـ response
        data['user'] = {
            'id': self.user.id,
            'university_id': self.user.university_id,
            'role': self.user.role,
            'username': self.user.username,
        }

        return data




class ProfileSerializer(serializers.ModelSerializer):

    total_hours = serializers.SerializerMethodField()
    required_hours = serializers.SerializerMethodField()
    remaining_hours = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "university_id",
            "email",
            "role",
            "phone",
            "profile_image",
            "total_hours",
            "required_hours",
            "remaining_hours",
            "completion_percentage",
        ]

    def get_total_hours(self, obj):

        return (
            VolunteerAttendance.objects.filter(
                participation__user=obj
            ).aggregate(
                total=Sum("hours")
            )["total"] or 0
        )

    def get_required_hours(self, obj):
        return 60

    def get_remaining_hours(self, obj):

        total = self.get_total_hours(obj)

        return max(0, 60 - total)

    def get_completion_percentage(self, obj):

        total = self.get_total_hours(obj)

        percentage = (total / 60) * 100

        return round(min(percentage, 100), 2)