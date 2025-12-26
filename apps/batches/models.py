from django.db import models

class Batch(models.Model):
    drug = models.ForeignKey(
        "drugs.Drug",
        on_delete=models.PROTECT,
        related_name="batches",
    )
    batch_number = models.CharField(max_length=50)          # серия / номер партии
    manufacture_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField()                        # срок годности
    quantity = models.PositiveIntegerField()                # начальное количество
    remaining_quantity = models.PositiveIntegerField()      # текущий остаток
    supplier = models.CharField(max_length=255, blank=True)
    purchase_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    location = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("drug", "batch_number")
        verbose_name = "Партия"
        verbose_name_plural = "Партии"

    def __str__(self):
        return f"{self.drug.name} ({self.batch_number})"
