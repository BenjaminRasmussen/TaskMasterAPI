# Generated by Django 2.1 on 2018-08-14 10:10

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taskMaster', '0003_auto_20180814_0928'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserRelation',
            new_name='UserListRelation',
        ),
    ]
