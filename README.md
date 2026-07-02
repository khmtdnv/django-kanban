# fastapi-restaurant

> Микросервисное приложение для управления процессами ресторана: от просмотра меню до обработки оплаты.

---

## Содержание

- [О проекте](#о-проекте)
- [Архитектура](#архитектура)
- [Сервисы](#сервисы)
- [Стек технологий](#стек-технологий)
- [Запуск](#запуск)
- [API Gateway](#api-gateway)
- [События RabbitMQ](#события-rabbitmq)

---

## О проекте

fastapi-restaurant — микросервисное приложение, реализующее полный цикл ресторанного заказа: регистрация пользователя, просмотр меню с категориями и фото, формирование заказа, обработка оплаты и уведомления об изменении статусов.

Каждый сервис имеет собственную зону ответственности, изолированную схему в PostgreSQL и взаимодействует с остальными через REST и асинхронные события (EDA через RabbitMQ).

---

## Архитектура

```
                        ┌─────────────┐
           Клиент ───►  │   Traefik   │  (API Gateway)
                        └──────┬──────┘
                               │  JWT-валидация → ms_auth
              ┌────────────────┼─────────────────────┐
              │                │                     │
       ┌──────▼─────┐  ┌───────▼────┐  ┌────────────▼───┐
       │  ms_auth   │  │  ms_menu   │  │   ms_order     │
       │            │  │            │  │                │
       │ PostgreSQL │  │ PostgreSQL │  │  PostgreSQL    │
       │   (auth)   │  │   (menu)   │  │   (orders)     │
       └────────────┘  └─────┬──────┘  └───────┬────────┘
                             │                  │
                      ┌──────▼──────────────────▼──────┐
                      │         RabbitMQ               │
                      │  (EDA: menu / order / payment) │
                      └─────────────────┬──────────────┘
                                        │
                               ┌────────▼────────┐
                               │   ms_payment    │
                               │                 │
                               │   PostgreSQL    │
                               │   (payments)    │
                               └─────────────────┘
                      
                   Redis — кэш меню (ms_menu)
                   MinIO — хранилище фото блюд
```

---

## Сервисы

### ms_auth — Авторизация
- Регистрация по номеру телефона + подтверждение SMS-кодом (Celery)
- JWT access + refresh токены с полем `is_phone_verified`
- Роли: `user` / `superuser (admin)`
- Роуты: `/auth` (авторизация), `/users` (профиль)
- Методы `get_current_user` / `get_current_admin_user` для инъекции в эндпоинты

### ms_menu — Меню
- CRUD блюд и категорий (только для администраторов)
- Система тегов (ManyToMany): «Острое», «Вегетарианское» и др.
- Комбо-наборы из нескольких блюд со специальной ценой
- Хранение фото блюд через MinIO (S3-совместимое)
- Кэширование агрегированного меню в Redis, инвалидация по событиям RabbitMQ
- Версионирование API: `v1` — плоское, `v2` — расширенное с вложенными данными
- Пагинация результатов

### ms_order — Заказы
- Разделение корзины и оформленного заказа
- Валидация блюд через `ms_menu` (проверка наличия и цен)
- Статусы: `Создан → Готовится → Готов → Выдан / Отменён`
- Политика ретраев и каскадных откатов при недоступности сервисов
- Rate-limiting, разграничение прав по роли (клиент vs администратор)

### ms_payment — Оплата
- Мок-реализация платёжного шлюза по принципу ЮKassa / CloudPayments
- Оплата по карте и СБП, обработка через callback (без переопроса)
- Возврат средств (refund) при отмене заказа
- Уведомление `ms_order` о статусе оплаты через RabbitMQ

---

## Стек технологий

| Категория              | Технологии                             |
| ---------------------- | -------------------------------------- |
| **Язык / Фреймворк**   | Python, FastAPI, asyncio               |
| **База данных**        | PostgreSQL (отдельная схема на сервис) |
| **ORM / Миграции**     | SQLAlchemy 2.0 + asyncpg, Alembic      |
| **Кэш**                | Redis                                  |
| **Очереди / EDA**      | RabbitMQ + aio_pika                    |
| **Файловое хранилище** | MinIO (S3)                             |
| **API Gateway**        | Traefik                                |
| **Контейнеризация**    | Docker, Docker Compose (multistage)    |
| **Качество кода**      | black, flake8, isort, pre-commit       |
| **Тесты**              | Pytest                                 |
| **Валидация**          | Pydantic v2, pydantic-settings         |

---

## Запуск

### Требования
- Docker
- Docker Compose

### Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone https://github.com/khmtdnv/fastapi-restaurant.git
cd fastapi-restaurant

# 2. Создать файлы окружения
cp .env.example .env
# Заполнить переменные

# 3. Запустить все сервисы
docker compose up -d --build

# 4. Выполнить миграции для каждого сервиса
docker compose exec ms_auth alembic upgrade head
docker compose exec ms_menu alembic upgrade head
docker compose exec ms_order alembic upgrade head
docker compose exec ms_payment alembic upgrade head
```

### Переменные окружения (.env.example)

```env
# Database
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Redis
REDIS_URL=redis://redis:6379/0

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=menu-images
```

---

## API Gateway

Все запросы проходят через **Traefik**. Для защищённых маршрутов Traefik перенаправляет запрос на `ms_auth` для валидации JWT-токена перед проксированием в целевой сервис.

| Сервис | Базовый путь |
|---|---|
| ms_auth | `/auth/`, `/users/` |
| ms_menu | `/menu/` |
| ms_order | `/orders/` |
| ms_payment | `/payments/` |

Swagger-документация каждого сервиса доступна по `/{service}/docs`.

---

## События RabbitMQ

Сервисы взаимодействуют асинхронно через события (EDA):

| Событие | Издатель | Подписчики | Описание |
|---|---|---|---|
| `menu.dish.created` | ms_menu | — | Добавлено новое блюдо |
| `menu.price.change` | ms_menu | ms_order | Изменилась цена блюда |
| `menu.updated` | ms_menu | — | Обновлено меню (инвалидация кэша) |
| `menu.item.availability` | ms_menu | ms_order | Блюдо в стоп-листе |
| `order.created` | ms_order | ms_payment | Заказ оформлен, ожидает оплаты |
| `payment.success` | ms_payment | ms_order | Оплата прошла успешно |
| `payment.failed` | ms_payment | ms_order | Оплата не прошла |
