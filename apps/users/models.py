from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, BaseUserManager
from .roles import get_role_choices,get_role_class
from rolepermissions.roles import assign_role

class EmployeeProfileManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        if not password:
            raise ValueError('Пароль обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        try:
            user.full_clean()
        except ValidationError as e:
            raise ValidationError(f"Ошибка валидации: {e}")
        with transaction.atomic():
            user.save(using=self._db)
            role_code = extra_fields.get('role', 'veterinarian')
            role_class = get_role_class(role_code)
            if role_class:
                assign_role(user, role_class)
            else:
                default_role = get_role_class('veterinarian')
                if default_role:
                    assign_role(user, default_role)
        return user
   
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'manager')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True')
        return self.create_user(email, password, **extra_fields)


class EmployeeProfile(AbstractUser):
    username = None
    email = models.EmailField(unique=True, blank=False)
    role = models.CharField(
        max_length=50,
        choices=get_role_choices(),
        default='veterinarian'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = EmployeeProfileManager()
    
    def get_role_class(self):
        return get_role_class(self.role)
    
    def __str__(self):
        return self.email