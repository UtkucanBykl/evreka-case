from django_filters import rest_framework as filters
from .models import Location


class LocationFilter(filters.FilterSet):
    
    # Filter by latitude range
    min_latitude = filters.NumberFilter(field_name='latitude', lookup_expr='gte')
    max_latitude = filters.NumberFilter(field_name='latitude', lookup_expr='lte')
    
    # Filter by longitude range 
    min_longitude = filters.NumberFilter(field_name='longitude', lookup_expr='gte')
    max_longitude = filters.NumberFilter(field_name='longitude', lookup_expr='lte')
    
    # Filter by timestamp range
    start_date = filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    end_date = filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    
    # Filter by device
    device = filters.CharFilter(field_name='device__name', lookup_expr='icontains')

    class Meta:
        model = Location
        fields = ('device', 'min_latitude', 'max_latitude', 'min_longitude', 'max_longitude', 
                 'start_date', 'end_date')
