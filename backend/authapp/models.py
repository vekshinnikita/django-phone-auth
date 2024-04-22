from typing import Union
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.hashers import make_password

# Create your models here.


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, phone: str, password: Union[str, None] = None, **extra_fields):
        """
        Создает пользователя
        """
        if not phone:
            raise ValueError("The given phone must be set")

        user = self.model(phone=phone, **extra_fields)

        if password is not None:
            user.password = make_password(password)

        user.save(using=self._db)
        return user

    def create_user(self, phone: str, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone, None, **extra_fields)

    def create_superuser(self, phone: str, password: Union[str, None], **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone, password, **extra_fields)


class User(AbstractUser):
    """Модель пользователя"""

    username = None
    phone = models.CharField("Телефонный номер", unique=True, max_length=11)
    firstname = models.CharField("Имя", null=True, max_length=255)
    lastname = models.CharField("Фамилия", null=True, max_length=255)
    patronymic = models.CharField("Отчество", null=True, max_length=255)
    referral_code = models.CharField(
        "Реферальный код", null=True, max_length=6)
    invited_user = models.ForeignKey(
        "self", verbose_name="Пригласивший пользователь", null=True, on_delete=models.SET_NULL)

    USERNAME_FIELD = "phone"

    objects = UserManager()

    def __str__(self):
        return self.phone

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class AuthTempCode(models.Model):
    """Модель одноразового кода для авторизации"""

    user = models.ForeignKey(
        User, verbose_name="Пользователь", on_delete=models.CASCADE)
    temp_code = models.CharField("Одноразовый код", max_length=4)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    retry_attempts = models.IntegerField(
        "Количество повторных попыток", default=0)

    class Meta:
        verbose_name = "Одноразовый код входа"
        verbose_name_plural = "Одноразовые коды входа"
