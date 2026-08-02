from django.db import models
from django.contrib.auth.hashers import make_password


class Organization(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    CATEGORY_CHOICES = (
        ('ngo', 'أهلية'),
        ('government', 'رسمية'),
        ('international', 'دولية'),
    )


    name = models.CharField(max_length=255)

    email = models.EmailField(
    blank=True,
    null=True
    )

    password = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    license = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    address = models.TextField(
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    verified = models.BooleanField(
        default=False
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False