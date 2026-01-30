from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Пользователь платформы.

    Расширяет `AbstractUser` полем `role`.
    Роль определяет доступ к сценариям и возможностям (ученик, родитель, учитель, методист).

    Пример:
        User.objects.create_user(username="ivan", password="secret", role="student")
    """

    ROLE_CHOICES = [
        ("student", "Student"),
        ("parent", "Parent"),
        ("teacher", "Teacher"),
        ("methodist", "Methodist"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="student"
    )
