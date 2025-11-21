from django.db import models
# Create your models here.

class EmployeeProfile(models.Model):
    name = models.CharField(max_length= 50)
    
    ROLE_CHOICES = [
        ('manager', 'Менеджер'),
        ('warehouse_manager', 'Завскладом'),
        ('veterinarian', 'Ветеринар'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='veterinarian'
    )
    phone = models.CharField(max_length=12)

    def __str__(self):
        return self.name
    