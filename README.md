# Online Book Shop

Учебный интернет-магазин книг (KBTU, Online Shop Team).
Первая версия делает **главное действие** из Task 9:

> Покупатель кладёт книгу в корзину → оформляет заказ (книги бронируются на 15 минут, BR-01) →
> оплачивает → склад уменьшается **одной транзакцией**, поэтому книгу, которой нет, продать нельзя
> (проблема overselling из Task 04).

## Из чего состоит проект

Проект — это две отдельные программы, которые общаются друг с другом:

```
bookshop/
├── backend/    ← Django REST: сервер + база данных (порт 8000)
└── frontend/   ← Angular: сайт, который видит покупатель (порт 4200)
```

Angular показывает страницы. Когда нужны данные (список книг, оформить заказ), он отправляет
HTTP-запрос в Django. Django работает с базой данных и отвечает в формате JSON.

### backend/ — Django

| Файл | Зачем он нужен |
|---|---|
| `manage.py` | «Пульт управления» Django: через него запускаются все команды (`runserver`, `migrate`…) |
| `requirements.txt` | Список Python-библиотек, которые нужно установить |
| `config/settings.py` | Настройки: какая база данных, какие приложения подключены, CORS |
| `config/urls.py` | Главные адреса: `/admin/` и `/api/` |
| `shop/models.py` | **Таблицы базы данных** — те же 6, что в Task 9 (customers, products, orders, order_items, payments, stock_log) |
| `shop/migrations/` | Инструкции, по которым Django создаёт таблицы в базе (сгенерированы автоматически) |
| `shop/services.py` | **Бизнес-логика**: бронь на 15 минут и транзакция оплаты |
| `shop/serializers.py` | Переводят данные из базы в JSON и проверяют то, что прислал Angular |
| `shop/views.py` | «Двери» API: принимают запрос и возвращают ответ |
| `shop/urls.py` | Адреса API (`/api/products/`, `/api/orders/` …) |
| `shop/admin.py` | Админка Django — смотреть и менять таблицы без SQL |
| `shop/tests.py` | Автотесты главного действия |
| `shop/management/commands/seed_books.py` | Команда, которая добавляет 5 книг из Task 9 |

### frontend/ — Angular

| Файл | Зачем он нужен |
|---|---|
| `package.json` | Список JavaScript-библиотек и команды (`npm start`) |
| `src/index.html` | Единственная HTML-страница, внутрь неё Angular вставляет весь сайт |
| `src/styles.css` | Общий дизайн сайта |
| `src/app/app.component.*` | Шапка сайта + место для текущей страницы |
| `src/app/app.routes.ts` | Какой адрес открывает какую страницу |
| `src/app/app.config.ts` | Подключение роутера и HttpClient |
| `src/app/models.ts` | Описание формы данных (книга, заказ, оплата) |
| `src/app/services/api.service.ts` | Все запросы к Django в одном месте |
| `src/app/services/cart.service.ts` | Корзина (хранится в браузере, пока заказ не оформлен) |
| `src/app/pages/catalog/` | Страница «Каталог» |
| `src/app/pages/cart/` | Страница «Корзина» + форма покупателя |
| `src/app/pages/order/` | Страница заказа: таймер брони, оплата, история попыток оплаты |

## Как запустить на Mac

### 0. Что должно быть установлено (один раз)

Откройте **Терминал** и проверьте:

```bash
python3 --version   # нужен 3.10 или новее
node --version      # нужен 18.19 или новее (лучше 20 или 22)
```

Если чего-то нет — скачайте установщик: Python с https://www.python.org/downloads/ ,
Node.js (LTS) с https://nodejs.org/ .

### 1. Запустить backend (первое окно Терминала)

```bash
cd ~/Downloads/bookshop/backend          # перейти в папку backend (путь — где лежит проект)
python3 -m venv venv                      # создать «виртуальное окружение» — отдельную папку для библиотек проекта
source venv/bin/activate                  # включить его (в начале строки появится (venv))
pip install -r requirements.txt           # установить Django и остальные библиотеки
python manage.py migrate                  # создать таблицы в базе данных по models.py
python manage.py seed_books               # добавить 5 книг из Task 9
python manage.py runserver                # запустить сервер на http://localhost:8000
```

Окно не закрывайте — сервер работает, пока оно открыто. Остановить: `Control + C`.

В следующий раз достаточно: `cd …/backend`, `source venv/bin/activate`, `python manage.py runserver`.

### 2. Запустить frontend (второе окно Терминала: `Command + T`)

```bash
cd ~/Downloads/bookshop/frontend
npm install        # скачать библиотеки Angular в папку node_modules (только первый раз, ~1–2 мин)
npm start          # запустить сайт на http://localhost:4200
```

Откройте в браузере **http://localhost:4200** — это и есть сайт.

## Как проверить главное действие

1. В каталоге у **Atomic Habits** склад 0 — кнопка неактивна («Нет в наличии»).
2. Положите в корзину, например, 2 × «1984» и «The Little Prince».
3. В корзине заполните имя и email → **Оформить заказ**. Заказ получает статус `reserved`, идёт таймер 15 минут.
   В каталоге у «1984» теперь «Осталось 5» — 2 книги забронированы за вами.
4. Оплата — это имитация банка:
   - карта `4111 1111 1111 0000` (заканчивается на 0000) → банк отказывает, попытка сохраняется как `failed`, склад не меняется;
   - любая другая карта из 16 цифр, например `4111 1111 1111 1111` → `success`.
5. После успешной оплаты: статус `paid`, склад уменьшен, в STOCK_LOG запись `-2, sale, payment-system`.
   У заказа видно 2 попытки оплаты — это связь **ORDERS 1 : M PAYMENTS**.

### Посмотреть таблицы

```bash
python manage.py createsuperuser     # придумать логин и пароль для админки
```

Затем откройте http://localhost:8000/admin/ — там все 6 таблиц.

API можно открыть прямо в браузере:
- http://localhost:8000/api/products/ — каталог
- http://localhost:8000/api/products/low-stock/ — книги, которых меньше 10 (запрос из Task 9)
- http://localhost:8000/api/orders/1/ — заказ №1

### Запустить автотесты

```bash
python manage.py test
```

Тесты проверяют: бронь, запрет overselling, транзакцию оплаты, неудачную + удачную оплату,
истёкшую бронь, CHECK `stock_quantity >= 0` и запрет удалять покупателя с заказами (ON DELETE RESTRICT).

## PostgreSQL вместо SQLite

По умолчанию используется **SQLite** — база в одном файле `backend/db.sqlite3`, ничего ставить не нужно.
Чтобы работать с PostgreSQL (как в Task 9):

1. В pgAdmin создайте новую базу `bookshop` (не `online_shop`, чтобы не задеть командную базу).
2. Перед командами Django в том же окне Терминала выполните:

```bash
export DB_ENGINE=postgres DB_NAME=bookshop DB_USER=postgres DB_PASSWORD=ваш_пароль
python manage.py migrate
python manage.py seed_books
python manage.py runserver
```

Таблицы в pgAdmin будут называться так же, как в Task 9: `customers`, `products`, `orders`, `order_items`, `payments`, `stock_log`.

## Как это связано с Task 9

| В Task 9 | В коде |
|---|---|
| 6 таблиц, PK и FK | `shop/models.py` |
| CHECK `stock_quantity >= 0`, `price > 0`, `quantity >= 1` | `constraints` в `models.py` |
| `email`, `transaction_id` UNIQUE | `unique=True` в `models.py` |
| ON DELETE RESTRICT | `on_delete=models.PROTECT` |
| BR-01: бронь 15 минут | `create_order()` и `expire_reservations()` в `services.py` |
| Транзакция BEGIN … COMMIT / ROLLBACK | `pay_order()` в `services.py` (`transaction.atomic`) |
| `UPDATE … WHERE stock_quantity >= 1` | `Product.objects.filter(stock_quantity__gte=…).update(…)` |
| SELECT книг, которых меньше 10 | `/api/products/low-stock/` (`LowStockView` в `views.py`) |

## Роли и доступ сотрудников
Сотрудник = пользователь Django + запись в Employee с ролью
(warehouse, finance, support, manager, admin). Права определяет роль
(`shop/permissions.py`); покупатели в админку не заходят.

Создать сотрудника: `/admin/` → Users → Add user → блок Employee → Role.
Правки склада сотрудником пишутся в STOCK_LOG с его логином.
Тесты ролей: `python manage.py test shop`.

## Что ещё не сделано

- Регистрация и вход покупателя (сейчас покупатель определяется по email).
- Страница для Inventory Manager (пока — Django admin).
- Таблицы ADDRESSES и CATEGORIES (план из Task 9).
- Настоящий платёжный сервис вместо имитации.
