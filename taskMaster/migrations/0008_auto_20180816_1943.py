# Generated by Django 2.1 on 2018-08-16 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskMaster', '0007_remove_userlistrelation_views'),
    ]

    operations = [
        migrations.RenameField(
            model_name='taskcomment',
            old_name='LinkedTaskList',
            new_name='LinkedTask',
        ),
        migrations.AlterField(
            model_name='userlistrelation',
            name='role',
            field=models.CharField(default='guest', help_text='case insensitive. Type admin to give special rights!', max_length=55),
        ),
    ]
