from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class Location(models.Model):
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self) -> str:
        return f'{self.state} {self.city} {self.zip_code}'


class Cargo(models.Model):
    pick_up_location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='pick_up_cargos', null=True, blank=True)
    delivery_location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='delivery_cargos', null=True, blank=True)
    weight = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(1000)])
    description = models.TextField()

    def __str__(self) -> str:
        return f'#{self.id} {self.description}'


class Car(models.Model):
    current_location = models.ForeignKey('Location', on_delete=models.PROTECT, null=True, blank=True)
    payload_capacity = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(1000)])
    unique_number = models.CharField(
        max_length=5,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[1-9][0-9]{3}[A-Z]$',
                message='Уникальный номер машины должен иметь вид {1000-9999}{A-Z}, например: 1234A 4321B 4444Z'
            )
        ]
    )

    @staticmethod
    def get_random_location() -> Location | None:
        try:
            return Location.objects.order_by("?").first()
        except ObjectDoesNotExist:
            return None

    def get_and_set_random_location(self):
        self.current_location = self.get_random_location()

    def save(self, *args, **kwargs):
        if not self.current_location:
            self.get_and_set_random_location()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.unique_number