# Generated by Django 2.2 on 2020-02-06 06:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Connector', '0004_sscconnector_flag'),
    ]

    operations = [
        migrations.CreateModel(
            name='Splunk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_url', models.CharField(max_length=512)),
                ('hec_token', models.CharField(max_length=512)),
                ('flag', models.BooleanField()),
                ('config', models.CharField(max_length=512)),
                ('created_date', models.DateTimeField()),
                ('source_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Connector.SSCConnector')),
            ],
        ),
    ]