# Generated by Django 2.2 on 2020-01-20 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Slack', '0002_slack_flag'),
    ]

    operations = [
        migrations.AddField(
            model_name='slack',
            name='config',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
    ]
