from django.db import models
from django.conf import settings
from organizations.models import Organization
from django.core.validators import MinValueValidator, MaxValueValidator

class Activity(models.Model):

    CATEGORY_CHOICES = (
        ('technical', 'Technical'),
        ('medical', 'Medical'),
        ('educational', 'Educational'),
        ('administrative', 'Administrative'),
)

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('closed', 'Closed'),
    )

    title = models.CharField(max_length=255)

    description = models.TextField()

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='activities'
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='technical'
    )

    location = models.CharField(
        max_length=255,
        default='Gaza'
    )

    start_date = models.DateField(
        default='2026-05-23'
    )

    end_date = models.DateField(
        default='2026-05-30'
    )

    registration_deadline = models.DateField(
        null=True,
        blank=True
    )

    volunteer_limit = models.PositiveIntegerField(
        default=20
    )

    applicants_count = models.PositiveIntegerField(
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    hours = models.PositiveIntegerField(
        default=60,

)

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.title




class ActivitySettings(models.Model):

    minimum_hours = models.PositiveIntegerField(
        default=60
    )

    maximum_hours = models.PositiveIntegerField(
        default=120
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"Activity Hours: {self.minimum_hours} - {self.maximum_hours}"


class Participation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='participations'
    )

    activity = models.ForeignKey(
        'Activity',
        on_delete=models.CASCADE,
        related_name='participants'
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
)

    class Meta:
        unique_together = ('user', 'activity')


    def __str__(self):
        return f"{self.user} -> {self.activity}"


class VolunteerAttendance(models.Model):
    participation = models.ForeignKey(
        Participation,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )

    attendance_date = models.DateField()

    hours = models.PositiveIntegerField()

    notes = models.TextField(
        blank=True,
        null=True
    )

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_attendance'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-attendance_date']
        unique_together = ('participation', 'attendance_date')

    def __str__(self):
        return (
            f"{self.participation.user.username} - "
            f"{self.attendance_date} ({self.hours}h)"
        )

class DailyActivityLog(models.Model):

    ACTIVITY_TYPES = (
        ('whatsapp', 'استفسارات واتس أب'),
        ('admission', 'قضايا قبول وتسجيل'),
        ('lecturers', 'مراجعة محاضرين'),
        ('administrative', 'قضايا إدارية'),
        ('elearning', 'تعليم إلكتروني'),
        ('volunteer', 'مراجعات عمل تطوعي'),
        ('technical', 'دعم فني'),
        ('calls', 'اتصالات'),
        ('sms', 'رسائل SMS'),
        ('institutions', 'مخاطبات مؤسسات'),
        ('field_visits', 'زيارات ميدانية'),
        ('design', 'أعمال تصميم'),
        ('media', 'تصوير ومونتاج'),
    )

    activity_type = models.CharField(
        max_length=50,
        choices=ACTIVITY_TYPES
    )

    title = models.CharField(
        max_length=255
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    date = models.DateField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='daily_logs'
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_logs'
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return f"{self.activity_type} - {self.date}"