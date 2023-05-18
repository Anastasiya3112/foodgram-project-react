# FoodGramm «Продуктовый помощник»
## Описание:
>Foodgram или «Продуктовый помощник». Сервис позволяет публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список "Избранное", а перед походом в магазин - скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Технологии:
* Python 3.8 
* Django 3.2.16
* Django REST framework 3.12.4
* Djoser 2.1.0


## Как запустить проект:

### Клонировать репозиторий и перейти в него в командной строке:
* git clone git@github.com:Anastasiya3112/foodgram-project-react.git

### Cоздать и активировать виртуальное окружение:
* python -m venv env
* source venv/Scripts/activate


### Установить зависимости из файла requirements.txt:
* python -m pip install --upgrade pip
* pip install -r requirements.txt

### Выполнить миграции:
* python manage.py makemigrations
* python manage.py migrate

### Запустить проект:
* python manage.py runserver


## Примеры запросов и ответов:
### Регистрация нового пользователя

#### Пример запроса
```URL
POST: http://127.0.0.1:8000/api/users/
```
```JSON
{
  "email": "user@example.com",
  "username": "string",
  "first_name": "string",
  "last_name": "string",
  "password": "string"
}
```
#### Пример ответа
```JSON
{
  "email": "user@example.com",
  "id": 0,
  "username": "string",
  "first_name": "string",
  "last_name": "string"
}
```
### Получение токена для авторизации
#### Пример запроса
```URL
POST: http://127.0.0.1:8000/api/auth/token/login/
```
```JSON
{
    "password": "string",
    "email": "string"
}
```
#### Пример ответа
```JSON
{
    "auth_token": "string"
}
```

### Создание рецепта
#### Пример запроса
```URL
POST: http://127.0.0.1:8000/api/recipes/
```
```JSON
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```
#### Пример ответа
```JSON
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "color": "#E26C2D",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "is_subscribed": false
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "text": "string",
  "cooking_time": 1
}
```

### Добавление рецепта в список покупок
#### Пример запроса
```URL
POST: http://127.0.0.1:8000/api/recipes/{id}/shopping_cart/
```

#### Пример ответа
```JSON
{
  "id": 0,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "cooking_time": 1
}
```

## Как посмотреть документацию:
### Переходим в папку с файлом docker-compose.yaml:
* cd infra/

### Запускаем приложения в контейнерах:
* docker-compose up

Полная документация прокта (redoc) доступна по адресу  http://localhost/api/docs/


## Автор:
* Анастасия Карелина
