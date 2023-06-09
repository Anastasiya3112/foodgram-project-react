![example workflow](https://github.com/Anastasiya3112/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

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
* cd foodgram-project-react/

### Переходим в папку с файлом docker-compose.yaml:
* cd infra/

### Создаем файл .env с содержимым:
* DB_ENGINE=django.db.backends.postgresql 
* DB_NAME=postgres 
* POSTGRES_USER=postgres 
* POSTGRES_PASSWORD=postgres31
* DB_HOST=db 
* DB_PORT=5432

### Установка и запуск приложения в контейнерах:
* docker-compose up -d

### Запускаем миграций, создаём суперпользователя, сбор статики и заполнение БД:
* docker-compose exec backend python manage.py migrate
* docker-compose exec backend python manage.py createsuperuser
* docker-compose exec backend python manage.py import_ingredients_csv
* docker-compose exec backend python manage.py import_tags_csv

### Собираем статику:
* docker-compose exec backend python manage.py collectstatic --no-input

## Автор:
* Анастасия Карелина

## Документация к API:
Полная документация прокта (redoc) доступна по адресу http://158.160.37.188/api/docs/redoc.html
