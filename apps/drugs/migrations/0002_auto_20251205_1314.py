from django.db import migrations

def create_initial_drugs(apps, schema_editor):
    Drug = apps.get_model("drugs", "Drug")
    Drug.objects.create(
        name="Амоксициллин",
        dosage_form="Таблетки",
        unit="мг",
        code="001",
    )
    Drug.objects.create(
        name="Йод",
        dosage_form="Раствор",
        unit="мл",
        code="002",
    )

def delete_initial_drugs(apps, schema_editor):
    Drug = apps.get_model("drugs", "Drug")
    Drug.objects.filter(code__in=["AMX001", "IOD003"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("drugs", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_initial_drugs, delete_initial_drugs),
    ]