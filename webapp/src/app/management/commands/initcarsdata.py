from django.core.management.base import BaseCommand
from django.db.utils import ProgrammingError

from app.models import Car

from random import randint, choice
from string import ascii_uppercase

class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Создаём машины')
        self.create_cars()
        print('Машины были успешно созданы')
            
    def create_cars(self):
        try:
            
            for _ in range(20):
                
                car = Car.objects.create(
                    unique_number=self.generate_and_validate_unique_car_number(),
                    current_location=Car.get_random_location(),
                    payload_capacity=randint(1, 1000)
                )
                car.save()
        except ProgrammingError:
            raise ProgrammingError('Миграции в базе данных не были проведены')
        
    def generate_and_validate_unique_car_number(self):
        while True:
            try:
                unique_number = self.generate_unique_car_number()
                Car.objects.get(unique_number=unique_number)
            except Car.DoesNotExist:
                return unique_number
        
    @staticmethod
    def generate_unique_car_number():
        four_digits = randint(1000, 9999)
        last_upper_letter = choice(ascii_uppercase)
        return f'{four_digits}{last_upper_letter}'
        
        
