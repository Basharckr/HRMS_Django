# Generated by Django 2.2.2 on 2021-06-03 03:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectlead', '0008_taskassigned_task_priority'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taskassigned',
            name='task_priority',
        ),
        migrations.AddField(
            model_name='tasks',
            name='task_priority',
            field=models.CharField(default='low', max_length=100),
        ),
    ]
