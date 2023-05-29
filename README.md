
## Почти закончил API, но вакансия ушла в архив, поэтому не настроил celery, а так API полностью рабочее.
# **Тестовое задание web-программист Python** (Middle)

### #API: Сервис поиска ближайших машин для перевозки грузов.

<aside>
🔥 Необходимо разработать REST API сервиc для поиска ближайших машин к грузам.

</aside>

## ◼Стек и требования:

- [x]  **Python** (Django Rest Framework / FastAPI) на выбор.
- [x]  **DB** - Стандартный PostgreSQL.
- [x]  Приложение должно запускаться в docker-compose без дополнительных доработок.
- [x]  Порт - 8000.
- [x]  БД по умолчанию должна быть заполнена 20 машинами.
- [x]  Груз обязательно должен содержать следующие характеристики:
    - локация pick-up;
    - локация delivery;
    - вес (1-1000);
    - описание.
- [x]  Машина обязательно должна в себя включать следующие характеристики:
    - уникальный номер (цифра от 1000 до 9999 + случайная заглавная буква английского алфавита в конце, пример: "1234A", "2534B", "9999Z")
    - текущая локация;
    - грузоподъемность (1-1000).
- [x]  Локация должна содержать в себе следующие характеристики:
    - город;
    - штат;
    - почтовый индекс (zip);
    - широта;
    - долгота.
- [x]  *Список уникальных локаций представлен в прикрепленном csv файле "uszips.csv".*
    
    [uszips.csv](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/73ce520f-5205-47d4-8169-2266c628f6a7/uszips.csv)
    
    - [x]  *Необходимо осуществить выгрузку списка в базу данных Postgres при запуске приложения.*
- [x]  При создании машин по умолчанию локация каждой машины заполняется случайным образом;
- [x]  Расчет и отображение расстояния осуществляется в милях;
- [x]  Расчет расстояния должен осуществляться с помощью библиотеки geopy. help(geopy.distance). Маршруты не учитывать, использовать расстояние от точки до точки.

<aside>
⭐ Задание разделено на 2 уровня сложности. Дедлайн по времени выполнения зависит от того, сколько уровней вы планируете выполнить.
**1 уровень** - 3 рабочих дня.
**2 уровень** - 4 рабочих дня.

</aside>

## ◼Уровень 1

Сервис должен поддерживать следующие базовые функции:

- [x]  Создание нового груза (характеристики локаций pick-up, delivery определяются по введенному zip-коду);
- [x]  Получение списка грузов (локации pick-up, delivery, количество ближайших машин до груза ( =< 450 миль));
- [x]  Получение информации о конкретном грузе по ID (локации pick-up, delivery, вес, описание, список номеров ВСЕХ машин с расстоянием до выбранного груза);
- [x]  Редактирование машины по ID (локация (определяется по введенному zip-коду));
- [x]  Редактирование груза по ID (вес, описание);
- [x]  Удаление груза по ID.

### ◼Уровень 2

Все что в уровне 1 + дополнительные функции:

- [x]  Фильтр списка грузов (вес, мили ближайших машин до грузов);
- [x]  Автоматическое обновление локаций всех машин раз в 3 минуты (локация меняется на другую случайную).
