# Generated by Django 4.0.6 on 2024-05-06 09:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('calendarapp', '0006_remove_event_address1_evt_remove_event_address2_evt_and_more'),
        ('myadmin', '0003_caseattachment'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientrecord',
            name='event',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='client_event', to='calendarapp.event'),
        ),
    ]
