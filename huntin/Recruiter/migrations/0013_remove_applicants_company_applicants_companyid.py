# Generated by Django 4.2.3 on 2023-09-02 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Recruiter', '0012_rename_companyid_applicants_company'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='applicants',
            name='company',
        ),
        migrations.AddField(
            model_name='applicants',
            name='companyid',
            field=models.IntegerField(default=2),
            preserve_default=False,
        ),
    ]