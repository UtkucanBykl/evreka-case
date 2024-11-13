import logging
from celery import shared_task
from django.core.cache import cache
from django.utils import timezone

from devices.models import Device, Location, LocationSummary
from devices.constants import DEVICES_LAST_DATA_CACHE_KEY

logger = logging.getLogger('django')


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 5},
    rate_limit='100/m'
)
def create_new_location(
    self, device_id: int, latitude: float, longitude: float, speed: float | None = None
) -> Location:
    try:
        device = Device.objects.get(id=device_id, is_active=True)
        
        # Create new location entry
        location = Location.objects.create(
            device=device,
            latitude=latitude,
            longitude=longitude,
            speed=speed,
            timestamp=timezone.now()
        )
        
        # Update cache with latest location data
        cache_key = DEVICES_LAST_DATA_CACHE_KEY.format(device_id)
        cache_data = {
            'latitude': float(location.latitude),
            'longitude': float(location.longitude),
            'speed': float(location.speed) if location.speed else 0,
            'timestamp': location.timestamp.isoformat(),
        }
        cache.set(cache_key, cache_data, timeout=3600)  # Cache for 1 hour

        return location

    except Device.DoesNotExist:
        logger.error(f"Device {device_id} not found or inactive")
        return False
    except Exception as e:
        logger.error(f"Error processing location data: {str(e)}")
        return False


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 5},
    rate_limit='100/m'
)
def update_or_create_location_summary(self, location_id: int) -> bool:
    try:
        # Get the location and related device
        location = Location.objects.select_related('device').get(id=location_id)
        device = location.device

        # Get or create location summary
        location_summary, created = LocationSummary.objects.get_or_create(
            device=device,
            defaults={
                "first_location": location,
                "last_location": location,
                "max_speed": location.speed,
                "max_speed_location": location,
            }
        )

        if not created:
            # Update last location
            location_summary.last_location = location
            
            # Update max speed if current speed is higher
            if location.speed > location_summary.max_speed:
                location_summary.max_speed = location.speed
                location_summary.max_speed_location = location
            # If no first location is set, set it
            if not location_summary.first_location:
                location_summary.first_location = location

            location_summary.save()

        return True

    except Location.DoesNotExist:
        logger.error(f"Location {location_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error updating location summary: {str(e)}")
        raise  # Let the task retry mechanism handle it


