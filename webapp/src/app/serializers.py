from rest_framework import serializers

from .services import try_to_get_location
from .models import Location, Cargo, Car


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
        
    def to_representation(self, instance):
        return str(instance)
    
    
class CargoSerializer(serializers.ModelSerializer):
    pick_up_location_zip_code = serializers.CharField(write_only=True)
    delivery_location_zip_code = serializers.CharField(write_only=True)
    pick_up_location = serializers.SerializerMethodField()
    delivery_location = serializers.SerializerMethodField()

    class Meta:
        model = Cargo
        fields = '__all__'
        
    def get_pick_up_location(self, obj):
        return str(obj.pick_up_location)

    def get_delivery_location(self, obj):
        return str(obj.delivery_location)

    def create(self, validated_data):
        pick_up_location_zip_code = validated_data.pop('pick_up_location_zip_code')
        delivery_location_zip_code = validated_data.pop('delivery_location_zip_code')

        pick_up_location = try_to_get_location(pick_up_location_zip_code)
        delivery_location = try_to_get_location(delivery_location_zip_code)

        cargo = Cargo.objects.create(
            pick_up_location=pick_up_location,
            delivery_location=delivery_location,
            **validated_data
        )
        return cargo
            

class CarSerializer(serializers.ModelSerializer):
    current_location_zip_code = serializers.CharField(write_only=True)
    current_location =  serializers.SerializerMethodField()
    
    class Meta: 
        model = Car
        fields = '__all__'
        
    def get_current_location(self, obj):
        return str(obj.current_location)

    def update(self, instance, validated_data):
        current_location_zip_code = validated_data.pop('current_location_zip_code', None)

        if current_location_zip_code:
            current_location = try_to_get_location(current_location_zip_code)
            instance.current_location = current_location

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance