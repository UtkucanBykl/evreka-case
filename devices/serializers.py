from celery import chain

from rest_framework import serializers

from devices.models import Device
from devices.tasks import create_new_location, update_or_create_location_summary

class LocationCreateSerializer(serializers.Serializer):
    device_id = serializers.PrimaryKeyRelatedField(queryset=Device.objects.all())
    latitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
    )
    longitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
    )
    speed = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
    )

    def create(self, validated_data):
        task_chain = chain(
            create_new_location.s(
                device_id=validated_data['device_id'],
                latitude=float(validated_data['latitude']), 
                longitude=float(validated_data['longitude']),
                speed=float(validated_data['speed']) if validated_data.get('speed') else None
            ),
            update_or_create_location_summary.s()
        )

        task_chain.apply_async()
        
        return validated_data




class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = (
            'id',
            'name', 
            'description'
        )


class LocationReadSerializer(serializers.ModelSerializer):
    device = DeviceSerializer()

    class Meta:
        from devices.models import Location
        model = Location
        fields = (
            'id',
            'device',
            'latitude',
            'longitude',
            'speed',
            'timestamp'
        )
        read_only_fields = fields




