# Generated by Django 4.2.7 on 2024-03-16 05:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0002_alter_personaldetail_contact_no"),
    ]

    operations = [
        migrations.AlterField(
            model_name="academicperformance",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="home.faculty_login"
            ),
        ),
    ]
