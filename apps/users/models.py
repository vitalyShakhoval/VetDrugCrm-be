from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from .roles import get_role_choices,get_role_class
from rolepermissions.roles import assign_role
from .roles import get_role_class

class EmployeProfileManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        role_code = extra_fields.get('role', 'veterinarian')
        role_class = get_role_class(role_code)
        if role_class:
            assign_role(user, role_class)
        return user
   
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'manager')
        return self.create_user(email, password, **extra_fields)

class EmployeProfile(AbstractUser):
    username = None
    email = models.EmailField(unique=True, blank=False)
    role = models.CharField(
        max_length=50,
        choices=get_role_choices(),
        default='veterinarian'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = EmployeProfileManager()
    
    def get_role_class(self):
        return get_role_class(self.role)
    
    def __str__(self):
        return self.email