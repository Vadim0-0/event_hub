# Event Hub

> [English version](README.md)

Платформа для управления мероприятиями: регистрация пользователей, создание событий, запись участников и уведомления.

Учебный pet-проект, демонстрирующий асинхронный Python, SQLAlchemy 2.0, фоновые задачи и полный стек с Docker.

## Features

- **Аутентификация** — регистрация и вход через JWT (python-jose + bcrypt)
- **События** — CRUD, фильтрация, пагинация, лимиты участников
- **Регистрации** — запись и отмена участия с валидацией
- **Уведомления** — фоновая обработка через ARQ worker и Redis
- **Кэширование** — Redis для часто запрашиваемых данных
- **Frontend** — Nuxt 4 SPA с Pinia и i18n
- **Тестирование** — pytest + httpx для ключевой логики API
- **Инфраструктура** — Docker Compose (PostgreSQL, Redis, Nginx)

## Tech Stack

| Слой | Технологии |
|------|------------|
| Backend | Python 3.14, FastAPI, Pydantic v2 |
| ORM & DB | SQLAlchemy 2.0 (async), PostgreSQL 16, Alembic |
| Auth | JWT (python-jose), bcrypt |
| Cache & Jobs | Redis, ARQ |
| Frontend | Nuxt 4, Vue 3, Pinia, Tailwind CSS |
| Tests | pytest, pytest-asyncio, httpx |
| Infra | Docker, Docker Compose, Nginx |

## Quick Start

### Требования

- Docker и Docker Compose

### Запуск

1. **Клонируйте репозиторий и перейдите в папку:**

   ```bash
   git clone <your-repo-url>
   cd event_hub
   ```

2. **Настройте переменные окружения:**

   ```bash
   cp .env.example .env
   # Отредактируйте .env при необходимости
   ```

3. **Запустите сервисы:**

   ```bash
   docker compose up -d --build
   # или
   make up
   ```

4. **Проверка работоспособности:**

   | Сервис | URL |
   |--------|-----|
   | Web (Nginx) | http://localhost |
   | API | http://localhost/api |
   | Swagger | http://localhost/api/docs |
   | Health check | http://localhost/health |

## Разработка

Для локальной разработки с hot reload API и отдельным портом для фронтенда:

```bash
make dev
# или
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

| Сервис | URL |
|--------|-----|
| API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| Web | http://localhost:3000 |
| pgAdmin | http://localhost:5050 |
| PostgreSQL | localhost:`POSTGRES_PORT` (по умолчанию 5436) |

### Полезные команды (Makefile)

```bash
make help          # список всех команд
make down          # остановить контейнеры
make logs          # логи API
make migrate       # применить миграции
make migration msg="описание"  # создать миграцию
make test-docker   # запустить pytest в контейнере
make shell-api     # shell внутри api-контейнера
make shell-db      # psql в postgres
```

### Миграции

```bash
make migration msg="initial schema"
make migrate
```

Тестовая БД `event_hub_test` создаётся автоматически при первом запуске PostgreSQL (скрипт `docker/postgres/init-test-db.sql`).

Для локального запуска pytest без Docker настройте `api/tests/.env.test` по примеру `api/tests/.env.test.example`.

## Переменные окружения

| Переменная | Описание | Пример |
|------------|----------|--------|
| `POSTGRES_USER` | Пользователь БД | `postgres` |
| `POSTGRES_PASSWORD` | Пароль | `password` |
| `POSTGRES_DB` | Имя БД | `event_hub` |
| `POSTGRES_PORT` | Порт PostgreSQL на хосте | `5436` |
| `SECRET_KEY` | Ключ для JWT | случайная строка |
| `REDIS_PORT` | Порт Redis на хосте | `6379` |
| `PGADMIN_DEFAULT_EMAIL` | Email pgAdmin (dev) | `admin@local.dev` |
| `PGADMIN_DEFAULT_PASSWORD` | Пароль pgAdmin (dev) | `admin` |
| `NUXT_PUBLIC_API_BASE` | Базовый URL API для фронтенда | `http://localhost/api` |

## API Overview

Полная документация — в Swagger (`/docs`). Краткий обзор:

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/auth/register` | Регистрация |
| POST | `/auth/login` | Вход, получение JWT |
| GET | `/auth/me` | Текущий пользователь |
| POST | `/events/` | Создать событие |
| GET | `/events/` | Список событий (фильтры, пагинация) |
| GET | `/events/count` | Количество предстоящих событий |
| GET | `/events/{id}` | Детали события |
| PATCH | `/events/{id}` | Обновить событие |
| DELETE | `/events/{id}` | Удалить событие |
| POST | `/events/{id}/join` | Записаться на событие |
| DELETE | `/events/{id}/leave` | Отменить участие |
| GET | `/events/{id}/participants` | Участники события |
| GET | `/events/me` | События, созданные пользователем |
| GET | `/events/joined/me` | События, на которые записан пользователь |
| GET | `/notifications/my` | Уведомления пользователя |
| GET | `/health` | Health check |

## Структура проекта

```
event_hub/
├── api/           # FastAPI backend, миграции, тесты, ARQ worker
├── web/           # Nuxt frontend
├── nginx/         # Reverse proxy (API + Web)
├── docker/        # Init-скрипты для PostgreSQL
├── docker-compose.yml
├── docker-compose.dev.yml
└── Makefile
```
