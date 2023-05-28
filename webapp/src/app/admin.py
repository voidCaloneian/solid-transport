from django.contrib import admin
from .models import Location, Car, Cargo


admin.site.register(Car)

admin.site.register(Location)
admin.site.register(Cargo)
