from django.core.management.base import BaseCommand
from accounts.models import User
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        users = [
            {
                "username": "hossam",
                "university_id": "120220267",
                "password": "1234",
                "role": "volunteer"
            },
            {
                "username": "yahia",
                "university_id": "120220857",
                "password": "1234",
                "role": "volunteer"
            },
            {
                "username": "ahmad",
                "university_id": "120220173",
                "password": "1234",
                "role": "volunteer"
            },
            {
                "username": "abdullah",
                "university_id": "120220610",
                "password": "1234",
                "role": "volunteer"
            },
        ]

        for u in users:
            if not User.objects.filter(university_id=u["university_id"]).exists():
                User.objects.create(
                    username=u["username"],
                    university_id=u["university_id"],
                    password=make_password(u["password"]),
                    role=u["role"]
                )

        self.stdout.write(self.style.SUCCESS("Users created successfully"))