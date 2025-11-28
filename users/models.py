from django.contrib.auth.models import AbstractUser
from django.db import models

class EmployeProfile(AbstractUser):
    username = None
    email = models.EmailField(unique=True, blank=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.email