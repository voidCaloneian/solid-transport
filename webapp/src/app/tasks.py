from .models import Car, Location
from proj.celery import app

from random import choice


@app.task
def update_all_cars_locations():
    """
    Функция обновления локаций у всех автомобилей, запускается каждые 3 минуты
    """
    locations = tuple(Location.objects.all())
    cars = Car.objects.all()

    for car in cars:
        randomed_location = choice(locations)
        car.current_location = randomed_location

    Car.objects.bulk_update(cars, ('current_location',))