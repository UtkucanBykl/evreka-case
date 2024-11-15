# Generated by Django 4.2 on 2024-11-14 13:14

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9, validators=[django.core.validators.MinValueValidator(-90), django.core.validators.MaxValueValidator(90)])),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9, validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)])),
                ('speed', models.DecimalField(decimal_places=2, help_text='Speed in kilometers per hour', max_digits=6)),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='devices.device')),
            ],
            options={
                'ordering': ['-timestamp'],
                'get_latest_by': 'timestamp',
            },
        ),
        migrations.CreateModel(
            name='LocationDailySummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_speed', models.DecimalField(decimal_places=2, help_text='Maximum recorded speed in kilometers per hour', max_digits=6)),
                ('summary_day', models.DateField()),
                ('device', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='location_summary', to='devices.device')),
                ('first_location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='summary_as_first', to='devices.location')),
                ('last_location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='summary_as_last', to='devices.location')),
                ('max_speed_location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='summary_as_max_speed', to='devices.location')),
            ],
            options={
                'verbose_name_plural': 'Location summaries',
            },
        ),
        migrations.AddIndex(
            model_name='device',
            index=models.Index(fields=['created_at'], name='devices_dev_created_f36e7e_idx'),
        ),
        migrations.AddIndex(
            model_name='device',
            index=models.Index(fields=['name'], name='devices_dev_name_7c6eed_idx'),
        ),
        migrations.AddIndex(
            model_name='locationdailysummary',
            index=models.Index(fields=['summary_day'], name='devices_loc_summary_1ff2b8_idx'),
        ),
        migrations.AddIndex(
            model_name='locationdailysummary',
            index=models.Index(fields=['device'], name='devices_loc_device__2292ab_idx'),
        ),
        migrations.AddIndex(
            model_name='locationdailysummary',
            index=models.Index(fields=['device', 'summary_day'], include=('max_speed', 'max_speed_location', 'first_location', 'last_location'), name='summary_covering_idx'),
        ),
        migrations.AddIndex(
            model_name='location',
            index=models.Index(fields=['timestamp'], name='devices_loc_timesta_0b1f65_idx'),
        ),
        migrations.AddIndex(
            model_name='location',
            index=models.Index(fields=['device', 'timestamp'], name='devices_loc_device__327c9e_idx'),
        ),
    ]
