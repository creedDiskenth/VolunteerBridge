from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('supervisor', 'Supervisor'),
        ('leader', 'Leader'),
        ('volunteer', 'Volunteer'),
    )
    username = models.CharField(max_length=150, unique=True)

    university_id = models.CharField(
        max_length=20,
        unique=True
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='volunteer'
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    profile_image = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )

    USERNAME_FIELD = 'university_id'

    REQUIRED_FIELDS = ['username', 'email']

    def __str__(self):
        return self.university_id