from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase

from devices.models import Device, Location, LocationDailySummary
from devices.tasks import create_new_location, update_or_create_location_summary
from devices.constants import DEVICES_LAST_DATA_CACHE_KEY


class DeviceViewSetTests(APITestCase):
    def setUp(self):
        self.device = Device.objects.create(
            name="Test Device",
            description="Test Description"
        )


    def test_list_devices(self):
        url = reverse('device-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Device')

    def test_retrieve_device(self):
        url = reverse('device-detail', args=[self.device.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Device')

    def test_last_location_cached(self):
        cache_key = DEVICES_LAST_DATA_CACHE_KEY.format(self.device.id)
        cache_data = {'test': 'data'}
        cache.set(cache_key, cache_data)

        url = reverse('device-last-location', args=[self.device.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, cache_data)


class LocationViewSetTests(APITestCase):
    def setUp(self):
        self.device = Device.objects.create(
            name="Test Device",
            description="Test Description"
        )
        self.valid_payload = {
            'device_id': self.device.id,
            'latitude': '41.015137',
            'longitude': '28.979530',
            'speed': '50.25'
        }

    @patch('devices.serializers.chain')
    def test_create_location(self, mock_chain):
        url = reverse('location-list')
        response = self.client.post(url, self.valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_chain.assert_called_once()

    def test_list_locations(self):
        Location.objects.create(
            device=self.device,
            latitude=Decimal('41.015137'),
            longitude=Decimal('28.979530'),
            speed=Decimal('50.25')
        )
        
        url = reverse('location-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class TaskTests(TestCase):
    def setUp(self):
        self.device = Device.objects.create(
            name="Test Device",
            description="Test Description"
        )

    def test_create_new_location(self):
        result = create_new_location(
            device_id=self.device.id,
            latitude=41.015137,
            longitude=28.979530,
            speed=50.25
        )
        
        self.assertIsInstance(result, Location)
        self.assertEqual(result.device, self.device)
        self.assertEqual(float(result.latitude), 41.015137)
        self.assertEqual(float(result.longitude), 28.979530)
        self.assertEqual(float(result.speed), 50.25)

        # Verify cache was set
        cache_key = DEVICES_LAST_DATA_CACHE_KEY.format(self.device.id)
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data['device']['id'], self.device.id)


    def test_update_or_create_location_summary_create(self):
        location = Location.objects.create(
            device=self.device,
            latitude=Decimal('41.015137'),
            longitude=Decimal('28.979530'),
            speed=Decimal('50.25')
        )

        result = update_or_create_location_summary(location.id)
        
        self.assertTrue(result)
        summary = LocationDailySummary.objects.get(device=self.device)
        self.assertEqual(summary.first_location, location)
        self.assertEqual(summary.last_location, location)
        self.assertEqual(summary.max_speed, location.speed)
        self.assertEqual(summary.max_speed_location, location)

    def test_update_or_create_location_summary_update(self):
        first_location = Location.objects.create(
            device=self.device,
            latitude=Decimal('41.015137'),
            longitude=Decimal('28.979530'),
            speed=Decimal('50.25')
        )
        
        # Create initial summary
        LocationDailySummary.objects.create(
            device=self.device,
            first_location=first_location,
            last_location=first_location,
            max_speed=first_location.speed,
            max_speed_location=first_location
        )

        # Create new location with higher speed
        new_location = Location.objects.create(
            device=self.device,
            latitude=Decimal('41.015137'),
            longitude=Decimal('28.979530'),
            speed=Decimal('60.25')
        )

        result = update_or_create_location_summary(new_location.id)
        
        self.assertTrue(result)
        summary = LocationDailySummary.objects.get(device=self.device)
        self.assertEqual(summary.first_location, first_location)
        self.assertEqual(summary.last_location, new_location)
        self.assertEqual(float(summary.max_speed), 60.25)
        self.assertEqual(summary.max_speed_location, new_location)

