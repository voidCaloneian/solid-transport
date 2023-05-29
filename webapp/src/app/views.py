from rest_framework.mixins import  CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CarSerializer, CargoSerializer
from .services import calculate_distance
from .models import Car, Cargo


MAX_EARTH_DISTANCE_LENGTH = 999999
CAR_SERIALIZER = CarSerializer()
CARGO_SERIALIZER = CargoSerializer()
ID = 'id'

class CarPatchViewSet(UpdateModelMixin, GenericViewSet):
    """
        Редактирование машины по ID (локация (определяется по введенному zip-коду))
    """
    serializer_class = CarSerializer
    queryset = Car.objects.all()
    lookup_field = ID
    

class CargoViewSet(CreateModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    """
    CRUD операции для модели Cargo
    """
    queryset = Cargo.objects.all()
    lookup_field = ID

    def retrieve(self, request, *args, **kwargs):
        """
            Получение информации о конкретном грузе по ID 
            (локации pick-up, delivery, вес, описание, список номеров ВСЕХ машин с расстоянием до выбранного груза)
        """
        instance = self.get_object()
        cargo_data = self.get_cargo_data(instance)
        return Response(cargo_data)

    def get_cargo_data(self, cargo):
        car_distances = self.get_car_distances(cargo)
        cargo_data = {
            **CARGO_SERIALIZER.to_representation(cargo),
            'car_distances': car_distances
        }
        return cargo_data

    def get_car_distances(self, cargo):
        cars = Car.objects.filter()
        car_distances = []

        for car in cars:
            if car.current_location:
                distance = round(calculate_distance(
                    car.current_location.latitude,
                    car.current_location.longitude,
                    cargo.pick_up_location.latitude,
                    cargo.pick_up_location.longitude
                ), 3)
            else:
                distance = 'Текущее местоположение автомобиля неизвестно'
            car_info = {
                **CAR_SERIALIZER.to_representation(car),
                'distance_to_cargo': distance
            }
            car_distances.append(car_info)

        return car_distances


class CargoFilterAPIView(APIView):
    """ 
    Фильтр списка грузов (вес, мили ближайших машин до грузов) 
    """ 

    def get(self, request):
        min_weight = request.GET.get('min_weight', 1)
        max_weight = request.GET.get('max_weight', 1000)
        max_distance = float(request.GET.get('max_distance', MAX_EARTH_DISTANCE_LENGTH))

        try:
            cargos = self.filter_cargos_by_weight(min_weight, max_weight)
            cars = self.get_cars_by_payload_capacity(min_weight, max_weight)
        except ValueError:
            raise ValidationError('Минимальный и максимальный вес должен быть в диапазоне от 1 и до 1000')

        data = self.cargos_set_and_find_nearest_cars(cargos, cars, max_distance)

        return Response(data)

    @staticmethod
    def filter_cargos_by_weight(min_weight, max_weight):
        return Cargo.objects.filter(
            weight__gte=min_weight,
            weight__lte=max_weight,
            pick_up_location__isnull=False,
        )

    @staticmethod
    def get_cars_by_payload_capacity(min_weight, max_weight):
        return Car.objects.filter(
            payload_capacity__gte=min_weight,
            payload_capacity__lte=max_weight
        ).select_related('current_location')

    def cargos_set_and_find_nearest_cars(self, cargos, cars, max_distance):
        cargo_data = []
        cargo_data_hash_table = self.build_cargo_data_hash_table(cargos, cars, max_distance)

        for cargo in cargos:
            pick_up_location = cargo.pick_up_location
            zip_code = pick_up_location.zip_code

            if zip_code not in cargo_data_hash_table:
                continue

            cars_in_distance, nearest_car, nearest_car_distance = cargo_data_hash_table[zip_code]
            nearest_car_info = self.build_nearest_car_info(nearest_car, nearest_car_distance)

            cargo_info = self.build_cargo_info(cargo, cars_in_distance, nearest_car_info)
            cargo_data.append(cargo_info)

        return cargo_data

    @staticmethod
    def build_cargo_data_hash_table(cargos, cars, max_distance):
        cargo_data_hash_table = {}
        for cargo in cargos:
            pick_up_location = cargo.pick_up_location

            if pick_up_location is None:
                continue

            zip_code = pick_up_location.zip_code
            if zip_code not in cargo_data_hash_table:
                cars_in_distance, nearest_car, nearest_car_distance = CargoFilterAPIView.find_cars_in_distance_and_nearest_car(
                    pick_up_location, cars, max_distance, cargo.weight
                )
                cargo_data_hash_table[zip_code] = cars_in_distance, nearest_car, nearest_car_distance

        return cargo_data_hash_table

    @staticmethod
    def find_cars_in_distance_and_nearest_car(location, cars, max_distance, cargo_weight):
        try:
            nearest_car = None
            nearest_car_distance = MAX_EARTH_DISTANCE_LENGTH
            cars_in_distance = []
            for car in cars:
                if car.payload_capacity >= cargo_weight:
                    away_distance = calculate_distance(
                        car.current_location.latitude, car.current_location.longitude,
                        location.latitude, location.longitude
                    )
                    if away_distance <= max_distance:
                        if nearest_car_distance > away_distance:
                            nearest_car_distance = away_distance
                            nearest_car = car
                        cars_in_distance.append(car)

            return cars_in_distance, nearest_car, nearest_car_distance
        except ValueError:
            raise NotFound('Машины по указанным фильтрам не были найдены')

    @staticmethod
    def build_nearest_car_info(nearest_car, nearest_car_distance):
        if nearest_car:
            return {
                **CAR_SERIALIZER.to_representation(nearest_car),
                'distance_to_cargo': nearest_car_distance
            }
        else:
            if nearest_car_distance != MAX_EARTH_DISTANCE_LENGTH:
                return f'Машины в радиусе {nearest_car_distance} не были найдены!'
            else:
                return 'На всей земле не нашлось машины, которая была бы в состоянии транспортировать этот груз!'

    @staticmethod
    def build_cargo_info(cargo, cars_in_distance, nearest_car_info):
        return {
            **CARGO_SERIALIZER.to_representation(cargo),
            'nearest_car': nearest_car_info,
            'cars_in_distance': [
                CAR_SERIALIZER.to_representation(car) for car in cars_in_distance
            ]
        }

class CargoNearestCarsAPIView(APIView):
    """ 
    Получение списка грузов 
    (локации pick-up, delivery, количество ближайших машин до груза 
    ( <= 450 миль и cargo.weight <= car.payload_capacity)) 
    """
    def get(self, request):
        cargo_data = self.process_cargos(
            self.get_cargos(), 
            self.get_available_cars()
        )
        return Response(cargo_data)

    @staticmethod
    def get_cargos():
        return Cargo.objects.all().select_related('pick_up_location', 'delivery_location')

    @staticmethod
    def get_available_cars():
        return Car.objects.filter(
            current_location__isnull=False,
            current_location__latitude__isnull=False,
            current_location__longitude__isnull=False
        ).prefetch_related('current_location').values('current_location__latitude', 'current_location__longitude', 'payload_capacity')

    def process_cargos(self, cargos, cars):
        cargo_data = []
        cargo_data_hash_table = self.build_cargo_data_hash_table(cargos, cars)

        for cargo in cargos:
            zip_code = cargo.pick_up_location.zip_code

            if zip_code not in cargo_data_hash_table:
                continue

            nearest_cars_count = cargo_data_hash_table[zip_code]
            cargo_info = self.build_cargo_info(cargo, nearest_cars_count)
            cargo_data.append(cargo_info)

        return cargo_data

    @staticmethod
    def build_cargo_data_hash_table(cargos, cars):
        cargo_data_hash_table = {}
        for cargo in cargos:
            pick_up_location = cargo.pick_up_location
            delivery_location = cargo.delivery_location

            if pick_up_location is None or delivery_location is None:
                continue

            zip_code = pick_up_location.zip_code
            if zip_code not in cargo_data_hash_table:
                nearest_cars_count = CargoNearestCarsAPIView.calculate_nearest_cars_count(cargo, cars)
                cargo_data_hash_table[zip_code] = nearest_cars_count

        return cargo_data_hash_table

    @staticmethod
    def calculate_nearest_cars_count(cargo, cars, default_away_distance=450):
        nearest_cars_count = 0
        for car in cars:
            if car['payload_capacity'] <= cargo.weight:
                away_distance = calculate_distance(
                    car['current_location__latitude'], car['current_location__longitude'],
                    cargo.pick_up_location.latitude, cargo.pick_up_location.longitude
                )
                if away_distance <= default_away_distance:
                    nearest_cars_count += 1

        return nearest_cars_count

    @staticmethod
    def build_cargo_info(cargo, nearest_cars_count):
        cargo_info = {
            **CARGO_SERIALIZER.to_representation(cargo),
            'nearest_cars_count': nearest_cars_count,
        }
        return cargo_info
