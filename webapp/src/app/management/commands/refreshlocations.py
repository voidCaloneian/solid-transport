from django.core.management.base import BaseCommand
from app.models import Location
from src.settings import BASE_DIR

import pandas as pd


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.csv_file_name = BASE_DIR / 'app/data/uszips.csv'  
        self.load_locations(self.csv_file_name)

    def load_locations(self, csv_file):
        self.clear_locations()
        locations = self.read_csv(csv_file)
        self.save_locations(locations)
        
        print(f'Локации из файла {self.csv_file_name} были успешно загружены')

    @staticmethod
    def clear_locations():
        Location.objects.all().delete()

    @staticmethod
    def read_csv(csv_file):
        try:
            dtype_dict = {
                'city': str,
                'state_name': str,
                'zip': str,
                'lat': float,
                'lng': float
            }
            columns_to_read = list(dtype_dict.keys())
            
            locations = pd.read_csv(csv_file, usecols=columns_to_read, dtype=dtype_dict)
        except FileNotFoundError:
            print(f'Файл по пути {csv_file} не был найден')
            raise SystemExit
        return locations

    @staticmethod
    def save_locations(locations):
        expected_columns = ('city', 'state_name', 'zip', 'lat', 'lng')
        if not all(col in locations.columns for col in expected_columns):
            print('Ожидалось наличие этих столбцов:', expected_columns)
            raise SystemExit
        
        locations_amount = len(locations) - 1 #  Отнял единицу у количества локаций, чтобы не добавлять в цикле каждый раз к индексу единицу
        one_percent_locations_amount = int(locations_amount / 100)
        
        for index, row in locations.iterrows():
            if index % one_percent_locations_amount == 0:
                progress_in_percents = index // one_percent_locations_amount
                print(f'Выгрузка локаций завершена на {progress_in_percents}%')
            try:
                Location.objects.create(
                    city=row['city'],
                    state=row['state_name'],
                    zip_code=row['zip'],
                    latitude=float(row['lat']),
                    longitude=float(row['lng'])
                )
            except (TypeError, ValueError):
                print(f'Неверный тип данных в строке под номером {index}')
            except Exception as e:
                print(f'Ошибка во время обработки строки под номером {index}: {type(e).__name__}')

