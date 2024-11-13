from django.db import models

# Create your models here.

from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Device(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['name']),
        ]


class Location(models.Model):
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='locations'
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90)
        ]
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ]
    )

    speed = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Speed in kilometers per hour"
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    def __str__(self):
        return f"{self.device.name} - {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['device', 'timestamp']),
        ]
        get_latest_by = 'timestamp'




class LocationSummary(models.Model):
    device = models.OneToOneField(
        Device,
        on_delete=models.CASCADE,
        related_name='location_summary'
    )
    first_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        related_name='summary_as_first'
    )
    last_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        related_name='summary_as_last'
    )
    max_speed = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Maximum recorded speed in kilometers per hour",
    )
    max_speed_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        related_name='summary_as_max_speed'
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Summary for {self.device.name}"

    class Meta:
        verbose_name_plural = "Location summaries"
        indexes = [
            models.Index(fields=['updated_at']),
            models.Index(fields=['device']),
        ]