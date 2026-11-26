#!/usr/bin/env bash
# Что Render делает при каждом деплое бэкенда (поле buildCommand в render.yaml).
set -o errexit   # если любая команда упала — деплой останавливается

pip install -r requirements.txt     # 1. библиотеки из requirements.txt
python manage.py collectstatic --no-input   # 2. CSS/JS админки -> staticfiles/
python manage.py migrate            # 3. создать/обновить таблицы в PostgreSQL

# 4. Демо-книги: добавляются только те категории и книги, которых ещё нет в базе.
#    Существующие книги не трогаем, поэтому деплой не сбрасывает остатки склада и цены.
python manage.py seed_books --only-missing

# 5. Администратор для /admin/ (логин и пароль задаются в Render -> Environment).
#    Если он уже есть, команда падает — "|| true" говорит не обращать внимания.
if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py createsuperuser --no-input || true
fi
