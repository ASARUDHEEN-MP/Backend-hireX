# Generated by Django 4.2.3 on 2023-09-02 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0012_alter_userdetails_expected_salary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdetails',
            name='current_position',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='userdetails',
            name='education',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='userdetails',
            name='experience',
            field=models.CharField(max_length=35),
        ),
        migrations.AlterField(
            model_name='userdetails',
            name='skills',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='userdetails',
            name='worked_company',
            field=models.TextField(),
        ),
    ]