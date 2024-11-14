from django.urls import path, include
from rest_framework.routers import DefaultRouter

from devices import views

router = DefaultRouter()
router.register(r'devices', views.DeviceViewSet)
router.register(r'locations', views.LocationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
