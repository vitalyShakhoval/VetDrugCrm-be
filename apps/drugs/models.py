from django.db import models

# Create your models here.
class Drug(models.Model):
    name = models.CharField("Название", max_length=200)
    dosage_form = models.CharField("Форма выпуска", max_length=50)
    unit = models.CharField("Единица измерения", max_length=20)
    code = models.CharField("Код", max_length=50, unique=True)

    def __str__(self):
        return f"{self.name} ({self.dosage_form})"

    class Meta:
        verbose_name = "Препарат"
        verbose_name_plural = "Справочник препаратов"