# Event Hub

> **Демо:** [event-hub.codewithvadim.dev](https://event-hub.codewithvadim.dev)

> [English version](README.md)

Платформа для управления мероприятиями: регистрация пользователей, создание событий с картой, запись участников, личные сообщения, AI-ассистент и realtime-уведомления.

Учебный pet-проект, демонстрирующий асинхронный Python, SQLAlchemy 2.0, фоновые задачи, WebSockets и полный стек с Docker.

## Live Demo

| Ресурс | URL |
|--------|-----|
| Сайт | [event-hub.codewithvadim.dev](https://event-hub.codewithvadim.dev) |
| API | [event-hub.codewithvadim.dev/api](https://event-hub.codewithvadim.dev/api) |
| Swagger | [event-hub.codewithvadim.dev/api/docs](https://event-hub.codewithvadim.dev/api/docs) |
| Health check | [event-hub.codewithvadim.dev/health](https://event-hub.codewithvadim.dev/health) |

## Features

- **Аутентификация** — подтверждение email через SMTP, регистрация и вход через JWT (python-jose + bcrypt)
- **Профиль пользователя** — смена username, пароля и email с подтверждением
- **Часовые пояса** — IANA timezone для каждого пользователя (например, `Europe/Moscow`), валидация при регистрации
- **События** — CRUD, фильтрация, пагинация, лимиты участников, история, локация с координатами
- **Карты** — интерактивный выбор места на фронтенде (Geoapify + Leaflet)
- **Регистрации** — запись и отмена участия с валидацией
- **Сообщения** — личные чаты 1-на-1: диалоги, история, unread, очистка и удаление
- **Realtime** — WebSocket-обновления новых сообщений и счётчика unread (Redis pub/sub)
- **AI-ассистент** — личный чат на базе Ollama с памятью диалога; умеет создавать события прямо в чате
- **Уведомления** — фоновая обработка через ARQ worker и Redis (в том числе о новых сообщениях)
- **Кэширование** — Redis для часто запрашиваемых данных (события, диалоги, unread)
- **Frontend** — Nuxt 4 SPA с Pinia и i18n (страница `/chats` для user- и AI-чата)
- **Тестирование** — pytest + httpx для ключевой логики API
- **Инфраструктура** — Docker Compose (PostgreSQL, Redis, Nginx, Ollama)

### Часовые пояса

- У каждого пользователя в профиле хранится IANA timezone (`UTC` по умолчанию).
- Валидация через Python `zoneinfo` (например, `Asia/Tokyo`, `America/New_York`).
- Все даты в БД хранятся в UTC (`DateTime(timezone=True)`); timezone пользователя используется для отображения на клиенте.

### Сообщения и Realtime

- Приватные диалоги между двумя зарегистрированными пользователями.
- Пагинация по курсору, мягкое удаление, очистка истории, удаление диалога.
- Отслеживание прочитанных/непрочитанных и общий счётчик unread.
- Новые сообщения создают in-app уведомления, инвалидируют кэш и отправляют WebSocket-события (`message.new`, `unread.updated`).
- Подключение клиента: `WebSocket /realtime/ws?token=<JWT>`.

### AI-ассистент

- Опциональный помощник для авторизованных пользователей на базе [Ollama](https://ollama.com/).
- История чата сохраняется per user; контекст передаётся модели при каждом запросе.
- Можно отключить через `AI_ENABLED=false`, если Ollama не нужен.
- Модель по умолчанию: `qwen2.5:3b` (настраивается через `AI_MODEL`).

**Создание события через AI-чат**

1. Откройте AI-виджет на любой странице событий (иконка робота в правом нижнем углу).
2. Попросите создать событие — например: *«Создай событие»* или *"Create an event"*.
3. Ассистент по диалогу собирает недостающие поля: название, дату/время (в timezone пользователя), описание, локацию и лимит участников — по желанию.
4. Когда данных достаточно, API возвращает `draft` с `ready_to_create: true`, и в чате появляется кнопка **Confirm**.
5. После подтверждения событие создаётся через `POST /ai/events/create` и появляется в **Мои события**.

Ассистент также отвечает на вопросы про UI (*«как создать событие»*, *"how to create"*) пошаговыми инструкциями, не запуская создание через чат.

### Локации событий

- У события есть текстовое поле `location` и опциональные `latitude` / `longitude`.
- На фронтенде используется Geoapify для геокодинга, автодополнения и тайлов карты.
- Для карт в UI нужен `NUXT_PUBLIC_GEOAPIFY_API_KEY`.

## Tech Stack

| Слой | Технологии |
|------|------------|
| Backend | Python 3.14, FastAPI, Pydantic v2 |
| ORM & DB | SQLAlchemy 2.0 (async), PostgreSQL 16, Alembic |
| Auth | JWT (python-jose), bcrypt |
| Cache & Jobs | Redis, ARQ |
| AI | Ollama, httpx |
| Realtime | WebSockets, Redis pub/sub |
| Maps | Geoapify, Leaflet (frontend) |
| Email (dev) | MailHog |
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

4. **Скачайте AI-модель (только при первом запуске, если AI включён):**

   ```bash
   make ollama-pull
   ```

5. **Проверка работоспособности (локально):**

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
| MailHog (dev) | http://localhost:8025 |
| Ollama (dev) | http://localhost:11434 |
| PostgreSQL | localhost:`POSTGRES_PORT` (по умолчанию 5436) |

### Полезные команды (Makefile)

```bash
make help          # список всех команд
make down          # остановить контейнеры
make logs          # логи API
make migrate       # применить миграции
make migration msg="описание"  # создать миграцию
make test-docker   # запустить pytest в контейнере
make ollama-pull   # скачать AI-модель в Ollama
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
| `AI_ENABLED` | Включить AI-ассистент | `true` |
| `AI_MODEL` | Имя модели Ollama | `qwen2.5:3b` |
| `AI_TIMEOUT_SECONDS` | Таймаут AI-запроса | `120` |
| `SMTP_HOST` | SMTP-сервер (MailHog в dev) | `mailhog` |
| `SMTP_PORT` | Порт SMTP | `1025` |
| `SMTP_FROM_EMAIL` | Email отправителя | `noreply@eventhub.local` |
| `PGADMIN_DEFAULT_EMAIL` | Email pgAdmin (dev) | `admin@local.dev` |
| `PGADMIN_DEFAULT_PASSWORD` | Пароль pgAdmin (dev) | `admin` |
| `NUXT_PUBLIC_API_BASE` | Базовый URL API для фронтенда | `http://localhost/api` |
| `WEB_APP_BASE_URL` | Публичный URL сайта (письма, ссылки) | `https://event-hub.codewithvadim.dev` |
| `DOMAIN` | Публичный домен | `event-hub.codewithvadim.dev` |
| `CORS_ORIGINS` | Разрешённые CORS origins (через запятую) | `https://event-hub.codewithvadim.dev` |
| `NUXT_PUBLIC_GEOAPIFY_API_KEY` | API-ключ Geoapify для карт | `your-key` |

## API Overview

Полная документация — в Swagger (`/docs`). Краткий обзор:

### Auth и пользователи

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/auth/register` | Регистрация (отправляет код; принимает `timezone`) |
| POST | `/auth/verify-email` | Подтверждение email и получение JWT |
| POST | `/auth/resend-verification-code` | Повторная отправка кода |
| POST | `/auth/login` | Вход, получение JWT |
| GET | `/auth/me` | Текущий пользователь (включая `timezone`) |
| GET | `/users/` | Список зарегистрированных пользователей |
| PATCH | `/users/me` | Обновление профиля |
| GET | `/users/me/events` | События, созданные текущим пользователем |
| GET | `/users/me/joined-events` | События, на которые записан пользователь |

### События

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/events/` | Создать событие (поля `location`, `latitude`, `longitude`) |
| GET | `/events/` | Предстоящие события (фильтры, пагинация) |
| GET | `/events/history` | Прошедшие события |
| GET | `/events/{id}` | Детали события |
| PATCH | `/events/{id}` | Обновить событие |
| DELETE | `/events/{id}` | Удалить событие |
| POST | `/events/{id}/join` | Записаться на событие |
| DELETE | `/events/{id}/leave` | Отменить участие |
| GET | `/events/{id}/participants` | Участники события |

### Диалоги

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/conversations/` | Список диалогов пользователя |
| GET | `/conversations/available-users` | Пользователи, с которыми можно начать чат |
| POST | `/conversations/` | Начать или получить диалог |
| GET | `/conversations/unread-count` | Общее число непрочитанных |
| GET | `/conversations/{id}/messages` | История сообщений (cursor pagination) |
| POST | `/conversations/{id}/messages` | Отправить сообщение |
| POST | `/conversations/{id}/read` | Отметить диалог прочитанным |
| POST | `/conversations/{id}/clear` | Очистить историю диалога |
| DELETE | `/conversations/{id}` | Удалить диалог |
| DELETE | `/conversations/{id}/messages/{message_id}` | Мягкое удаление своего сообщения |

### AI

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/ai/health` | Статус AI (`enabled`, `available`, `model`) |
| GET | `/ai/messages` | История AI-чата пользователя |
| POST | `/ai/chat` | Отправить сообщение (может вернуть `draft` + `ready_to_create`) |
| POST | `/ai/events/create` | Создать событие из подтверждённого черновика |
| DELETE | `/ai/messages` | Очистить историю AI-чата |

### Realtime

| Протокол | Путь | Описание |
|----------|------|----------|
| WebSocket | `/realtime/ws?token=<JWT>` | Live-обновления: `message.new`, `unread.updated` |

### Прочее

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/notifications/my` | Уведомления пользователя |
| GET | `/health` | Health check |

## Структура проекта

```
event_hub/
├── api/           # FastAPI backend, миграции, тесты, ARQ worker, AI и realtime
├── web/           # Nuxt frontend (события, чаты, карта, AI-виджет)
├── nginx/         # Reverse proxy (API + Web + WebSocket upgrade)
├── docker/        # Init-скрипты для PostgreSQL
├── docker-compose.yml
├── docker-compose.dev.yml
└── Makefile
```
