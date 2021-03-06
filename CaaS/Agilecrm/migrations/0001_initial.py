# Generated by Django 2.2 on 2020-03-06 07:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Connector', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agilecrmmodel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=512)),
                ('username', models.CharField(max_length=512)),
                ('api_key', models.CharField(max_length=512)),
                ('config', models.CharField(max_length=512)),
                ('flag', models.BooleanField(default=False)),
                ('created_date', models.DateTimeField()),
                ('source_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Connector.SSCConnector')),
            ],
        ),
    ]
