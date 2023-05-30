
## Установка проекта

```code
git clone https://github.com/voidCaloneian/solid-transport.git
cd solid-transport
docker-compose build
docker-compose run django sh -c “python3 ./src/manage.py makemigrations && python3 ./src/manage.py migrate && python3 ./src/manage.py initlocationsdata && python3 ./src/manage.py initcarsdata“ && docker-compose up 
echo !
```

# Добавленные команды
    - initlocationsdata - выгрузка локаций из uszips.csv файла через pandas
    - initcarsdata - генерация и добавление 20 машин со случайными данными

## Работа с API

- Создание нового груза (характеристики локаций pick-up, delivery определяются по введенному zip-коду)
    - Отправляем **POST** запрос на ```http://127.0.0.1:8000/api/cargo/```
    - Пример body запроса:
	     ```code
	    {
			"description": "Везем коня",
			"weight": 277,
			"pick_up_location_zip_code": "00950",
			"delivery_location_zip_code": "00636"
		}
		```
	 
- Получение списка грузов (локации pick-up, delivery, количество ближайших машин до груза ( =< 450 миль))
	 -  Отправляем **GET** запрос на ```http://127.0.0.1:8000/api/cargo/list/```
- Получение информации о конкретном грузе по ID (локации pick-up, delivery, вес, описание, список номеров ВСЕХ машин с расстоянием до выбранного груза)
	-  Отправляем **GET** запрос на ```http://127.0.0.1:8000/api/cargo/айди_груза/```
- Редактирование машины по ID (локация (определяется по введенному zip-коду))
	 - Отправляем **PATCH** запрос на  ```http://127.0.0.1:8000/api/car/patch/айди_машины/```
	- Пример  body запроса:
		 ```code
		{
			"current_location_zip_code":  "68018",
			"payload_capacity":  265,
			"unique_number":  "2100A"
		}
		```
- Редактирование груза по ID (вес, описание)
	-  Отправляем **PATCH** запрос  на ```http://127.0.0.1:8000/api/cargo/айди_груза/```
	- Пример body запроса:
	  ```
      {
		"weight":  189,
		"description":  "Транспортируем Коня назад (вес меньше, так как конь похудел)"
	  }
		```
- Удаление груза по ID
  - Отправляем **DELETE** запрос на ```http://127.0.0.1:8000/api/cargo/айди_груза/```
- Фильтр списка грузов (вес, мили ближайших машин до грузов)
	- Отправляем **GET** запрос на ```http://127.0.0.1:8000/api/cargo/filter/?min_weight=277&max_weight=277&max_distance=1100```
	  - Где:
		- min_weight - минимальный вес груза
		- max_weight - максимальный вес груза
		- max_distance - максимальная дистанция 
		
	  
# Как и требовалось, локации обновляются раз в 3 минуты через celery
