from rest_framework.serializers import ValidationError

from .models import Location

from geopy.distance import geodesic


def calculate_distance(lat1, long1, lat2, long2) -> float:
        point1 = (lat1, long1)
        point2 = (lat2, long2)
        distance_miles = geodesic(point1, point2).miles
        return distance_miles

def try_to_get_location(zip_code):
        try:
            location = Location.objects.get(zip_code=zip_code)
            return location
        except Location.DoesNotExist:
            raise ValidationError(f'Адресс с почтовым индексом {zip_code} не был найден')