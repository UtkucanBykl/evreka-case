from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Device, Location
from django.core.cache import cache

from devices.serializers import (
    DeviceSerializer,
    LocationCreateSerializer,
    LocationReadSerializer
)
from devices.filters import LocationFilter
from devices.constants import DEVICES_LAST_DATA_CACHE_KEY


class LocationViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     viewsets.GenericViewSet):
    queryset = Location.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = LocationFilter

    def get_serializer_class(self):
        if self.action == 'create':
            return LocationCreateSerializer
        return LocationReadSerializer


class DeviceViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin, 
                   viewsets.GenericViewSet):
    
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    @action(detail=True, methods=['get'])
    def last_location(self, request, pk=None):
        cache_key = DEVICES_LAST_DATA_CACHE_KEY.format(pk)
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        # If not in cache, get latest location from DB
        try:
            latest_location = Location.objects.filter(
                device_id=pk
            ).select_related('device').latest('timestamp')
            
            location_data = LocationReadSerializer(latest_location).data
            cache.set(cache_key, location_data, timeout=3600)
            
            return Response(location_data)

        except Location.DoesNotExist:
            return Response(
                {"detail": "No location data found for this device"},
                status=status.HTTP_404_NOT_FOUND
            )

