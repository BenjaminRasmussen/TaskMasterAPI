# Generated by Django 2.1 on 2018-08-17 18:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('taskMaster', '0008_auto_20180816_1943'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='owner',
        ),
    ]