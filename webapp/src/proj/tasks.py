# from app.models import Car, Location

from celery import shared_task
from random import choice
from django.apps import apps

@shared_task
def sayHello():
    for _ in range(15):
        print('hello')

@shared_task
def update_all_cars_locations():
    """
    Функция обновления локаций у всех автомобилей, запускается каждые 3 минуты
    """
    Location = apps.get_model(app_label='app', model_name='Location')
    Car = apps.get_model(app_label='app', model_name='Car')
    locations = tuple(Location.objects.all())
    cars = Car.objects.all()

    for car in cars:
        randomed_location = choice(locations)
        car.current_location = randomed_location

    Car.objects.bulk_update(cars, ('current_location',))