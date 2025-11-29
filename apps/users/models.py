from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class EmployeProfileManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
   
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class EmployeProfile(AbstractUser):
    username = None
    USER_ROLES = [
        ('manager', 'Менеджер'),
        ('warehouse_supervisor', 'Заведующий складом'),
        ('veterinarian', 'Ветеринар'),
    ]
    role = models.CharField(
        max_length=50,
        choices=USER_ROLES,
        default='veterinarian'
    )
    email = models.EmailField(unique=True, blank=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = EmployeProfileManager()

    def __str__(self):
        return self.email
    

    def is_manager(self):
        return self.role == 'manager'
    
    def is_warehouse_supervisor(self):
        return self.role == 'warehouse_supervisor'
    
    def is_veterinarian(self):
        return self.role == 'veterinarian'