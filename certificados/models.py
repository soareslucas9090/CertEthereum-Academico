from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Permission,
    PermissionsMixin,
)
from django.db import models


class UserManager(BaseUserManager):
    def create_user(
        self,
        name,
        email,
        password=None,
        **extra_fields,
    ):
        if not email:
            raise ValueError("User must have an email address")
        if not name:
            raise ValueError("User must have a name")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        name,
        email,
        password=None,
        **extra_fields,
    ):
        user = self.create_user(
            name=name,
            email=self.normalize_email(email),
            password=password,
            is_admin=True,
            is_superuser=True,
            **extra_fields,
        )

        permissions = Permission.objects.all()
        user.user_permissions.set(permissions)

        return user


class Users(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255, null=False)
    cnpj = models.CharField(max_length=14, null=False, unique=True)
    email = models.EmailField(null=False, unique=True)
    password = models.CharField(max_length=512, null=False)
    is_admin = models.BooleanField(null=False, default=False)
    is_active = models.BooleanField(null=False, default=True)

    REQUIRED_FIELDS = [
        "name",
        "cnpj",
    ]

    USERNAME_FIELD = "email"

    objects = UserManager()

    def __str__(self):
        str = f"{self.email}"
        return str

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
