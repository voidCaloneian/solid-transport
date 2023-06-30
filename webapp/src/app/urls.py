from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import (
    CargoFilterAPIView,
    CargoNearestCarsAPIView,
    CarPatchAPIView,
    CargoViewSet,
)


router = DefaultRouter()
router.register('cargo', CargoViewSet, basename='cargo')

car_urls = [
    path('patch/<int:id>/', CarPatchAPIView.as_view(), name='car-patch'),
]

cargo_urls = [
    path('list/', CargoNearestCarsAPIView.as_view(), name='cargo-list'),
    path('filter/', CargoFilterAPIView.as_view(), name='cargo-filter'),
]

urlpatterns = [
    path('car/', include(car_urls)),
    path('cargo/', include(cargo_urls)),
] + router.urls
