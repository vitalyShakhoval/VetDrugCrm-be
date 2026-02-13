from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, Sum
from django.utils import timezone


class Warehouse(models.Model):
    name = models.CharField("Название склада", max_length=255, unique=True)
    address = models.CharField("Адрес", max_length=255, blank=True)

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады"

    def __str__(self) -> str:
        return self.name


class Section(models.Model):
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="sections",
        verbose_name="Склад",
    )
    name = models.CharField("Название секции", max_length=100)
    code = models.CharField("Код секции", max_length=50, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["warehouse", "name"],
                name="uniq_section_name_per_warehouse",
            ),
            models.UniqueConstraint(
                fields=["warehouse", "code"],
                condition=Q(code__isnull=False),
                name="uniq_section_code_per_warehouse",
            ),
        ]
        verbose_name = "Секция"
        verbose_name_plural = "Секции"

    def __str__(self) -> str:
        return f"{self.warehouse.name} / {self.name}"

    def save(self, *args, **kwargs):
        if self.code == "":
            self.code = None
        return super().save(*args, **kwargs)


class Batch(models.Model):
    drug = models.ForeignKey(
        "drugs.Drug",
        on_delete=models.PROTECT,
        related_name="batches",
        verbose_name="Препарат",
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="batches",
        verbose_name="Склад",
    )

    batch_number = models.CharField("Номер партии", max_length=50)
    manufacture_date = models.DateField("Дата производства", null=True, blank=True)
    expiry_date = models.DateField("Срок годности")

    received_quantity = models.PositiveIntegerField("Количество при поступлении")

    supplier = models.CharField("Поставщик", max_length=255, blank=True)
    purchase_price = models.DecimalField(
        "Закупочная цена",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    location = models.CharField("Локация", max_length=255, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["drug", "batch_number", "warehouse"],
                name="uniq_batch_per_drug_wh",
            ),
        ]
        indexes = [
            models.Index(fields=["warehouse", "batch_number"]),
            models.Index(fields=["expiry_date"]),
        ]
        verbose_name = "Партия"
        verbose_name_plural = "Партии"

    def __str__(self) -> str:
        return f"{self.drug} ({self.batch_number})"

    def clean(self):
        if self.manufacture_date and self.expiry_date and self.manufacture_date > self.expiry_date:
            raise ValidationError("Дата производства не может быть позже срока годности.")

    @property
    def remaining_quantity(self) -> int:
        total = self.section_links.aggregate(s=Sum("quantity"))["s"]
        return int(total or 0)


class BatchSection(models.Model):
    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name="section_links",
        verbose_name="Партия",
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        related_name="batch_links",
        verbose_name="Секция",
    )
    quantity = models.PositiveIntegerField("Количество в секции")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["batch", "section"], name="uniq_batch_section"),
        ]
        verbose_name = "Партия в секции"
        verbose_name_plural = "Партии по секциям"

    def __str__(self) -> str:
        return f"{self.batch} @ {self.section} = {self.quantity}"

    def clean(self):
        if self.batch_id and self.section_id:
            if self.batch.warehouse_id != self.section.warehouse_id:
                raise ValidationError("Секция должна принадлежать складу партии.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class InventorySession(models.Model):
    STATUS_CHOICES = [
        ("in_progress", "В процессе"),
        ("completed", "Завершена"),
        ("cancelled", "Отменена"),
    ]

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="inventory_sessions",
        verbose_name="Склад",
    )
    sections = models.ManyToManyField(
        Section,
        through="InventorySessionSection",
        blank=True,
        related_name="inventory_sessions",
        verbose_name="Секции",
    )
    drug_group = models.ForeignKey(
        "drugs.DrugGroup",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="inventory_sessions",
        verbose_name="Группа препаратов",
    )

    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default="in_progress")
    started_at = models.DateTimeField("Начата", auto_now_add=True)
    completed_at = models.DateTimeField("Завершена", null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["warehouse", "status", "started_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["warehouse"],
                condition=Q(status="in_progress"),
                name="uniq_active_inventory_per_warehouse",
            ),
        ]
        verbose_name = "Инвентаризация"
        verbose_name_plural = "Инвентаризации"

    def __str__(self) -> str:
        return f"Инвентаризация {self.warehouse} ({self.started_at:%Y-%m-%d %H:%M})"

    def mark_completed(self, save=True):
        self.status = "completed"
        self.completed_at = timezone.now()
        if save:
            self.save(update_fields=["status", "completed_at"])


class InventorySessionSection(models.Model):
    session = models.ForeignKey(
        InventorySession,
        on_delete=models.CASCADE,
        related_name="section_links",
        verbose_name="Сессия",
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        related_name="session_links",
        verbose_name="Секция",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["session", "section"], name="uniq_inventory_session_section"),
        ]
        verbose_name = "Секция в инвентаризации"
        verbose_name_plural = "Секции в инвентаризациях"

    def clean(self):
        if self.session_id and self.section_id:
            if self.session.warehouse_id != self.section.warehouse_id:
                raise ValidationError("Нельзя добавить секцию чужого склада в инвентаризацию.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class InventoryRecord(models.Model):
    session = models.ForeignKey(
        InventorySession,
        on_delete=models.CASCADE,
        related_name="records",
        verbose_name="Сессия",
    )
    batch = models.ForeignKey(
        Batch,
        on_delete=models.PROTECT,
        related_name="inventory_records",
        verbose_name="Партия",
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        related_name="inventory_records",
        verbose_name="Секция",
    )

    expected_quantity = models.PositiveIntegerField("Учётное количество")
    actual_quantity = models.PositiveIntegerField("Фактическое количество", null=True, blank=True)
    difference = models.IntegerField("Расхождение", null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["session", "batch", "section"], name="uniq_inventory_line"),
        ]
        indexes = [
            models.Index(fields=["session"]),
            models.Index(fields=["batch"]),
            models.Index(fields=["section"]),
        ]
        verbose_name = "Строка инвентаризации"
        verbose_name_plural = "Строки инвентаризации"

    def __str__(self) -> str:
        return f"{self.batch} @ {self.section}"

    def clean(self):
        if self.batch_id and self.session_id:
            if self.batch.warehouse_id != self.session.warehouse_id:
                raise ValidationError("Партия должна относиться к складу инвентаризации.")

        if self.section_id and self.session_id:
            if self.section.warehouse_id != self.session.warehouse_id:
                raise ValidationError("Секция должна относиться к складу инвентаризации.")

            if self.session.sections.exists() and not self.session.sections.filter(pk=self.section_id).exists():
                raise ValidationError("Секция не входит в выбранные секции инвентаризации.")

        if self.batch_id and self.section_id:
            if self.batch.warehouse_id != self.section.warehouse_id:
                raise ValidationError("Секция должна принадлежать складу партии.")

    def save(self, *args, **kwargs):
        if self.actual_quantity is None:
            self.difference = None
        else:
            self.difference = int(self.actual_quantity) - int(self.expected_quantity)
        self.full_clean()
        return super().save(*args, **kwargs)
